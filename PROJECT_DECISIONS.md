# Project Decisions

Why each major technology and architecture choice was made, and what this
project deliberately does not solve.

## Architecture: why a monolith instead of microservices?

There is one consumer-facing concern (answer a recruiter's question) and one
owner-facing concern (update the knowledge base). Both share the same
retrieval index and the same LLM call. Splitting that into separate services
would add network calls, deployment coordination, and operational surface
area without adding any capability — there's no independent scaling need,
no separate team, and no reason the ingestion path and the chat path can't
share a process. A single Streamlit app with clearly separated modules
(`app/ui`, `app/graph`, `app/rag`, `app/services`, plus `pages/` for routes) gets the same
separation of concerns without the infrastructure tax.

## Why Streamlit instead of a FastAPI + custom frontend?

This project used to be a FastAPI JSON API backing a hand-rolled HTML/JS
frontend. That split made sense while there was a reason to keep API and UI
independently deployable — there wasn't one. Streamlit collapses the UI and
the application layer into one Python process: `st.chat_message` and
`st.chat_input` replace the hand-rolled chat frontend and its fetch calls,
`st.session_state` replaces the in-memory session dict, and
`st.cache_resource` replaces the manual `lru_cache` singletons FastAPI code
used for the embedding model, LLM client, and compiled graph. The result is
less code, no HTTP boundary between "the UI" and "the app," and a natural
fit for a small single-owner tool like this one.

## Why a portfolio site instead of just a chatbot?

A chatbot alone asks a recruiter to trust an unfamiliar interface before
they've seen any actual signal. A portfolio homepage gives them the fast,
skimmable version — name, skills, experience, projects — with the AI
assistant as an optional deeper-dive for specific questions, not the only
way in. Both experiences read from the same underlying facts, so there's no
risk of the chatbot and the static page disagreeing.

## Why `st.navigation`/`st.Page` instead of a hand-rolled top nav?

Streamlit ships an official multipage mechanism as of 1.36+ (`st.Page`,
`st.navigation`, `st.switch_page`) with a native `position="top"` layout —
exactly the small top nav bar this project needed, without reimplementing
routing, URL paths, or page state by hand. `pages/admin.py` uses the same
mechanism's `visibility="hidden"` option to stay reachable (by direct link)
without appearing in the nav — a supported way to have a route that isn't
part of the public surface, rather than hacking something together with
query params or session-state view-switching.

## Why LangGraph instead of calling an LLM directly?

A single `llm.invoke(prompt)` call would work for this feature set today.
LangGraph is used anyway because:

1. It makes the RAG pipeline **explicit and inspectable** — `retrieve_context`
   and `generate_answer` are separate, independently traceable nodes rather
   than one opaque function. In LangSmith, that means you can see exactly
   what was retrieved and what the model was asked to do with it, as two
   distinct spans.
2. It demonstrates a real, working LangGraph integration — this project
   exists partly as a portfolio piece, and "I used LangGraph" should mean
   the graph does something, not that it's an unused import.
3. It leaves room to grow (e.g. adding a query-rewrite node, or a
   verification/grounding-check node) without restructuring the codebase.

The graph is intentionally small:

```text
START
  ↓
retrieve_context   (queries Chroma for top_k relevant knowledge chunks)
  ↓
generate_answer    (builds a grounded prompt, calls the LLM)
  ↓
END
```

State passed between nodes: `question`, `chat_history`, `profile`,
`retrieved_context`, `answer`. None of `app/graph` or `app/rag` imports
Streamlit — the Streamlit UI calls `run_graph()` and gets back plain data,
which is what keeps LangSmith tracing a config-only addition rather than a
UI change (see "Why LangSmith?" below).

## Why is presentation content separate from the RAG knowledge base?

`data/profile.json`, `projects.json`, `experience.json`, and `skills.json`
drive the Home and Projects pages (`app/services/content.py`).
`data/knowledge/` — a different `profile.json`, plus any resume PDF or
Markdown — is what actually gets chunked, embedded, and retrieved by the
chatbot (`app/rag/profile_store.py`, `app/rag/ingestion.py`). They describe
the same person but serve different jobs: the portfolio data is small,
hand-curated, and needs to render fast on every page load; the knowledge
base is optimized for semantic retrieval and can grow to include a full
resume PDF without bloating what the Home page has to parse. Keeping them
as separate files means updating one never risks silently breaking the
other, and the chatbot's grounding data can keep growing (more documents,
richer profile fields) independent of what the portfolio chooses to display.

