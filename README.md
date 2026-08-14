# Varun Teja — Portfolio + AI Resume Assistant

A minimal, dark personal developer portfolio with an integrated AI chatbot.
Recruiters can browse the site normally, or ask the AI assistant questions
about my experience — answered only from my actual resume and profile,
grounded by RAG, never invented.

## Overview

Two experiences, one app:

- **Portfolio** — Home and Projects pages, driven by plain JSON content files.
- **AI Assistant** — a LangGraph RAG chatbot answering from a Chroma vector
  store built from my resume/profile.

## Features

- Native Streamlit multipage navigation (`st.navigation`, top bar): Home,
  Projects, AI Assistant.
- Minimal dark theme — exactly three colors (background, text, accent),
  no default Streamlit blue/purple, no gradients, no icon soup.
- Chat UI with `st.chat_message` / `st.chat_input`, markdown + code block
  support, empty-state suggestion chips.
- Owner-only knowledge management (hidden page, password-gated) — upload a
  resume PDF, a Markdown profile, or a JSON profile, then rebuild the index.
- Knowledge base auto-rebuilds on startup if empty but source files exist —
  no manual re-upload after a redeploy.

## Architecture

```text
                  ┌──────────────────┐
                  │    Streamlit     │
                  │ (portfolio + UI) │
                  └────────┬─────────┘
                           │  AI Assistant page
                           ▼
                  ┌──────────────────┐
                  │    LangGraph     │
                  │  retrieve_context │
                  │  → generate_answer│
                  └────────┬─────────┘
                           │
                 ┌─────────┴──────────┐
                 ▼                    ▼
        ┌────────────────┐   ┌─────────────────┐
        │ Chroma Vector  │   │ Profile / JSON  │
        │ Store          │   │ Structured Data │
        └────────────────┘   └─────────────────┘
                 │
                 ▼
        Knowledge (PDF / Markdown)
```

Home and Projects read from `data/profile.json`, `projects.json`,
`experience.json`, `skills.json` — plain presentation content, kept
separate from the chatbot's grounding data (`data/knowledge/`). See
[PROJECT_DECISIONS.md](PROJECT_DECISIONS.md) for the reasoning behind this
split and every other major choice.

## Project structure

```text
streamlit_app.py             Entrypoint: theme, page registration, top nav

pages/
  home.py                    Portfolio landing page
  projects.py                 Projects list
  assistant.py                  AI chat (LangGraph RAG)
  admin.py                        Hidden: knowledge management (password-gated)

app/
  config.py                  All environment-based configuration
  ui/
    theme.py                 Three-color dark theme (CSS + page config)
    components.py             Shared blocks: brand header, section titles, skill pills, footer
    chat.py                     Chat history rendering + empty-state suggestions
  rag/
    ingestion.py              PDF/Markdown/JSON extract -> chunk -> embed -> store
    embeddings.py               Local Sentence Transformers / Gemini embeddings
    vectorstore.py                Chroma access behind add_documents()/search()
    retrieval.py                    top_k similarity search
    profile_store.py                  Structured profile JSON read (chatbot grounding)
  graph/
    state.py                  LangGraph state shape
    nodes.py                    retrieve_context / generate_answer nodes
    edges.py                      Graph wiring
    graph.py                        build_graph() / run_graph()
    prompts.py                        System prompt + grounding rules
  services/
    llm.py                     Gemini chat model client
    content.py                   Loads presentation content (profile/projects/experience/skills)

data/
  profile.json                Portfolio bio, tagline, current focus, contact links
  projects.json                Projects list
  experience.json               Work history
  skills.json                     Homepage skill list
  knowledge/                  Chatbot's RAG source of truth — loaded on startup
    resume.pdf
    profile.md
    profile.json               Structured profile merged into every chat prompt
    profile.example.json        Template for the schema above (not real data)
  vectorstore/                Chroma index (rebuilt from data/knowledge/)

.streamlit/config.toml       Streamlit's native theme (background/text/accent)
tests/                        Unit tests for ingestion (chunking, validation)
```

## Local setup

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
| `LLM_MODEL` | no | Overrides the default Gemini model (`gemini-3.5-flash-lite`) |
| `GOOGLE_API_KEY` | yes | Google AI Studio API key (has a free tier) |
| `LANGCHAIN_TRACING_V2` | no | `true` to enable LangSmith tracing |
| `LANGCHAIN_API_KEY` | no | LangSmith API key |
| `LANGCHAIN_PROJECT` | no | LangSmith project name |
| `ADMIN_PASSWORD` | yes | Password gating the hidden knowledge management page |
| `CHROMA_PATH` | no | Local Chroma storage path (default `./data/vectorstore`) |
| `TOP_K` | no | Number of knowledge chunks retrieved per question (default `5`) |

Never commit `.env` — it's already in `.gitignore`.

## Running locally

```bash
streamlit run streamlit_app.py
```

## Adding/updating profile knowledge

**Portfolio content** (Home/Projects pages): edit `data/profile.json`,
`projects.json`, `experience.json`, `skills.json` directly — plain JSON,
no admin UI needed.

**Chatbot knowledge base**:

1. Open the app and go to the `/admin` URL path directly, or click the
   small "Owner" link in the footer, then enter `ADMIN_PASSWORD` to unlock.
   It's a real page, just not listed in the top navigation.
2. Upload a resume (PDF), a Markdown profile, and/or a profile JSON
   (see `data/knowledge/profile.example.json` for the required shape).
3. Click **Rebuild Knowledge Base** — this re-extracts, re-chunks, and
   re-embeds everything in `data/knowledge/`, so rebuilding never produces
   duplicate chunks.

Until a profile exists, the AI Assistant responds with a "not configured
yet" message instead of crashing or hallucinating. Files committed to
`data/knowledge/` are picked up automatically on startup if the vector
store is empty — no manual upload needed after a fresh deploy.

## LangSmith

Not enabled by default. To turn it on later, set `LANGCHAIN_TRACING_V2=true`,
`LANGCHAIN_API_KEY`, and `LANGCHAIN_PROJECT` — no code changes required.
`run_graph()` already attaches project metadata and a tag to every run, and
nothing in `app/graph` or `app/rag` depends on Streamlit, so tracing can be
layered on without touching the UI.

## Deployment

See [STREAMLIT_DEPLOYMENT.md](STREAMLIT_DEPLOYMENT.md) for step-by-step
instructions on hosting this on Streamlit Community Cloud.
