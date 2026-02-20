# synchestra/tools/patent_epo.py

import asyncio
import time
from playwright.async_api import async_playwright

SEARCH_URL = "https://worldwide.espacenet.com/patent/"

# ------------------------------------------------------------
# FETCH ESPACENET API (con header + cookie forwarding)
# ------------------------------------------------------------

async def fetch_epo_api(patent_id):
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)

        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/121.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 2000},
            java_script_enabled=True
        )

        page = await context.new_page()

        # 1. Apri Espacenet search
        await page.goto(SEARCH_URL, wait_until="domcontentloaded")

        # 2. Inserisci ID
        await page.fill("input[type=search]", patent_id)

        # 3. Premi Enter
        await page.keyboard.press("Enter")

        # 4. Attendi redirect
        await page.wait_for_url("**/family/**", timeout=20000)
        final_url = page.url

        # 5. Estrai ID reale dalla URL
        real_id = final_url.split("/publication/")[-1].split("?")[0]

        # 6. API base
        api_base = f"https://worldwide.espacenet.com/api/patents/v3/publication/{real_id}"

        # 7. Prepara header + cookie forwarding
        cookies = await context.cookies()
        cookie_header = "; ".join([f"{c['name']}={c['value']}" for c in cookies])

        base_headers = {
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": final_url,
            "Origin": "https://worldwide.espacenet.com",
            "Cookie": cookie_header
        }

        async def fetch_json(endpoint):
            url = f"{api_base}/{endpoint}"
            resp = await context.request.get(url, headers=base_headers)
            if resp.ok:
                try:
                    return await resp.json()
                except:
                    return None
            return None

        # 8. Chiamate API reali
        abstract_json = await fetch_json("abstract")
        claims_json = await fetch_json("claims")
        description_json = await fetch_json("description")
        biblio_json = await fetch_json("bibliographic-data")

        screenshot = await page.screenshot(type="png")
        await browser.close()

        return {
            "final_url": final_url,
            "real_id": real_id,
            "abstract_json": abstract_json,
            "claims_json": claims_json,
            "description_json": description_json,
            "biblio_json": biblio_json,
            "screenshot": screenshot
        }

# ------------------------------------------------------------
# PARSING
# ------------------------------------------------------------

def parse_abstract(j):
    if not j:
        return None
    return j.get("abstractText")

def parse_claims(j):
    if not j:
        return []
    claims = []
    for c in j.get("claims", []):
        claims.append({
            "id": str(c.get("claimNumber")),
            "text": c.get("claimText"),
            "dependencies": c.get("dependencies", [])
        })
    return claims

def parse_description(j):
    if not j:
        return None
    return j.get("descriptionText")

def parse_biblio(j):
    if not j:
        return {}
    return {
        "title": j.get("title"),
        "inventors": j.get("inventors", []),
        "assignees": j.get("assignees", []),
        "priority_date": j.get("priorityDate"),
        "filing_date": j.get("filingDate"),
        "publication_date": j.get("publicationDate")
    }

# ------------------------------------------------------------
# MAIN RUN
# ------------------------------------------------------------

def run(patent_id, session_id, chat_id):
    data = asyncio.run(fetch_epo_api(patent_id))

    biblio = parse_biblio(data["biblio_json"])
    abstract = parse_abstract(data["abstract_json"])
    claims = parse_claims(data["claims_json"])
    description = parse_description(data["description_json"])

    return {
        "tool": "patent_epo",
        "query": patent_id,
        "session_id": session_id,
        "chat_id": chat_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "normalized_url": data["final_url"],
        "patent_id": data["real_id"],
        "source": "epo-api",
        "meta": {
            "final_url": data["final_url"]
        },
        "data": {
            "title": biblio.get("title"),
            "abstract": abstract,
            "claims": claims,
            "description": description,
            "inventors": biblio.get("inventors"),
            "assignees": biblio.get("assignees"),
            "priority_date": biblio.get("priority_date"),
            "filing_date": biblio.get("filing_date"),
            "publication_date": biblio.get("publication_date"),
            "metadata": {}
        },
        "screenshot": data["screenshot"]
    }
