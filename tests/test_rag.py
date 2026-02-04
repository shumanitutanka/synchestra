def test_tool_rag_no_documents(tools, tmp_path):
    base = tmp_path / "uploads"
    base.mkdir(parents=True, exist_ok=True)

    tools.KB_PATH = base

    res = tools.tool_rag("test", "s1", "c1")
    assert res["docs_count"] == 0

def test_tool_rag_with_txt(tools, tmp_path):
    base = tmp_path / "uploads"
    base.mkdir(parents=True, exist_ok=True)

    f = base / "doc.txt"
    f.write_text("contenuto di prova")

    tools.KB_PATH = base

    res = tools.tool_rag("test", "s1", "c1")
    assert res["docs_count"] == 1

