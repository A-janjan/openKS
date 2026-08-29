from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from storage.models import Base

# Read from environment variables (use python-dotenv later)
DATABASE_URL = "postgresql://knowledge:knowledge@localhost:5433/knowledge"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI later, but useful for scripts."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
