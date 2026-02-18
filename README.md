# Domain Expansion: Infinite Interviews

A stateful job-application automation system that treats your placement hunt like an engineering pipeline.

## Is it finished?

Not fully. This is now an **implemented starter backend** with real orchestration foundations (FastAPI + LangGraph + optional LangChain model usage), but scraping, LaTeX rendering, and browser submission are still placeholder integrations to complete next.

## What is implemented now

- FastAPI service and background workflow execution.
- SQLite application ledger (`Pending` → `Found` → `Tailored` → `Applied`/`Failed`).
- **LangGraph** state graph with explicit node flow:
  - Scout
  - Strategist
  - Adapter
  - Executioner
- **LangChain/OpenAI integration path** in Strategist node when `OPENAI_API_KEY` is configured.
- Deterministic fallback logic when API key is not configured.
- `.env` based configuration with `pydantic-settings` and `.env.example` template.
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

3. Run API:

   ```bash
   uvicorn app.main:app --reload
   ```

4. Submit a job URL:

   ```bash
   curl -X POST http://127.0.0.1:8000/apply \
     -H 'Content-Type: application/json' \
     -d '{"job_url":"https://example.com/job/123"}'
   ```

5. Check applications:

   ```bash
   curl http://127.0.0.1:8000/applications
   ```

## Config (`.env`)

Use `.env` (from `.env.example`):

- `APP_NAME`
- `APP_VERSION`
- `OPENAI_API_KEY` (optional; enables model-assisted Strategist step)

## Current API

- `GET /health`
- `POST /apply`
- `GET /applications`
- `GET /applications/{id}`

## Architecture snapshot

### Gateway: FastAPI

- Receives incoming jobs.
- Persists initial record.
- Starts background workflow.

### Orchestration: LangGraph

- Strict state graph with deterministic node order.
- Shared state fields:
  - `job_url`
  - `job_description`
  - `extracted_skills`
  - `selected_projects`
  - `resume_pdf_path`
  - `application_status`
  - `error_log`

## Remaining build items

1. Replace Scout placeholder with real URL scraping/extraction.
2. Connect Strategist to vector store (ChromaDB) for RAG.
3. Implement Adapter LaTeX rewriting + `pdflatex` output.
4. Implement Executioner portal automation using Playwright.
5. Add auth, retries, queueing, and observability hardening.
6. Add frontend dashboard and interview-coaching mode.
