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

streamlit run streamlit_app.py
```

## GitHub setup

**Commit:**
- All of `app/`, `pages/`, `streamlit_app.py`, `.streamlit/config.toml`,
  `requirements.txt`, `runtime.txt`, `.python-version`
- `data/profile.json`, `projects.json`, `experience.json`, `skills.json` —
  the portfolio's presentation content
- `data/knowledge/` — the chatbot's real resume/profile files (`resume.pdf`,
  `profile.md`, `profile.json`). This app's whole purpose is to surface this
  data to recruiters, so it's meant to be public. It also lets the app
  auto-rebuild its knowledge base on a fresh deploy, since Streamlit
  Community Cloud's disk is ephemeral.
- `data/knowledge/profile.example.json` (a template, not real data)

**Never commit:**
- `.env` (already git-ignored)
- `.streamlit/secrets.toml` (already git-ignored)
- `data/vectorstore/` (already git-ignored) — it's a rebuildable index, not
  source data; committing it just bloats the repo with binary files

If you'd rather keep your resume/profile out of the git history, that's a
valid choice too — see "Updating knowledge" below for the tradeoff.

## Streamlit Community Cloud

1. Push your repository to GitHub.
2. Go to https://share.streamlit.io and sign in.
3. Click **New app** and select your repository and branch.
4. Set the **Main file path** to `streamlit_app.py`.
5. Under **Advanced settings → Secrets**, paste your environment variables
   in TOML format (see below).
6. Click **Deploy**.

## Secrets

Streamlit Community Cloud doesn't read `.env` files — it uses a
`secrets.toml`-style block instead. The app reads secrets under the exact
same variable names as `.env` (nothing is renamed), so paste something like:

```toml
LLM_MODEL = "gemini-3.5-flash-lite"
GOOGLE_API_KEY = "AIza..."

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

Note: `.streamlit/config.toml` (the app's dark theme) **is** committed and
public — only `.streamlit/secrets.toml` is git-ignored.

**Never commit real API keys or `ADMIN_PASSWORD`** — only ever set them as
Streamlit secrets or in your local, git-ignored `.env`.

## Updating knowledge

**Portfolio content** (Home/Projects pages) — edit `data/profile.json`,
`projects.json`, `experience.json`, `skills.json` directly and push. No
admin UI involved; these are read on every page load.

**Chatbot knowledge base**:
- **Locally:** run the app, go to the hidden `/admin` page (password-gated,
  not in the top nav), upload PDF/Markdown/JSON files, then click **Rebuild
  Knowledge Base**. Commit the updated files in `data/knowledge/` and push.
- **On Streamlit Cloud:** the same admin page works against the live app's
  disk, but that disk resets on every redeploy — so for changes to survive
  redeploys, update the files under `data/knowledge/` in your repo and
  push. On the next deploy (or app restart), the app detects an empty
  vector store and automatically rebuilds it from `data/knowledge/`.
- `profile.json` inside `data/knowledge/` is the structured data merged
  directly into every chat prompt; `resume.pdf` / `profile.md` are chunked
  and embedded for retrieval. Rebuilding always replaces the entire vector
  store, so there's no risk of duplicate or stale chunks.

## Troubleshooting

**"GOOGLE_API_KEY is not set"**
Set `GOOGLE_API_KEY` in Streamlit Cloud's Secrets panel (or your local
`.env`) — it's required, the app only supports Gemini.

**Dependency installation failure on deploy**
Check the app's build logs in the Streamlit Cloud dashboard. `chromadb`
pulls in native wheels (`onnxruntime`, `tokenizers`) — if a specific
pinned version fails to build, try relaxing that pin in `requirements.txt`.

**"Failed building wheel for tokenizers" / PyO3 "Python interpreter version
is newer than PyO3's maximum supported version"**
`chromadb==0.5.23` pinned `tokenizers<=0.20.3`, a version that predates
`tokenizers`'s move to `abi3` wheels (one wheel works across all Python
versions — no per-version prebuilt binary, no compilation). On a Python
version newer than what 0.20.3 shipped binaries for, pip has to compile it
from source via Rust/PyO3, which fails outright on very new Python
versions PyO3 doesn't support yet. **Fixed by upgrading to
`chromadb==1.5.9`** (current `requirements.txt`), which has no upper bound
on `tokenizers` and so resolves to a recent `abi3` release — no
compilation, no Rust toolchain, no Python-version sensitivity at all. This
is the actual fix; `runtime.txt` and `.python-version` (both `3.11`) are
still in the repo as defense-in-depth but shouldn't be load-bearing anymore.
If you ever see this error again after bumping a pinned dependency, check
whether that package caps a native-wheel dependency below its first
`abi3` release before reaching for a Python-version pin.

**If a dependency install still fails for a Python-version reason** after
that, the reliable override is the Streamlit Cloud dashboard: open the app
→ **Settings (⚙️) → General → Python version** → pick a version → **Save**
→ reboot. That takes precedence over any file in the repo.

**Vector store initialization issues / empty responses**
The AI Assistant replies "not configured yet" until a valid `profile.json`
exists in `data/knowledge/`. If you've uploaded files but see no results,
go to `/admin` and click **Rebuild Knowledge Base** — the vector store only
rebuilds automatically when it's empty, not on every file change.

**Streamlit startup errors**
Run `streamlit run streamlit_app.py` locally first — errors surface faster
locally than in Cloud build logs. Most startup failures are a missing or
misnamed environment variable, or a `requirements.txt` version conflict.

**Knowledge disappears after a redeploy**
Expected if `data/knowledge/` isn't committed to your repo — Streamlit
Cloud's disk is ephemeral. Commit your knowledge files (see "GitHub setup"
above) so the app can rebuild automatically on startup.

**Default Streamlit colors showing through (blue links, red errors, etc.)**
Make sure `.streamlit/config.toml` is committed and deployed — it's what
overrides Streamlit's default theme with the app's three colors.
