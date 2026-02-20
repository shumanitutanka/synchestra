# synchestra/state.py

import json
from pathlib import Path
from datetime import datetime

STATE_PATH = Path("/app/backend/data/synchestra_state.json")
STATE_DIR = STATE_PATH.parent

DEFAULT_STATE = {
    "sessions": {},
    "last_session_id": None,
    "version": 1
}

def load_state():
    """Carica lo stato da disco in modo sicuro."""
    try:
        if not STATE_DIR.exists():
            STATE_DIR.mkdir(parents=True, exist_ok=True)

        if STATE_PATH.exists():
            raw = STATE_PATH.read_text()
            data = json.loads(raw)

            # Validazione minima
            if "sessions" not in data:
                data["sessions"] = {}
            if "last_session_id" not in data:
                data["last_session_id"] = None

            return data

    except Exception as e:
        print("STATE ERROR:", e)

    # fallback → stato vuoto
    return DEFAULT_STATE.copy()

def save_state(state):
    """Salva lo stato in modo atomico e sicuro."""
    try:
        if not STATE_DIR.exists():
            STATE_DIR.mkdir(parents=True, exist_ok=True)

        tmp = STATE_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2))
        tmp.replace(STATE_PATH)

    except Exception as e:
        print("STATE SAVE ERROR:", e)

