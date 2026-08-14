"""Projects: a compact list of what I've built."""

import streamlit as st

from app.services import content
from app.ui import components

profile = content.load_profile()
projects = content.load_projects()

components.render_brand_header(profile.get("name", ""), profile.get("title", ""))

st.markdown(
    '<div style="font-size: 0.78rem; letter-spacing: 0.12em; text-transform: uppercase;" class="text-muted">'
    "Projects</div>",
    unsafe_allow_html=True,
)

for project in projects:
    tech = " · ".join(project.get("technologies", []))
    st.markdown(
        f"""
        <div style="margin: 1.4rem 0;">
            <div style="font-size: 1.05rem; font-weight: 600;">{project.get("name", "")}</div>
            <div class="text-muted" style="font-size: 0.82rem; margin: 0.15rem 0 0.5rem;">
                {project.get("category", "")}
            </div>
            <div style="font-size: 0.85rem; color: var(--accent); margin-bottom: 0.5rem;">{tech}</div>
            <div style="font-size: 0.92rem;">{project.get("description", "")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if project.get("result"):
        st.markdown(f'<div class="text-muted" style="font-size: 0.85rem;">{project["result"]}</div>', unsafe_allow_html=True)
    if project.get("github_url"):
        st.markdown(f'<a href="{project["github_url"]}" target="_blank">GitHub →</a>', unsafe_allow_html=True)
    st.markdown('<hr style="margin: 1rem 0; opacity: 0.4;" />', unsafe_allow_html=True)

if not projects:
    st.markdown('<span class="text-muted">No projects listed yet.</span>', unsafe_allow_html=True)

components.render_footer()
