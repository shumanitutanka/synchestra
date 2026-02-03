from pathlib import Path


def test_tool_rag_no_documents(tools, tmp_path, monkeypatch):
    base = tmp_path / "uploads"
    base.mkdir(parents=True, exist_ok=True)

    # monkeypatch del Path usato in tool_rag
    import synchestra
    def fake_path(p):
        if str(p) == "/app/backend/data/uploads":
            return base
        return Path(p)

    monkeypatch.setattr(synchestra, "Path", fake_path)

    res = tools.tool_rag("test", "s1", "c1")
    assert res["docs_count"] == 0
    assert "No documents found" in res["note"]


def test_tool_rag_with_txt(tools, tmp_path, monkeypatch):
    base = tmp_path / "uploads"
    base.mkdir(parents=True, exist_ok=True)
    f = base / "doc.txt"
    f.write_text("contenuto di prova")

    import synchestra
    def fake_path(p):
        if str(p) == "/app/backend/data/uploads":
            return base
        return Path(p)

    monkeypatch.setattr(synchestra, "Path", fake_path)

    res = tools.tool_rag("test", "s1", "c1")
    assert res["docs_count"] == 1
    assert res["documents"][0]["text"] == "contenuto di prova"
    assert res["documents"][0]["extension"] == ".txt"

