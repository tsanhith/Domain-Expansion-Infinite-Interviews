# Domain Expansion: Infinite Interviews

A stateful job-application automation system that treats your placement hunt like an engineering pipeline.

## Is it finished?

Not fully. This is an implemented starter backend with FastAPI + LangGraph orchestration and provider-backed strategist logic. Scraping, LaTeX rendering, vector-RAG, and browser submission are still placeholder integrations to complete next.

## What changed for your latest issue

- Added `GET /` so opening `http://127.0.0.1:8000/` returns a status payload instead of 404.
- Added `GET /favicon.ico` returning `204` so browser favicon requests no longer produce noisy 404 logs.
- Replaced deprecated Google LangChain integration path with the newer `google-genai` SDK path for Google AI Studio keys.

## What is implemented now

- FastAPI service and background workflow execution.
- SQLite application ledger (`Pending` → `Found` → `Tailored` → `Applied`/`Failed`).
- LangGraph state graph with explicit node flow:
  - Scout
  - Strategist
  - Adapter
  - Executioner
- Strategist model integration with provider selection:
  - Google AI Studio (`GOOGLE_API_KEY`) via `google-genai`
  - OpenAI (`OPENAI_API_KEY`) via `langchain-openai`
- Deterministic fallback logic when no provider key is configured.
- `.env` configuration via `pydantic-settings` and `.env.example` template.
- Basic API tests.

## Quickstart

1. Copy env template:

   ```bash
   cp .env.example .env
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Add your Google AI Studio key in `.env`:

   ```dotenv
   LLM_PROVIDER=google
   LLM_MODEL=gemini-1.5-flash
   GOOGLE_API_KEY=your_key_here
   ```

4. Run API:

   ```bash
   uvicorn app.main:app --reload
   ```

5. Validate service:

   ```bash
   curl http://127.0.0.1:8000/
   curl http://127.0.0.1:8000/health
   ```

6. Submit a job URL:

   ```bash
   curl -X POST http://127.0.0.1:8000/apply \
     -H 'Content-Type: application/json' \
     -d '{"job_url":"https://example.com/job/123"}'
   ```

7. Check applications:

   ```bash
   curl http://127.0.0.1:8000/applications
   ```

## Config (`.env`)

Use `.env` (from `.env.example`):

- `APP_NAME`
- `APP_VERSION`
- `LLM_PROVIDER` (`google` or `openai`)
- `LLM_MODEL` (e.g. `gemini-1.5-flash`)
- `GOOGLE_API_KEY` (for Google AI Studio)
- `OPENAI_API_KEY` (optional fallback provider)

## Current API

- `GET /`
- `GET /favicon.ico`
- `GET /health`
- `POST /apply`
- `GET /applications`
- `GET /applications/{id}`

## Remaining build items

1. Replace Scout placeholder with real URL scraping/extraction.
2. Connect Strategist to vector store (ChromaDB) for RAG.
3. Implement Adapter LaTeX rewriting + `pdflatex` output.
4. Implement Executioner portal automation using Playwright.
5. Add auth, retries, queueing, and observability hardening.
6. Add frontend dashboard and interview-coaching mode.
