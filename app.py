"""Streamlit entrypoint: recruiter-facing chat UI wired to the LangGraph RAG pipeline."""

import logging

import streamlit as st

from src.graph.graph import run_graph
from src.graph.prompts import NO_KNOWLEDGE_BASE_MESSAGE
from src.ingestion.pipeline import ensure_knowledge_base
from src.rag.profile_store import has_profile, load_profile
from src.ui import components, layout

logger = logging.getLogger("recruiter_bot.app")

MAX_HISTORY_TURNS = 20

layout.configure_page()
layout.apply_styles()

ensure_knowledge_base()
components.render_knowledge_sidebar()

if "messages" not in st.session_state:
    st.session_state.messages = []

profile = load_profile()
layout.render_header(profile.get("name", "AI Resume Assistant"))

components.render_chat_history(st.session_state.messages)

question = st.chat_input("Ask a question...")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        if not has_profile():
            answer = NO_KNOWLEDGE_BASE_MESSAGE
        else:
            with st.spinner("Thinking..."):
                try:
                    result = run_graph(
                        question=question,
                        chat_history=st.session_state.messages[:-1],
                        profile=profile,
                    )
                    answer = result["answer"]
                except Exception:
                    logger.exception("Chat request failed")
                    answer = (
                        "Sorry, I ran into a problem answering that just now. "
                        "Please try again in a moment."
                    )
        st.write(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    del st.session_state.messages[: max(0, len(st.session_state.messages) - MAX_HISTORY_TURNS)]
