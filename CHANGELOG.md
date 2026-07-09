# Changelog

All notable changes to RAG—X are documented here.

---

## v1.4.0
> UI Overhaul — "Slate & Steel"

### Fixed
- Sidebar toggle restored — stopped hiding the Streamlit header entirely, which was nuking the collapse/expand button in v1.58.0
- `st.rerun()` removed from bottom of chat handler — was killing the stream before it finished rendering
- `st.selectbox` empty label replaced with hidden label — v1.58.0 throws a warning/error on empty strings
- Canvas column ratio flipped to `[3, 2]` — source canvas was taking more than half the screen

### Added
- `styles.py` — dedicated CSS module, keeps `app.py` clean
- Custom dark theme: near-black backgrounds (`#0C0C0E`), teal accents (`#14B8A6`), neutral grey borders
- RAG—X sticky header with live Ollama connection status indicator (green/red dot)
- Streamlit footer, deploy button, and hamburger menu hidden
- Source file chips rendered inline under every assistant response
- Expandable source chunk viewer — see the exact text the model used to answer
- Codebase mode: 2-column layout with a "Source Canvas" panel on the right
- Canvas shows retrieved source files in a syntax-highlighted code block with a file picker
- Temperature and k (chunks retrieved) exposed as live sidebar sliders
- `st.status` progress indicator for ingestion with step-by-step feedback
- Clear chat button resets conversation and canvas state

### Changed
- `retrieve.py` and `ask_code.py` now expose `get_sources()` separately from `build_chain()`
- Both chains accept `temperature` and `k` as parameters instead of hardcoded values
- Chat input disabled when no collection is selected
- `st.selectbox` label set to `"Collection"` with `label_visibility="collapsed"`

---

## v1.3.0
> Named Collections + Streaming Output

### Added
- Auto-named ChromaDB collections — derived from filename, repo name, or folder name
- Collection dropdown in sidebar — switch between indexed sources mid-session
- Streaming token output — words appear as the model generates instead of waiting for the full response
- `get_collections()` reads directly from ChromaDB — no separate tracking file needed

### Changed
- `ingest.py` — `collection_name` parameter replaces hardcoded `"documents"`
- `ingest_code.py` — `collection_name` parameter replaces hardcoded `"codebase"`
- `retrieve.py` — `build_chain()` accepts `collection_name`
- `ask_code.py` — `build_chain()` accepts `collection_name`
- Chat input disabled when no collection is active

---

## v1.2.0
> Streamlit UI + GitHub URL Ingestion

### Added
- Browser-based chat UI via Streamlit
- PDF upload directly from the browser — no manual file dropping into `./data/`
- GitHub URL ingestion in Codebase mode — paste a URL, it clones with `--depth=1`, ingests, then deletes the clone
- Chat history persists across questions within a session via `st.session_state`
- Mode switcher between Document Q&A and Codebase Assistant in the sidebar

---

## v1.1.0
> Codebase Assistant

### Added
- `ingest_code.py` — language-aware chunking using LangChain's `RecursiveCharacterTextSplitter.from_language()`
- `ask_code.py` — retrieval chain with source file citations in every answer
- Supports Python, JS, TS, JSX, TSX, Go, Rust, Java, C, C++, Ruby, HTML, Markdown
- Separate ChromaDB collection (`"codebase"`) — coexists with the document pipeline
- Smart directory skipping — ignores `.git`, `.venv`, `node_modules`, `__pycache__`, `dist`, `build`

---

## v1.0.0
> MVP

### Added
- PDF ingestion pipeline via PyMuPDF + LangChain
- `RecursiveCharacterTextSplitter` with 800-token chunks, 100-token overlap
- ChromaDB persistent vector store
- `nomic-embed-text` embeddings via Ollama
- `phi3:mini` LLM via Ollama — fully local, CPU-only
- LCEL retrieval chain with grounded prompt (no hallucination fallback)
- CLI interface for both ingestion and querying