from storage.database import engine
from storage.models import Base
from sqlalchemy import text


def init_db():
    # 1. Enable pgvector extension FIRST
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
        print("✅ pgvector extension enabled.")

    # 2. Create tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created.")


if __name__ == "__main__":
    init_db()