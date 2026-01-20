# Document Intelligence – Review & Critique

## Overview
The project delivers both a FastAPI backend and Streamlit UI that orchestrate OCR, NLP, summarization, and RAG across modular services (`app/main.py`, `app/streamlit_app.py`, `src/*`). Configuration is centralized in YAML (`config/settings.yaml:1`), prompts live under `prompts/`, and the README plus PRD clearly explain scope (`README.md`, `DI-PRD.md`). Tests are organized into phased suites under `tests/test_phase*.py` to exercise each capability.

## Strengths
- **End-to-end pipeline**: The FastAPI workflow coordinates upload → OCR → chunking → entity extraction → indexing → summarization before exposing REST endpoints (`app/main.py:120-320`).
- **Streamlit parity**: The UI mirrors backend logic so the same features can be demoed interactively (`app/streamlit_app.py:230-420`).
- **Graceful fallbacks**: Summarization and embeddings degrade to extractive summaries or local models when `OPENROUTER_API_KEY` is missing (`src/summarizer.py:41-129`, `src/vector_store.py:37-134`).
- **Config-driven behavior**: Limits, thresholds, and model choices are all configurable via `config/settings.yaml:1`, making portfolio customization straightforward.
- **Layered tests**: Phase tests cover validation, OCR, Q&A, and text processing (`tests/test_phase1.py`, `tests/test_phase4.py`), which helps catch regressions early.

## Key Findings & Critique
1. **Session TTL/cleanup is never activated** – The in-memory `DocumentStore` implements TTL-aware eviction and background cleanup (`src/document_store.py:317-360`), but `start_cleanup_task()` is never called anywhere in the codebase (no references outside its definition). As a result, documents remain in memory indefinitely, directly contradicting the “privacy-first / deleted after session” promise in the PRD (DI-PRD.md:90-112) and risking unbounded RAM use on long-running servers. At minimum the store should start its cleanup loop when instantiated (or run synchronous cleanup on each CRUD call) so the TTL and `max_documents_per_session` settings actually take effect.

2. **Heavy file validation logic is implemented but unused** – `DocumentLoader.validate_file()` enforces extension, size, corruption, and page-count limits (`src/document_loader.py:56-139`), yet neither the FastAPI pipeline (`app/main.py:124`) nor the Streamlit path (`app/streamlit_app.py:252`) call it before loading files. The API only checks extension and size in the request handler, so critical checks like “≤50 pages” (DI-PRD.md:96-103) and corrupt PDF detection are silently skipped. The Streamlit UI performs no size/page validation at all despite advertising a 25 MB limit (`app/streamlit_app.py:234-258`). Hooking `validate_file()` into both entry points (and surfacing the resulting `FileValidation` errors) would keep uploads inside spec and fail fast on malformed documents.

3. **Background processing blocks the event loop** – `process_document_async` is declared `async` but performs CPU-bound PyMuPDF parsing, OCR, pandas work, and HTTP calls synchronously (`app/main.py:120-205`). FastAPI `BackgroundTasks` simply run this coroutine after the response on the same event loop thread, so each upload can monopolize the server for tens of seconds, preventing other requests from being served and violating the p95 latency goals in the README (`README.md:179-184`). Offloading the heavy sections to worker threads/processes (e.g., `asyncio.to_thread` or a task queue) would keep the API responsive under concurrent uploads.

4. **Q&A “graceful degradation” isn’t implemented** – The README promises that without embeddings the Q&A module falls back to keyword matching (`README.md:168-177`), but `QAEngine.answer()` immediately returns `_no_context_response()` whenever the vector store search fails (`src/qa_engine.py:67-121`). The keyword-based `_fallback_response()` is only reached if an LLM call fails *after* context was retrieved, so on systems without embeddings (or with Chroma disabled) users just get “I don't have any document loaded…” despite having uploaded a doc. To meet the spec, the engine should fall back to lexical search over raw text when context retrieval yields no chunks, not just when the LLM errors out.

## Testing
- Attempting to run the full suite (`source venv/bin/activate && pytest -q`) exhausts the sandbox after ~70 % and is killed by the OS (exit code 137). This suggests the suite currently exceeds resource limits locally; consider sharding or slimming the heaviest tests.
- Targeted smoke: `source venv/bin/activate && pytest tests/test_phase1.py -q` → **32 passed**.

## Recommendations / Next Steps
1. Initialize the document-store cleanup loop (or run TTL checks on every operation) so documents are purged per the privacy requirements.
2. Invoke `DocumentLoader.validate_file()` in both the API and Streamlit flows, surfacing detailed validation errors (page-count, corruption, etc.) to users.
3. Move the expensive parts of `process_document_async` into background workers (Celery, RQ, or even `asyncio.to_thread`) to avoid blocking FastAPI’s event loop under load.
4. Rework `QAEngine.answer()` so it performs keyword/regex retrieval when embeddings are unavailable, aligning runtime behavior with the promised “keyword matching” fallback.
5. Investigate why the full pytest run OOMs/timeouts and either optimize those tests or document the hardware expectations.
