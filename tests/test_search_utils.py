from urllib.parse import urlparse


def test_detect_intent_navigational(tools):
    assert tools.detect_intent("apri github.com") == "navigational"


def test_detect_intent_developer(tools):
    assert tools.detect_intent("python requests api") == "developer"


def test_canonical_url_removes_tracking(tools):
    url = "https://example.com/path?utm_source=test&x=1&fbclid=abc"
    canon = tools.canonical_url(url)
    parsed = urlparse(canon)
    assert "utm_source" not in parsed.query
    assert "fbclid" not in parsed.query
    assert "x=1" in parsed.query


def test_remove_duplicates(tools):
    results = [
        {"url": "https://example.com?a=1"},
        {"url": "https://example.com?a=1&utm_source=test"},
    ]
    unique = tools.remove_duplicates(results)
    assert len(unique) == 1
