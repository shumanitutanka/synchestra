import pytest
from synchestra import Tools

@pytest.fixture
def tools_semantic(tools):
    tools._lazy_load_embeddings()
    assert tools._EMB_MODEL is not None
    return tools

def test_semantic_pipeline_end_to_end(tools_semantic):
    query = "install docker on ubuntu"

    raw_results = [
        {"url": "https://example.com/docker?utm_source=test",
         "title": "Install Docker on Ubuntu",
         "snippet": "Guide step by step",
         "score": 10},
        {"url": "https://example.com/docker",
         "title": "Install Docker on Ubuntu",
         "snippet": "Guide step by step",
         "score": 9},
        {"url": "https://example.com/cake",
         "title": "How to bake a cake",
         "snippet": "Cooking tutorial",
         "score": 10},
    ]

    # 1. Deduplica
    dedup = tools_semantic.remove_duplicates(raw_results)
    assert len(dedup) == 2

    # 2. Semantic rerank
    reranked = tools_semantic.semantic_rerank(query, dedup, tools_semantic.embed_fn)
    assert reranked[0]["title"].lower().startswith("install docker")

    # 3. Clustering
    clusters = tools_semantic.cluster_results(reranked, tools_semantic.embed_fn)
    assert len(clusters) >= 2

    # 4. Labeling
    for c in clusters:
        label = tools_semantic.label_cluster(c)
        assert isinstance(label, str)
        assert len(label) > 0
