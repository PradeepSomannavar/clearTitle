"""
Document-level persistence operations.

Extracted verbatim from `backend/services/mysql_store.py` (document operations).
"""

from __future__ import annotations

import json
from typing import Any

from backend.database.connection import _get_conn


def init_document(*, case_id: str, doc_id: str, doc_index: int, filename: str, file_paths: dict | None = None, expected_type: str | None = None) -> None:
    with _get_conn() as conn:
        cursor = conn.cursor()
        file_paths_str = json.dumps(file_paths, ensure_ascii=False) if file_paths else None
        cursor.execute(
            "INSERT INTO documents (case_id, doc_id, doc_index, filename, status, file_paths, expected_type) "
            "VALUES (%s, %s, %s, %s, 'uploaded', %s, %s) "
            "ON DUPLICATE KEY UPDATE filename=VALUES(filename), doc_index=VALUES(doc_index), "
            "file_paths=COALESCE(VALUES(file_paths), file_paths), "
            "expected_type=VALUES(expected_type)",
            (case_id, doc_id, doc_index, filename, file_paths_str, expected_type),
        )
        conn.commit()


def update_document_status(
    *,
    case_id: str,
    doc_id: str,
    status: str,
    document_type: str | None = None,
    file_paths: dict | None = None,
    error: str | None = None,
    page_count: int = 0,
) -> None:
    with _get_conn() as conn:
        cursor = conn.cursor()
        fields: dict[str, Any] = {"status": status}
        if document_type is not None:
            fields["document_type"] = document_type
        if error is not None:
            fields["error"] = error
        if page_count:
            fields["page_count"] = page_count

        set_clause = ", ".join(f"{k} = %s" for k in fields)
        values = [*list(fields.values())]

        # Use MySQL JSON_MERGE_PATCH for atomic file_paths merge (no read-modify-write race)
        if file_paths is not None:
            for key, val in file_paths.items():
                set_clause += ", file_paths = JSON_SET(COALESCE(file_paths, '{}'), %s, %s)"
                values.extend([f"$.{key}", json.dumps(val, ensure_ascii=False) if not isinstance(val, str) else val])

        values.extend([case_id, doc_id])
        cursor.execute(
            f"UPDATE documents SET {set_clause} WHERE case_id = %s AND doc_id = %s",
            values,
        )
        conn.commit()


def get_case_documents(case_id: str) -> list[dict]:
    with _get_conn() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT doc_id, doc_index, filename, document_type, page_count, status, "
            "file_paths, error, created_at "
            "FROM documents WHERE case_id = %s ORDER BY doc_index ASC",
            (case_id,),
        )
        result = []
        for row in cursor.fetchall():
            doc = dict(row)
            if doc.get("file_paths") and isinstance(doc["file_paths"], str):
                doc["file_paths"] = json.loads(doc["file_paths"])
            result.append(doc)
        return result


def increment_retry(*, case_id: str, doc_id: str, error: str) -> None:
    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE documents SET retry_count = retry_count + 1, "
            "status = 'failed', error = %s "
            "WHERE case_id = %s AND doc_id = %s",
            (error, case_id, doc_id),
        )
        conn.commit()


def get_failed_documents(case_id: str) -> list[dict]:
    with _get_conn() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT doc_id, doc_index, filename, document_type, error, retry_count "
            "FROM documents WHERE case_id = %s AND status IN ('failed', 'pending_retry') "
            "ORDER BY doc_index ASC",
            (case_id,),
        )
        return [dict(row) for row in cursor.fetchall()]


def replace_document(
    *,
    case_id: str,
    doc_id: str,
    filename: str,
    file_paths: dict,
) -> None:
    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE documents SET "
            "filename = %s, "
            "file_paths = %s, "
            "status = 'failed', "
            "retry_count = 0, "
            "error = 'Document replaced — pending retry', "
            "document_type = '' "
            "WHERE case_id = %s AND doc_id = %s",
            (filename, json.dumps(file_paths, ensure_ascii=False),
             case_id, doc_id),
        )
        conn.commit()


def skip_document(*, case_id: str, doc_id: str) -> None:
    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE documents SET "
            "status = 'skipped', "
            "retry_count = 0, "
            "error = NULL "
            "WHERE case_id = %s AND doc_id = %s",
            (case_id, doc_id),
        )
        conn.commit()


def get_classification_failed_documents(case_id: str) -> list[dict]:
    with _get_conn() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT doc_id, doc_index, filename, document_type, error "
            "FROM documents "
            "WHERE case_id = %s AND status = 'classification_failed' "
            "ORDER BY doc_index ASC",
            (case_id,),
        )
        return [dict(row) for row in cursor.fetchall()]


def get_document_status(case_id: str, doc_id: str) -> str | None:
    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT status FROM documents WHERE case_id = %s AND doc_id = %s",
            (case_id, doc_id),
        )
        row = cursor.fetchone()
        return row[0] if row else None


def get_expected_type(case_id: str, doc_id: str) -> str | None:
    """Read the slot-declared expected_type (sale_deed/ec) for a document."""
    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT expected_type FROM documents WHERE case_id = %s AND doc_id = %s",
            (case_id, doc_id),
        )
        row = cursor.fetchone()
        return row[0] if row else None


def set_document_stage(case_id: str, doc_id: str, stage) -> None:
    status_str = stage.name.lower()
    with _get_conn() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE documents SET status = %s WHERE case_id = %s AND doc_id = %s",
            (status_str, case_id, doc_id),
        )
        conn.commit()


def load_document_paths(case_id: str, doc_id: str) -> dict:
    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT file_paths FROM documents WHERE case_id = %s AND doc_id = %s", (case_id, doc_id))
        row = cursor.fetchone()
        if row and row[0]:
            try:
                return json.loads(row[0])
            except Exception:
                pass
        return {}
