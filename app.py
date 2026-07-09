import subprocess
import tempfile
import shutil
import urllib.request
from pathlib import Path

import chromadb
import streamlit as st

from styles import apply_styles, render_header, render_sources
from ingest import ingest as ingest_pdfs
from ingest_code import ingest as ingest_code
from retrieve import build_chain as pdf_chain, get_sources as pdf_sources
from ask_code import build_chain as code_chain, get_sources as code_sources

CHROMA_PATH = "./chroma_db"

st.set_page_config(page_title="RAG—X", layout="wide", initial_sidebar_state="expanded")
apply_styles()


def check_ollama() -> bool:
    try:
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
        return True
    except Exception:
        return False


def get_collections() -> list[str]:
    try:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        return [c.name for c in client.list_collections()]
    except Exception:
        return []


def derive_pdf_name(files: list) -> str:
    import re
    name = Path(files[0].name).stem if len(files) == 1 else f"{Path(files[0].name).stem}+{len(files) - 1}"
    # replace spaces and illegal chars with hyphens
    name = re.sub(r"[^a-zA-Z0-9._-]", "-", name)
    # strip leading/trailing hyphens/dots
    name = name.strip("-.")
    # if it starts with a non-letter, prepend "doc-"
    if not name[0].isalpha():
        name = "doc-" + name
    return name[:512]


def derive_repo_name(source: str) -> str:
    return source.rstrip("/").split("/")[-1].removesuffix(".git")


# ── Session state defaults ────────────────────────────────────────────────────

for key, default in {
    "history": [],
    "temperature": 0.0,
    "k": 4,
    "canvas_sources": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚡ RAG—X")
    mode = st.radio("Mode", ["Document Q&A", "Codebase Assistant"], label_visibility="collapsed")
    st.divider()

    st.markdown("**Data Ingestion**")
    if mode == "Document Q&A":
        uploaded = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
        if st.button("Ingest PDFs"):
            if not uploaded:
                st.error("Upload at least one PDF.")
            else:
                collection_name = derive_pdf_name(uploaded)
                Path("./data").mkdir(exist_ok=True)
                for f in uploaded:
                    (Path("./data") / f.name).write_bytes(f.read())
                with st.status(f"Ingesting as '{collection_name}'…", expanded=True) as s:
                    st.write("Parsing PDFs…")
                    ingest_pdfs(collection_name)
                    s.update(label=f"✅ Saved as '{collection_name}'", state="complete")
    else:
        repo_input = st.text_input("Local path or GitHub URL", placeholder="https://github.com/…")
        if st.button("Ingest Codebase"):
            if not repo_input:
                st.error("Provide a path or URL.")
            else:
                collection_name = derive_repo_name(repo_input)
                is_url = repo_input.startswith("http")
                clone_dir = None
                try:
                    with st.status(f"Ingesting as '{collection_name}'…", expanded=True) as s:
                        if is_url:
                            st.write("Cloning repo…")
                            clone_dir = tempfile.mkdtemp(prefix="rag_repo_")
                            result = subprocess.run(
                                ["git", "clone", "--depth=1", repo_input, clone_dir],
                                capture_output=True, text=True
                            )
                            if result.returncode != 0:
                                s.update(label="❌ Clone failed", state="error")
                                st.error(result.stderr)
                                st.stop()
                            target = clone_dir
                        else:
                            target = repo_input
                        st.write("Chunking and embedding…")
                        ingest_code(target, collection_name)
                        s.update(label=f"✅ Saved as '{collection_name}'", state="complete")
                finally:
                    if clone_dir:
                        shutil.rmtree(clone_dir, ignore_errors=True)

    st.divider()

    st.markdown("**Active Collection**")
    collections = get_collections()
    if collections:
        active_collection = st.selectbox("Collection", collections, label_visibility="collapsed")
    else:
        active_collection = None
        st.caption("No collections yet. Ingest something first.")

    st.divider()

    with st.expander("⚙️ Model Settings"):
        st.session_state.temperature = st.slider(
            "Temperature", 0.0, 1.0, st.session_state.temperature, 0.05,
            help="0 = factual, 1 = creative"
        )
        st.session_state.k = st.slider(
            "Chunks retrieved (k)", 1, 10, st.session_state.k,
            help="More chunks = more context, slower response"
        )

    st.divider()

    if st.button("🗑 Clear chat"):
        st.session_state.history = []
        st.session_state.canvas_sources = []
        st.rerun()


# ── Main area ─────────────────────────────────────────────────────────────────

render_header(check_ollama())
is_code = mode == "Codebase Assistant"

if is_code:
    chat_col, canvas_col = st.columns([3, 2], gap="large")
else:
    chat_col = st.container()
    canvas_col = None

# ── Chat history ──────────────────────────────────────────────────────────────

with chat_col:
    for msg in st.session_state.history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("sources"):
                render_sources(msg["sources"], is_code)

# ── Canvas ────────────────────────────────────────────────────────────────────

if canvas_col:
    with canvas_col:
        st.markdown(
            '<div style="font-family:monospace;font-size:0.75rem;color:#1B6FEB;'
            'border-bottom:1px solid #334155;padding-bottom:8px;margin-bottom:12px;">'
            '📁 SOURCE CANVAS</div>',
            unsafe_allow_html=True
        )
        sources = st.session_state.canvas_sources
        if sources:
            options = [doc.metadata.get("source", f"Source {i+1}") for i, doc in enumerate(sources)]
            selected = st.selectbox("Select file to inspect", options)
            idx = options.index(selected)
            doc = sources[idx]
            lang = doc.metadata.get("language", ".py").lstrip(".")
            st.code(doc.page_content, language=lang)
        else:
            st.markdown(
                '<div class="canvas-empty">'
                '📂<br>Source chunks appear here<br>after your first question.'
                '</div>',
                unsafe_allow_html=True
            )

# ── Chat input ────────────────────────────────────────────────────────────────

question = st.chat_input("Ask a question…", disabled=not active_collection)

if question and active_collection:
    sources = (
        code_sources(question, active_collection, st.session_state.k)
        if is_code else
        pdf_sources(question, active_collection, st.session_state.k)
    )
    # update canvas before streaming so it's visible while answer renders
    st.session_state.canvas_sources = sources

    st.session_state.history.append({"role": "user", "content": question})

    with chat_col:
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            chain = (
                code_chain(active_collection, st.session_state.temperature, st.session_state.k)
                if is_code else
                pdf_chain(active_collection, st.session_state.temperature, st.session_state.k)
            )
            # this is the fix — no st.rerun() after this, let it stream fully
            answer = st.write_stream(chain.stream(question))
            render_sources(sources, is_code)

    st.session_state.history.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
    })