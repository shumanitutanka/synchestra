from datetime import datetime
from pathlib import Path
from synchestra.state import load_state, save_state

state = load_state()

def run(query, session_id, chat_id):
    session = state["sessions"].setdefault(session_id, {"history": []})

    base = Path("/app/backend/data/uploads")
    documents = []

    if base.exists():
        for f in base.iterdir():
            if f.is_file():
                try:
                    text = f.read_text(errors="ignore")
                except:
                    text = ""
                documents.append({"filename": f.name, "text": text})

    result = {
        "tool": "rag",
        "query": query,
        "documents": documents,
        "session_id": session_id,
        "chat_id": chat_id,
        "timestamp": datetime.utcnow().isoformat(),
    }

    session["history"].append(result)
    save_state(state)
    return result
