"""Recruiter-facing chat endpoint."""

import logging
import uuid

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.graph.recruiter_graph import run_graph
from app.prompts.recruiter import NO_KNOWLEDGE_BASE_MESSAGE
from app.rag.profile_store import has_profile

logger = logging.getLogger("recruiter_bot.chat")
router = APIRouter()

MAX_HISTORY_TURNS = 20

# In-memory session store: session_id -> list of {"role", "content"}.
# Adequate for a single-process demo; resets on restart (documented in README).
_sessions: dict[str, list[dict]] = {}


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    session_id: str


@router.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    message = request.message.strip()
    if not message:
        return ChatResponse(
            answer="Please ask a question about my experience.",
            session_id=request.session_id or str(uuid.uuid4()),
        )

    session_id = request.session_id or str(uuid.uuid4())
    history = _sessions.setdefault(session_id, [])

    if not has_profile():
        return ChatResponse(answer=NO_KNOWLEDGE_BASE_MESSAGE, session_id=session_id)

    from app.rag.profile_store import load_profile

    try:
        result = run_graph(question=message, chat_history=history, profile=load_profile())
        answer = result["answer"]
    except Exception:
        logger.exception("Chat request failed")
        answer = (
            "Sorry, I ran into a problem answering that just now. "
            "Please try again in a moment."
        )

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": answer})
    del history[: max(0, len(history) - MAX_HISTORY_TURNS)]

    return ChatResponse(answer=answer, session_id=session_id)
