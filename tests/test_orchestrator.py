def test_orchestrator_core_uses_supervisor_action(tools):
    sup = tools.supervisor("cerca docker", "s1", "c1")["result"]
    out = tools.orchestrator_core(sup, "s1", "c1")
    assert out["result"]["action"] == "search"
    assert out["result"]["status"] == "dispatch"
    assert out["result"]["session_id"] == "s1"
