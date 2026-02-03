def test_tool_summarize_truncation(tools):
    text = "ciao " * 3000
    res = tools.tool_summarize(text, "s1", "c1")
    assert res["tool"] == "summarize"
    assert len(res["text"]) <= 8000


def test_tool_analysis_echo(tools):
    res = tools.tool_analysis("testo di analisi", "s1", "c1")
    assert res["tool"] == "analysis"
    assert res["text"] == "testo di analisi"


def test_tool_format_markdown(tools):
    res = tools.tool_format("contenuto", "s1", "c1")
    assert res["tool"] == "format_markdown"
    assert res["markdown"].startswith("```")
    assert res["markdown"].endswith("```")

