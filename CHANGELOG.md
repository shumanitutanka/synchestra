# Changelog  
All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)  
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] – 2026-02-20  
### Added
- **Complete modular architecture** replacing the previous monolithic design.
- New `app.py` exposing a clean HTTP API (`POST /synchestra`).
- New `supervisor.py` with deterministic routing, session handling, and tool orchestration.
- New `state.py` for persistent session state and history tracking.
- Full tool suite under `tools/`:
  - Patent tools: `patent_google`, `patent_uspto`, `patent_wipo`, `patent_universal`
  - Utility tools: `search`, `rag`, `summarize`, `analysis`, `postprocess`
  - Loader system: `dynamic_loader`, `static_loader`, `universal_loader`
- Stable patent routing:  
  EP, US, CN, JP, KR, WO → **Google Patents backend** for reliability.
- Clean post‑processing pipeline for LLM‑friendly output.
- Production‑ready project structure suitable for integration with OpenWebUI or external LLM agents.

### Changed
- Replaced the legacy monolithic orchestrator with a fully modular system.
- Unified tool interface: all tools now expose a consistent `run()` signature.
- Improved error handling, logging, and session isolation.
- Patent routing no longer depends on Espacenet (deprecated APIs).

### Removed
- `patent_epo` module (Espacenet backend deprecated).
- Legacy `synchestra.py` monolithic orchestrator.
- Old test suite and obsolete utilities.
- All unused or dead code from the previous architecture.

---

## [0.1.0] – 2026-02-06  
### Added
- First public release of Synchestra.
- Initial supervisor (intent detection + routing).
- Early orchestrator core.
- Web search tool (semantic reranking, clustering, canonicalization).
- RAG engine (text + PDF image extraction).
- Summarization, analysis, formatting, math tools.
- Persistent state + logging system.
- Upload‑based document ingestion.

### Notes
This release was experimental.  
APIs, internal structures, and tool interfaces were subject to change.

---

## [Unreleased]
### Planned
- Additional patent backends (optional).
- Extended RAG pipeline with embeddings cache.
- Tool sandboxing and execution limits.
- Optional authentication layer for API access.
