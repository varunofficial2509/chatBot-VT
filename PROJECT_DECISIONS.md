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
share a process. A single FastAPI app with clearly separated modules
(`api/`, `graph/`, `rag/`, `llm/`) gets the same separation of concerns
without the infrastructure tax.

## Why FastAPI?

It gives typed request/response models (Pydantic) with essentially no
boilerplate, native `async` support for I/O-bound calls to the LLM provider,
automatic OpenAPI docs for free, and it's the natural fit for serving a
small static frontend alongside a JSON API from one process. There's no
requirement here (websockets, GraphQL, heavy middleware) that would justify
a heavier framework.

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
retrieve_context   (queries Chroma for top_k relevant resume chunks)
  ↓
generate_answer    (builds a grounded prompt, calls the LLM)
  ↓
END
```

State passed between nodes: `question`, `chat_history`, `profile`,
`retrieved_context`, `answer`.

## Why RAG?

The chatbot must never invent experience, and it must be able to answer
specific factual questions ("what did you do at Company X?") that a short
system prompt can't hold in full. Splitting the resume into chunks, indexing
them, and retrieving only the top-k relevant ones per question keeps the
prompt small and keeps every answer traceable back to a specific piece of
the resume, rather than the model relying on parametric memory or a
crammed-in full-document prompt.

## Why Chroma instead of a production vector database?

This is a single-owner, low-QPS, single-collection use case — there's no
need for the operational complexity of a hosted vector database (Pinecone,
Weaviate, pgvector-on-a-managed-Postgres). Chroma runs embedded, persists to
local disk, requires no separate service to run or pay for, and its Python
API is simple enough to read end-to-end in `app/rag/`. The tradeoff
(documented below) is that it doesn't scale past one process and its
storage isn't guaranteed to persist on every free hosting tier.

## Why Sentence Transformers (local embeddings)?

Embeddings are generated once per document upload and once per question —
low volume, latency-tolerant. Running them locally via
`sentence-transformers` (`all-MiniLM-L6-v2` by default) means:

- No per-embedding API cost or external dependency for the most
  frequently-called part of the pipeline.
- No API key required just to get retrieval working.
- The model is small enough (~80MB) to run comfortably in a small container.

The embedding model is configurable (`EMBEDDING_MODEL` env var) if a larger
model is ever justified.

## Why the selected LLM provider?

The LLM call is the one place where an external, paid API is unavoidable —
someone has to generate the actual answer text. The provider is fully
abstracted behind `app/llm/provider.py` (`get_llm()`), selected by the
`LLM_PROVIDER` env var, so switching providers is a config change, not a
code change. Two providers are wired up:

- **Anthropic (Claude)** — the default. Strong instruction-following is
  exactly what's needed for a chatbot with hard grounding rules ("never
  invent X") — it needs to actually respect them.
- **Google Gemini** — a genuinely free-tier-friendly alternative for anyone
  who wants to run this project without a paid API key during development.

Nothing in `app/graph`, `app/api`, or `app/prompts` references a specific
provider — they only call `get_llm()`.

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

## Why is the UI intentionally minimal and restricted to three colors?

The chatbot represents a candidate to recruiters — it's a small portfolio
signal in itself. A restrained UI (background / text / one accent color, no
gradients, no shadows-as-decoration, no icon soup) reads as deliberate and
confident rather than under-designed, and it keeps the frontend code small
enough to be fully understandable in one sitting — which matters for an
interview walkthrough.

## Why is admin ingestion separated from recruiter access?

The recruiter-facing surface and the owner-facing surface have completely
different trust levels and completely different failure costs. A recruiter
being able to see who else's resume was uploaded, or being able to
overwrite the knowledge base, is a real problem; a recruiter asking a
question that doesn't get answered is not. Splitting them into `/` (public,
read-only) and `/admin` + `/api/admin/*` (password-gated, mutating) means
the blast radius of "someone found the chat URL" is zero — they can only
ask questions against whatever the owner already published.

## Why is simple password authentication sufficient here?

There is exactly one legitimate admin: the candidate who owns the resume.
There's no multi-user permission model to build, no role hierarchy, no
audit trail requirement beyond "did ingestion succeed." A shared secret
(`ADMIN_PASSWORD`) checked server-side, exchanged for a short-lived
HMAC-signed bearer token (`app/api/auth.py`), is proportionate: it prevents
a recruiter or a random visitor from ever reaching the ingestion endpoint,
without introducing OAuth, sessions-in-a-database, or a user table for a
system that will only ever have one user. The token is signed with the
admin password itself (HMAC-SHA256) and expires after one hour — no
additional secret or dependency required.

## Why the selected deployment option, and its limitations?

The app is documented for deployment on any small container/Python host
(Render, Railway, Fly.io) that can build from the included `Dockerfile` and
accept environment-variable secrets — no cloud-specific infrastructure is
required, so the choice of host stays portable. The explicit limitation:
Chroma's persistence and the profile JSON both live on local disk
(`data/chroma`, `data/profile.json`). Free tiers on most of these platforms
do **not** guarantee that disk survives a redeploy or restart. This project
does not paper over that — the README says plainly that re-ingestion may be
required after a redeploy on ephemeral-disk hosting, rather than silently
losing the knowledge base and leaving the recruiter chat broken with no
explanation.

## Tradeoffs — what this project intentionally does not solve

- **Multi-user authentication.** One shared admin password, one candidate.
  No user accounts, no per-recruiter identity, no RBAC.
- **Enterprise security.** No SSO, no audit logging beyond app logs, no
  rate limiting beyond FastAPI/Uvicorn defaults, no WAF. Appropriate for a
  low-traffic personal portfolio project, not for handling sensitive data
  at scale.
- **Persistent production vector storage.** Chroma is embedded and
  file-based; it does not survive ephemeral disk on some free hosts, and it
  does not scale across multiple processes/replicas.
- **Advanced retrieval ranking.** Retrieval is plain top-k cosine similarity
  over chunk embeddings — no re-ranking model, no hybrid keyword+vector
  search, no query rewriting.
- **Agentic tool calling.** The LLM only answers from the context it's
  given; it doesn't call external tools, browse, or take actions.
- **Complex conversation memory.** Session history is an in-memory Python
  dict, capped at the last 20 turns, keyed by a client-held session ID. It
  resets on server restart and doesn't survive across multiple worker
  processes. There's no per-user persistent memory across sessions.
- **Horizontal scaling.** The in-memory session store and the local Chroma
  index both assume a single process. Running multiple replicas behind a
  load balancer would break session continuity and require moving both to
  shared storage — deliberately out of scope for this project's size.

## How I Would Explain This Project in an Interview

"I built a personal recruiter chatbot — a small RAG application that lets a
recruiter ask questions about my background and get answers grounded only
in my actual resume and a structured JSON profile, never invented content.

Architecturally, it's a single FastAPI app with two surfaces: a public chat
endpoint for recruiters, and a password-protected admin endpoint I use to
upload my resume and profile. When I upload a resume, it goes through a
pipeline that extracts the text, chunks it, embeds the chunks locally with
Sentence Transformers, and stores them in a Chroma vector database on disk.

When a recruiter asks a question, it runs through a LangGraph graph with two
nodes: retrieve the most relevant resume chunks for that question, then
generate an answer using an LLM — Claude by default, but the provider is
abstracted so it's a config change to swap to Gemini. The system prompt is
explicit that the model must never invent experience and must say when it
doesn't have enough information. Every request is traced end-to-end in
LangSmith, so I can see exactly what was retrieved and what was sent to the
model for any given question.

I kept it deliberately minimal — no microservices, no production vector
database, no complex auth — because the point wasn't to show off
infrastructure, it was to build a clean, understandable, working example of
RAG plus LangGraph plus a real LLM, with clear tradeoffs I can defend."

## Architecture Walkthrough

```text
Recruiter
 → FastAPI            (POST /api/chat)
 → LangGraph           (compiled graph, invoked with question + history + profile)
 → retrieve_context     (Chroma similarity search, top_k chunks)
 → generate_answer      (system prompt + profile + retrieved chunks + history -> LLM)
 → Response             (answer + session_id)
 → LangSmith Trace      (retrieve_context and generate_answer as separate spans)
```

## Likely Interview Questions

**Why LangGraph instead of a single function calling the LLM?**
Because it makes retrieval and generation independently traceable and
extensible nodes instead of one opaque call — you can see exactly what was
retrieved before generation ran, both in code and in LangSmith, and it's
straightforward to insert another node (e.g. query rewriting) later without
restructuring.

**Why RAG instead of just putting the whole resume in the system prompt?**
A resume plus a structured profile can be long, and RAG keeps the prompt
scoped to only what's relevant to the specific question, which is cheaper,
faster, and easier to keep grounded — plus it's the realistic pattern for
when the knowledge base grows beyond one document.

**Why Chroma instead of Pinecone/Weaviate/pgvector?**
Single-owner, low-QPS, single-collection workload — an embedded, local,
free vector store is the right size for the problem. It doesn't need a
managed service's operational overhead or cost.

**Why local embeddings instead of an embeddings API?**
No per-call cost or external dependency for the highest-frequency operation
in the pipeline (every question re-embeds), and no API key needed just to
get retrieval working locally.

**How does ingestion work?**
Upload through `/admin` → validate file types and size → extract text
(PyMuPDF for PDF, python-docx for DOCX) → normalize whitespace → chunk with
a recursive character splitter → embed each chunk locally → replace the
Chroma collection with the new chunks (so re-ingesting never creates
duplicates) → save the structured profile JSON to disk.

**How do you prevent hallucination?**
Three layers: (1) the system prompt explicitly forbids inventing
experience, projects, technologies, or metrics, and requires the model to
say when it lacks enough information; (2) the model is only ever given
retrieved resume chunks plus the structured profile as its factual
grounding — nothing else; (3) if no resume/profile has been ingested yet,
the API short-circuits before ever calling the LLM and returns a fixed
"not configured" message instead of letting the model improvise.

**How does LangSmith work here?**
Setting `LANGCHAIN_TRACING_V2=true` plus a LangSmith API key and project
name is enough for LangGraph to automatically emit traces for every graph
run, with no code changes. `run_graph()` additionally attaches project
metadata and a tag so runs are easy to filter in the LangSmith UI.

**How is admin access protected?**
A single shared `ADMIN_PASSWORD` (never hardcoded, only in environment
variables) is exchanged for a short-lived HMAC-signed bearer token. The
ingestion endpoint requires that token; the recruiter-facing chat endpoint
never sees or needs it.

**What happens when the resume changes?**
The owner re-uploads through `/admin`. Ingestion always rebuilds the Chroma
collection from scratch rather than appending, so there's no risk of stale
or duplicate chunks from a previous version of the resume.

**How would you scale this?**
Move the vector store to a managed/hosted option reachable from multiple
processes, move session history from an in-memory dict to a shared store
(e.g. Redis) if it needed to survive restarts or run behind multiple
replicas, and put the ingestion pipeline behind a queue if uploads ever
needed to handle larger files or run concurrently at volume. None of that
is needed for the actual use case (one owner, one resume, low traffic).

**What would you change for production?**
Real user auth if this ever served more than one candidate's data, rate
limiting on the chat endpoint, structured logging/metrics, a managed vector
store with persistent storage guarantees, and probably moving session
history to Redis or a database so it survives restarts and multiple
workers.

**Why not use a traditional database?**
There's no relational data to model — the two data shapes are "unstructured
resume text I need to search semantically" (Chroma's job) and "one
structured JSON profile" (a flat file is enough for one document). Adding
Postgres would be infrastructure with nothing relational to store.

**How would you evaluate answer quality?**
Build a small set of recruiter-style questions with known-good grounded
answers (and known "should refuse" questions where the resume doesn't have
the information), run them through the graph, and check both that
technologies/claims match the resume and that the model correctly declines
when information is missing. LangSmith's trace history is useful here for
spotting cases where retrieval returned the wrong chunks versus cases where
retrieval was fine but generation still drifted.

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
