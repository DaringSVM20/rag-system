# RAG—X: Ask Your Documents, Locally

> Built with learnings from my training internship at TBRL, Ramgarh (DRDO) as a way to actually implement RAG in an isolated environment since the defence sector keeps things isolated for national security. No unauthorized information goes in or comes out.

---

## What is this?

This is a **Retrieval-Augmented Generation (RAG)** system that lets you ask questions about your documents or an entire codebase — and get answers grounded in the actual content, not hallucinated guesses.

It runs entirely on your machine. No cloud. No API keys. No data leaving your hands.

There are two pipelines:
- **Document pipeline** — point it at PDFs, ask questions
- **Codebase pipeline** — paste a GitHub URL or a local path, ask questions like "where is auth handled?" and get answers with file citations

Both are accessible through a clean chat UI — no terminal required after setup.

---

<!-- SCREENSHOT: Full UI overview — dark slate theme, RAG—X header, sidebar visible -->
<img width="1920" height="995" alt="image" src="https://github.com/user-attachments/assets/50b8186b-aed7-4219-be85-b822fd249b3a" />

*RAG—X — Document Q&A mode*

<!-- SCREENSHOT: Codebase mode — 2-column layout with source canvas on the right -->
<img width="1920" height="994" alt="image" src="https://github.com/user-attachments/assets/d2a1938a-9a26-48e7-988c-af152b937412" />

*Codebase Assistant with source canvas and file citations*

---

## Why local? Why CPU-only?

Short answer: I'm doing this at a DRDO lab.

Longer answer: TBRL is a defence research establishment. Sensitive documents, internal codebases, research data — none of that goes to OpenAI, Anthropic, or anyone else's servers. Local-first isn't a nice-to-have here, it's a hard requirement.

The machine I'm running this on is an **i7-10750H with 16GB RAM and no dedicated GPU** (My Intel UHD 630 doesn't count). So everything here is picked to run on CPU: quantized small models, lightweight embeddings, no CUDA anywhere. It's actually pretty usable once you get past the "but what about a GPU" instinct. The only thing you'd need is some patience so you give the model some time to think *using your CPU* before answering. There are other models recommended for everyone with stronger hardware. ✌🏻

---

## How it works (no jargon)

Imagine you have a 200-page document and you want to find an answer. You can't dump all 200 pages into a chatbot — that's too much text. So instead:

1. **Chop it up** — the document gets split into small overlapping chunks (like cutting a book into index cards)
2. **Convert to numbers** — each chunk gets turned into a list of numbers (a "vector") that captures its meaning. Similar meaning = similar numbers.
3. **Store it** — all those number-lists go into a vector database (ChromaDB)
4. **Ask a question** — your question also gets converted to numbers the same way
5. **Find matches** — the database finds the chunks whose numbers are closest to your question's numbers
6. **Generate an answer** — those matching chunks get handed to a local LLM along with your question, and it writes an answer based only on that context

That's it. The LLM never "reads" the whole document — it only sees the relevant bits you fetched for it. The retrieval step is doing the real work.

---

## Stack

| Layer | Tool | Why |
|---|---|---|
| LLM | phi3:mini (Ollama) | 3.8B params, ~2.3GB, fast enough on CPU |
| Embeddings | nomic-embed-text (Ollama) | Small, good quality, local |
| Vector DB | ChromaDB | Simple, persistent, no server needed |
| PDF parsing | PyMuPDF | Fast, handles messy PDFs well |
| Code chunking | LangChain + Language splitters | Splits at function/class boundaries |
| Orchestration | LangChain LCEL | Clean chain composition |
| UI | Streamlit | Fast to build, runs in browser |
| Package manager | uv | Faster than pip, proper lockfile |

---

## Prerequisites

