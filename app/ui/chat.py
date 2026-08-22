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
    st.html(
        """
        <div class="vt-ai-hero">
            <div class="vt-ai-hero-title">Ask <span class="accent">Varun</span>.</div>
            <div class="vt-ai-hero-sub">
                An AI assistant grounded in my experience, projects and skills.
            </div>
        </div>
        """
    )

    clicked = None
    with st.container(key="vt_suggestions"):
        for i, suggestion in enumerate(SUGGESTIONS):
            if st.button(suggestion, key=f"suggestion_{i}", use_container_width=True):
                clicked = suggestion
    return clicked
