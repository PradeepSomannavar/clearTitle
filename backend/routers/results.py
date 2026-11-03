"""Results endpoints: raw OCR output (no structured JSON)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from backend.database.repositories.case_repo import get_case_owner
from backend.logger import get_logger
from backend.services.auth import get_optional_user

router = APIRouter()
logger = get_logger(__name__)


def _enforce_access(case_id: str, user: dict | None) -> None:
    owner = get_case_owner(case_id)
    if owner and (user is None or owner != user["id"]):
        raise HTTPException(status_code=403, detail="Not your case")


@router.get("/results/{case_id}/ocr")
async def get_case_ocr(case_id: str, user: dict | None = Depends(get_optional_user)):
    """Raw OCR `full_text` for every document in a case (from outputs/<case>/ocr_raw)."""
    _enforce_access(case_id, user)
    from backend.database.repositories.document_repo import get_case_documents
    from backend.integrations.storage.file_utils import BASE_DIR, read_json

    documents = get_case_documents(case_id)
    ocr_dir = BASE_DIR / "outputs" / case_id / "ocr_raw"

    result = []
    for d in documents:
        doc_id = d["doc_id"]
        entry = {
            "doc_id": doc_id,
            "doc_index": d.get("doc_index"),
            "filename": d.get("filename"),
            "document_type": d.get("document_type"),
            "status": d.get("status"),
            "total_pages": d.get("page_count"),
            "full_text": "",
            "available": False,
        }
        merged_path = ocr_dir / f"{doc_id}_merged.json"
        if merged_path.is_file():
            try:
                merged = read_json(merged_path)
                entry["full_text"] = merged.get("full_text") or ""
                entry["total_pages"] = merged.get("total_pages") or entry["total_pages"]
                entry["available"] = bool(entry["full_text"])
            except Exception as e:  # pragma: no cover - corrupt file must not 500
                logger.warning("Failed to read OCR for %s/%s: %s", case_id, doc_id, e)
        result.append(entry)

    return {"case_id": case_id, "documents": result}
