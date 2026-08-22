"""Home: the personal portfolio landing page."""

import streamlit as st

from app.services import content
from app.ui import components
from app.ui.theme import inject_css

inject_css()

profile = content.load_profile()
experience = content.load_experience()
skills = content.load_skills()

components.render_nav_header(active="home", name=profile.get("name", ""))

hero_col, visual_col = st.columns([5, 6], gap="large", vertical_alignment="center")
with hero_col:
    components.render_hero(profile)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("View Projects", use_container_width=True):
            st.switch_page("pages/projects.py")
    with col2:
        if st.button("Ask My AI →", type="primary", use_container_width=True):
            st.switch_page("pages/assistant.py")
with visual_col:
    with st.container(key="vt_hero_visual"):
        components.render_hero_visual()

# --- skills -------------------------------------------------------------------

if skills:
    components.render_section_title("skills")
    components.render_skills(skills)

# --- experience ---------------------------------------------------------------

if experience:
    components.render_section_title("experience", anchor_id="experience")
    for job in experience:
        technologies = content.mentioned_technologies(job.get("description", ""), skills)
        components.render_experience_item(job, technologies)

# --- current focus --------------------------------------------------------------

focus = profile.get("current_focus", [])
if focus:
    components.render_section_title("focus")
    st.html(f'<div class="vt-body-text mono">{" &nbsp;→&nbsp; ".join(focus)}</div>')

# --- contact ----------------------------------------------------------------

contact = profile.get("contact", {})
links = []
if contact.get("github"):
    links.append(f'<a href="{contact["github"]}" target="_blank" rel="noopener noreferrer">GitHub</a>')
if contact.get("linkedin"):
    links.append(f'<a href="{contact["linkedin"]}" target="_blank" rel="noopener noreferrer">LinkedIn</a>')
if contact.get("email"):
    links.append(f'<a href="mailto:{contact["email"]}">Email</a>')

if links or content.resume_path():
    components.render_section_title("contact")
    st.html(" &nbsp;·&nbsp; ".join(links))
    resume = content.resume_path()
    if resume:
        st.download_button(
            "Download Resume",
            data=resume.read_bytes(),
            file_name=resume.name,
            mime="application/pdf",
        )

components.render_footer()
