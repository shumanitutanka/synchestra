# Synchestra — Modular AI Orchestrator for OpenWebUI

Synchestra is a modular, deterministic, and extensible orchestration engine designed to enhance OpenWebUI with intelligent tool routing, semantic search, document processing, and multi‑step reasoning.

It provides a clean separation between:
- **Supervisor** — intent detection and routing  
- **Orchestrator Core** — dispatch logic  
- **Tools** — search, RAG, summarization, math, formatting, analysis  

Synchestra is built for reliability, transparency, and reproducibility.  
Every action is logged, every session is tracked, and every tool is isolated.

---

## ✨ Features

### 🔍 Intelligent Web Search (via SearXNG)
- URL cleaning and canonicalization  
- Duplicate removal  
- Semantic reranking (SentenceTransformers)  
- Clustering and noise filtering  
- Engine/category scoring  
- Intent‑aware ranking (informational, navigational, transactional, etc.)

### 📄 RAG Engine (Retrieval‑Augmented Generation)
- Automatic ingestion of documents from `/uploads`  
- Text extraction from TXT, MD, HTML, DOCX, ODT, PDF  
- Image extraction from PDF (PyMuPDF)  
- Embedding‑based similarity search  
- Fully local, no external dependencies  

### 🧠 Supervisor
- Keyword + semantic intent detection  
- Multi‑intent scoring  
- Fallback chat mode  
- Session‑aware routing  

### 🧰 Tools
- `tool_search` — semantic web search  
- `tool_rag` — document retrieval  
- `tool_summarize` — text condensation  
- `tool_analysis` — structural analysis  
- `tool_format` — markdown formatting  
- `tool_math` — safe expression evaluation  

### 🧾 Logging & State
- Persistent JSON state  
- Timestamped logs  
- Full trace of decisions  
- Session history  

---

## 📦 Installation

Synchestra is designed to run inside OpenWebUI as a Python tool.
