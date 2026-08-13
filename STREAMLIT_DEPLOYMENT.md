# Streamlit Community Cloud Deployment Guide

## Local setup

```bash
git clone https://github.com/<you>/chatBot-VT.git
cd chatBot-VT
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env with your real values (see README.md for the variable list)

streamlit run app.py
```

## GitHub setup

**Commit:**
- All of `src/`, `app.py`, `requirements.txt`
- `data/knowledge/` — your real resume/profile files (`resume.pdf`,
  `profile.md`, `profile.json`). This app's whole purpose is to surface this
  data to recruiters, so it's meant to be public. It also lets the app
  auto-rebuild its knowledge base on a fresh deploy, since Streamlit
  Community Cloud's disk is ephemeral.
- `data/profile.example.json` (a template, not real data)

**Never commit:**
- `.env` (already git-ignored)
- `.streamlit/secrets.toml` (already git-ignored)
- `data/vectorstore/` (already git-ignored) — it's a rebuildable index, not
  source data; committing it just bloats the repo with binary files

If you'd rather keep your resume/profile out of the git history, that's a
valid choice too — see the "Updating knowledge" section below for the
tradeoff.

## Streamlit Community Cloud

1. Push your repository to GitHub.
2. Go to https://share.streamlit.io and sign in.
3. Click **New app** and select your repository and branch.
4. Set the **Main file path** to `app.py`.
5. Under **Advanced settings → Secrets**, paste your environment variables
   in TOML format (see below).
6. Click **Deploy**.

## Secrets

Streamlit Community Cloud doesn't read `.env` files — it uses a
`secrets.toml`-style block instead. The app reads secrets under the exact
same variable names as `.env` (nothing is renamed), so paste something like:

```toml
LLM_PROVIDER = "anthropic"
LLM_MODEL = "claude-sonnet-5"
ANTHROPIC_API_KEY = "sk-ant-..."
GOOGLE_API_KEY = ""

LANGCHAIN_TRACING_V2 = "false"
LANGCHAIN_API_KEY = ""
LANGCHAIN_PROJECT = "personal-recruiter-chatbot"

ADMIN_PASSWORD = "choose-a-real-password"

CHROMA_PATH = "./data/vectorstore"
TOP_K = "5"
```

For local development, you can instead create `.streamlit/secrets.toml`
with the same content (it's git-ignored), or just keep using `.env` — both
work, since the app checks the environment first and falls back to
`st.secrets`.

**Never commit real API keys or `ADMIN_PASSWORD`** — only ever set them as
Streamlit secrets or in your local, git-ignored `.env`.

## Updating knowledge

- **Locally:** run the app, unlock the sidebar **Knowledge** panel with
  `ADMIN_PASSWORD`, upload PDF/Markdown/JSON files, then click **Rebuild
  Knowledge Base**. Commit the updated files in `data/knowledge/` and push.
- **On Streamlit Cloud:** the same sidebar panel works against the live
  app's disk, but that disk resets on every redeploy — so for changes to
  survive redeploys, update the files under `data/knowledge/` in your repo
  and push. On the next deploy (or app restart), the app detects an empty
  vector store and automatically rebuilds it from whatever's in
  `data/knowledge/`.
- `profile.json` is the structured data merged directly into every prompt;
  `resume.pdf` / `profile.md` are chunked and embedded for retrieval.
  Rebuilding always replaces the entire vector store, so there's no risk of
  duplicate or stale chunks from a previous version.

## Troubleshooting

**"ANTHROPIC_API_KEY is not set" / "GOOGLE_API_KEY is not set"**
The secret isn't set for the provider selected by `LLM_PROVIDER`. Check
Streamlit Cloud's Secrets panel (or your local `.env`) matches the provider.

**Dependency installation failure on deploy**
Check the app's build logs in the Streamlit Cloud dashboard. `chromadb` and
`sentence-transformers` pull in native wheels — if a specific pinned version
fails to build, try relaxing that pin in `requirements.txt`.

**Vector store initialization issues / empty responses**
The chat replies "not configured yet" until a valid `profile.json` exists in
`data/knowledge/`. If you've uploaded files but see no results, click
**Rebuild Knowledge Base** in the sidebar — the vector store only rebuilds
automatically when it's empty, not on every file change.

**Streamlit startup errors**
Run `streamlit run app.py` locally first — errors surface faster locally
than in Cloud build logs. Most startup failures are a missing/misnamed
environment variable or a `requirements.txt` version conflict.

**Knowledge disappears after a redeploy**
Expected if `data/knowledge/` isn't committed to your repo — Streamlit
Cloud's disk is ephemeral. Commit your knowledge files (see "GitHub setup"
above) so the app can rebuild automatically on startup.
