"""Chat rendering and the owner-only knowledge management panel."""

import logging

import streamlit as st

from src.config import settings
from src.ingestion.parser import IngestionError
from src.ingestion.pipeline import list_knowledge_files, rebuild_knowledge_base, save_uploaded_file

logger = logging.getLogger("recruiter_bot.ui")


def render_chat_history(messages: list[dict]) -> None:
    for turn in messages:
        with st.chat_message(turn["role"]):
            st.write(turn["content"])


def _status(message: str, ok: bool) -> None:
    css_class = "knowledge-status-ok" if ok else "knowledge-status-error"
    st.markdown(f'<p class="{css_class}">{message}</p>', unsafe_allow_html=True)


def render_knowledge_sidebar() -> None:
    """Owner-only panel: upload PDF/Markdown/JSON knowledge and rebuild the index."""
    with st.sidebar:
        st.markdown("#### Knowledge")

        if not settings.ADMIN_PASSWORD:
            st.caption("Set ADMIN_PASSWORD to manage knowledge from here.")
            return

        if not st.session_state.get("admin_unlocked"):
            password = st.text_input("Owner password", type="password", key="admin_password_input")
            if st.button("Unlock"):
                if password and password == settings.ADMIN_PASSWORD:
                    st.session_state.admin_unlocked = True
                    st.rerun()
                else:
                    _status("Incorrect password.", ok=False)
            return

        uploaded = st.file_uploader(
            "Upload document",
            type=["pdf", "md", "json"],
            key="knowledge_uploader",
        )
        if uploaded is not None and st.button("Upload"):
            try:
                saved_name = save_uploaded_file(uploaded.name, uploaded.getvalue())
                _status(f"Saved {saved_name}. Rebuild the knowledge base to apply it.", ok=True)
            except IngestionError as exc:
                _status(str(exc), ok=False)
            except Exception:
                logger.exception("Failed to save uploaded knowledge file")
                _status("Failed to process document.", ok=False)

        st.markdown("**Current knowledge:**")
        files = list_knowledge_files()
        if files:
            items = "".join(f"<li>{name}</li>" for name in files)
            st.markdown(f'<ul class="knowledge-file-list">{items}</ul>', unsafe_allow_html=True)
        else:
            st.caption("No knowledge files yet.")

        if st.button("Rebuild Knowledge Base"):
            with st.spinner("Rebuilding..."):
                try:
                    result = rebuild_knowledge_base()
                    _status(
                        f"Knowledge added successfully "
                        f"({result['chunks_indexed']} chunks from {result['documents_indexed']} documents).",
                        ok=True,
                    )
                except IngestionError as exc:
                    _status(str(exc), ok=False)
                except Exception:
                    logger.exception("Failed to rebuild knowledge base")
                    _status("Failed to process document.", ok=False)
