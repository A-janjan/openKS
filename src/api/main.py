from fastapi import FastAPI, Query
from retrieval.search import hybrid_search
from query.understanding import analyze_query

app = FastAPI(title="Open Knowledge Search")


@app.get("/search")
def search(query: str = Query(..., min_length=1), limit: int = 10):
    analysis = analyze_query(query)
    results = hybrid_search(query, limit)
    return {"query": query, "results": results, "analysis": analysis}