- [Ollama](https://ollama.com) installed and running
- Python 3.11+
- [uv](https://astral.sh/uv)
- Git (for GitHub URL ingestion)

```bash
ollama pull phi3:mini
ollama pull nomic-embed-text
```

---

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/rag-system.git
cd rag-system
uv sync
```

---

## Usage

### UI (recommended)

```bash
uv run streamlit run app.py
```

Opens in your browser. Pick a mode from the sidebar, ingest your source, start asking.

### CLI

#### Document Q&A

```bash
# Drop PDFs into ./data/, then:
uv run python ingest.py
uv run python retrieve.py "What are the key findings in section 3?"
```

#### Codebase Assistant

```bash
# Local path:
uv run python ingest_code.py ./some-repo

# OR clone manually first:
git clone https://github.com/someone/some-repo.git
uv run python ingest_code.py ./some-repo

uv run python ask_code.py "how does authentication work here?"
uv run python ask_code.py "where does the database connection get initialized?"
```

Answers come with source file citations — not just "somewhere in the code."

---

## GitHub URL Ingestion

In the UI, you can paste a GitHub URL directly into the Codebase Assistant sidebar instead of a local path. Here's what happens under the hood:

1. The repo gets cloned with `--depth=1` (no git history, just the files — keeps it fast)
2. Ingestion runs against the cloned folder
3. The clone gets deleted — only the vector store is kept

Your disk stays clean, ChromaDB keeps everything it needs.

---

## Named Collections

Every ingest creates a named collection in ChromaDB — derived automatically from the source:

- PDF upload → named after the filename (`lecture-notes`, `thesis+2`)
- GitHub URL → named after the repo (`langchain`, `rag-system`)
- Local path → named after the folder

A dropdown in the sidebar lets you switch between collections mid-session. You can have your study material, a work codebase, and a GitHub repo all indexed at the same time and switch between them instantly.

---

## Tuning

The UI exposes these directly via sliders in the sidebar — no file editing needed:

| Parameter | Default | Effect |
|---|---|---|
| Temperature | 0.0 | 0 = factual, 1 = creative |
| Chunks retrieved (k) | 4–5 | More chunks = more context, slower response |

For chunk size and overlap, edit `ingest.py` / `ingest_code.py` directly:

| Parameter | Default | Effect |
|---|---|---|
| `chunk_size` | 800 | Tokens per chunk |
| `chunk_overlap` | 100 | Context preserved at chunk boundaries |

---

## Project Structure

```
rag-system/
├── data/               # PDFs go here (gitignored)
├── chroma_db/          # Persistent vector store (gitignored)
├── ingest.py           # PDF ingestion pipeline
├── retrieve.py         # PDF retrieval + Q&A
├── ingest_code.py      # Codebase ingestion pipeline
├── ask_code.py         # Codebase Q&A with file citations
├── styles.py           # All UI CSS — slate/steel theme
├── app.py              # Streamlit UI
└── pyproject.toml      # Dependencies (managed with uv)
```

---

## Hardware Guide — What to Run

Not everyone has the same machine. Here's a quick cheat sheet.

| Tier | Specs | LLM | Embeddings | Notes |
|---|---|---|---|---|
| Potato | i3 10th gen, 8GB RAM | `tinyllama:1.1b` | `nomic-embed-text` | Slow but works. Close other apps. |
| This repo's default | i7 10th gen, 16GB RAM, no dGPU | `phi3:mini` | `nomic-embed-text` | Comfortable. ~5-10s per answer. |
| Mid-range laptop GPU | RTX 4050 6GB / RX 6600M | `llama3.2:3b` or `mistral:7b` | `nomic-embed-text` | GPU handles inference, much faster. |
| Decent gaming laptop/PC | RTX 4060 8GB+ | `llama3.1:8b` | `nomic-embed-text` | The sweet spot. Fast, smart, local. |
| You have money | RTX 4090 / 3090 24GB | `llama3.1:70b` (Q4) | `nomic-embed-text` | Basically GPT-4 quality, at home. |

```bash
# swap in any model name — ollama handles the rest
ollama pull tinyllama        # ~600MB
ollama pull phi3:mini        # ~2.3GB  ← default here
ollama pull llama3.2:3b      # ~2GB
ollama pull mistral:7b       # ~4.1GB
ollama pull llama3.1:8b      # ~4.7GB
ollama pull llama3.1:70b     # ~40GB, don't do this on 16GB RAM
```

To switch models, change `LLM_MODEL` in `retrieve.py` and `ask_code.py`. One line each.

> **dGPU users:** Ollama auto-detects your GPU via CUDA (NVIDIA) or ROCm (AMD). No configuration needed — if the drivers are installed, it just uses the GPU.

---

## Version History

See [CHANGELOG.md](./CHANGELOG.md) for the full history.

### Latest: v1.4.0
- Full UI overhaul — "Slate & Steel" dark theme
- Streamlit chrome removed (header, footer, hamburger)
- RAG—X sticky header with live Ollama connection indicator
- Source citations rendered as file chips with expandable chunk viewer
- Codebase mode: side-by-side artifacts canvas showing retrieved source files
- Temperature and k controls exposed as sidebar sliders
- `st.status` ingestion feedback replacing plain spinners

---

## Context

This started as a learning project during my internship at **TBRL, Ramgarh** — a DRDO establishment. The goal was to understand RAG architecture hands-on rather than just reading about it. The CPU-only, local-first constraints turned out to be a good forcing function: you learn a lot more about what actually matters when you can't just throw GPU money at the problem.
