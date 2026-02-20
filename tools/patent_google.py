# synchestra/tools/patent_google.py

from synchestra.tools.loader.universal_loader import load_page
from bs4 import BeautifulSoup
import re
import time


# ------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------

def clean_text(t):
    if not t:
        return None
    return " ".join(t.split())


def extract_claim_dependencies(text):
    """
    Estrae dipendenze da testo claim.
    Esempi:
    - "The method of claim 1"
    - "The system of claims 3 and 5"
    - "The device of claims 1-4"
    """
    deps = set()

    # claim 1
    for m in re.findall(r"claim\s+(\d+)", text, flags=re.IGNORECASE):
        deps.add(m)

    # claims 3 and 5
    for m in re.findall(r"claims\s+(\d+)\s+and\s+(\d+)", text, flags=re.IGNORECASE):
        deps.add(m[0])
        deps.add(m[1])

    # claims 1-4
    for m in re.findall(r"claims\s+(\d+)\s*-\s*(\d+)", text, flags=re.IGNORECASE):
        start, end = int(m[0]), int(m[1])
        for i in range(start, end + 1):
            deps.add(str(i))

    # claims 1, 3, 5
    for m in re.findall(r"claims?\s+((?:\d+\s*,\s*)+\d+)", text, flags=re.IGNORECASE):
        nums = re.findall(r"\d+", m)
        for n in nums:
            deps.add(n)

    return sorted(list(deps))


# ------------------------------------------------------------
# PARSING FUNCTIONS
# ------------------------------------------------------------

def parse_title(soup):
    t = soup.find("title")
    return clean_text(t.get_text()) if t else None


def parse_abstract(soup):
    meta = soup.find("meta", {"name": "description"})
    return clean_text(meta["content"]) if meta else None


def parse_claims(soup):
    """
    Restituisce claims in formato gerarchico:
    [
        { "id": "1", "text": "...", "dependencies": [] },
        { "id": "2", "text": "...", "dependencies": ["1"] }
    ]
    """

    claims_section = soup.find("section", {"data-section": "claims"})
    if not claims_section:
        return []

    claims = []
    for div in claims_section.find_all("div", class_="claim"):
        # ID claim
        cid = None

        # 1) Provo a estrarre dal testo
        txt_tag = div.find("span", class_="claim-text")
        if not txt_tag:
            continue

        raw_text = clean_text(txt_tag.get_text())

        m = re.match(r"(\d+)\.\s*(.*)", raw_text)
        if m:
            cid = m[1]
            text = m[2]
        else:
            # fallback: nessun numero iniziale → claim senza ID
            text = raw_text

        # 2) Provo a estrarre ID dal tag HTML
        if not cid and div.get("id"):
            m2 = re.findall(r"(\d+)", div.get("id"))
            if m2:
                cid = m2[-1]

        if not cid:
            continue

        deps = extract_claim_dependencies(text)

        claims.append({
            "id": cid,
            "text": text,
            "dependencies": deps
        })

    return claims


def parse_description(soup):
    """
    Description lineare (formato A).
    """
    sec = soup.find("section", {"data-section": "description"})
    if not sec:
        return None

    text = clean_text(sec.get_text(" "))
    return text


def parse_prior_art(soup):
    sec = soup.find("section", {"data-section": "prior-art"})
    if not sec:
        return []

    items = []
    for li in sec.find_all("li"):
        t = clean_text(li.get_text())
        if t:
            items.append(t)

    return items


def parse_citations(soup):
    """
    Citations da:
    - references
    - cited-by
    """
    citations = []

    for sec_name in ["references", "cited-by"]:
        sec = soup.find("section", {"data-section": sec_name})
        if not sec:
            continue

        for li in sec.find_all("li"):
            t = clean_text(li.get_text())
            if t:
                citations.append(t)

    return citations


def parse_metadata(soup):
    inventors = [clean_text(dd.get_text()) for dd in soup.find_all("dd", {"itemprop": "inventor"})]
    assignee = soup.find("dd", {"itemprop": "assigneeOriginal"})
    filing = soup.find("time", {"itemprop": "filingDate"})
    publication = soup.find("time", {"itemprop": "publicationDate"})

    return {
        "inventors": inventors,
        "assignee": clean_text(assignee.get_text()) if assignee else None,
        "dates": {
            "filing": filing["datetime"] if filing and filing.has_attr("datetime") else None,
            "publication": publication["datetime"] if publication and publication.has_attr("datetime") else None
        }
    }


# ------------------------------------------------------------
# FETCH HTML (print view → fallback)
# ------------------------------------------------------------

def fetch_html_print_view(patent_id):
    url = f"https://patents.google.com/patent/{patent_id}/en?printsec=abstract"
    return load_page(
        url,
        mode="auto",
        selector="section[data-section='claims'], .claim",
        screenshot="file"
    )


def fetch_html_normal(patent_id):
    url = f"https://patents.google.com/patent/{patent_id}"
    return load_page(
        url,
        mode="auto",
        selector="section[data-section='claims'], .claim",
        screenshot="file"
    )


# ------------------------------------------------------------
# ORCHESTRATORE
# ------------------------------------------------------------

def run(query, session_id, chat_id):
    # 1) Print view
    html, meta = fetch_html_print_view(query)
    soup = BeautifulSoup(html, "html.parser")

    claims = parse_claims(soup)

    # 2) Se print view non contiene claims → fallback
    if not claims:
        html, meta = fetch_html_normal(query)
        soup = BeautifulSoup(html, "html.parser")
        claims = parse_claims(soup)

    # 3) Parsing completo
    title = parse_title(soup)
    abstract = parse_abstract(soup)
    description = parse_description(soup)
    prior_art = parse_prior_art(soup)
    citations = parse_citations(soup)
    metadata = parse_metadata(soup)

    return {
        "tool": "patent_google",
        "query": query,
        "session_id": session_id,
        "chat_id": chat_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "normalized_url": f"https://patents.google.com/patent/{query}",
        "patent_id": query,
        "source": "google-playwright",
        "meta": meta,
        "data": {
            "title": title,
            "abstract": abstract,
            "claims": claims,
            "description": description,
            "prior_art": prior_art,
            "citations": citations,
            "metadata": metadata
        }
    }
