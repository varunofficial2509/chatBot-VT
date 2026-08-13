"""Shared CSS. Exactly three colors: background, text, one accent."""

BACKGROUND = "#fafaf9"
TEXT = "#1a1a1a"
ACCENT = "#2f6f4f"
MUTED = "#8a8a85"  # a tint of text, not a fourth color
BORDER = "#e4e2dd"  # a tint of background, not a fourth color

CSS = f"""
<style>
:root {{
    --bg: {BACKGROUND};
    --text: {TEXT};
    --accent: {ACCENT};
    --muted: {MUTED};
    --border: {BORDER};
}}

#MainMenu, header[data-testid="stHeader"], footer {{ visibility: hidden; height: 0; }}

html, body, .stApp {{
    background: var(--bg);
    color: var(--text);
}}

.block-container {{
    max-width: 720px;
    padding-top: 3rem;
    padding-bottom: 2rem;
}}

.recruiter-header {{
    text-align: center;
    margin-bottom: 2rem;
}}

.recruiter-header .name {{
    font-size: 1.4rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin: 0;
}}

.recruiter-header .tagline {{
    color: var(--muted);
    font-size: 0.85rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin: 0.25rem 0 1rem;
}}

.recruiter-header .prompt {{
    color: var(--muted);
    font-size: 0.95rem;
    max-width: 480px;
    margin: 0 auto;
}}

[data-testid="stChatMessage"] {{
    background: transparent;
}}

[data-testid="stChatMessageAvatarUser"],
[data-testid="stChatMessageAvatarAssistant"] {{
    background: var(--accent) !important;
    color: var(--bg) !important;
}}

[data-testid="stChatInput"] {{
    border-color: var(--border) !important;
}}

[data-testid="stChatInput"] textarea {{
    color: var(--text) !important;
}}

.stButton > button, .stFormSubmitButton > button {{
    background: var(--accent);
    color: var(--bg);
    border: none;
}}

.stButton > button:hover, .stFormSubmitButton > button:hover {{
    background: var(--accent);
    opacity: 0.85;
}}

a, a:visited {{
    color: var(--accent);
}}

.knowledge-status-ok {{
    color: var(--accent);
    font-size: 0.85rem;
}}

.knowledge-status-error {{
    color: var(--text);
    font-size: 0.85rem;
}}

.knowledge-file-list {{
    color: var(--muted);
    font-size: 0.85rem;
    line-height: 1.6;
}}
</style>
"""
