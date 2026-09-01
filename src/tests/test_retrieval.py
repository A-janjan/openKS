from retrieval.search import reciprocal_rank_fusion

def test_rrf():
    results1 = [{"id": "a", "score": 0.9}, {"id": "b", "score": 0.8}]
    results2 = [{"id": "b", "score": 0.9}, {"id": "c", "score": 0.7}]
    fused = reciprocal_rank_fusion([results1, results2], k=60)
    assert fused[0]["id"] == "b"
    assert fused[1]["id"] == "a"
    assert fused[2]["id"] == "c"
    # check fusion_score exists
    assert "fusion_score" in fused[0]