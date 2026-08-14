"""Home: the personal portfolio landing page."""

import streamlit as st

from app.services import content
from app.ui import components

profile = content.load_profile()
experience = content.load_experience()
skills = content.load_skills()

# --- hero ---------------------------------------------------------------

st.markdown(
    f"""
    <div style="margin: 0.5rem 0 0.25rem; font-size: 1.9rem; font-weight: 700; letter-spacing: 0.01em;">
        {profile.get("name", "")}
    </div>
    <div style="font-size: 1.05rem; margin-bottom: 0.4rem;">
        {profile.get("title", "")}
    </div>
    <div class="text-muted" style="font-size: 0.95rem;">
        {profile.get("tagline", "")}
    </div>
    <div style="margin: 1rem 0 1.5rem; font-size: 1rem; max-width: 46ch;">
        {profile.get("summary", "")}
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)
with col1:
    if st.button("View Projects", use_container_width=True):
        st.switch_page("pages/projects.py")
with col2:
    if st.button("Ask My AI", type="primary", use_container_width=True):
        st.switch_page("pages/assistant.py")

# --- about ----------------------------------------------------------------

components.render_section_title("About")
st.markdown(f'<div style="max-width: 62ch;">{profile.get("about", "")}</div>', unsafe_allow_html=True)

# --- skills -----------------------------------------------------------------

if skills:
    components.render_section_title("Skills")
    components.render_skill_pills(skills)

# --- experience -----------------------------------------------------------

if experience:
    components.render_section_title("Experience")
    for i, job in enumerate(experience):
        product = f" · {job['product']}" if job.get("product") else ""
        st.markdown(
            f"""
            <div style="margin-bottom: 1.1rem;">
                <div style="font-weight: 600;">{job.get("company", "")}{product}</div>
                <div class="text-muted" style="font-size: 0.85rem; margin-bottom: 0.35rem;">
                    {job.get("role", "")} &nbsp;·&nbsp; {job.get("period", "")}
                </div>
                <div style="font-size: 0.92rem;">{job.get("description", "")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# --- current focus ----------------------------------------------------------

focus = profile.get("current_focus", [])
if focus:
    components.render_section_title("Current Focus")
    st.markdown(
        " &nbsp;·&nbsp; ".join(focus),
        unsafe_allow_html=False,
    )

# --- contact ----------------------------------------------------------------

contact = profile.get("contact", {})
links = []
if contact.get("github"):
    links.append(f'<a href="{contact["github"]}" target="_blank">GitHub</a>')
if contact.get("linkedin"):
    links.append(f'<a href="{contact["linkedin"]}" target="_blank">LinkedIn</a>')
if contact.get("email"):
    links.append(f'<a href="mailto:{contact["email"]}">Email</a>')

if links or content.resume_path():
    components.render_section_title("Contact")
    st.markdown(" &nbsp;·&nbsp; ".join(links), unsafe_allow_html=True)
    resume = content.resume_path()
    if resume:
        st.download_button(
            "Download Resume",
            data=resume.read_bytes(),
            file_name=resume.name,
            mime="application/pdf",
        )

components.render_footer()
