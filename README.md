# Open Knowledge Search

A local, end-to-end knowledge search system: ingest documents, retrieve with hybrid BM25 + vector search, rerank with a cross-encoder, understand the query, and walk a knowledge graph.

Built as a portfolio-scale stack that still looks like production architecture — one Postgres (with pgvector) for documents, full-text, embeddings, and graph edges.

---

## For developers

The **[wiki](../../wiki)** is the place to start if you want to understand how this repo was built.

In particular, read **[Development Process](../../wiki/Development-Process)**. It is a phase-by-phase log of Phases: why each piece exists, the schemas and code that landed, the decisions behind them, and the pitfalls we hit.

| If you want… | Go here |
|--------------|---------|
| How the system was built, phase by phase | [Wiki → Development Process](../../wiki/Development-Process) |
| What to run right now | [Quick start](#quick-start) below |
| What is done vs planned | [Roadmap](#roadmap) below |

---

## What it does

```
query
  │
  ├─► query understanding     intent, entities, tokens
  │
  ├─► BM25 (Postgres FTS)  ─┐
  │                          ├─► RRF fusion ─► cross-encoder rerank ─► results
  └─► vector (pgvector)    ─┘
                                              │
graph neighbours ( /graph )  ─────────────────┘  not yet mixed into ranking
```

- **Ingest** `.txt` / `.md` files: chunk, embed (`all-MiniLM-L6-v2`), store in Postgres
- **Hybrid search**: lexical (`tsvector` / `ts_rank`) + semantic (pgvector cosine), fused with Reciprocal Rank Fusion
- **Neural reranking**: `cross-encoder/ms-marco-MiniLM-L-6-v2` over the fused shortlist
- **Query understanding**: spaCy entities + a rule-based intent classifier
- **Knowledge graph**: subject–verb–object extraction into `entities` / `relationships`, neighbour lookup via `/graph`

---

## Tech stack

| Layer | Choice |
|-------|--------|
| API | FastAPI + Uvicorn |
| Database | PostgreSQL 16 + pgvector |
| Cache | Redis 7 (reserved) |
| ORM | SQLAlchemy |
| Embeddings | sentence-transformers (`all-MiniLM-L6-v2`, 384-d) |
| Reranking | CrossEncoder MiniLM |
| NLP | spaCy `en_core_web_sm` |
| Graph | Postgres tables + NetworkX |

---

## Repository layout

```
open-knowledge-search/
├── api/                  # FastAPI endpoints
├── ingestion/            # Parsers, chunkers, embedding generation
├── storage/              # Database models, session
├── retrieval/            # BM25, vector, hybrid, reranking
├── query/                # Intent classification, entity extraction
├── knowledge_graph/      # Entity/relation extraction, graph helpers
├── scripts/              # init_db and other one-off tools
├── data/                 # Sample .txt / .md documents
├── docker-compose.yml
└── run_ingestion.py
```

---

## Quick start

```bash
# 1. Services
docker compose up -d

# 2. Python env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 3. Schema + ingest
python scripts/init_db.py
python run_ingestion.py data/

# 4. API
uvicorn api.main:app --reload
```

Then:

```
GET /search?query=how+does+postgresql+implement+mvcc
GET /graph/entity/PostgreSQL
```

The first run downloads MiniLM (~90 MB) and the cross-encoder (~400 MB).

---

## Roadmap

| Phase | Focus | Status |
|-------|--------|--------|
| 0 | Skeleton, Docker Compose, models | Done |
| 1 | Document ingestion | Done |
| 2 | BM25 + vector search | Done |
| 3 | Hybrid retrieval + neural reranking | Done |
| 4 | Query understanding | Done |
| 5 | Knowledge graph | Done |
| 6 | RAG — context builder, LLM answers, citations | Planned |
| 7 | Evaluation, verification, monitoring | Planned |
| 8 | Caching, failure handling, CI/CD, benchmarks | Planned |

The rationale for each completed phase is in the [wiki](../../wiki/Development-Process).

---

## License

TBD.
