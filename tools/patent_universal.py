# synchestra/tools/patent_universal.py

import re
from datetime import datetime
from synchestra.tools import (
    patent_google,
    patent_epo,
    patent_wipo
)

PATENT_ID_REGEX = re.compile(
    r"\b("
    r"US\d+[A-Z]?\d*"
    r"|EP\d+[A-Z]?\d*"
    r"|WO\d+[A-Z]?\d*"
    r"|JP\d+[A-Z]?\d*"
    r")\b",
    re.IGNORECASE
)

def extract_id(query):
    m = PATENT_ID_REGEX.search(query)
    if not m:
        return None
    return m.group(1).upper()

def run(query, session_id, chat_id):
    patent_id = extract_id(query)
    if not patent_id:
        return {
            "tool": "patent_universal",
            "error": "No valid patent ID found",
            "query": query,
            "session_id": session_id,
            "chat_id": chat_id,
            "timestamp": datetime.utcnow().isoformat()
        }

    # -----------------------------
    # US → Google Patents (stabile)
    # -----------------------------
    if patent_id.startswith("US"):
        return patent_google.run(patent_id, session_id, chat_id)

    # -----------------------------
    # EPO
    # -----------------------------
    if patent_id.startswith("EP"):
        return patent_epo.run(patent_id, session_id, chat_id)

    # -----------------------------
    # WIPO
    # -----------------------------
    if patent_id.startswith("WO"):
        return patent_wipo.run(patent_id, session_id, chat_id)

    # -----------------------------
    # fallback → Google Patents
    # -----------------------------
    return patent_google.run(patent_id, session_id, chat_id)