## Why RAG?

The chatbot must never invent experience, and it must be able to answer
specific factual questions ("what did you do at Company X?") that a short
system prompt can't hold in full. Splitting the knowledge base into chunks,
indexing them, and retrieving only the top-k relevant ones per question
keeps the prompt small and keeps every answer traceable back to a specific
piece of source material, rather than the model relying on parametric
memory or a crammed-in full-document prompt.

## Why Chroma instead of a production vector database?

This is a single-owner, low-QPS, single-collection use case — there's no
need for the operational complexity of a hosted vector database (Pinecone,
Weaviate, pgvector-on-a-managed-Postgres). Chroma runs embedded, persists to
local disk, requires no separate service to run or pay for, and its Python
API is simple enough to read end-to-end in `app/rag/vectorstore.py`, which
wraps it behind a plain `add_documents()` / `search()` interface so the
storage backend could be swapped later without touching ingestion or
retrieval callers. The tradeoff (documented below) is that it doesn't scale
past one process and its storage isn't guaranteed to persist on every free
hosting tier.

## Why Gemini embeddings instead of local Sentence Transformers?

This project used to support local embeddings via `sentence-transformers`
as a no-API-key fallback. In practice it was never used — `.env` was
always configured for Gemini embeddings — and it had a real cost:
`sentence-transformers` depends on `torch`, whose default Linux wheel pulls
in NVIDIA CUDA libraries (`nvidia-cublas-cu12`, `nvidia-cudnn-cu12`, etc.)
as dependencies even though nothing here has a GPU. That's several
gigabytes of unnecessary download and a much slower, more fragile
Streamlit Cloud build, for an option nobody was exercising. Since the app
already requires `GOOGLE_API_KEY` for the LLM (see above), requiring it for
embeddings too costs nothing extra and removes `sentence-transformers` (and
`torch`) from the dependency tree entirely. Embeddings are still generated
once per document upload and once per question — low volume, latency- and
cost-tolerant — so the per-call API cost is negligible.

The embedding model is configurable (`EMBEDDING_MODEL` env var) if a
different Gemini embedding model is ever preferred.

## Why Gemini as the only LLM provider?

The LLM call is the one place where an external, paid API is unavoidable —
someone has to generate the actual answer text. This project used to
support both Anthropic and Gemini behind a `LLM_PROVIDER` switch, but that
abstraction was paying for optionality nobody was using: Gemini (which has
a genuinely free-tier-friendly API key, unlike Anthropic) was the only
provider actually configured in `.env`. Keeping the branch, the
`langchain-anthropic` dependency, and the unused `ANTHROPIC_API_KEY` /
`LLM_PROVIDER` env vars around was dead weight, not flexibility — so
`app/services/llm.py` (`get_llm()`) now builds a `ChatGoogleGenerativeAI`
directly. The model name is still overridable via `LLM_MODEL`, so swapping
to a different Gemini model is a config change, not a code change. If a
second provider becomes genuinely necessary later, reintroducing the
branch is a small, contained change — `get_llm()` is still the only thing
`app/graph` calls.

## Why LangSmith?

