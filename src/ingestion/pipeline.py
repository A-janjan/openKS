import os
from pathlib import Path
from typing import List
from datetime import datetime, timezone
from sqlalchemy import func


from storage.database import SessionLocal
from storage.models import Document, Chunk, Entity, Relationship
from knowledge_graph.extraction import extract_entities_and_relations
from ingestion.embeddings import get_embedding


def read_file_content(file_path: Path) -> str:
    """Read .txt or .md; for .md we might strip Markdown later."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def chunking_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
    """Simple token-based chunking (approximate by whitespace token count)."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end == len(words):
            break
        start = end - overlap
    return chunks


def ingest_file(file_path: Path):
    """Ingest a single file into the DB."""
    content = read_file_content(file_path)
    chunks = chunking_text(content)

    # 1. Create Document record
    doc = Document(
        title=file_path.stem,
        source=str(file_path.absolute()),
        source_type="file",
        created_at=datetime.now(timezone.utc),
    )

    db = SessionLocal()
    db.add(doc)
    db.flush()  # get doc.id

    # 2. For each chunk, compute embedding and store
    for pos, chunk_text in enumerate(chunks):
        # store chuncks
        embedding_vector = get_embedding(chunk_text)
        tsv = func.to_tsvector("english", chunk_text)
        chunk_obj = Chunk(
            document_id=doc.id,
            content=chunk_text,
            position=pos,
            embedding=embedding_vector,
            tsv=tsv,
        )
        db.add(chunk_obj)
        db.flush()

        # extract entities and relationships
        entities_list, relations_list = extract_entities_and_relations(chunk_text)

        # store entities
        for ent in entities_list:
            existing = db.query(Entity).filter(Entity.name == ent["name"]).first()
            if not existing:
                entity = Entity(name=ent["name"], type=ent["type"])
                db.add(entity)
                db.flush()  # to get id
            else:
                entity = existing

        # store relationships
        for rel in relations_list:
            src = db.query(Entity).filter(Entity.name == rel["source"]).first()
            tgt = db.query(Entity).filter(Entity.name == rel["target"]).first()
            if src and tgt:
                rel_obj = Relationship(
                    source_id=src.id,
                    target_id=tgt.id,
                    relation_type=rel["relation"],
                    source_chunk_id=chunk_obj.id,
                )
                db.add(rel_obj)

    db.commit()
    db.close()
    print(f"Ingested {file_path.name} -> {len(chunks)} chunks")


def ingest_directory(data_dir: str):
    for ext in ["*.txt", "*.md"]:
        for file_path in Path(data_dir).glob(ext):
            ingest_file(file_path)
