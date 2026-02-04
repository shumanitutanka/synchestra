import sys
from pathlib import Path
import pytest

# Aggiunge la root del progetto al PYTHONPATH
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Ora l'import funziona perché synchestra.py è nella root
from synchestra import Tools


@pytest.fixture
def tools(tmp_path, monkeypatch):
    """
    Istanza di Tools con LOG_PATH e STATE_PATH reindirizzati
    in una directory temporanea, così non tocchi /app/backend/data.
    """
    t = Tools()

    base = tmp_path / "synchestra_data"
    base.mkdir(parents=True, exist_ok=True)

    t.LOG_PATH = base / "synchestra.log"
    t.STATE_PATH = base / "synchestra_state.json"

    # reset stato in memoria
    t.state = {"sessions": {}, "last_session_id": None}
    t.trace = []

    # DISATTIVA SEMANTICA PER I TEST DEL SUPERVISOR
    t._EMB_MODEL = None
    t._util = None

    return t

@pytest.fixture
def tools_semantic(tmp_path):
    t = Tools()

    base = tmp_path / "synchestra_data"
    base.mkdir(parents=True, exist_ok=True)

    t.LOG_PATH = base / "synchestra.log"
    t.STATE_PATH = base / "synchestra_state.json"

    # NON disattivare la semantica
    t._lazy_load_embeddings()
    assert t._EMB_MODEL is not None

    return t

