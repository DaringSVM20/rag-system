import streamlit as st

TEAL       = "#14B8A6"
TEAL_DIM   = "#0D9488"
BG         = "#0C0C0E"
SURFACE    = "#161618"
SURFACE2   = "#1E1E21"
BORDER     = "#2C2C30"
MUTED      = "#6B6B72"
TEXT       = "#ECECF0"
TEXT_DIM   = "#A0A0A8"
GREEN      = "#22C55E"
RED        = "#EF4444"


def apply_styles():
    st.markdown(f"""
    <style>
        /* ── Strip Streamlit chrome ── */
        footer {{ visibility: hidden; }}
        #MainMenu {{ visibility: hidden; }}
        .stDeployButton {{ display: none; }}
                
        /* 1.58.x button naming */
        button[data-testid="stBaseButton-headerNoPadding"] {{
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
        }}

        /* ── Base ── */
        html, body, .stApp {{
            background-color: {BG};
            color: {TEXT};
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
        }}

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {{
            background-color: {SURFACE} !important;
            border-right: 1px solid {BORDER} !important;
        }}
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label {{
            color: {TEXT_DIM} !important;
            font-size: 0.85rem;
        }}

        /* ── Chat bubbles ── */
        [data-testid="stChatMessage"] {{
            background-color: transparent !important;
            border: 1px solid {BORDER};
            border-radius: 14px;
            padding: 14px 18px;
            margin-bottom: 10px;
        }}

        /* ── Chat input ── */
        [data-testid="stChatInputContainer"] {{
            background-color: {SURFACE} !important;
            border: 1px solid {BORDER} !important;
            border-radius: 12px !important;
            padding: 4px 8px !important;
        }}
        [data-testid="stChatInputTextArea"] {{
            background-color: transparent !important;
            color: {TEXT} !important;
            font-size: 0.9rem !important;
        }}
        [data-testid="stChatInputContainer"]:focus-within {{
            border-color: {TEAL} !important;
        }}

        /* ── Expander ── */
        .streamlit-expanderHeader {{
            background-color: {SURFACE2} !important;
            border: 1px solid {BORDER} !important;
            border-radius: 8px !important;
            color: {TEXT_DIM} !important;
            font-size: 0.8rem !important;
        }}
        .streamlit-expanderContent {{
            background-color: {SURFACE2} !important;
            border: 1px solid {BORDER} !important;
            border-top: none !important;
        }}

        /* ── Source chips ── */
        .source-chip {{
            font-family: 'Courier New', monospace;
            font-size: 0.72rem;
            background-color: {SURFACE2};
            border: 1px solid {TEAL}44;
            border-radius: 6px;
            padding: 3px 10px;
            margin: 3px 4px;
            color: {TEAL};
            display: inline-block;
        }}

        /* ── Canvas empty state ── */
        .canvas-empty {{
            color: {MUTED};
            font-size: 0.85rem;
            text-align: center;
            margin-top: 80px;
            line-height: 1.8;
        }}

        /* ── Buttons ── */
        .stButton button {{
            background-color: {SURFACE2} !important;
            border: 1px solid {BORDER} !important;
            color: {TEXT_DIM} !important;
            border-radius: 8px !important;
            font-size: 0.85rem !important;
            width: 100%;
            transition: all 0.15s ease;
        }}
        .stButton button:hover {{
            background-color: {TEAL} !important;
            border-color: {TEAL} !important;
            color: {BG} !important;
        }}

        /* ── Selectbox ── */
        [data-testid="stSelectbox"] > div > div {{
            background-color: {SURFACE2} !important;
            border: 1px solid {BORDER} !important;
            color: {TEXT} !important;
            border-radius: 8px !important;
        }}

        /* ── Slider ── */
        [data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {{
            background-color: {TEAL} !important;
            border-color: {TEAL} !important;
        }}

        /* ── Radio ── */
        [data-testid="stRadio"] label {{
            color: {TEXT_DIM} !important;
        }}

        /* ── Scrollbar ── */
        ::-webkit-scrollbar {{ width: 4px; height: 4px; }}
        ::-webkit-scrollbar-track {{ background: {BG}; }}
        ::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 2px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: {MUTED}; }}

        /* ── Divider ── */
        hr {{ border-color: {BORDER} !important; }}

        /* ── Code blocks ── */
        [data-testid="stCode"] {{
            background-color: {SURFACE2} !important;
            border: 1px solid {BORDER} !important;
            border-radius: 8px !important;
        }}
    </style>
    """, unsafe_allow_html=True)


def render_header(ollama_online: bool):
    dot = (
        f'<span style="display:inline-block;width:7px;height:7px;background:{GREEN};'
        f'border-radius:50%;margin-right:6px;box-shadow:0 0 6px {GREEN}88;"></span>'
        if ollama_online else
        f'<span style="display:inline-block;width:7px;height:7px;background:{RED};'
        f'border-radius:50%;margin-right:6px;"></span>'
    )
    label = "Ollama online" if ollama_online else "Ollama offline"
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:space-between;
                padding:10px 0 18px 0;border-bottom:1px solid {BORDER};margin-bottom:16px;">
        <div>
            <span style="font-size:1.25rem;font-weight:600;letter-spacing:0.03em;color:{TEXT};">RAG</span>
            <span style="font-size:1.25rem;font-weight:600;letter-spacing:0.03em;color:{TEAL};">—X</span>
            <span style="font-size:0.7rem;color:{MUTED};margin-left:12px;letter-spacing:0.1em;text-transform:uppercase;">
                Local · Private · Precise
            </span>
        </div>
        <div style="font-size:0.78rem;color:{TEXT_DIM};display:flex;align-items:center;">
            {dot}{label}
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_sources(sources: list, is_code: bool):
    if not sources:
        return
    icon = "📁" if is_code else "📄"
    chips = "".join(
        f'<span class="source-chip">{icon} {doc.metadata.get("source", "unknown")}</span>'
        for doc in sources
    )
    st.markdown(f'<div style="margin-top:8px;">{chips}</div>', unsafe_allow_html=True)
    with st.expander(f"View {len(sources)} source chunks"):
        for i, doc in enumerate(sources):
            path = doc.metadata.get("source", "unknown")
            lang = doc.metadata.get("language", ".txt").lstrip(".")
            st.markdown(
                f'<div style="font-family:monospace;font-size:0.75rem;color:{TEAL};'
                f'margin-bottom:6px;">{icon} {path}</div>',
                unsafe_allow_html=True
            )
            if is_code:
                st.code(doc.page_content, language=lang)
            else:
                st.caption(
                    doc.page_content[:400] + "…"
                    if len(doc.page_content) > 400
                    else doc.page_content
                )
            if i < len(sources) - 1:
                st.divider()