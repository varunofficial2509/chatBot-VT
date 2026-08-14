"""The application's single dark theme: exactly three colors.

Base colors live in .streamlit/config.toml so Streamlit's native widgets
(buttons, inputs, the top nav's active link, focus rings) pick them up
automatically. This module adds the CSS Streamlit's theme system can't
reach: hiding default chrome, chat message styling, and a couple of
opacity-based surfaces (never new hues) for subtle separation.
"""

import streamlit as st

BACKGROUND = "#0F1115"
TEXT = "#F5F5F5"
ACCENT = "#3B8C6E"

_CSS = f"""
<style>
:root {{
    --bg: {BACKGROUND};
    --text: {TEXT};
    --accent: {ACCENT};
    --text-muted: rgba(245, 245, 245, 0.60);
    --surface: rgba(245, 245, 245, 0.045);
    --surface-strong: rgba(245, 245, 245, 0.09);
    --border: rgba(245, 245, 245, 0.12);
    --accent-soft: rgba(59, 140, 110, 0.16);
}}

#MainMenu, footer {{ visibility: hidden; height: 0; }}

html, body, .stApp {{
    background: var(--bg);
    color: var(--text);
}}

[data-testid="stHeader"] {{
    background: var(--bg);
    border-bottom: 1px solid var(--border);
}}

[data-testid="stSidebar"] {{
    background: var(--bg);
    border-right: 1px solid var(--border);
}}

.block-container {{
    max-width: 760px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}}

p, li, span, label, div {{
    color: var(--text);
}}

a, a:visited, a:link, [data-testid="stMarkdown"] a {{
    color: var(--accent) !important;
}}

hr {{
    border-color: var(--border);
}}

/* Muted helper text (page taglines, captions, meta rows) */
.text-muted {{
    color: var(--text-muted) !important;
}}

/* Buttons: subtle outline by default, filled only for primary actions */
.stButton > button, .stFormSubmitButton > button {{
    background: transparent;
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 6px;
}}

.stButton > button:hover, .stFormSubmitButton > button:hover {{
    border-color: var(--accent);
    color: var(--accent);
}}

.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {{
    background: var(--accent);
    color: var(--bg);
    border: 1px solid var(--accent);
}}

.stButton > button[kind="primary"]:hover {{
    opacity: 0.88;
    color: var(--bg);
}}

/* Inputs */
input, textarea {{
    background: var(--surface) !important;
    color: var(--text) !important;
    border-color: var(--border) !important;
}}

/* Chat: assistant turns are plain readable text, user turns get a subtle
   container. No default colored bubbles. */
[data-testid="stChatMessage"] {{
    background: transparent;
    border-radius: 10px;
    padding: 0.2rem 0.1rem;
    gap: 0.5rem;
}}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
    background: var(--surface);
    border: 1px solid var(--border);
    padding: 0.7rem 1rem;
}}

[data-testid="stChatMessage"] p, [data-testid="stChatMessage"] li {{
    line-height: 1.65;
    font-size: 0.97rem;
}}

[data-testid="stChatMessage"] code {{
    background: var(--surface-strong);
    border-radius: 4px;
    padding: 0.1rem 0.3rem;
}}

[data-testid="stChatMessage"] pre {{
    background: var(--surface-strong);
    border: 1px solid var(--border);
    border-radius: 8px;
}}

[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"] {{
    background: var(--surface-strong) !important;
    color: var(--text) !important;
}}

[data-testid="stChatInput"] {{
    background: var(--surface);
    border: 1px solid var(--border) !important;
    border-radius: 10px;
}}

[data-testid="stChatInput"] textarea {{
    background: transparent !important;
    color: var(--text) !important;
}}

[data-testid="stChatInputSubmitButton"] {{
    background: var(--accent) !important;
    color: var(--bg) !important;
}}

/* File uploader / misc widgets */
[data-testid="stFileUploaderDropzone"] {{
    background: var(--surface);
    border: 1px dashed var(--border);
}}

[data-testid="stExpander"] {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
}}
</style>
"""


def configure_page(title: str) -> None:
    st.set_page_config(
        page_title=title,
        page_icon="◆",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    st.markdown(_CSS, unsafe_allow_html=True)
