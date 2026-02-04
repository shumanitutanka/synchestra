import pytest
from pathlib import Path
from synchestra import Tools

@pytest.fixture
def tools_semantic(tmp_path):
    t = Tools()

    base = tmp_path / "synchestra_data"
    base.mkdir(parents=True, exist_ok=True)

    t.LOG_PATH = base / "synchestra.log"
    t.STATE_PATH = base / "synchestra_state.json"

    # Attiva la semantica
    t._lazy_load_embeddings()
    assert t._EMB_MODEL is not None

    # KB reale: [root]/data/uploads
    project_root = Path(__file__).resolve().parents[1]
    kb = project_root / "data" / "uploads"
    assert kb.exists(), f"KB path non esiste: {kb}"
    t.KB_PATH = kb

    return t

def test_rag_semantic_retrieval(tools_semantic):
    query = "how do I install docker on ubuntu"

    res = tools_semantic.tool_rag(query, "s1", "c1")

    assert res["tool"] == "rag"
    assert "error" not in res or res["error"] == ""

    assert res.get("docs_count", 0) > 0, f"Nessun documento indicizzato: {res}"

    if "results" in res and len(res["results"]) > 0:
        first = res["results"][0]
        assert first["score"] >= 0