Tracing answers the two questions that matter most when debugging a RAG
chatbot: *what did it retrieve* and *what did it actually send to the
model*. LangGraph integrates with LangSmith by just setting environment
variables (`LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY`, `LANGCHAIN_PROJECT`)
— no code changes required beyond loading them, and `run_graph()` attaches
`project` metadata and a `recruiter-chat` tag to every run so traces are
easy to filter. What's traced: the full graph run, broken into the
`retrieve_context` and `generate_answer` spans, including the retrieved
chunks and the exact prompt sent to the LLM. Passwords, API keys, and raw
uploaded files are never included in trace metadata.

Verified end-to-end with a real trace: `LangGraph` (root) → `retrieve_context`
+ `generate_answer` → `ChatGoogleGenerativeAI` nested under `generate_answer`
— exactly the hierarchy the two-node design was meant to produce. Queried
via the `langsmith` CLI (installed alongside the
[langsmith-skills](https://github.com/langchain-ai/langsmith-skills)
plugin under `.claude/skills/`), which is also the tool to reach for later
if this project adds an eval dataset or custom evaluators.

## Why is the UI intentionally minimal, dark, and restricted to three colors?

The site represents a candidate to recruiters — it's a small portfolio
signal in itself. A restrained dark UI (`#0F1115` background, `#F5F5F5`
text, `#3B8C6E` accent — no gradients, no shadows-as-decoration, no icon
soup) reads as deliberate and confident rather than under-designed, and it
keeps `app/ui` small enough to be fully understandable in one sitting —
which matters for an interview walkthrough. The three colors are set once
in `.streamlit/config.toml` (Streamlit's native theme system), so buttons,
links, focus rings, and the active nav item all pick up the accent
automatically instead of needing per-widget overrides — `app/ui/theme.py`
only adds the CSS Streamlit's theme system can't reach (hiding default
chrome, chat message styling, opacity-based surfaces for subtle
separation like the user chat bubble).

## Why is knowledge management gated by a simple password instead of real auth?

There is exactly one legitimate admin: the candidate who owns the resume.
There's no multi-user permission model to build, no role hierarchy, no
audit trail requirement beyond "did the rebuild succeed." Comparing a
password field on the hidden `/admin` page against `ADMIN_PASSWORD` and
gating it behind `st.session_state.admin_unlocked` is proportionate: it
prevents a recruiter
or random visitor from ever reaching the upload/rebuild controls, without
introducing OAuth, sessions-in-a-database, or a user table for a system
that will only ever have one user. Unlike the previous FastAPI version,
there's no separate HTTP boundary to protect with a signed token — the
whole app is one Streamlit process, so a session-state flag is sufficient.

## Why does the knowledge base rebuild automatically on startup?

Streamlit Community Cloud's disk is ephemeral — anything not in the git
repo disappears on every redeploy. Rather than requiring a manual
re-upload after every restart, `data/knowledge/` (resume, Markdown profile,
JSON profile) is committed to the repo, and the app checks on startup
whether the vector store is empty; if so, it rebuilds from whatever's on
disk. This means the base knowledge always survives a redeploy without
the owner touching the UI, while the **Rebuild Knowledge Base** button
still exists for applying changes made through the admin page or a fresh
`git push` without waiting for a restart.

## Why the selected deployment option, and its limitations?

The app is a single Python process with local disk storage (Chroma +
profile JSON), which fits Streamlit Community Cloud's model directly —
push to GitHub, point Streamlit Cloud at `streamlit_app.py`, set secrets. The
explicit limitation: Chroma's persistence lives on local disk
(`data/vectorstore`), which does **not** survive a redeploy. This project
does not paper over that — the vector store is rebuilt automatically from
`data/knowledge/` on startup instead, which is a stronger guarantee than
the old FastAPI version had (that version required a manual re-upload after
every redeploy on ephemeral-disk hosts).

## Tradeoffs — what this project intentionally does not solve

- **Multi-user authentication.** One shared password, one candidate. No
  user accounts, no per-recruiter identity, no RBAC.
- **Enterprise security.** No SSO, no audit logging beyond app logs, no
  rate limiting, no WAF. Appropriate for a low-traffic personal portfolio
  project, not for handling sensitive data at scale.
- **Persistent production vector storage.** Chroma is embedded and
  file-based; on ephemeral-disk hosts it's rebuilt from `data/knowledge/`
  on startup rather than truly persisted, and it does not scale across
  multiple processes/replicas.
- **Advanced retrieval ranking.** Retrieval is plain top-k cosine similarity
  over chunk embeddings — no re-ranking model, no hybrid keyword+vector
  search, no query rewriting.
- **Agentic tool calling.** The LLM only answers from the context it's
  given; it doesn't call external tools, browse, or take actions.
- **Complex conversation memory.** Session history lives in
  `st.session_state`, capped at the last 20 turns. It's scoped to one
  browser session and doesn't persist across restarts or devices.
- **Horizontal scaling.** Streamlit Community Cloud runs a single instance
  per app; the local Chroma index assumes a single process. Deliberately
  out of scope for this project's size.

## How I Would Explain This Project in an Interview

"I built a personal developer portfolio with an integrated AI assistant — a
small RAG application that lets a recruiter browse my background normally
or ask questions and get answers grounded only in my actual resume and a
structured JSON profile, never invented content.

Architecturally, it's a single Streamlit app with three public pages (Home,
Projects, AI Assistant) built on `st.navigation`'s native top nav, plus a
password-gated admin page — not linked from navigation — I use to upload my
resume and profile. When I upload a document, it goes through a
pipeline that extracts the text (PyMuPDF for PDF, plain read for Markdown),
chunks it, embeds the chunks with Gemini, and stores them in a Chroma
vector database on disk.

When a recruiter asks a question, it runs through a LangGraph graph with two
nodes: retrieve the most relevant knowledge chunks for that question, then
generate an answer using Gemini. The system prompt is
explicit that the model must never invent experience and must say when it
doesn't have enough information. Every request is traceable end-to-end in
LangSmith once tracing is enabled, so I can see exactly what was retrieved
and what was sent to the model for any given question.

I kept it deliberately minimal — no microservices, no production vector
database, no complex auth — because the point wasn't to show off
infrastructure, it was to build a clean, understandable, working example of
RAG plus LangGraph plus a real LLM, with clear tradeoffs I can defend."

## Architecture Walkthrough

```text
Recruiter
 → Streamlit           (st.chat_input -> run_graph())
 → LangGraph            (compiled graph, invoked with question + history + profile)
 → retrieve_context      (Chroma similarity search, top_k chunks)
 → generate_answer       (system prompt + profile + retrieved chunks + history -> LLM)
 → Response              (answer rendered via st.chat_message, appended to session_state)
 → LangSmith Trace       (retrieve_context and generate_answer as separate spans)
```

## Likely Interview Questions

**Why LangGraph instead of a single function calling the LLM?**
Because it makes retrieval and generation independently traceable and
extensible nodes instead of one opaque call — you can see exactly what was
retrieved before generation ran, both in code and in LangSmith, and it's
straightforward to insert another node (e.g. query rewriting) later without
restructuring.

**Why RAG instead of just putting everything in the system prompt?**
A resume plus a structured profile can be long, and RAG keeps the prompt
scoped to only what's relevant to the specific question, which is cheaper,
faster, and easier to keep grounded — plus it's the realistic pattern for
when the knowledge base grows beyond one document.

**Why Chroma instead of Pinecone/Weaviate/pgvector?**
Single-owner, low-QPS, single-collection workload — an embedded, local,
free vector store is the right size for the problem. It doesn't need a
managed service's operational overhead or cost.

**Why Gemini embeddings instead of running them locally?**
Local embeddings via `sentence-transformers` were tried and dropped —
its `torch` dependency pulls in gigabytes of NVIDIA CUDA libraries on
Linux even without a GPU, which made Streamlit Cloud builds slow and
fragile for a fallback path nobody used. The app already requires a Google
API key for the LLM, so using it for embeddings too was free simplicity.

**How does ingestion work?**
Upload through the hidden admin page → validate file type and size → extract text
(PyMuPDF for PDF, plain read for Markdown) → normalize whitespace → chunk
with a recursive character splitter → embed each chunk locally → replace
the Chroma collection with the new chunks (so rebuilding never creates
duplicates) → JSON files are validated and kept as the structured profile,
merged directly into every prompt rather than chunked.

**How do you prevent hallucination?**
Three layers: (1) the system prompt explicitly forbids inventing
experience, projects, technologies, or metrics, and requires the model to
say when it lacks enough information; (2) the model is only ever given
retrieved knowledge chunks plus the structured profile as its factual
grounding — nothing else; (3) if no profile has been ingested yet, the app
short-circuits before ever calling the LLM and returns a fixed "not
configured" message instead of letting the model improvise.

**How does LangSmith work here?**
Setting `LANGCHAIN_TRACING_V2=true` plus a LangSmith API key and project
name is enough for LangGraph to automatically emit traces for every graph
run, with no code changes. `run_graph()` additionally attaches project
metadata and a tag so runs are easy to filter in the LangSmith UI.

**How is the knowledge management page protected?**
A single shared `ADMIN_PASSWORD` (never hardcoded, only in environment
variables or Streamlit secrets) gates a `st.session_state` flag for the
hidden `/admin` page. There's no separate HTTP boundary to protect — the
whole app is one Streamlit process, so this is proportionate to the actual
risk.

**What happens when the resume changes?**
The owner uploads through the admin page and clicks Rebuild, or commits new
files to `data/knowledge/` and pushes. Rebuilding always replaces the
Chroma collection from scratch rather than appending, so there's no risk of
stale or duplicate chunks from a previous version.

**How would you scale this?**
Move the vector store to a managed/hosted option reachable from multiple
processes, move session history to a shared store (e.g. Redis) if it needed
to survive restarts or be shared across devices, and put the ingestion
pipeline behind a queue if uploads ever needed to handle larger files or run
concurrently at volume. None of that is needed for the actual use case (one
owner, one knowledge base, low traffic).

**What would you change for production?**
Real user auth if this ever served more than one candidate's data, rate
limiting, structured logging/metrics, a managed vector store with
persistent storage guarantees, and probably moving session history to Redis
or a database so it survives restarts and is shared across devices.

**Why not use a traditional database?**
There's no relational data to model — the two data shapes are "unstructured
text I need to search semantically" (Chroma's job) and "one structured JSON
profile" (a flat file is enough for one document). Adding Postgres would be
infrastructure with nothing relational to store.

**How would you evaluate answer quality?**
Build a small set of recruiter-style questions with known-good grounded
answers (and known "should refuse" questions where the knowledge base
doesn't have the information), run them through the graph, and check both
that technologies/claims match the source material and that the model
correctly declines when information is missing. LangSmith's trace history
is useful here for spotting cases where retrieval returned the wrong chunks
versus cases where retrieval was fine but generation still drifted.

**How would you improve retrieval?**
Add a re-ranking step after the initial top-k similarity search, try hybrid
keyword+vector retrieval for exact-term questions (e.g. a specific
technology name), or add a query-rewriting node to the graph so follow-up
questions that reference earlier context ("what about that project?") embed
well on their own.

**How would you handle multiple users?**
That would mean multiple candidates' profiles behind one deployment, which
this project explicitly doesn't do. It would require per-candidate Chroma
collections (or a `candidate_id` metadata filter), per-candidate profile
storage, and real authentication distinguishing "recruiter viewing
candidate A" from "candidate A's own admin session" — a meaningfully
different, larger system than this one.
