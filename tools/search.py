# synchestra/tools/search.py

from datetime import datetime
from synchestra.state import load_state, save_state
import requests

state = load_state()

SEARX_URL = "http://192.168.100.18:8888/search"
TIMEOUT = 8  # secondi

def normalize_result(item):
    """Normalizza un singolo risultato SearxNG."""
    return {
        "title": item.get("title") or "",
        "url": item.get("url") or "",
        "snippet": item.get("content") or item.get("snippet") or "",
        "engine": item.get("engine") or "",
    }

def run(query, session_id, chat_id):
    session = state["sessions"].setdefault(session_id, {"history": []})

    result = {
        "tool": "search",
        "query": query,
        "results": [],
        "error": "",
        "session_id": session_id,
        "chat_id": chat_id,
        "timestamp": datetime.utcnow().isoformat(),
    }

    params = {
        "q": query,
        "format": "json",
        "language": "it",
        "safesearch": 0,
    }

    try:
        r = requests.get(SEARX_URL, params=params, timeout=TIMEOUT)
        r.raise_for_status()

        data = r.json()
        raw_results = data.get("results", [])

        # Normalizzazione
        result["results"] = [normalize_result(x) for x in raw_results]

        # Se tutto ok, rimuovi il campo error
        result.pop("error", None)

    except Exception as e:
        result["error"] = f"Errore nella ricerca: {str(e)}"

    session["history"].append(result)
    save_state(state)
    return result
