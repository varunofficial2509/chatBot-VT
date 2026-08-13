# Personal Recruiter AI Chatbot

A minimal RAG chatbot that lets a recruiter ask questions about a candidate's
resume and experience. Answers are grounded only in an uploaded resume and a
structured JSON profile — nothing is invented.

> Give a recruiter the URL. They ask questions. The bot answers using your
> resume and profile, or says it doesn't know.

## What this is (and isn't)

- A small, single-process FastAPI app with a LangGraph RAG pipeline.
- Not a generic chatbot platform, not multi-tenant, not enterprise-grade.
- See [PROJECT_DECISIONS.md](PROJECT_DECISIONS.md) for the reasoning behind
  every major choice and the tradeoffs this project intentionally accepts.

## Architecture

```text
                    ┌──────────────────────┐
                    │      Recruiter       │
                    │      Chat UI         │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      FastAPI         │
                    │      API Layer       │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     LangGraph         │
                    │  retrieve_context →  │
                    │   generate_answer    │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┴──────────────┐
                 ▼                            ▼
        ┌────────────────┐          ┌─────────────────┐
        │ Chroma Vector  │          │ Profile / JSON  │
        │ Store          │          │ Structured Data │
        └────────────────┘          └─────────────────┘
                 │
                 ▼
        Resume (PDF / DOCX)
```

Every chat request runs through the LangGraph graph (`retrieve_context` →
`generate_answer`), which LangSmith traces end to end when tracing is
enabled.

## Project structure

```text
app/
  main.py              FastAPI app, mounts routes and static frontend
  config.py            All environment-based configuration
  api/
    chat.py            POST /api/chat — recruiter-facing
    admin.py           GET /admin, POST /api/admin/login, POST /api/admin/ingest
    auth.py            Signed-token admin auth
  graph/
    state.py           LangGraph state shape
    recruiter_graph.py retrieve_context -> generate_answer graph
  rag/
    ingestion.py        PDF/DOCX extraction, chunking, Chroma indexing
    retriever.py         top_k similarity search
    embeddings.py         local Sentence Transformers embedding function
    vectorstore.py        Chroma client/collection access
    profile_store.py      structured profile JSON read/write
  llm/
    provider.py          LLM provider abstraction (Anthropic / Gemini)
  prompts/
    recruiter.py          system prompt + grounding rules
frontend/
  index.html, app.js       recruiter chat UI
  admin.html, admin.js      admin ingestion UI
  styles.css                shared 3-color styling
data/
  profile.example.json      example profile shape (not real data)
```

## Setup

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: set ADMIN_PASSWORD and your LLM provider's API key
```

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `LLM_PROVIDER` | yes | `anthropic` or `gemini` |
| `LLM_MODEL` | no | Overrides the provider's default model |
| `ANTHROPIC_API_KEY` | if using Anthropic | Anthropic API key |
| `GOOGLE_API_KEY` | if using Gemini | Google AI Studio API key (has a free tier) |
| `LANGCHAIN_TRACING_V2` | no | `true` to enable LangSmith tracing |
| `LANGCHAIN_API_KEY` | no | LangSmith API key |
| `LANGCHAIN_PROJECT` | no | LangSmith project name |
| `ADMIN_PASSWORD` | yes | Password gating `/admin` ingestion |
| `CHROMA_PATH` | no | Local Chroma storage path (default `./data/chroma`) |
| `TOP_K` | no | Number of resume chunks retrieved per question (default `5`) |

Never commit `.env` — it's already in `.gitignore`.

## Running locally

```bash
uvicorn app.main:app --reload
```

- Recruiter chat: http://localhost:8000/
- Admin ingestion: http://localhost:8000/admin

## Ingesting your resume and profile

1. Copy `data/profile.example.json`, fill in your real information, save it
   somewhere on disk (do **not** commit real personal data to the repo).
2. Open `/admin`, enter `ADMIN_PASSWORD`.
3. Upload your resume (PDF or DOCX) and your filled-in profile JSON.
4. Click **Update Knowledge**. This rebuilds the Chroma collection from
   scratch, so re-ingesting never produces duplicate chunks.

Until you do this, the recruiter chat responds with a "not configured yet"
message instead of crashing or hallucinating.

## Using the recruiter UI

Visit `/`, type a question, and press enter or click send. Follow-up
questions are answered using the same session's short conversation history
(kept in-memory on the server — no external database).

## LangSmith setup

1. Create a project at https://smith.langchain.com.
2. Set `LANGCHAIN_TRACING_V2=true`, `LANGCHAIN_API_KEY`, and
   `LANGCHAIN_PROJECT` in `.env`.
3. Every `/api/chat` call traces the full LangGraph run — retrieval and
   generation — under that project.

## Docker

```bash
docker build -t recruiter-bot .
docker run --env-file .env -p 8000:8000 recruiter-bot
```

## Deployment

This app is a single Python process with local disk storage (Chroma +
profile JSON) — it fits comfortably on any small container host with
persistent-or-not disk, for example:

- **Render** / **Railway** / **Fly.io** — build from the included
  `Dockerfile`, set the environment variables above as secrets, expose port
  `8000`.

**Ephemeral storage limitation:** on free tiers of most of these platforms,
local disk (including `data/chroma`) is **not guaranteed to persist** across
deploys or restarts. If your host's disk is ephemeral, you will need to
re-run ingestion via `/admin` after every deploy/restart, or attach a
persistent volume if the platform offers one. This project does not pretend
otherwise — it's a documented limitation, not a bug.

Never commit real API keys or `ADMIN_PASSWORD` — set them as platform
environment variables/secrets.
