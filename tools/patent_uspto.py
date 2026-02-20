# synchestra/tools/patent_uspto.py

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
    deps = set()

    for m in re.findall(r"claim\s+(\d+)", text, flags=re.IGNORECASE):
        deps.add(m)

    for m in re.findall(r"claims\s+(\d+)\s+and\s+(\d+)", text, flags=re.IGNORECASE):
        deps.add(m[0])
        deps.add(m[1])

    for m in re.findall(r"claims\s+(\d+)\s*-\s*(\d+)", text, flags=re.IGNORECASE):
        start, end = int(m[0]), int(m[1])
        for i in range(start, end + 1):
            deps.add(str(i))

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
    div = soup.find("div", id="abstract")
    if div:
        return clean_text(div.get_text())

    meta = soup.find("meta", {"name": "description"})
    return clean_text(meta["content"]) if meta else None

def parse_claims(soup):
    claims_root = soup.find("div", id="claims")
    if not claims_root:
        return []

    claims = []

    for div in claims_root.find_all("div", class_="claim"):
        txt_tag = div.find("p", class_="claim-text")
        if not txt_tag:
            continue

        raw = clean_text(txt_tag.get_text())

        cid = None
        m = re.match(r"(\d+)\.\s*(.*)", raw)
        if m:
            cid = m[1]
            text = m[2]
        else:
            text = raw

        if not cid:
            if div.get("id"):
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
    div = soup.find("div", id="description")
    if not div:
        return None
    return clean_text(div.get_text(" "))

def parse_metadata(soup):
    inventors = []
    assignee = None
    filing = None
    publication = None

    table = soup.find("table", class_="bibliographic-data")
    if table:
        for row in table.find_all("tr"):
            th = clean_text(row.find("th").get_text()) if row.find("th") else None
            td = clean_text(row.find("td").get_text()) if row.find("td") else None

            if not th or not td:
                continue

            if "Inventor" in th:
                inventors.append(td)
            if "Assignee" in th:
                assignee = td
            if "Filed" in th:
                filing = td
            if "Published" in th:
                publication = td

    return {
        "inventors": inventors,
        "assignee": assignee,
        "dates": {
            "filing": filing,
            "publication": publication
        }
    }

# ------------------------------------------------------------
# FETCH HTML (PATCHED)
# ------------------------------------------------------------

def fetch_html_uspto(patent_id):
    # Rimuove suffissi tipo A1, B2, ecc.
    core = re.sub(r"[A-Z]+$", "", patent_id.replace("US", ""))

    # URL USPTO full-text (patft)
    url = f"https://patft.uspto.gov/netacgi/nph-Parser?patentnumber={core}"

    return load_page(
        url,
        mode="auto",
        selector="#claims, .claim",
        screenshot="file"
    )

# ------------------------------------------------------------
# ORCHESTRATORE
# ------------------------------------------------------------

def run(patent_id, session_id, chat_id):
    html, meta = fetch_html_uspto(patent_id)
    soup = BeautifulSoup(html, "html.parser")

    claims = parse_claims(soup)
    title = parse_title(soup)
    abstract = parse_abstract(soup)
    description = parse_description(soup)
    metadata = parse_metadata(soup)

    return {
        "tool": "patent_uspto",
        "query": patent_id,
        "session_id": session_id,
        "chat_id": chat_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "normalized_url": f"https://patft.uspto.gov/netacgi/nph-Parser?patentnumber={patent_id}",
        "patent_id": patent_id,
        "source": "uspto-html",
        "meta": meta,
        "data": {
            "title": title,
            "abstract": abstract,
            "claims": claims,
            "description": description,
            "prior_art": [],
            "citations": [],
            "metadata": metadata
        }
    }
