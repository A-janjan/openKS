from sqlalchemy import text
from storage.database import SessionLocal
from storage.models import Chunk
from ingestion.embeddings import get_embedding
from retrieval.reranking import rerank


def bm25_search(query: str, limit: int = 10):
    db = SessionLocal()
    # Convert query to tsquery (handle simple syntax)
    tsquery = " & ".join(query.split())  # simple: all words must appear
    # Use ts_rank (similar to BM25) – you can also use ts_rank_cd
    stmt = text("""
                    SELECT id, content, document_id,
                            ts_rank(tsv, to_tsquery('english', :tsquery)) AS rank
                    FROM document_chunks
                    WHERE tsv @@ to_tsquery('english', :tsquery)
                    ORDER BY rank DESC
                    LIMIT :limit
                """)

    result = db.execute(stmt, {"tsquery": tsquery, "limit": limit})
    rows = result.fetchall()
    db.close()
    return [
        {"id": row[0], "content": row[1], "document_id": row[2], "score": row[3]}
        for row in rows
    ]


def vector_search(query: str, limit: int = 10):
    db = SessionLocal()
    query_vec = get_embedding(query)
    # Convert the list to a Postgres‑compatible vector string
    query_vec_str = "[" + ",".join(str(x) for x in query_vec) + "]"
    stmt = text("""
                    SELECT id, content, document_id,
                        1 - (embedding <=> CAST(:query_vec AS vector)) AS similarity
                    FROM document_chunks
                    ORDER BY similarity DESC
                    LIMIT :limit
                """)
    result = db.execute(stmt, {"query_vec": query_vec_str, "limit": limit})
    rows = result.fetchall()
    db.close()
    return [
        {"id": row[0], "content": row[1], "doc_id": row[2], "score": row[3]}
        for row in rows
    ]


def reciprocal_rank_fusion(results_lists, k=60):
    """
    results_lists: list of lists of dicts with 'id' and 'score'
    returns sorted list with fused scores.
    """
    scores = {}
    for results in results_lists:
        for rank, item in enumerate(results, start=1):
            item_id = item["id"]
            scores[item_id] = scores.get(item_id, 0) + 1.0 / (k + rank)
    # collect items with score
    fused = []
    for item_id, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        # retrieve the full item from the first list that has it (or merge)
        # We'll store the original item dict; we need to retrieve from one of the lists
        for lst in results_lists:
            for it in lst:
                if it["id"] == item_id:
                    fused.append({**it, "fusion_score": score})
                    break
            else:
                continue
            break
    return fused


def hybrid_search(query: str, limit: int = 10, use_reranker: bool = True):
    bm25_results = bm25_search(query, limit=50)  # fetch more for fusion
    vec_results = vector_search(query, limit=50)
    fused = reciprocal_rank_fusion([bm25_results, vec_results], k=60)

    if use_reranker:
        reranked = rerank(query, fused, limit)
        return reranked
    else:
        return fused[:limit]
