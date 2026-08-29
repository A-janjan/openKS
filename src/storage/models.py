from sqlalchemy import Column, String, Integer, DateTime, JSON, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime, timezone

Base = declarative_base()


class Document(Base):
    __tablename__ = "documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    source = Column(String, nullable=False)  # file path or URL
    source_type = Column(String)  # "file", "url", "github", etc.
    version = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    custom_metadata = Column(JSONB, default={})


class Chunk(Base):
    __tablename__ = "document_chunks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"))
    content = Column(Text, nullable=False)
    position = Column(Integer, nullable=False)  # position of the chunk in the document
    embedding = Column(Vector(384))  # length depends on model
    custom_metadata = Column(JSONB, default={})


