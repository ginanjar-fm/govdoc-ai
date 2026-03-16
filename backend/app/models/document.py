import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    text_content = Column(Text, nullable=True)
    uploaded_by = Column(String(100), default="api_user")
    created_at = Column(DateTime, default=datetime.utcnow)

    metadata_records = relationship(
        "ExtractedMetadata", back_populates="document", cascade="all, delete-orphan"
    )
    analyses = relationship(
        "AnalysisHistory", back_populates="document", cascade="all, delete-orphan"
    )
    audit_logs = relationship(
        "AuditLog", back_populates="document", cascade="all, delete-orphan"
    )


class ExtractedMetadata(Base):
    __tablename__ = "extracted_metadata"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    classification = Column(String(100), nullable=True)
    summary = Column(Text, nullable=True)
    entities = Column(Text, nullable=True)  # JSON string
    compliance_flags = Column(Text, nullable=True)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="metadata_records")


class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    analysis_type = Column(String(50), nullable=False)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    model_used = Column(String(100), nullable=True)
    duration_ms = Column(Integer, default=0)
    status = Column(
        Enum("pending", "completed", "failed", name="analysis_status"),
        default="pending",
    )
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="analyses")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=True,
    )
    action = Column(String(100), nullable=False)
    actor = Column(String(100), default="api_user")
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="audit_logs")
