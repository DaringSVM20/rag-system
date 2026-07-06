
# RAG System

A local, privacy-first Retrieval-Augmented Generation system. Ask questions about your documents. No cloud, no API keys, no data leaving your machine.

## Stack

- **LLM:** phi3:mini via Ollama (runs on CPU)
- **Embeddings:** nomic-embed-text via Ollama
- **Vector Store:** ChromaDB (persistent, local)
- **Parsing:** PyMuPDF
- **Orchestration:** LangChain (LCEL)
- **Package Manager:** uv

## Prerequisites

- [Ollama](https://ollama.com) installed and running
- Python 3.11+
- [uv](https://astral.sh/uv)

```bash
ollama pull phi3:mini
ollama pull nomic-embed-text
```

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/rag-system.git
cd rag-system
uv sync
```

## Usage

**1. Add PDFs to `./data/`**

**2. Ingest:**
```bash
uv run python ingest.py
```

**3. Query:**
```bash
uv run python retrieve.py "What does the document say about X?"
```

## Architecture

```
Ingestion:
PDFs → PyMuPDF → RecursiveCharacterTextSplitter → nomic-embed-text → ChromaDB

Retrieval:
Query → nomic-embed-text → ChromaDB (top-k similarity) → prompt → phi3:mini → answer
```

## Tuning

| Parameter | File | Default | Effect |
|---|---|---|---|
| `chunk_size` | ingest.py | 800 | Tokens per chunk |
| `chunk_overlap` | ingest.py | 100 | Context preserved at boundaries |
| `k` | retrieve.py | 4 | Chunks retrieved per query |
| `temperature` | retrieve.py | 0 | 0 = factual, 1 = creative |

## Version History

### v1.0.0
- PDF ingestion pipeline
- ChromaDB vector storage
- Local LLM retrieval via Ollama
- LCEL chain
