from unittest.mock import patch
import numpy as np
import synchestra


def fake_requests_get(*args, **kwargs):
    class FakeResp:
        status_code = 200

        def json(self):
            return {
                "results": [
                    {
                        "title": "Installare Docker su Ubuntu",
                        "url": "https://example.com/docker",
                        "content": "Guida completa per installare docker su ubuntu.",
                        "engine": "duckduckgo",
                        "category": "general",
                    },
                    {
                        "title": "Installare Docker su Ubuntu (duplicato)",
                        "url": "https://example.com/docker?utm_source=test",
                        "content": "Stessa guida.",
                        "engine": "duckduckgo",
                        "category": "general",
                    },
                ]
            }

    return FakeResp()


def fake_embed(text: str):
    return np.ones(384, dtype=float)


@patch("synchestra.requests.get", side_effect=fake_requests_get)
def test_tool_search_basic_flow(mock_get, tools):
    tools.embed_fn = fake_embed

    res = tools.tool_search("installare docker su ubuntu", "s1", "c1")

    assert res["tool"] == "search"
    assert res["error"] == ""
    assert res["count"] >= 1
    urls = {r["url"] for r in res["results"]}
    assert len(urls) == 1  # deduplica


@patch("synchestra.requests.get", side_effect=fake_requests_get)
def test_tool_search_handles_no_results(mock_get, tools):
    def fake_empty(*args, **kwargs):
        class FakeResp:
            status_code = 200

            def json(self):
                return {"results": []}

        return FakeResp()

    mock_get.side_effect = fake_empty

    res = tools.tool_search("query senza risultati", "s1", "c1")
    assert res["error"] == "no results query error"
    assert res["results"] == []

