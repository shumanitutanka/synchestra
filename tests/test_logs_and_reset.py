def test_read_logs_and_reset(tools):
    tools.tool_math("1+1", "s1", "c1")
    logs = tools.read_logs()
    assert "error" not in logs
    assert "log_tail" in logs

    state_before = tools.dump_state()
    assert state_before["state"]["sessions"]

    res = tools.reset_state()
    assert res["status"] == "ok"
    state_after = tools.dump_state()
    assert state_after["state"]["sessions"] == {}

