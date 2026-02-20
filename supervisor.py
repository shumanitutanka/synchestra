from synchestra.tools import search
from synchestra.tools import analysis
from synchestra.tools import patent_universal
from synchestra.tools import postprocess
import re

PATENT_ID_REGEX = re.compile(
    r"\b("
    r"[A-Z]{2}\d{4,}[A-Z]\d?"
    r"|WO\d{4,}"
    r"|EP\d{4,}"
    r"|US\d{4,}"
    r")\b",
    re.IGNORECASE
)

def contains_patent_id(q):
    return bool(PATENT_ID_REGEX.search(q))

def contains_patent_url(q):
    return "patents.google.com/patent/" in q

def supervisor(query, session_id, chat_id):
    q = query.lower()

    # ============================================================
    # 1) ROUTER BREVETTI (UNICO PUNTO DI INGRESSO)
    # ============================================================
    if (
        q.startswith("patent ")
        or "brevetto" in q
        or contains_patent_id(q)
        or contains_patent_url(q)
    ):
        # Estrai ID se query inizia con "patent <ID>"
        if q.startswith("patent "):
            parts = query.split()
            if len(parts) >= 2:
                patent_id = parts[1].strip()
                result = patent_universal.run(patent_id, session_id, chat_id)
            else:
                result = patent_universal.run(query, session_id, chat_id)
        else:
            # fallback: passa l'intera query al router
            result = patent_universal.run(query, session_id, chat_id)

    # ============================================================
    # 2) RICERCA
    # ============================================================
    elif "cerca" in q or "search" in q:
        cleaned = q.replace("cerca", "").replace("search", "").strip()
        result = search.run(cleaned, session_id, chat_id)

    # ============================================================
    # 3) ANALISI
    # ============================================================
    elif "analizza" in q or "analysis" in q:
        result = analysis.run(query, session_id, chat_id)

    # ============================================================
    # 4) FALLBACK → SEARCH
    # ============================================================
    else:
        result = search.run(query, session_id, chat_id)

    # ============================================================
    # POSTPROCESS
    # ============================================================
    if "error" in result and not result["error"]:
        result.pop("error")

    processed = postprocess.run(result, session_id, chat_id)
    return processed
