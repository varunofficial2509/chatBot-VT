"""Projects: a compact list of what I've built."""

import streamlit as st

from app.services import content
from app.ui import components
from app.ui.theme import inject_css

inject_css()

profile = content.load_profile()
projects = content.load_projects()

components.render_nav_header(active="projects", name=profile.get("name", ""))
components.render_section_title("projects")

if projects:
    components.render_projects_grid(projects)
else:
    st.html('<span class="text-muted">No projects listed yet.</span>')

components.render_footer()
