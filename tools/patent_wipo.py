# synchestra/tools/patent_wipo.py

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
    # Patentscope: abstract in <div id="abstract">
    div = soup.find("div", id="abstract")
    if div:
        return clean_text(div.get_text())

    # fallback: meta description
    meta = soup.find("meta", {"name": "description"})
    return clean_text(meta["content"]) if meta else None


def parse_claims(soup):
    """
    Claims da Patentscope:
    <div id="claims">
        <p>1. A method...</p>
    </div>
    """

    claims_root = soup.find("div", id="claims")
    if not claims_root:
        return []

    claims = []

    for p in claims_root.find_all("p"):
        raw = clean_text(p.get_text())
        if not raw:
            continue

        # Estrarre ID
        cid = None
        m = re.match(r"(\d+)\.\s*(.*)", raw)
        if m:
            cid = m[1]
            text = m[2]
        else:
            text = raw

        if not cid:
            # fallback: cerca numeri nel tag id
            if p.get("id"):
                m2 = re.findall(r"(\d+)", p.get("id"))
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
    Description lineare da Patentscope:
    <div id="description"> ... </div>
    """
    div = soup.find("div", id="description")
    if not div:
        return None

    return clean_text(div.get_text(" "))


def parse_metadata(soup):
    inventors = []
    assignee = None
    filing = None
    publication = None

    # Patentscope metadata in <table class="bibliographic-data">
    table = soup.find("table", class_="bibliographic-data")
    if table:
        for row in table.find_all("tr"):
            th = clean_text(row.find("th").get_text()) if row.find("th") else None
            td = clean_text(row.find("td").get_text()) if row.find("td") else None

            if not th or not td:
                continue

            if "Inventor" in th:
                inventors.append(td)
            if "Applicant" in th or "Assignee" in th:
                assignee = td
            if "Filing" in th:
                filing = td
            if "Publication" in th:
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
# FETCH HTML (EN only)
# ------------------------------------------------------------

def fetch_html_wipo(patent_id):
    # Patentscope EN view
    url = f"https://patentscope.wipo.int/search/en/detail.jsf?docId={patent_id}"
    return load_page(
        url,
        mode="auto",
        selector="#claims, .claim",
        screenshot="file"
    )


# ------------------------------------------------------------
# ORCHESTRATORE
# ------------------------------------------------------------

def run(query, session_id, chat_id):
    html, meta = fetch_html_wipo(query)
    soup = BeautifulSoup(html, "html.parser")

    claims = parse_claims(soup)

    # Parsing completo
    title = parse_title(soup)
    abstract = parse_abstract(soup)
    description = parse_description(soup)
    metadata = parse_metadata(soup)

    return {
        "tool": "patent_wipo",
        "query": query,
        "session_id": session_id,
        "chat_id": chat_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "normalized_url": f"https://patentscope.wipo.int/search/en/detail.jsf?docId={query}",
        "patent_id": query,
        "source": "wipo-html",
        "meta": meta,
        "data": {
            "title": title,
            "abstract": abstract,
            "claims": claims,
            "description": description,
            "prior_art": [],      # Patentscope non fornisce prior art HTML
            "citations": [],      # Patentscope non fornisce citations HTML
            "metadata": metadata
        }
    }
