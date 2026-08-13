# Personal Recruiter AI Chatbot

A minimal RAG chatbot that lets a recruiter ask questions about a candidate's
resume and experience. Answers are grounded only in uploaded knowledge (a
resume, a Markdown profile, a structured JSON profile) — nothing is invented.

> Give a recruiter the URL. They ask questions. The bot answers using your
> resume and profile, or says it doesn't know.

## What this is (and isn't)

- A small, single-process Streamlit app with a LangGraph RAG pipeline.
- Not a generic chatbot platform, not multi-tenant, not enterprise-grade.
- See [PROJECT_DECISIONS.md](PROJECT_DECISIONS.md) for the reasoning behind
  every major choice and the tradeoffs this project intentionally accepts.

## Architecture

```text
                    ┌──────────────────────┐
                    │      Streamlit       │
                    │          UI          │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      LangGraph        │
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
        Knowledge (PDF / Markdown)
```

Every chat request runs through the LangGraph graph (`retrieve_context` →
`generate_answer`), which LangSmith traces end to end once tracing is
enabled (see below).

## Project structure

```text
app.py                       Streamlit entrypoint/orchestrator

src/
  config/settings.py         All environment-based configuration
  ui/
    layout.py                Page config, header
    styles.py                 Three-color CSS
    components.py              Chat rendering + owner-only knowledge panel
  ingestion/
    loader.py                  PDF/Markdown text extraction
    parser.py                   Text normalization + profile JSON validation
    chunker.py                   Recursive character chunking
    pipeline.py                   Orchestrates extract -> chunk -> embed -> store
  rag/
    embeddings.py                Local Sentence Transformers / Gemini embeddings
    vectorstore.py                 Chroma access behind add_documents()/search()
    retriever.py                    top_k similarity search
    profile_store.py                 Structured profile JSON read
  graph/
    state.py                      LangGraph state shape
    nodes.py                       retrieve_context / generate_answer nodes
    edges.py                        Graph wiring
    graph.py                        build_graph() / run_graph()
    prompts.py                      System prompt + grounding rules
  llm/
    client.py                     LLM provider abstraction (Anthropic / Gemini)

data/
  knowledge/                  Your resume/profile — loaded on startup
    resume.pdf
    profile.md
    profile.json
  vectorstore/                Chroma index (rebuilt from data/knowledge/)
  profile.example.json        Example profile shape (not real data)

tests/                        Unit tests for ingestion (chunking, validation)
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
| `ADMIN_PASSWORD` | yes | Password gating the in-app knowledge management panel |
| `CHROMA_PATH` | no | Local Chroma storage path (default `./data/vectorstore`) |
| `TOP_K` | no | Number of knowledge chunks retrieved per question (default `5`) |

Never commit `.env` — it's already in `.gitignore`.

## Running locally

```bash
streamlit run app.py
```

## Managing your knowledge

1. Copy `data/profile.example.json`, fill in your real information.
2. Open the app, expand the sidebar, enter `ADMIN_PASSWORD` to unlock the
   **Knowledge** panel.
3. Upload a resume (PDF), a Markdown profile, and/or your profile JSON.
4. Click **Rebuild Knowledge Base**. This re-extracts, re-chunks, and
   re-embeds everything in `data/knowledge/`, so re-ingesting never produces
   duplicate chunks.

Until a profile exists, the chat responds with a "not configured yet"
message instead of crashing or hallucinating.

Files placed directly in `data/knowledge/` (e.g. by committing them to the
repo) are picked up automatically on startup if the vector store is empty —
no manual upload needed after a fresh deploy.

## Using the chat

Type a question in the chat box at the bottom and press enter. Follow-up
questions are answered using the same browser session's conversation
history (kept in `st.session_state`, capped at the last 20 turns).

## LangSmith setup

1. Create a project at https://smith.langchain.com.
2. Set `LANGCHAIN_TRACING_V2=true`, `LANGCHAIN_API_KEY`, and
   `LANGCHAIN_PROJECT` in `.env`.
3. Every chat turn traces the full LangGraph run — retrieval and
   generation — under that project. No code changes are required.

## Deployment

See [STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md) for step-by-step
instructions on hosting this on Streamlit Community Cloud.
