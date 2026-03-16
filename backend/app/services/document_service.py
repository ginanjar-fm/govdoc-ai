import json
import os
import uuid

from PyPDF2 import PdfReader
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.models.document import AnalysisHistory, AuditLog, Document, ExtractedMetadata
from app.services.llm_service import analyze_document


def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
    return "\n".join(text_parts)


async def upload_document(
    db: AsyncSession,
    file_content: bytes,
    filename: str,
    content_type: str,
    uploaded_by: str = "api_user",
) -> Document:
    os.makedirs(settings.upload_dir, exist_ok=True)
    stored_filename = f"{uuid.uuid4()}_{filename}"
    file_path = os.path.join(settings.upload_dir, stored_filename)

    with open(file_path, "wb") as f:
        f.write(file_content)

    # Extract text
    if content_type == "application/pdf":
        text_content = extract_text_from_pdf(file_path)
    else:
        text_content = file_content.decode("utf-8", errors="replace")

    doc = Document(
        filename=stored_filename,
        original_filename=filename,
        content_type=content_type,
        file_size=len(file_content),
        text_content=text_content,
        uploaded_by=uploaded_by,
    )
    db.add(doc)

    audit = AuditLog(
        document_id=doc.id,
        action="document_uploaded",
        actor=uploaded_by,
        details=f"Uploaded {filename} ({len(file_content)} bytes)",
    )
    db.add(audit)

    await db.flush()
    return doc


async def analyze_doc(db: AsyncSession, document_id: uuid.UUID) -> ExtractedMetadata:
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise ValueError(f"Document {document_id} not found")

    if not doc.text_content:
        raise ValueError("Document has no text content to analyze")

    analysis_record = AnalysisHistory(
        document_id=doc.id,
        analysis_type="full_analysis",
        status="pending",
    )
    db.add(analysis_record)
    await db.flush()

    try:
        result = analyze_document(doc.text_content)
        analysis = result["analysis"]

        metadata = ExtractedMetadata(
            document_id=doc.id,
            classification=analysis.get("classification", "other"),
            summary=analysis.get("summary", ""),
            entities=json.dumps(analysis.get("entities", [])),
            compliance_flags=json.dumps(analysis.get("compliance_flags", [])),
        )
        db.add(metadata)

        analysis_record.status = "completed"
        analysis_record.input_tokens = result["input_tokens"]
        analysis_record.output_tokens = result["output_tokens"]
        analysis_record.model_used = result["model"]
        analysis_record.duration_ms = result["duration_ms"]

        audit = AuditLog(
            document_id=doc.id,
            action="document_analyzed",
            actor="system",
            details=f"Analysis completed in {result['duration_ms']}ms using {result['model']}",
        )
        db.add(audit)

        await db.flush()
        return metadata

    except Exception as e:
        analysis_record.status = "failed"
        analysis_record.error_message = str(e)
        audit = AuditLog(
            document_id=doc.id,
            action="analysis_failed",
            actor="system",
            details=str(e),
        )
        db.add(audit)
        await db.flush()
        raise


async def get_document(db: AsyncSession, document_id: uuid.UUID) -> Document | None:
    result = await db.execute(
        select(Document)
        .where(Document.id == document_id)
        .options(
            selectinload(Document.metadata_records),
            selectinload(Document.analyses),
        )
    )
    return result.scalar_one_or_none()


async def list_documents(
    db: AsyncSession, search: str | None = None, skip: int = 0, limit: int = 20
) -> list[Document]:
    query = select(Document).options(
        selectinload(Document.metadata_records),
    ).order_by(Document.created_at.desc())

    if search:
        query = query.where(Document.original_filename.ilike(f"%{search}%"))

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())
