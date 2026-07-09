import subprocess
import tempfile
import shutil
from pathlib import Path

import chromadb
import streamlit as st

from ingest import ingest as ingest_pdfs
from ingest_code import ingest as ingest_code
from retrieve import build_chain as pdf_chain
from ask_code import build_chain as code_chain

CHROMA_PATH = "./chroma_db"

st.set_page_config(page_title="RAG System", layout="wide")
st.title("RAG System")


def get_collections() -> list[str]:
    try:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        return [c.name for c in client.list_collections()]
    except Exception:
        return []


def derive_pdf_name(files: list) -> str:
    if len(files) == 1:
        return Path(files[0].name).stem
    return f"{Path(files[0].name).stem}+{len(files) - 1}"


def derive_repo_name(source: str) -> str:
    # works for both URLs and local paths
    return source.rstrip("/").split("/")[-1].removesuffix(".git")


# ── Sidebar ────────────────────────────────────────────────────────────────────
mode = st.sidebar.radio("Mode", ["Document Q&A", "Codebase Assistant"])
st.sidebar.divider()

if mode == "Document Q&A":
    st.sidebar.subheader("Ingest PDFs")
    uploaded = st.sidebar.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)
    if st.sidebar.button("Ingest"):
        if not uploaded:
            st.sidebar.error("Upload at least one PDF.")
        else:
            collection_name = derive_pdf_name(uploaded)
            data_dir = Path("./data")
            data_dir.mkdir(exist_ok=True)
            for f in uploaded:
                (data_dir / f.name).write_bytes(f.read())
            with st.spinner(f"Ingesting as '{collection_name}'..."):
                ingest_pdfs(collection_name)
            st.sidebar.success(f"Saved as '{collection_name}'.")

else:
    st.sidebar.subheader("Ingest Codebase")
    repo_input = st.sidebar.text_input("Local path or GitHub URL")
    if st.sidebar.button("Ingest"):
        if not repo_input:
            st.sidebar.error("Provide a path or URL.")
        else:
            collection_name = derive_repo_name(repo_input)
            is_url = repo_input.startswith("http")
            clone_dir = None
            try:
                if is_url:
                    clone_dir = tempfile.mkdtemp(prefix="rag_repo_")
                    with st.spinner(f"Cloning {repo_input}..."):
                        result = subprocess.run(
                            ["git", "clone", "--depth=1", repo_input, clone_dir],
                            capture_output=True, text=True
                        )
                    if result.returncode != 0:
                        st.sidebar.error(f"Clone failed:\n{result.stderr}")
                        st.stop()
                    target = clone_dir
                else:
                    target = repo_input

                with st.spinner(f"Ingesting as '{collection_name}'..."):
                    ingest_code(target, collection_name)
                st.sidebar.success(f"Saved as '{collection_name}'.")
            finally:
                if clone_dir:
                    shutil.rmtree(clone_dir, ignore_errors=True)

# ── Collection picker ──────────────────────────────────────────────────────────
st.sidebar.divider()
collections = get_collections()
if collections:
    active_collection = st.sidebar.selectbox("Active collection", collections)
else:
    active_collection = None
    st.sidebar.info("No collections yet. Ingest something first.")

# ── Chat ───────────────────────────────────────────────────────────────────────
st.divider()

if "history" not in st.session_state:
    st.session_state.history = []

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = st.chat_input("Ask a question...", disabled=not active_collection)

if question and active_collection:
    st.session_state.history.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        chain = (
            pdf_chain(active_collection)
            if mode == "Document Q&A"
            else code_chain(active_collection)
        )
        answer = st.write_stream(chain.stream(question))

    st.session_state.history.append({"role": "assistant", "content": answer})