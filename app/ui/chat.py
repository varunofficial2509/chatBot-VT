"""Chat rendering: message history and the empty-state suggestion chips."""

import streamlit as st

SUGGESTIONS = [
    "Tell me about your Java experience",
    "What GenAI projects have you built?",
    "Explain your AeroWebb experience",
    "What is your experience with Kafka?",
]


def render_history(messages: list[dict]) -> None:
    for turn in messages:
        with st.chat_message(turn["role"]):
            st.markdown(turn["content"])


def render_empty_state() -> str | None:
    """Shows the intro + suggestion chips. Returns the clicked suggestion, if any."""
    st.markdown(
        """
        <div style="text-align: center; margin: 1.5rem 0 2rem;">
            <div style="font-size: 1.2rem; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase;">
                AI Resume Assistant
            </div>
            <div class="text-muted" style="font-size: 0.95rem; margin-top: 0.5rem;">
                Ask me anything about my experience, projects, skills, or background.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    clicked = None
    cols = st.columns(2)
    for i, suggestion in enumerate(SUGGESTIONS):
        with cols[i % 2]:
            if st.button(suggestion, key=f"suggestion_{i}", use_container_width=True):
                clicked = suggestion
    return clicked
