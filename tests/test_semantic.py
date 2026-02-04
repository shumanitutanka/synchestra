import numpy as np
import pytest
from synchestra import Tools


@pytest.fixture
def tools_semantic(tools):
    """
    Usa l'istanza tools ma forza il lazy load degli embeddings.
    Questo garantisce che MiniLM-L6-v2 sia caricato una sola volta.
    """
    tools._lazy_load_embeddings()
    assert tools._EMB_MODEL is not None, "sentence-transformers non è disponibile"
    return tools


# -------------------------------------------------------------------------
# TEST _semantic_score
# -------------------------------------------------------------------------

def test_semantic_score_similarity(tools_semantic):
    score_same = tools_semantic._semantic_score(
        "install docker on ubuntu",
        ["how to install docker on ubuntu"]
    )
    score_diff = tools_semantic._semantic_score(
        "install docker on ubuntu",
        ["recipe for tiramisu"]
    )

    assert score_same > score_diff
    assert 0.0 <= score_same <= 1.0
    assert -1.0 <= score_diff <= 1.0


# -------------------------------------------------------------------------
# TEST semantic_rerank
# -------------------------------------------------------------------------

def test_semantic_rerank_ordering(tools_semantic):
    query = "install docker on ubuntu"

    results = [
        {
            "title": "Install Docker on Ubuntu",
            "snippet": "Step by step guide",
            "score": 10,
        },
        {
            "title": "How to bake a cake",
            "snippet": "Cooking tutorial",
            "score": 10,
        },
    ]

    reranked = tools_semantic.semantic_rerank(query, results, tools_semantic.embed_fn)

    # Il primo deve essere quello semanticamente più vicino
    assert reranked[0]["title"].lower().startswith("install docker")


# -------------------------------------------------------------------------
# TEST cluster_results
# -------------------------------------------------------------------------

def test_cluster_results_grouping(tools_semantic):
    query = "docker installation"

    results = [
        {"title": "Install Docker on Ubuntu", "snippet": "Guide", "score": 10},
        {"title": "Docker installation steps", "snippet": "Tutorial", "score": 10},
        {"title": "How to cook pasta", "snippet": "Recipe", "score": 10},
    ]

    clusters = tools_semantic.cluster_results(results, tools_semantic.embed_fn)

    # Devono esserci almeno 2 cluster: uno tecnico, uno culinario
    assert len(clusters) >= 2

    # Ogni cluster deve avere almeno 1 item
    assert all(len(c["items"]) >= 1 for c in clusters)


# -------------------------------------------------------------------------
# TEST label_cluster
# -------------------------------------------------------------------------

def test_label_cluster_uses_best_item(tools_semantic):
    cluster = {
        "centroid": tools_semantic.embed_fn("docker installation guide"),
        "items": [
            {
                "title": "Install Docker on Ubuntu",
                "snippet": "Guide",
                "embedding": tools_semantic.embed_fn("Install Docker on Ubuntu"),
            },
            {
                "title": "Random unrelated",
                "snippet": "Nothing",
                "embedding": tools_semantic.embed_fn("banana apple pear"),
            },
        ],
    }

    label = tools_semantic.label_cluster(cluster)
    assert "docker" in label.lower()


# -------------------------------------------------------------------------
# TEST semantic_density + filter_noise
# -------------------------------------------------------------------------

def test_filter_noise_removes_low_density(tools_semantic):
    good_emb = tools_semantic.embed_fn("docker installation guide for ubuntu server step by step")

    bad_emb = np.zeros_like(good_emb)

    results = [
        {
            "title": "Good",
            "snippet": "This is a long enough snippet about docker installation on ubuntu server.",
            "embedding": good_emb,
        },
        {
            "title": "Bad",
            "snippet": "Short",
            "embedding": bad_emb,
        },
    ]

    filtered = tools_semantic.filter_noise(results, density_threshold=0.01)

    assert any(r["title"] == "Good" for r in filtered)
    assert all(r["title"] != "Bad" for r in filtered)

