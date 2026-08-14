"""AI Assistant: recruiter-facing chat over the RAG knowledge base."""

import logging

import streamlit as st

from app.graph.graph import run_graph
from app.graph.prompts import NO_KNOWLEDGE_BASE_MESSAGE
from app.rag.profile_store import has_profile, load_profile
from app.services import content
from app.ui import chat, components

logger = logging.getLogger("recruiter_bot.assistant")

MAX_HISTORY_TURNS = 20

profile_meta = content.load_profile()
components.render_brand_header(profile_meta.get("name", ""), profile_meta.get("title", ""))

if "messages" not in st.session_state:
    st.session_state.messages = []

rag_profile = load_profile()

if not st.session_state.messages:
    suggestion = chat.render_empty_state()
    if suggestion:
        st.session_state.messages.append({"role": "user", "content": suggestion})
        st.rerun()
else:
    chat.render_history(st.session_state.messages)

question = st.chat_input("Ask anything about my experience...")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    st.rerun()

# The last turn is a user message awaiting a response (either just typed, or
# just appended above before the rerun) — generate and show the answer now.
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    with st.chat_message("assistant"):
        if not has_profile():
            answer = NO_KNOWLEDGE_BASE_MESSAGE
        else:
            with st.spinner("Thinking..."):
                try:
                    result = run_graph(
                        question=st.session_state.messages[-1]["content"],
                        chat_history=st.session_state.messages[:-1],
                        profile=rag_profile,
                    )
                    answer = result["answer"]
                except Exception:
                    logger.exception("Chat request failed")
                    answer = (
                        "Sorry, I ran into a problem answering that just now. "
                        "Please try again in a moment."
                    )
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    del st.session_state.messages[: max(0, len(st.session_state.messages) - MAX_HISTORY_TURNS)]
