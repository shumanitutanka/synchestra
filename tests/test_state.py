from synchestra import Tools


def test_get_session_creates_and_tracks(tools):
    s = tools._get_session("s1", "c1")
    assert "history" in s
    assert tools.state["last_session_id"] == "s1"
    assert "s1" in tools.state["sessions"]


def test_state_persistence_roundtrip(tools, tmp_path):
    tools._get_session("s1", "c1")
    tools._save_state_to_disk()

    t2 = Tools()
    t2.LOG_PATH = tools.LOG_PATH
    t2.STATE_PATH = tools.STATE_PATH
    t2._load_state_from_disk()

    assert "s1" in t2.state.get("sessions", {})
