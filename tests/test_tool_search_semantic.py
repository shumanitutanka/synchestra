import pytest
from unittest.mock import patch
from synchestra import Tools


def fake_requests_get(url, params=None, timeout=10, **kwargs):
    class FakeResponse:
        status_code = 200

        def json(self):
            return {
                "results": [
                    {
                        "url": "https://example.com/docker",
                        "title": "Install Docker on Ubuntu",
                        "snippet": "Guide step by step",
                        "content": "Guide step by step",
                        "score": 10,
                    }
                ]
            }

        @property
        def text(self):
            return "<html><title>Install Docker on Ubuntu</title></html>"

    return FakeResponse()


@pytest.fixture
def tools_semantic(tmp_path):
    t = Tools()

    base = tmp_path / "synchestra_data"
    base.mkdir(parents=True, exist_ok=True)

    t.LOG_PATH = base / "synchestra.log"
    t.STATE_PATH = base / "synchestra_state.json"

    t._lazy_load_embeddings()
    assert t._EMB_MODEL is not None

    return t


@patch("synchestra.requests.get", side_effect=fake_requests_get)
def test_tool_search_semantic(mock_get, tools_semantic):
    res = tools_semantic.tool_search("install docker on ubuntu", "s1", "c1")

    assert res["tool"] == "search"
    assert res["error"] == ""

    # struttura coerente, anche se eventualmente vuota
    assert "results" in res
    assert "clusters" in res

