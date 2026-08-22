"""The application's single dark theme: exactly three colors.

Base colors live in .streamlit/config.toml so Streamlit's native widgets
(buttons, inputs, focus rings) pick them up automatically. This module adds
the CSS Streamlit's theme system can't reach: hiding default chrome, the
custom terminal-style nav, hero/skills/projects layout, chat styling, and
font loading. Never introduce a new hue here — only these three colors and
opacity-based surfaces derived from them.
"""

import streamlit as st

BACKGROUND = "#0D0F14"
TEXT = "#F2F2F2"
ACCENT = "#B77BE8"

_CSS = f"""
<style>
:root {{
    --bg: {BACKGROUND};
    --text: {TEXT};
    --accent: {ACCENT};
    --text-muted: rgba(242, 242, 242, 0.58);
    --text-faint: rgba(242, 242, 242, 0.38);
    --surface: rgba(242, 242, 242, 0.04);
    --surface-strong: rgba(242, 242, 242, 0.08);
    --border: rgba(242, 242, 242, 0.12);
    --accent-soft: rgba(183, 123, 232, 0.12);
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
}}

/* ---------------------------------------------------------------------- */
/* Streamlit chrome removal                                               */
/* ---------------------------------------------------------------------- */

#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"] {{
    visibility: hidden;
    height: 0;
}}

[data-testid="stHeader"] {{
    display: none;
}}

[data-testid="stSidebar"] {{
    background: var(--bg);
    border-right: 1px solid var(--border);
}}

[data-testid="stSidebarNav"] {{ display: none; }}

html, body, .stApp {{
    background: var(--bg);
    color: var(--text);
    font-family: var(--font-sans);
}}

.block-container {{
    max-width: 1040px;
    padding-top: 1.25rem;
    padding-bottom: 3rem;
}}

h1, h2, h3, h4, h5, h6 {{
    font-family: var(--font-sans);
    color: var(--text);
}}

p, li, span, label, div {{
    color: var(--text);
}}

a, a:visited, a:link, [data-testid="stMarkdown"] a {{
    color: var(--accent) !important;
    text-decoration: none;
    transition: opacity 0.15s ease;
}}
a:hover {{ text-decoration: underline; text-underline-offset: 3px; }}

hr {{ border-color: var(--border); }}

.mono {{ font-family: var(--font-mono); }}
.text-muted {{ color: var(--text-muted) !important; }}
.text-faint {{ color: var(--text-faint) !important; }}
.accent {{ color: var(--accent) !important; }}

/* ---------------------------------------------------------------------- */
/* Nav                                                                    */
/* ---------------------------------------------------------------------- */

.vt-nav {{
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    flex-wrap: wrap;
    row-gap: 0.5rem;
    padding: 0.5rem 0 0.9rem;
    margin-bottom: 1.1rem;
    border-bottom: 1px solid var(--border);
}}

.vt-nav-brand {{
    font-family: var(--font-mono);
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--text) !important;
    white-space: nowrap;
}}

.vt-nav-links {{
    display: flex;
    flex-wrap: wrap;
    gap: 1.1rem;
}}

.vt-nav-links a {{
    font-family: var(--font-mono);
    font-size: 0.82rem;
    color: var(--text-muted) !important;
    text-decoration: none !important;
    transition: color 0.15s ease;
}}

.vt-nav-links a:hover {{ color: var(--text) !important; }}
.vt-nav-links a.active {{ color: var(--accent) !important; }}

@media (max-width: 560px) {{
    .vt-nav {{ flex-direction: column; align-items: flex-start; }}
    .vt-nav-links {{ gap: 0.85rem 1rem; }}
}}

/* ---------------------------------------------------------------------- */
/* Hero                                                                   */
/* ---------------------------------------------------------------------- */

.vt-hero {{
    display: flex;
    align-items: center;
    gap: 1.1rem;
    margin: 0 0 1.1rem;
}}

.vt-avatar-img {{
    width: 64px;
    height: 64px;
    border-radius: 8px;
    object-fit: cover;
    border: 1px solid var(--border);
    flex-shrink: 0;
}}

.vt-avatar-fallback {{
    width: 64px;
    height: 64px;
    border-radius: 8px;
    border: 1px solid var(--border);
    background: var(--surface);
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: var(--font-mono);
    font-size: 1.1rem;
    color: var(--accent);
    flex-shrink: 0;
}}

.vt-hero-name {{
    font-size: 2.15rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    line-height: 1.2;
}}

.vt-hero-title {{
    font-size: 1.05rem;
    color: var(--text-muted);
    margin-top: 0.2rem;
}}

.vt-hero-tagline {{
    font-family: var(--font-mono);
    font-size: 0.82rem;
    color: var(--accent);
    margin: 0.8rem 0;
}}

.vt-hero-summary {{
    font-size: 1rem;
    color: var(--text-muted);
    max-width: 52ch;
    line-height: 1.6;
    margin-bottom: 1.1rem;
}}

/* Generative node-graph beside the hero text. No border/background of its
   own — it floats directly on the page, not inside a card. Purely
   decorative, so it's dropped on narrow viewports rather than squeezed.
   st.columns(vertical_alignment="center") doesn't actually reach the row's
   CSS in this Streamlit version (computed align-items stays "stretch"), so
   it's forced here instead — that's what centers the graph against the
   hero text rather than pinning both to the row's top. */
[data-testid="stHorizontalBlock"]:has(.st-key-vt_hero_visual) {{
    align-items: center !important;
}}
.st-key-vt_hero_visual {{
    position: relative;
    height: 680px !important;
    min-height: 680px !important;
}}
.st-key-vt_hero_visual canvas {{
    position: absolute;
    inset: 0;
    display: block;
}}
/* Scales down at narrower widths rather than disappearing — the JS reads
   the container's actual size each resize and fits the object to it. */
@media (max-width: 900px) {{
    .st-key-vt_hero_visual {{ height: 480px !important; min-height: 480px !important; }}
}}
@media (max-width: 640px) {{
    .st-key-vt_hero_visual {{ height: 300px !important; min-height: 300px !important; margin-top: 0.5rem; }}
}}

/* ---------------------------------------------------------------------- */
/* Section titles ("$ about", "$ skills", ...)                            */
/* ---------------------------------------------------------------------- */

.vt-section-title {{
    display: flex;
    align-items: center;
    gap: 0.7rem;
    font-family: var(--font-mono);
    font-size: 0.95rem;
    font-weight: 500;
    letter-spacing: 0.02em;
    color: var(--text);
    margin: 2.25rem 0 1.25rem;
    padding-top: 0.25rem;
}}
.vt-section-title::after {{
    content: "";
    flex: 1;
    height: 1px;
    background: var(--border);
}}
.vt-section-title .accent {{ margin-right: -0.15rem; }}
.vt-section-anchor {{ position: relative; top: -4.5rem; }}

.vt-body-text {{
    font-size: 1rem;
    line-height: 1.7;
    color: var(--text-muted);
    max-width: 62ch;
}}

/* ---------------------------------------------------------------------- */
/* Skills                                                                 */
/* ---------------------------------------------------------------------- */

.vt-skills {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
}}

@media (max-width: 860px) {{
    .vt-skills {{ grid-template-columns: repeat(2, 1fr); }}
}}
@media (max-width: 560px) {{
    .vt-skills {{ grid-template-columns: 1fr; }}
}}

.vt-skill-card {{
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--surface);
    padding: 1.1rem 1.25rem;
    transition: border-color 0.18s ease, transform 0.18s ease, box-shadow 0.18s ease;
}}
.vt-skill-card:hover {{
    border-color: var(--accent);
    transform: translateY(-2px);
    box-shadow: 0 10px 24px -14px var(--accent-soft), 0 0 0 1px var(--accent-soft);
}}

.vt-skill-cat-label {{
    font-family: var(--font-mono);
    font-size: 0.72rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-faint);
    margin-bottom: 0.7rem;
}}

.vt-skill-items {{
    display: flex;
    flex-direction: column;
    gap: 0.55rem;
}}

.vt-skill-item {{
    display: flex;
    align-items: center;
    gap: 0.55rem;
    font-size: 0.9rem;
    color: var(--text);
}}

.vt-skill-item img {{
    width: 16px;
    height: 16px;
    opacity: 0.82;
}}

.vt-skill-item .vt-skill-dot {{
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: var(--accent);
    flex-shrink: 0;
}}

/* ---------------------------------------------------------------------- */
/* Experience                                                             */
/* ---------------------------------------------------------------------- */

.vt-exp {{
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--surface);
    padding: 1.3rem 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.18s ease, transform 0.18s ease, box-shadow 0.18s ease;
}}
.vt-exp:last-child {{ margin-bottom: 0; }}
.vt-exp:hover {{
    border-color: var(--accent);
    transform: translateY(-2px);
    box-shadow: 0 10px 24px -14px var(--accent-soft), 0 0 0 1px var(--accent-soft);
}}
.vt-exp-period {{
    font-family: var(--font-mono);
    font-size: 0.78rem;
    color: var(--accent);
    margin-bottom: 0.35rem;
}}
.vt-exp-role {{ font-size: 1.08rem; font-weight: 600; }}
.vt-exp-company {{ font-size: 0.88rem; color: var(--text-muted); margin-bottom: 0.7rem; }}
.vt-exp-desc {{ font-size: 0.94rem; color: var(--text-muted); line-height: 1.6; max-width: 62ch; }}
.vt-exp-tech {{ font-family: var(--font-mono); font-size: 0.78rem; color: var(--accent); margin-top: 0.85rem; }}

/* ---------------------------------------------------------------------- */
/* Projects                                                               */
/* ---------------------------------------------------------------------- */

.vt-projects-grid {{
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 1.1rem;
}}
@media (max-width: 720px) {{
    .vt-projects-grid {{ grid-template-columns: 1fr; }}
}}

.vt-project {{
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--surface);
    padding: 1.4rem 1.5rem;
    display: flex;
    flex-direction: column;
    transition: border-color 0.18s ease, transform 0.18s ease, box-shadow 0.18s ease;
}}
.vt-project:hover {{
    border-color: var(--accent);
    transform: translateY(-3px);
    box-shadow: 0 12px 28px -14px var(--accent-soft), 0 0 0 1px var(--accent-soft);
}}
.vt-project-head {{
    display: flex;
    gap: 0.7rem;
    align-items: baseline;
    margin-bottom: 0.3rem;
}}
.vt-project-num {{ font-family: var(--font-mono); font-size: 0.82rem; color: var(--text-faint); }}
.vt-project-title {{ font-size: 1.1rem; font-weight: 600; }}
.vt-project-category {{ font-size: 0.8rem; color: var(--text-faint); margin: 0.1rem 0 0.75rem; }}
.vt-project-desc {{ font-size: 0.92rem; color: var(--text-muted); line-height: 1.6; margin: 0 0 0.9rem; flex: 1; }}
.vt-project-result {{ font-size: 0.85rem; color: var(--text-muted); margin: -0.4rem 0 0.9rem; }}
.vt-project-tech {{ font-family: var(--font-mono); font-size: 0.78rem; color: var(--accent); margin: 0 0 0.6rem; }}
.vt-project-link {{ font-family: var(--font-mono); font-size: 0.82rem; }}

/* ---------------------------------------------------------------------- */
/* Buttons                                                                */
/* ---------------------------------------------------------------------- */

.stButton > button, .stFormSubmitButton > button {{
    background: transparent;
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 6px;
    font-family: var(--font-sans);
    font-weight: 500;
    transition: border-color 0.15s ease, color 0.15s ease, transform 0.15s ease, box-shadow 0.15s ease;
}}

.stButton > button:hover, .stFormSubmitButton > button:hover {{
    border-color: var(--accent);
    color: var(--accent);
    transform: translateY(-1px);
}}

.stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"] {{
    background: var(--accent);
    color: var(--bg);
    border: 1px solid var(--accent);
}}

.stButton > button[kind="primary"]:hover {{
    opacity: 0.9;
    color: var(--bg);
    transform: translateY(-1px);
    box-shadow: 0 8px 20px -10px var(--accent);
}}

/* Suggestion rows on the AI assistant landing: left-aligned, minimal */
.st-key-vt_suggestions .stButton > button {{
    background: transparent;
    border: 1px solid var(--border);
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: 0.85rem;
    padding: 0.7rem 1rem;
}}
.st-key-vt_suggestions .stButton > button > div {{
    justify-content: flex-start;
    width: 100%;
}}
.st-key-vt_suggestions .stButton > button p {{
    text-align: left;
}}
.st-key-vt_suggestions .stButton > button:hover {{
    border-color: var(--accent);
    color: var(--text);
}}
.st-key-vt_suggestions [data-testid="stVerticalBlock"] {{ gap: 0.6rem; }}

/* ---------------------------------------------------------------------- */
/* Inputs                                                                 */
/* ---------------------------------------------------------------------- */

input, textarea {{
    background: var(--surface) !important;
    color: var(--text) !important;
    border-color: var(--border) !important;
    font-family: var(--font-sans) !important;
}}

/* ---------------------------------------------------------------------- */
/* Chat                                                                   */
/* ---------------------------------------------------------------------- */

.vt-ai-hero {{ text-align: center; margin: 1.75rem 0 2.25rem; }}
.vt-ai-hero .vt-section-title {{ margin: 0 0 0.5rem; justify-content: center; display: block; }}
.vt-ai-hero-title {{ font-size: 1.7rem; font-weight: 700; margin-bottom: 0.6rem; }}
.vt-ai-hero-sub {{ font-size: 0.95rem; color: var(--text-muted); max-width: 42ch; margin: 0 auto; line-height: 1.6; }}

/* Match st.chat_input's native centered width (Streamlit doesn't derive it
   from .block-container) so the conversation and the input box line up. */
.st-key-vt_chat_col {{
    max-width: 704px !important;
    margin: 0 auto !important;
}}

[data-testid="stChatMessage"] {{
    background: transparent;
    border-radius: 8px;
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
    font-size: 0.95rem;
}}

[data-testid="stChatMessage"] code {{
    background: var(--surface-strong);
    border-radius: 4px;
    padding: 0.1rem 0.3rem;
    font-family: var(--font-mono);
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
    font-family: var(--font-sans) !important;
}}

[data-testid="stChatInputSubmitButton"] {{
    background: var(--accent) !important;
    color: var(--bg) !important;
}}
[data-testid="stChatInputSubmitButton"]:hover {{ opacity: 0.85; }}

/* ---------------------------------------------------------------------- */
/* Misc widgets                                                           */
/* ---------------------------------------------------------------------- */

[data-testid="stFileUploaderDropzone"] {{
    background: var(--surface);
    border: 1px dashed var(--border);
}}

[data-testid="stExpander"] {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
}}

.vt-footer {{
    margin-top: 3.5rem;
    padding-top: 1.25rem;
    border-top: 1px solid var(--border);
    display: flex;
    justify-content: space-between;
    align-items: center;
}}
.vt-footer-credit {{ font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-faint); }}
</style>
"""


def configure_page(title: str) -> None:
    """Sets page config. Must run once, from the entrypoint script, before
    ``st.navigation(...).run()`` — that's the one Streamlit command that
    can't be delegated to a page script.
    """
    st.set_page_config(
        page_title=title,
        page_icon="◆",
        layout="centered",
        initial_sidebar_state="collapsed",
    )


def inject_css() -> None:
    """Applies the theme CSS. Must be called from within each page script
    (not from the entrypoint before ``nav.run()``): ``st.html()`` queues
    style-only content through Streamlit's "event container", and that
    queue gets dropped when ``st.navigation`` hands off into a page rather
    than persisting from the parent script.
    """
    st.html(_CSS)
