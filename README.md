# RAG System — Ask Your Documents, Locally

> Built with learnings from my training internship at TBRL, Ramgarh (DRDO) as a way to actually implement RAG in an isolated environment since the defence sector keeps things isolated for national security. No unauthorized infomation goes in or comes out. 

---

## What is this?

This is a **Retrieval-Augmented Generation (RAG)** system that lets you ask questions about your documents or an entire codebase — and get answers grounded in the actual content, not hallucinated guesses.

It runs entirely on your machine. No cloud. No API keys. No data leaving your hands.

There are two pipelines:
- **Document pipeline** — point it at PDFs, ask questions
- **Codebase pipeline** — point it at any local repo, ask questions like "where is auth handled?" and get answers with file citations

---

## Why local? Why CPU-only?

Short answer: I'm doing this at a DRDO lab.

Longer answer: TBRL is a defence research establishment. Sensitive documents, internal codebases, research data — none of that goes to OpenAI, Anthropic, or anyone else's servers. Local-first isn't a nice-to-have here, it's a hard requirement.

The machine I'm running this on is an **i7-10750H with 16GB RAM and no dedicated GPU** (Intel UHD 630 doesn't count). So everything here is picked to run on CPU: quantized small models, lightweight embeddings, no CUDA anywhere. It's actually pretty usable once you get past the "but what about a GPU" instinct. The only thing you'd need is some patience so you give the model some time to think *using your CPU* before answering. There are other models recommended for everyone with stronger hardware. ✌🏻

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
| Package manager | uv | Faster than pip, proper lockfile |

---

## Prerequisites

- [Ollama](https://ollama.com) installed and running
- Python 3.11+
- [uv](https://astral.sh/uv)

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

## Usage:

### 1. Document Q&A

```bash
# Drop PDFs into ./data/, then:
uv run python ingest.py
uv run python retrieve.py "What are the key findings in section 3?"
```

### 2. Codebase Assistant

```bash
# Clone any repo locally first, then point at it:
git clone https://github.com/someone/some-repo.git
uv run python ingest_code.py ./some-repo
uv run python ask_code.py "how does authentication work here?"
uv run python ask_code.py "where does the database connection get initialized?"
```

Answers come with source file citations — not just "somewhere in the code."

---

## Tuning

| Parameter | File | Default | Effect |
|---|---|---|---|
| `chunk_size` | ingest.py / ingest_code.py | 800 | Tokens per chunk |
| `chunk_overlap` | ingest.py / ingest_code.py | 100 | Context preserved at chunk boundaries |
| `k` | retrieve.py / ask_code.py | 4–5 | Chunks retrieved per query |
| `temperature` | retrieve.py / ask_code.py | 0 | 0 = factual, higher = creative |

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
└── pyproject.toml      # Dependencies (managed with uv)
```

---

## Version History

### v1.1.0
- Codebase assistant with language-aware chunking
- Source file citations in every answer
- Supports Python, JS, TS, Go, Rust, Java, C, C++, Ruby, HTML, Markdown
- Separate ChromaDB collection — both pipelines coexist

### v1.0.0
- PDF ingestion pipeline
- ChromaDB vector storage
- Local LLM retrieval via Ollama
- LCEL chain

---

## Context

This started as a learning project during my internship at **TBRL, Ramgarh** — a DRDO establishment. The goal was to understand RAG architecture hands-on rather than just reading about it. The CPU-only, local-first constraints turned out to be a good forcing function: you learn a lot more about what actually matters when you can't just throw GPU money at the problem.