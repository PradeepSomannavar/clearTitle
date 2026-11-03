"""Results payload builders for the results endpoint."""

from __future__ import annotations

from backend.database.repositories.document_repo import get_case_documents


def _case_row(case_id: str) -> dict:
    from backend.database.connection import _get_conn
    with _get_conn() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, status, total_docs, completed_docs, failed_docs, "
            "created_at, updated_at "
            "FROM cases WHERE id = %s",
            (case_id,),
        )
        row = cursor.fetchone()
    if not row:
        raise KeyError(f"Case {case_id} not found in DB")
    return dict(row)


def build_case_results(case_id: str) -> dict:
    case = _case_row(case_id)
    documents = get_case_documents(case_id)

    return {
        "case": {
            "case_id": case["id"],
            "status": case["status"],
            "total_docs": case["total_docs"],
            "completed_docs": case["completed_docs"],
            "failed_docs": case["failed_docs"],
            "created_at": case.get("created_at"),
            "updated_at": case.get("updated_at"),
        },
        "documents": [
            {
                "doc_id": d["doc_id"],
                "doc_index": d["doc_index"],
                "filename": d["filename"],
                "document_type": d.get("document_type"),
                "status": d.get("status"),
                "page_count": d.get("page_count"),
                "structured": d.get("structured_json") or {},
                "error": d.get("error"),
                "model_used": d.get("model_used"),
                "cost_usd": d.get("cost_usd"),
            }
            for d in documents
        ],
        "needs_action": _needs_action(case_id),
    }


def _needs_action(case_id: str) -> list[dict]:
    from backend.database.repositories.document_repo import get_classification_failed_documents
    return [
        {
            "doc_id": d["doc_id"],
            "filename": d["filename"],
            "message": f"'{d['filename']}' — document type not recognised.",
            "choices": [
                {"action": "skip", "method": "POST",
                 "url": f"/api/case/{case_id}/doc/{d['doc_id']}/skip",
                 "label": "Continue without this document"},
                {"action": "replace", "method": "POST",
                 "url": f"/api/case/{case_id}/doc/{d['doc_id']}/replace",
                 "label": "Upload a replacement document"},
            ],
        }
        for d in get_classification_failed_documents(case_id)
    ]
