"""Streamlit entrypoint: app shell, theme, and native top navigation."""

import streamlit as st

from app.rag.ingestion import ensure_knowledge_base
from app.ui.theme import configure_page

configure_page("Varun Teja Jaladhula — Software Engineer")

ensure_knowledge_base()

pages = [
    st.Page("pages/home.py", title="Home", url_path="home", default=True),
    st.Page("pages/projects.py", title="Projects", url_path="projects"),
    st.Page("pages/assistant.py", title="AI Assistant", url_path="assistant"),
    st.Page("pages/admin.py", title="Manage Knowledge", url_path="admin", visibility="hidden"),
]

nav = st.navigation(pages, position="top")
nav.run()
