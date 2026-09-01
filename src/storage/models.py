from sqlalchemy import Column, String, Integer, DateTime, JSON, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR
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
    __table_args__ = (Index("idx_chunk_tsv", "tsv", postgresql_using="gin"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"))
    content = Column(Text, nullable=False)
    position = Column(Integer, nullable=False)  # position of the chunk in the document
    embedding = Column(Vector(768))  
    custom_metadata = Column(JSONB, default={})
    tsv = Column(TSVECTOR, nullable=True)


class Entity(Base):
    __tablename__ = "entities"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)  # normalized
    type = Column(String)  # e.g., "PERSON", "ORG", "CONCEPT", "TECHNOLOGY"
    custom_metadata = Column(JSONB, default={})


class Relationship(Base):
    __tablename__ = "relationships"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("entities.id"))
    target_id = Column(UUID(as_uuid=True), ForeignKey("entities.id"))
    relation_type = Column(String)  # e.g., "implements", "uses", "part_of"
    source_chunk_id = Column(UUID(as_uuid=True), ForeignKey("document_chunks.id"))
    custom_metadata = Column(JSONB, default={})
