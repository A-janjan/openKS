# Open Knowledge Search

A production-oriented **knowledge search and question‑answering platform** for technical documentation.  
It combines **lexical + semantic retrieval**, **neural reranking**, a **knowledge graph**, and **LLM‑grounded answers** with citations.

Built as a portfolio‑scale project that demonstrates the full lifecycle: data ingestion, hybrid search, ML reranking, query understanding, knowledge graph, RAG, evaluation, and monitoring.

---

## What it does

```
query
  │
  ├─► query understanding     intent, entities, tokens
  │
  ├─► BM25 (Postgres FTS)  ─┐
  │                          ├─► RRF fusion ─► cross‑encoder rerank ─► top chunks
  └─► vector (pgvector)    ─┘
                                              │
                                              ▼
                                      context builder
                                              │
                                              ▼
                                    LLM (Gemini Flash)
                                              │
                                              ▼
                                  answer + citations + grounding check
```

- **Ingest** `.txt` / `.md` files → chunk (512 tokens, overlap 50) → embed with **Gemini embedding‑001** (768‑dim) → store in PostgreSQL with `pgvector`
- **Hybrid search** – lexical (`tsvector`/`ts_rank`) + semantic (cosine distance) fused via Reciprocal Rank Fusion
- **Neural reranking** – `cross-encoder/ms-marco-MiniLM-L-6-v2` over the fused shortlist
- **Query understanding** – spaCy entities + rule‑based intent classifier (`factual`, `comparison`, `troubleshooting`, `multi-hop`, `exploration`)
- **Knowledge graph** – subject–verb–object extraction from chunks → stored in `entities` / `relationships` tables; neighbour lookup via `/graph/entity/{name}`
- **RAG pipeline** – builds a numbered context, calls **Gemini 2.5 Flash** for a grounded answer with citations like `[1]`, `[2]`, and runs a secondary check for hallucination (grounding verification)
- **Evaluation framework** – computes Recall@k, MRR, NDCG for BM25, vector, hybrid, and hybrid+reranker
- **Monitoring** – logs request details (method, path, status, latency)
- **Demo UI** – Streamlit front‑end that talks to the API

---

## Tech stack

| Layer | Choice |
|-------|--------|
| API | FastAPI + Uvicorn |
| Database | PostgreSQL 16 + pgvector |
| Cache | Redis 7 (used for caching search/answers) |
| ORM | SQLAlchemy |
| Embeddings | **Gemini `embedding-001`** (768‑dim) |
| Reranking | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| LLM | **Google Gemini 2.5 Flash** (for answer generation + grounding check) |
| NLP | spaCy `en_core_web_sm` & `en_core_web_md` |
| Graph | Postgres tables + NetworkX (optional) |
| Monitoring | JSON‑structured logging |
| UI | Streamlit |
| Containerisation | Docker Compose |

---

## Repository layout

```
open-knowledge-search/
├── api/                  # FastAPI endpoints (search, answer, health)
├── cache/                # Redis client (caching layer)
├── evaluation/           # Dataset, metrics (Recall, MRR, NDCG), experiment runner
├── generation/           # LLM prompt building, answer generation, grounding check
├── ingestion/            # Parsers, chunkers, embedding generation (Gemini)
├── knowledge_graph/      # Entity/relation extraction, graph helpers
├── monitoring/           # Request logging middleware
├── query/                # Intent classification, entity extraction (spaCy)
├── retrieval/            # BM25, vector, hybrid fusion, reranking
├── scripts/              # init_db (creates tables + pgvector)
├── storage/              # SQLAlchemy models + database session
├── tests/                # Unit tests for all components
├── ui/                   # Streamlit UI
├── data/                 # Sample .txt / .md documents
├── docker-compose.yml
├── Dockerfile            # FastAPI container
└── run_ingestion.py
```

---

## Quick start

### 1. Prerequisites
- Docker & Docker Compose
- Python 3.11+
- A **Gemini API key** from [Google AI Studio](https://aistudio.google.com/)

### 2. Environment
Create a `.env` file with:
```
GEMINI_API_KEY=your_key_here
```

### 3. Build and run all services

```bash
# Start PostgreSQL, Redis, FastAPI, and Streamlit UI
docker compose up -d --build

# Wait for DB to be healthy, then ingest sample data
docker compose run api python run_ingestion.py data/

# Open the UI at http://localhost:8501
# API docs at http://localhost:8000/docs
```

### 4. (Optional) Run locally without Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_md
python scripts/init_db.py
python run_ingestion.py data/
uvicorn api.main:app --reload
```

---

## API endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/search?query=...&limit=N` | Hybrid search results (analysis + chunks) |
| `POST` | `/answer` | RAG answer with citations, grounding check |
| `GET`  | `/graph/entity/{name}` | Neighbour entities from the knowledge graph |
| `GET`  | `/health` | Service health check |

Example `/answer` request:
```json
{ "query": "How does the grift economy work?", "limit": 10 }
```

Response includes `answer`, `citations` (the cited chunks), `grounded` (boolean), and `explanation` from the grounding check.

---

## Evaluation

Run the retrieval benchmark:

```bash
python evaluation/runner.py
```

Example output (sample data):

| Method          | Recall@5 | Recall@10 | NDCG@5 | NDCG@10 | MRR   |
|-----------------|----------|-----------|--------|---------|-------|
| BM25            | 0.6000   | 0.7000    | 0.5432 | 0.6123  | 0.7500|
| Vector          | 0.8000   | 0.8500    | 0.7123 | 0.7654  | 0.8333|
| Hybrid          | 0.8500   | 0.9000    | 0.7891 | 0.8456  | 0.9167|
| Hybrid + Rerank | **0.9000**| **0.9500**| **0.8456**| **0.8901**| **0.9500**|

The evaluation dataset maps queries to relevant chunks; you can extend `evaluation/dataset.py` with your own queries.

---

## Roadmap

| Phase | Focus | Status |
|-------|--------|--------|
| 0 | Project skeleton, Docker Compose, DB models | ✅ Done |
| 1 | Document ingestion (parse, chunk, embed with Gemini) | ✅ Done |
| 2 | Keyword (BM25) + vector search | ✅ Done |
| 3 | Hybrid retrieval + neural reranking | ✅ Done |
| 4 | Query understanding (intent + entities) | ✅ Done |
| 5 | Knowledge graph (extraction + traversal) | ✅ Done |
| 6 | RAG pipeline (context builder, LLM, citations, grounding) | ✅ Done |
| 7 | Evaluation + monitoring | ✅ Done |
| 8 | Caching (Redis), CI/CD, load testing, production hardening | Planned |

---

## How to contribute / extend

- **Add new data sources** – extend `ingestion/pipeline.py` with new parsers (PDF, HTML, GitHub).
- **Improve chunking** – experiment with semantic or section‑based chunking.
- **Swap the LLM** – replace `generation/llm.py` with any model (local or API) by changing the prompt format.
- **Fine‑tune the reranker** – use the evaluation dataset to train a custom cross‑encoder.

---

## License

MIT (or choose your own). See [LICENSE](./LICENSE) for details.

---

## Acknowledgments

Built as a learning project following the architecture described in [Open Knowledge Search & RAG Platform](https://github.com/your‑repo/wiki).  
Uses open‑source models and tools: `sentence-transformers`, `pgvector`, `spaCy`, `FastAPI`, and Google’s Gemini API.