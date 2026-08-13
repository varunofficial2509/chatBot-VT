"""Page configuration, global styling, and the header block."""

import streamlit as st

from src.ui.styles import CSS


def configure_page() -> None:
    st.set_page_config(
        page_title="AI Resume Assistant",
        page_icon="■",
        layout="centered",
        initial_sidebar_state="collapsed",
    )


def apply_styles() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


def render_header(name: str) -> None:
    st.markdown(
        f"""
        <div class="recruiter-header">
            <p class="name">{name}</p>
            <p class="tagline">AI Resume Assistant</p>
            <p class="prompt">Ask me anything about my experience, projects, skills, or background.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
