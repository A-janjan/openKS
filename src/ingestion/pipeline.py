import os
from pathlib import Path
from typing import List
import uuid
from datetime import datetime, timezone

from sentence_transformers import SentenceTransformer

from storage.database import SessionLocal
from storage.models import Document, Chunk

# Load embedding model once
embedder = SentenceTransformer("all-MiniLM-L6-v2")


def read_file_content(file_path: Path) -> str:
    """Read .txt or .md; for .md we might strip Markdown later."""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
    

def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
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
    chunks = chunk_text(content)
    
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
    for pos, chunk in enumerate(chunks):
        embedding_vector = embedder.encode(chunk).tolist()  # list of floats
        chunk = Chunk(
            document_id=doc.id,
            content=chunk,
            position=pos,
            embedding=embedding_vector,
        )
        db.add(chunk)

    db.commit()
    db.close()
    print(f"Ingested {file_path.name} -> {len(chunks)} chunks")
    

def ingest_directory(data_dir: str):
    for ext in ["*.txt", "*.md"]:
        for file_path in Path(data_dir).glob(ext):
            ingest_file(file_path)