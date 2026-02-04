# -------------------------
# Standard library imports
# -------------------------
import re
import json
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, urlunparse, urlencode, parse_qs
from functools import lru_cache
from typing import Dict, Any, List, Tuple, Optional

# -------------------------
# Third‑party imports
# -------------------------
import numpy as np
import requests
from pydantic import Field
from sentence_transformers.util import cos_sim

# -------------------------
# Local project imports
# -------------------------
# (none in questo file)


class Tools:
    def __init__(self):
        # Stato interno condiviso tra tutti i metodi
        self.state: Dict[str, Any] = {
            "sessions": {},
            "last_session_id": None,
        }
        self.trace: List[Dict[str, Any]] = []

        # Debug mode
        self.debug: bool = True

        # Logging su file
        self.LOG_PATH = Path("/app/backend/data/synchestra.log")
        self.STATE_PATH = Path("/app/backend/data/synchestra_state.json")

        # Path per i files 
        self.KB_PATH = None

        # Embedding model (lazy load)
        self._EMB_MODEL = None
        self._util = None

        # Carica stato persistente
        self._load_state_from_disk()

    # -------------------------------------------------------------------------
    # LOGGING CON TIMESTAMP
    # -------------------------------------------------------------------------

    def _log(self, event: str, data: Dict[str, Any]):
        """Scrive un evento nel file di log con timestamp e aggiorna il trace."""
        timestamp = datetime.utcnow().isoformat()

        entry = {
            "timestamp": timestamp,
            "event": event,
            "data": data,
        }

        try:
            self.LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            with self.LOG_PATH.open("a") as f:
                f.write(f"{timestamp} | {event} | {data}\n")
        except Exception as e:
            print(f"[SYNCHESTRA_LOG_ERROR] {e}")

        self.trace.append(entry)

    # -------------------------------------------------------------------------
    # STATO
    # -------------------------------------------------------------------------

    def _save_state_to_disk(self):
        try:
            import json

            self.STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
            with self.STATE_PATH.open("w") as f:
                json.dump(self.state, f)
        except Exception as e:
            print(f"[SYNCHESTRA_STATE_SAVE_ERROR] {e}")

    def _load_state_from_disk(self):
        try:
            import json

            if self.STATE_PATH.exists():
                with self.STATE_PATH.open("r") as f:
                    self.state = json.load(f)
        except Exception as e:
            print(f"[SYNCHESTRA_STATE_LOAD_ERROR] {e}")

    # -------------------------------------------------------------------------
    # NORMALIZZAZIONE E SEMANTICA
    # -------------------------------------------------------------------------

    def _normalize(self, text: str) -> str:
        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)
        return text

    def _lazy_load_embeddings(self):
        if self._EMB_MODEL is None:
            try:
                from sentence_transformers import SentenceTransformer, util

                self._EMB_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
                self._util = util
            except Exception:
                self._EMB_MODEL = None
                self._util = None

    def _keyword_score(self, text: str, keywords: List[str]) -> float:
        hits = sum(1 for k in keywords if k in text)
        if hits == 0:
            return 0.0
        return min(1.0, 0.4 + 0.15 * hits)

    def _semantic_score(self, text: str, labels: List[str]) -> float:
        self._lazy_load_embeddings()
        if self._EMB_MODEL is None or self._util is None:
            return 0.0
        emb_q = self._EMB_MODEL.encode(text, convert_to_tensor=True)
        emb_l = self._EMB_MODEL.encode(labels, convert_to_tensor=True)
        sims = self._util.cos_sim(emb_q, emb_l)[0]
        return float(sims.max().item())

    # -------------------------------------------------------------------------
    # SESSIONI
    # -------------------------------------------------------------------------

    def _get_session(
        self,
        session_id: Optional[str],
        chat_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Restituisce lo stato di una sessione, creandola se necessario."""
        if not session_id or session_id == "default":
            session_id = chat_id or "default"

        self.state.setdefault("sessions", {})
        if session_id not in self.state["sessions"]:
            self.state["sessions"][session_id] = {
                "history": [],
                "last_action": None,
                "last_result": None,
            }

        self.state["last_session_id"] = session_id
        return self.state["sessions"][session_id]

    # -------------------------------------------------------------------------
    # SUPERVISOR
    # -------------------------------------------------------------------------

    def supervisor(
        self,
        query: str,
        session_id: str = "default",
        chat_id: str = None,
    ) -> Dict[str, Any]:

        if chat_id is None:
            raise ValueError("chat_id is required")

        if session_id == "default":
            session_id = chat_id

        session = self._get_session(session_id, chat_id)
        q_norm = self._normalize(query)

        intents: Dict[str, Dict[str, Any]] = {
            "search": {
                "keywords": ["search", "cerca", "web", "google", "internet", "trova"],
                "labels": ["web search", "internet lookup", "find information online"],
            },
            "summarize": {
                "keywords": ["riassumi", "summary", "sintesi", "resume", "condensa"],
                "labels": ["summarize text", "create a summary", "condense content"],
            },
            "rag": {
                "keywords": [
                    "documento",
                    "file",
                    "rag",
                    "knowledge",
                    "kb",
                    "contenuto",
                ],
                "labels": [
                    "retrieve from documents",
                    "knowledge base query",
                    "RAG over files",
                ],
            },
            "math": {
                "keywords": [
                    "calcola",
                    "compute",
                    "math",
                    "formula",
                    "=",
                    "+",
                    "-",
                    "*",
                    "/",
                ],
                "labels": [
                    "math calculation",
                    "numeric computation",
                    "evaluate expression",
                ],
            },
            "analysis": {
                "keywords": [
                    "analizza",
                    "analysis",
                    "estrai",
                    "parse",
                    "struttura",
                    "classifica",
                ],
                "labels": ["text analysis", "extract structure", "classify content"],
            },
            "format": {
                "keywords": ["formatta", "markdown", "tabella", "table", "json"],
                "labels": ["format output", "markdown formatting", "table formatting"],
            },
        }

        detected: List[Tuple[str, float]] = []

        for action, cfg in intents.items():
            kw_score = self._keyword_score(q_norm, cfg["keywords"])
            sem_score = self._semantic_score(q_norm, cfg["labels"])
            score = max(kw_score, sem_score)
            if score > 0.0:
                detected.append((action, score))

        timestamp = datetime.utcnow().isoformat()

        if not detected:
            result = {
                "action": "chat",
                "payload": {"query": query},
                "confidence": 0.35,
                "secondary_intents": [],
                "mode": "fallback_chat",
                "session_id": session_id,
                "chat_id": chat_id,
                "timestamp": timestamp,
            }
            session["last_action"] = "supervisor_fallback"
            session["last_result"] = result
            session["history"].append(result)
            self._log("SUPERVISOR_FALLBACK", result)
            self._save_state_to_disk()
            return result

        detected.sort(key=lambda x: x[1], reverse=True)
        primary_action, primary_conf = detected[0]

        secondary = [
            {"action": a, "confidence": c} for a, c in detected[1:] if c >= 0.55
        ]

        result = {
            "action": primary_action,
            "payload": {"query": query},
            "confidence": float(round(primary_conf, 3)),
            "secondary_intents": secondary,
            "mode": "routed",
            "session_id": session_id,
            "chat_id": chat_id,
            "timestamp": timestamp,
        }

        session["last_action"] = "supervisor"
        session["last_result"] = result
        session["history"].append(result)

        self._log("SUPERVISOR_DECISION", result)
        self._save_state_to_disk()

        if self.debug:
            return {"debug": "Supervisor decision trace recorded.", "result": result}

        return result

    # -------------------------------------------------------------------------
    # ORCHESTRATOR CORE
    # -------------------------------------------------------------------------

    def orchestrator_core(
        self,
        supervisor_result: Dict[str, Any],
        session_id: str = "default",
        chat_id: str = None,
    ) -> Dict[str, Any]:

        # Fallback robusto
        if chat_id is None:
            chat_id = "default"

        if session_id == "default":
            session_id = chat_id

        session = self._get_session(session_id, chat_id)

        action = supervisor_result.get("action", "chat")
        payload = supervisor_result.get("payload", {})

        result = {
            "status": "dispatch",
            "action": action,
            "payload": payload,
            "session_id": session_id,
            "chat_id": chat_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

        session["last_action"] = "orchestrator_core"
        session["last_result"] = result
        session["history"].append(result)

        self._log("ORCHESTRATOR_CORE_DISPATCH", result)
        self._save_state_to_disk()

        if self.debug:
            return {"debug": "Core dispatch prepared.", "result": result}

        return result

    # -------------------------------------------------------------------------
    # TOOL: SEARCH
    # -------------------------------------------------------------------------

    def detect_intent(self, query: str) -> str:
        q = query.lower()

        informational = [
            "what",
            "how",
            "why",
            "chi",
            "come",
            "perché",
            "cos'è",
            "definizione",
        ]
        navigational = [
            "facebook",
            "youtube",
            "github",
            "amazon",
            ".com",
            ".it",
            ".org",
        ]
        transactional = ["buy", "price", "acquista", "prezzo", "download", "scaricare"]
        news = ["news", "oggi", "ultime", "breaking", "today"]
        technical = [
            "protocol",
            "error",
            "stacktrace",
            "linux",
            "kernel",
            "http",
            "tcp",
        ]
        developer = ["python", "javascript", "api", "sdk", "library", "framework"]
        local = ["bari", "vicino", "near me", "puglia"]

        if not query:
            return "informational"
        if any(w in q for w in navigational):
            return "navigational"
        if any(w in q for w in transactional):
            return "transactional"
        if any(w in q for w in news):
            return "news"
        if any(w in q for w in developer):
            return "developer"
        if any(w in q for w in technical):
            return "technical"
        if any(w in q for w in local):
            return "local"
        if any(w in q for w in informational):
            return "informational"

        return "informational"

    def score_with_intent(
        self, base_score, intent, clean_url, title, snippet, engine, category
    ):
        score = base_score
        url_l = clean_url.lower()

        # --- NAVIGATIONAL ---
        if intent == "navigational":
            if any(
                url_l.startswith(f"https://{d}") or url_l.startswith(f"http://{d}")
                for d in ["facebook.com", "youtube.com", "github.com", "amazon.com"]
            ):
                score += 30
            if category == "general":
                score += 5

        # --- INFORMATIONAL ---
        elif intent == "informational":
            if snippet and len(snippet) > 80:
                score += 10
            if engine in ("duckduckgo", "brave", "bing", "google"):
                score += 8

        # --- TRANSACTIONAL ---
        elif intent == "transactional":
            if any(s in url_l for s in ["amazon", "ebay", "aliexpress", "store"]):
                score += 20
            if "price" in title.lower() if title else False:
                score += 10

        # --- NEWS ---
        elif intent == "news":
            if category == "news":
                score += 20
            if any(n in url_l for n in ["repubblica", "ansa", "bbc", "cnn"]):
                score += 15

        # --- DEVELOPER ---
        elif intent == "developer":
            if any(d in url_l for d in ["github.com", "stackoverflow.com", "pypi.org"]):
                score += 25
            if "api" in title.lower() if title else False:
                score += 10

        # --- TECHNICAL ---
        elif intent == "technical":
            if any(t in url_l for t in ["ietf.org", "rfc-editor.org", "man7.org"]):
                score += 25
            if "error" in title.lower() if title else False:
                score += 10

        # --- LOCAL ---
        elif intent == "local":
            if url_l.endswith(".it"):
                score += 10
            if "bari" in snippet.lower() if snippet else False:
                score += 10

        return score

    def score_result(self, title, snippet, engine, category, clean_url):
        score = 0

        # --- URL QUALITY ---
        if clean_url.startswith("http"):
            score += 10
        if len(clean_url) < 120:
            score += 5
        if "?" not in clean_url:
            score += 3

        # penalità per domini sospetti
        bad_domains = ["click", "redirect", "adservice", "tracking"]
        if any(b in clean_url for b in bad_domains):
            score -= 20

        # --- CONTENT QUALITY ---
        if title:
            score += 5
        if snippet:
            score += 5
        if snippet and len(snippet) > 80:
            score += 3

        # --- ENGINE RELIABILITY ---
        engine_weights = {
            "duckduckgo": 10,
            "brave": 10,
            "bing": 8,
            "google": 8,
            "wikipedia": 5,
            "mojeek": 3,
            "qwant": 3,
            "yandex": -5,
        }

        engine_key = engine.lower() if isinstance(engine, str) else ""
        score += engine_weights.get(engine_key, 0)

        # --- CATEGORY ---
        cat = category or ""
        if cat == "general":
            score += 2
        elif cat == "news":
            score += 5
        elif cat in ("images", "videos", "files"):
            score -= 5

        return score

    def canonical_url(self, url: str) -> str:
        parsed = urlparse(url)

        # normalizza schema
        scheme = "https"

        # normalizza dominio
        netloc = parsed.netloc.lower()

        # normalizza path
        path = parsed.path.rstrip("/").lower()

        # rimuovi parametri di tracking
        tracking_keys = {
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "utm_term",
            "utm_content",
            "fbclid",
            "gclid",
            "mc_cid",
            "mc_eid",
        }
        query_dict = parse_qs(parsed.query)
        filtered = {k: v for k, v in query_dict.items() if k not in tracking_keys}
        query = urlencode(filtered, doseq=True)

        # ricostruzione canonical
        return urlunparse((scheme, netloc, path, "", query, ""))

    def remove_duplicates(self, results):
        seen = set()
        unique = []

        for item in results:
            url = item["url"]
            canon = self.canonical_url(url)

            if canon in seen:
                continue

            seen.add(canon)
            unique.append(item)

        return unique

    def semantic_rerank(self, query, results, embed_fn):
        try:
            q_emb = embed_fn(query)
            for item in results:
                title = item.get("title") or ""
                snippet = item.get("snippet") or ""

                t_emb = embed_fn(title)
                s_emb = embed_fn(snippet)

                sim_title = float(cos_sim(q_emb, t_emb))
                sim_snippet = float(cos_sim(q_emb, s_emb))

                semantic_score = (0.7 * sim_title) + (0.3 * sim_snippet)
                item["score"] += semantic_score * 100

            return results

        except Exception:
            return results  # fallback silenzioso

    def average_embeddings(self, emb_list):
        return np.mean(emb_list, axis=0)

    def cluster_results(self, results, embed_fn, threshold=0.25):
        clusters = []

        for item in results:
            text = (item.get("title") or "") + " " + (item.get("snippet") or "")
            try:
                emb = embed_fn(text)
            except Exception:
                continue

            if not isinstance(emb, np.ndarray):
                continue

            item["embedding"] = emb
            placed = False

            for cluster in clusters:
                centroid = cluster["centroid"]
                try:
                    sim = float(cos_sim(emb, centroid))
                except Exception:
                    continue

                if sim > (1 - threshold):
                    cluster["items"].append(item)
                    cluster["centroid"] = self.average_embeddings(
                        [i["embedding"] for i in cluster["items"]]
                    )
                    placed = True
                    break

            if not placed:
                clusters.append({"centroid": emb, "items": [item]})

        return clusters

    def label_cluster(self, cluster):
        # estrai embedding del centroide
        centroid = cluster["centroid"]

        best_item = None
        best_sim = -1

        for item in cluster["items"]:
            text = (item.get("title") or "") + " " + (item.get("snippet") or "")
            emb = item["embedding"]
            if not isinstance(emb, np.ndarray):
                continue

            sim = float(cos_sim(emb, centroid))

            if sim > best_sim:
                best_sim = sim
                best_item = item

        # fallback
        if not best_item:
            return "Cluster"

        # usa il titolo come label
        return best_item.get("title") or "Cluster"

    def semantic_density(self, embedding):
        return np.linalg.norm(embedding)

    def filter_noise(self, results, density_threshold=1.0, min_snippet_len=20):
        filtered = []
        for item in results:
            snippet = item.get("snippet") or ""
            emb = item.get("embedding")

            if not isinstance(emb, np.ndarray):
                continue

            if len(snippet) < min_snippet_len:
                continue

            if self.semantic_density(emb) < density_threshold:
                continue

            filtered.append(item)

        return filtered

    @lru_cache(maxsize=2048)
    def _cached_embed(self, text: str):
        self._lazy_load_embeddings()
        if self._EMB_MODEL is None:
            return np.zeros(384)
        return self._EMB_MODEL.encode(text)

    def embed_fn(self, text: str):
        return self._cached_embed(text)

    def tool_search(
        self,
        query: str,
        session_id: str = "default",
        chat_id: str = None,
    ) -> Dict[str, Any]:

        # Fallback robusto
        if chat_id is None:
            chat_id = "default"

        if session_id == "default":
            session_id = chat_id

        session = self._get_session(session_id, chat_id)

        url = "http://192.168.100.18:8888/search"
        params = {"q": query, "format": "json"}
        session_time = datetime.utcnow().isoformat()

        # struttura base del risultato
        result = {
            "tool": "search",
            "query": query,
            "results": [],
            "error": "search error",
            "session_id": session_id,
            "chat_id": chat_id,
            "timestamp": session_time,
        }

        used_engine = []
        used_category = []

        tracking_keys = {
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "utm_term",
            "utm_content",
            "fbclid",
            "gclid",
            "mc_cid",
            "mc_eid",
        }

        try:
            r = requests.get(url, params=params, timeout=10)
            if r.status_code != 200:
                raise Exception("HTTP error")

            data = r.json()
            results = data.get("results", [])

            if not isinstance(results, list) or len(results) == 0:
                # nessun risultato
                result["error"] = "no results query error"
                session["last_action"] = "tool_search"
                session["last_result"] = result
                session["history"].append(result)
                self._log("TOOL_SEARCH_CALLED", result)
                self._save_state_to_disk()
                return result

            parsed_results = []

            for element in results:
                title = element.get("title")
                raw_url = element.get("url")
                snippet = element.get("content")
                engine = element.get("engine")
                category = element.get("category")

                if not raw_url:
                    continue

                # --- URL CLEANING ---
                clean = raw_url.strip()
                clean = clean.replace("\n", "").replace("\t", "")
                clean = clean.replace("\\n", "").replace("\\t", "")

                if not clean:
                    continue

                # normalizzazione schema //example.com
                if clean.startswith("//"):
                    clean = "https:" + clean

                parsed = urlparse(clean)

                # se manca schema ma c’è netloc → aggiungi http
                if not parsed.scheme and parsed.netloc:
                    clean = "http://" + clean
                    parsed = urlparse(clean)

                # se manca tutto → scarta
                if not parsed.netloc and not parsed.scheme:
                    continue

                # --- RIMOZIONE TRACKING ---
                query_dict = parse_qs(parsed.query)
                filtered = {
                    k: v for k, v in query_dict.items() if k not in tracking_keys
                }
                new_query = urlencode(filtered, doseq=True)
                clean = urlunparse(parsed._replace(query=new_query))

                if not clean:
                    continue

                intent = self.detect_intent(query)
                base_score = self.score_result(title, snippet, engine, category, clean)
                final_score = self.score_with_intent(
                    base_score, intent, clean, title, snippet, engine, category
                )

                parsed_results.append(
                    {
                        "title": title,
                        "url": clean,
                        "snippet": snippet,
                        "engine": engine,
                        "type": category,
                        "score": final_score,
                    }
                )

                used_engine.append(engine)
                used_category.append(category)

            parsed_results = self.remove_duplicates(parsed_results)
            parsed_results = self.semantic_rerank(query, parsed_results, self.embed_fn)
            clusters = self.cluster_results(parsed_results, self.embed_fn)

            labeled_clusters = []
            for cluster in clusters:
                items = self.filter_noise(cluster["items"])
                if not items:
                    continue
                label = self.label_cluster(
                    {"centroid": cluster["centroid"], "items": items}
                )
                labeled_clusters.append({"label": label, "items": items})

            final_results = [item for c in labeled_clusters for item in c["items"]]
            final_results.sort(key=lambda x: x["score"], reverse=True)

            # costruzione risultato finale
            result = {
                "tool": "search",
                "query": query,
                "results": final_results,
                "clusters": labeled_clusters,
                "count": len(final_results),
                "error": "",
                "session_id": session_id,
                "chat_id": chat_id,
                "timestamp": session_time,
            }

            session["last_action"] = "tool_search"
            session["last_result"] = result
            session["history"].append(result)
            session["history"].append(used_engine)
            session["history"].append(used_category)

            self._log("TOOL_SEARCH_CALLED", result)
            self._save_state_to_disk()

            return result

        except Exception as e:
            result["error"] = str(e)
            session["last_action"] = "tool_search"
            session["last_result"] = result
            session["history"].append(result)
            self._log("TOOL_SEARCH_ERROR", {"error": str(e)})
            self._save_state_to_disk()
            return result

    # -------------------------------------------------------------------------
    # TOOL: estrattore testo da documenti pdf
    # -------------------------------------------------------------------------

    def _extract_text(self, path: Path) -> str:
        ext = path.suffix.lower()

        # TXT / MD: lettura diretta
        if ext in {".txt", ".md", ".markdown"}:
            try:
                return path.read_text(errors="ignore")
            except Exception:
                return ""

        # HTML: estrazione testo con BeautifulSoup
        if ext in {".html", ".htm"}:
            try:
                from bs4 import BeautifulSoup

                html = path.read_text(errors="ignore")
                soup = BeautifulSoup(html, "html.parser")
                return soup.get_text(" ", strip=True)
            except Exception:
                return ""

        # DOCX: Word
        if ext == ".docx":
            try:
                import docx

                doc = docx.Document(str(path))
                return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
            except Exception:
                return ""

        # ODT: OpenOffice
        if ext == ".odt":
            try:
                from odf.opendocument import load
                from odf.text import P

                doc = load(str(path))
                paragraphs = doc.getElementsByType(P)
                return "\n".join(p.firstChild.data for p in paragraphs if p.firstChild)
            except Exception:
                return ""

        # PDF: testo con pdfminer.six
        if ext == ".pdf":
            try:
                from pdfminer.high_level import extract_text

                return extract_text(str(path))
            except Exception:
                return ""

        # Fallback
        try:
            return path.read_text(errors="ignore")
        except Exception:
            return ""

    # -------------------------------------------------------------------------
    # TOOL: estrattore immagini da documenti pdf
    # -------------------------------------------------------------------------

    def _extract_images_from_pdf(self, path: Path) -> List[Dict[str, Any]]:
        images: List[Dict[str, Any]] = []
        try:
            import fitz  # PyMuPDF
        except Exception:
            return images

        try:
            doc = fitz.open(str(path))
        except Exception:
            return images

        for page_index, page in enumerate(doc):
            try:
                for img_index, img in enumerate(page.get_images(full=True)):
                    xref = img[0]
                    try:
                        pix = fitz.Pixmap(doc, xref)
                        if pix.n < 5:  # RGB o GRAY
                            data = pix.tobytes("png")
                        else:
                            pix_converted = fitz.Pixmap(fitz.csRGB, pix)
                            data = pix_converted.tobytes("png")
                            pix_converted = None
                        images.append(
                            {
                                "page": page_index,
                                "index": img_index,
                                "bytes": data,
                            }
                        )
                        pix = None
                    except Exception:
                        continue
            except Exception:
                continue

        return images

    # -------------------------------------------------------------------------
    # TOOL: RAG (POTENZIATO)
    # -------------------------------------------------------------------------

    def tool_rag(
        self,
        query: str,
        session_id: str = "default",
        chat_id: str = None,
    ):
        # Fallback robusto
        if chat_id is None:
            chat_id = "default"

        if session_id == "default":
            session_id = chat_id

        session = self._get_session(session_id, chat_id)


        # Se l’utente/test ha impostato KB_PATH, usalo
        if self.KB_PATH is not None:
            base = Path(self.KB_PATH)
        else:
        # fallback: directory reale del progetto
            project_root = Path(__file__).resolve().parent
            base = project_root / "data" / "uploads"


        documents: List[Dict[str, Any]] = []
        filenames: List[str] = []

        if base.exists():
            for f in base.iterdir():
                if not f.is_file():
                    continue

                ext = f.suffix.lower()
                # Estensioni che vogliamo considerare
                if ext not in {
                    ".txt",
                    ".md",
                    ".markdown",
                    ".html",
                    ".htm",
                    ".docx",
                    ".odt",
                    ".pdf",
                }:
                    continue

                text = self._extract_text(f)
                images: List[Dict[str, Any]] = []

                if ext == ".pdf":
                    images = self._extract_images_from_pdf(f)

                if not text and not images:
                    # Documento vuoto o non leggibile: lo saltiamo
                    continue

                documents.append(
                    {
                        "filename": f.name,
                        "extension": ext,
                        "text": text,
                        "images": images,
                    }
                )
                filenames.append(f.name)

        docs_count = len(documents)

        if docs_count == 0:
            note = "No documents found or readable in RAG source directory."
        else:
            note = f"{docs_count} documents loaded and processed from RAG source directory."

        result = {
            "tool": "rag",
            "query": query,
            "documents": documents,
            "docs_count": docs_count,
            "filenames": filenames,
            "note": note,
            "session_id": session_id,
            "chat_id": chat_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

        session["last_action"] = "tool_rag"
        session["last_result"] = result
        session["history"].append(result)

        self._log(
            "TOOL_RAG_CALLED",
            {
                "query": query,
                "docs_count": docs_count,
                "filenames": filenames,
                "session_id": session_id,
                "chat_id": chat_id,
            },
        )
        self._save_state_to_disk()

        return result

    # -------------------------------------------------------------------------
    # TOOL: MATH
    # -------------------------------------------------------------------------

    def tool_math(
        self,
        expression: str,
        session_id: str = "default",
        chat_id: str = None,
    ) -> Dict[str, Any]:

        if chat_id is None:
            chat_id = "default"

        if session_id == "default":
            session_id = chat_id

        session = self._get_session(session_id, chat_id)

        try:
            result_value = eval(expression, {"__builtins__": {}})
            result = {
                "tool": "math",
                "expression": expression,
                "result": result_value,
                "session_id": session_id,
                "chat_id": chat_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            result = {
                "tool": "math",
                "expression": expression,
                "error": str(e),
                "session_id": session_id,
                "chat_id": chat_id,
                "timestamp": datetime.utcnow().isoformat(),
            }

        session["last_action"] = "tool_math"
        session["last_result"] = result
        session["history"].append(result)

        self._log("TOOL_MATH_CALLED", result)
        self._save_state_to_disk()

        return result

    # -------------------------------------------------------------------------
    # TOOL: SUMMARIZE
    # -------------------------------------------------------------------------

    def tool_summarize(
        self,
        text: str,
        session_id: str = "default",
        chat_id: str = None,
    ) -> Dict[str, Any]:

        if chat_id is None:
            chat_id = "default"

        if session_id == "default":
            session_id = chat_id

        session = self._get_session(session_id, chat_id)
        truncated = text[:8000]

        result = {
            "tool": "summarize",
            "text": truncated,
            "session_id": session_id,
            "chat_id": chat_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

        session["last_action"] = "tool_summarize"
        session["last_result"] = result
        session["history"].append(result)

        self._log("TOOL_SUMMARIZE_CALLED", {"len": len(truncated)})
        self._save_state_to_disk()

        return result

    # -------------------------------------------------------------------------
    # TOOL: ANALYSIS
    # -------------------------------------------------------------------------

    def tool_analysis(
        self,
        text: str,
        session_id: str = "default",
        chat_id: str = None,
    ) -> Dict[str, Any]:

        if chat_id is None:
            chat_id = "default"

        if session_id == "default":
            session_id = chat_id

        session = self._get_session(session_id, chat_id)

        result = {
            "tool": "analysis",
            "text": text,
            "session_id": session_id,
            "chat_id": chat_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

        session["last_action"] = "tool_analysis"
        session["last_result"] = result
        session["history"].append(result)

        self._log("TOOL_ANALYSIS_CALLED", {"len": len(text)})
        self._save_state_to_disk()

        return result

    # -------------------------------------------------------------------------
    # TOOL: FORMAT
    # -------------------------------------------------------------------------

    def tool_format(
        self,
        content: str,
        session_id: str = "default",
        chat_id: str = None,
    ) -> Dict[str, Any]:

        if chat_id is None:
            chat_id = "default"

        if session_id == "default":
            session_id = chat_id

        session = self._get_session(session_id, chat_id)

        md = f"```\n{content}\n```"

        result = {
            "tool": "format_markdown",
            "markdown": md,
            "session_id": session_id,
            "chat_id": chat_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

        session["last_action"] = "tool_format"
        session["last_result"] = result
        session["history"].append(result)

        self._log("TOOL_FORMAT_CALLED", {"len": len(content)})
        self._save_state_to_disk()

        return result

    # -------------------------------------------------------------------------
    # DEBUG / TRACE / STATO
    # -------------------------------------------------------------------------

    def read_logs(self, lines: int = 200) -> Dict[str, Any]:
        if not self.LOG_PATH.exists():
            return {"error": "Log file not found."}
        content = self.LOG_PATH.read_text().splitlines()
        tail = content[-lines:] if lines > 0 else content
        return {"log_tail": "\n".join(tail), "lines_returned": len(tail)}

    def dump_state(self) -> Dict[str, Any]:
        return {"state": self.state, "trace_len": len(self.trace)}

    def reset_state(self) -> Dict[str, Any]:
        self.state = {"sessions": {}, "last_session_id": None}
        self.trace = []
        self._save_state_to_disk()
        self._log("STATE_RESET", {"info": "State and trace cleared."})
        return {"status": "ok", "message": "Synchestra state and trace reset."}
