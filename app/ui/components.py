"""Shared, presentation-only building blocks used across every page."""

import streamlit as st


def render_brand_header(name: str, title: str) -> None:
    st.markdown(
        f"""
        <div style="margin-bottom: 1.75rem;">
            <div style="font-size: 1.05rem; font-weight: 600; letter-spacing: 0.03em; text-transform: uppercase;">
                {name}
            </div>
            <div class="text-muted" style="font-size: 0.85rem; letter-spacing: 0.06em; text-transform: uppercase;">
                {title}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_title(label: str) -> None:
    st.markdown(
        f"""
        <div style="margin: 2.25rem 0 0.9rem;
                    font-size: 0.78rem; letter-spacing: 0.12em; text-transform: uppercase;"
             class="text-muted">
            {label}
        </div>
        <hr style="margin: 0 0 1rem; opacity: 0.5;" />
        """,
        unsafe_allow_html=True,
    )


def render_skill_pills(skills: list[str]) -> None:
    pills = "".join(
        f'<span style="display:inline-block; padding:0.3rem 0.7rem; margin:0 0.4rem 0.4rem 0; '
        f'border:1px solid var(--border); border-radius:999px; font-size:0.82rem; '
        f'color:var(--text-muted);">{skill}</span>'
        for skill in skills
    )
    st.markdown(f'<div>{pills}</div>', unsafe_allow_html=True)


def render_footer() -> None:
    st.markdown(
        '<hr style="margin-top: 3rem; opacity: 0.4;" />',
        unsafe_allow_html=True,
    )
    cols = st.columns([6, 1])
    with cols[0]:
        st.markdown(
            '<span class="text-muted" style="font-size: 0.78rem;">'
            "Built with Streamlit, LangGraph and RAG.</span>",
            unsafe_allow_html=True,
        )
    with cols[1]:
        st.page_link("pages/admin.py", label="Owner", icon=None)
