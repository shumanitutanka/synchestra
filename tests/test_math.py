def test_tool_math_ok(tools):
    res = tools.tool_math("2+2", "s1", "c1")
    assert res["tool"] == "math"
    assert res["result"] == 4


def test_tool_math_error(tools):
    res = tools.tool_math("2+", "s1", "c1")
    assert res["tool"] == "math"
    assert "error" in res

