import json
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_api_key
from app.config import settings
from app.database import get_db
from app.services.document_service import (
    analyze_doc,
    get_document,
    list_documents,
    upload_document,
)

router = APIRouter(prefix="/api/documents", tags=["documents"])

ALLOWED_TYPES = {"application/pdf", "text/plain"}


def _serialize_document(doc) -> dict:
    result = {
        "id": str(doc.id),
        "filename": doc.original_filename,
        "content_type": doc.content_type,
        "file_size": doc.file_size,
        "uploaded_by": doc.uploaded_by,
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
        "has_text": bool(doc.text_content),
    }
    if hasattr(doc, "metadata_records") and doc.metadata_records:
        meta = doc.metadata_records[-1]
        result["analysis"] = {
            "classification": meta.classification,
            "summary": meta.summary,
            "entities": json.loads(meta.entities) if meta.entities else [],
            "compliance_flags": json.loads(meta.compliance_flags) if meta.compliance_flags else [],
            "analyzed_at": meta.created_at.isoformat() if meta.created_at else None,
        }
    return result


@router.post("/upload", status_code=201)
async def upload(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file.content_type}' not allowed. Accepted: {', '.join(ALLOWED_TYPES)}",
        )

    content = await file.read()
    max_size = settings.max_file_size_mb * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB",
        )

    doc = await upload_document(db, content, file.filename or "unnamed", file.content_type)
    return {"id": str(doc.id), "filename": doc.original_filename, "message": "Document uploaded successfully"}


@router.post("/{document_id}/analyze")
async def analyze(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
):
    try:
        metadata = await analyze_doc(db, document_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    return {
        "document_id": str(document_id),
        "classification": metadata.classification,
        "summary": metadata.summary,
        "entities": json.loads(metadata.entities) if metadata.entities else [],
        "compliance_flags": json.loads(metadata.compliance_flags) if metadata.compliance_flags else [],
    }


@router.get("/{document_id}")
async def get_doc(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
):
    doc = await get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return _serialize_document(doc)


@router.get("")
async def list_docs(
    search: str | None = Query(None, description="Search by filename"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
):
    docs = await list_documents(db, search=search, skip=skip, limit=limit)
    return {"documents": [_serialize_document(d) for d in docs], "count": len(docs)}


@router.get("/{document_id}/text")
async def get_text(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
):
    doc = await get_document(db, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"document_id": str(doc.id), "text_content": doc.text_content or ""}
