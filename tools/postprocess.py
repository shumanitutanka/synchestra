# synchestra/tools/postprocess.py

from datetime import datetime
from synchestra.state import load_state, save_state

state = load_state()

# ============================================================
# FORMATTER SEARCH
# ============================================================

def _format_search(result):
    items = result.get("results", [])
    if not items:
        return "Nessun risultato trovato."

    lines = ["### Risultati della ricerca:\n"]
    for item in items[:10]:
        title = item.get("title") or "(senza titolo)"
        url = item.get("url") or ""
        snippet = item.get("snippet") or ""
        engine = item.get("engine") or ""

        lines.append(f"- **{title}**\n  {snippet}\n  {url}\n  _({engine})_\n")

    return "\n".join(lines).strip()

# ============================================================
# FORMATTER PATENT (universale per Google/USPTO/EPO/WIPO)
# ============================================================

def _format_patent(result):
    data = result.get("data", {}) or {}
    url = result.get("normalized_url") or result.get("query")

    title = data.get("title")
    abstract = data.get("abstract")
    claims = data.get("claims")
    description = data.get("description")
    inventors = data.get("inventors")
    assignees = data.get("assignees")
    priority_date = data.get("priority_date")
    filing_date = data.get("filing_date")
    publication_date = data.get("publication_date")

    lines = []

    # Titolo
    lines.append(f"## {title or 'Brevetto'}")

    # URL
    if url:
        lines.append(f"**URL:** {url}")

    # Inventori
    if inventors:
        lines.append(f"**Inventori:** {', '.join(inventors)}")

    # Assignees
    if assignees:
        lines.append(f"**Assegnatari:** {', '.join(assignees)}")

    # Date
    if priority_date:
        lines.append(f"**Priorità:** {priority_date}")
    if filing_date:
        lines.append(f"**Deposito:** {filing_date}")
    if publication_date:
        lines.append(f"**Pubblicazione:** {publication_date}")

    # Abstract
    if abstract:
        lines.append("\n### Abstract")
        lines.append(abstract)

    # Claims
    if claims:
        lines.append("\n### Claims (strutturati)")
        lines.append(claims)

    # Description
    if description:
        lines.append("\n### Description (estratto)")
        lines.append(description)

    return "\n".join(lines).strip()

# ============================================================
# FORMATTER ANALYSIS
# ============================================================

def _format_analysis(result):
    kw = result.get("keywords", [])
    summary = result.get("summary", [])
    text = result.get("original_text", "")

    lines = ["## Analisi del testo"]

    if kw:
        lines.append("**Keywords:** " + ", ".join(kw))

    if summary:
        lines.append("\n### Riassunto")
        for s in summary:
            lines.append(f"- {s}")

    lines.append("\n### Testo originale")
    lines.append(text)

    return "\n".join(lines)

# ============================================================
# FORMATTER RAG
# ============================================================

def _format_rag(result):
    docs = result.get("documents", [])
    if not docs:
        return "Nessun documento caricato."

    lines = ["## Documenti caricati:\n"]
    for d in docs[:10]:
        lines.append(f"- **{d['filename']}** ({len(d['text'])} caratteri)")

    return "\n".join(lines)

# ============================================================
# FORMATTER SUMMARIZE
# ============================================================

def _format_summarize(result):
    text = result.get("text", "")
    return f"## Testo (troncato)\n\n{text}"

# ============================================================
# ENTRYPOINT POSTPROCESS
# ============================================================

def run(tool_output, session_id, chat_id):
    session = state["sessions"].setdefault(session_id, {"history": []})

    tool_name = tool_output.get("tool")
    error = tool_output.get("error")

    if error:
        text = f"Errore: {error}"

    else:
        if tool_name == "search":
            text = _format_search(tool_output)

        elif tool_name in (
            "patent_google",
            "patent_uspto",
            "patent_epo",
            "patent_wipo",
            "patent_universal"
        ):
            text = _format_patent(tool_output)

        elif tool_name == "analysis":
            text = _format_analysis(tool_output)

        elif tool_name == "rag":
            text = _format_rag(tool_output)

        elif tool_name == "summarize":
            text = _format_summarize(tool_output)

        else:
            text = str(tool_output)

    result = {
        "tool": "postprocess",
        "session_id": session_id,
        "chat_id": chat_id,
        "timestamp": datetime.utcnow().isoformat(),
        "text": text,
    }

    session["history"].append(result)
    save_state(state)
    return result
