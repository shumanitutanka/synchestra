# Synchestra  
### Modular Tool Orchestrator for LLM Agents and OpenWebUI

[![Status](https://img.shields.io/badge/status-stable-brightgreen)]()
[![Version](https://img.shields.io/badge/version-1.0.0-blue)]()
[![Python](https://img.shields.io/badge/python-3.10+-blue)]()
[![License](https://img.shields.io/badge/license-MIT-lightgrey)]()

Synchestra is a lightweight, modular orchestration layer designed to extend LLM systems with **deterministic, auditable tool execution**.  
It integrates seamlessly with **OpenWebUI** (via custom builds or external service mode) and provides a clean HTTP API for structured tool calls.

The project focuses on:

- **Reproducibility**  
- **Modularity**  
- **Auditability**  
- **Deterministic tool behavior**  
- **Zero hidden state**

Synchestra v1.0.0 is the first **official stable release**, replacing the earlier experimental v0.1.0.

---

## ✨ Features

- **Modular tool architecture**  
  Each tool is a standalone Python module with a simple `run()` interface.

- **Stable patent extraction**  
  - Google Patents backend for EP, US, CN, JP, KR, WO  
  - USPTO backend  
  - WIPO backend  

- **Playwright‑based automation**  
  Dynamic loaders for browser‑level extraction when needed.

- **RAG utilities**  
  Document retrieval, semantic search, and PDF text/image extraction.

- **Summarization, analysis, search**  
  Clean, deterministic utilities for LLM pipelines.

- **Stateless HTTP API**  
  A single endpoint for all tool calls.

---

## 🚀 Running Synchestra (Standalone Mode)

Install dependencies:

```bash
pip install -r requirements.txt
playwright install chromium

Start the service:
python3 app.py

Synchestra will listen on:
http://localhost:6001/synchestra

🔗 Integration with OpenWebUI

Synchestra is designed to run alongside OpenWebUI as an external service.

🧩 API Usage
POST /synchestra

Example:
bash

curl -X POST http://localhost:6001/synchestra \
  -H "Content-Type: application/json" \
  -d '{
        "query": "patent EP3803302A1",
        "session_id": "demo",
        "chat_id": "demo"
      }'

Example response:
json

{
  "tool": "postprocess",
  "session_id": "demo",
  "chat_id": "demo",
  "text": "... formatted output ...",
  "timestamp": "2026-02-20T12:00:00"
}


🧠 Design Philosophy

    Deterministic execution  
    Tools return structured JSON, never free‑form text.

    Auditability  
    All tool calls are logged in session state.

    Modularity  
    Tools are isolated and easy to extend.

    Zero magic  
    No hidden behavior, no implicit state.

    Stability over cleverness  
