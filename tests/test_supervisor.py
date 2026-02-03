from unittest.mock import patch

def test_supervisor_fallback_chat(tools):
    tools.debug = True
    with patch.object(tools, "_semantic_score", return_value=0.0), \
         patch.object(tools, "_keyword_score", return_value=0.0):
        res = tools.supervisor("asdfghjkl", "s1", "c1")

        # Il supervisor in fallback NON wrappa in {"result": ...}
        if "result" in res:
            action = res["result"]["action"]
        else:
            action = res["action"]

        assert action == "chat"

def test_supervisor_requires_chat_id(tools):
    try:
        tools.supervisor("ciao")
        assert False, "Doveva sollevare ValueError"
    except ValueError:
        assert True


def test_supervisor_routing_search(tools):
    res = tools.supervisor("cerca su internet docker", "s1", "c1")
    assert res["result"]["action"] == "search"
    assert res["result"]["mode"] == "routed"


def test_supervisor_routing_rag(tools):
    res = tools.supervisor("leggi il documento nella knowledge base", "s1", "c1")
    assert res["result"]["action"] == "rag"
