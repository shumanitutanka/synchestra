from datetime import datetime
from synchestra.state import load_state, save_state

state = load_state()

def run(text, session_id, chat_id):
    session = state["sessions"].setdefault(session_id, {"history": []})

    truncated = text[:8000]

    result = {
        "tool": "summarize",
        "text": truncated,
        "session_id": session_id,
        "chat_id": chat_id,
        "timestamp": datetime.utcnow().isoformat(),
    }

    session["history"].append(result)
    save_state(state)
    return result
