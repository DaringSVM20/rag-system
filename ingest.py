# ingest.py
# Loads PDFs from ./data, chunks them, embeds, stores in ChromaDB.

import sys
from pathlib import Path

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

CHROMA_PATH = "./chroma_db"
DATA_PATH = "./data"
EMBED_MODEL = "nomic-embed-text"


def load_pdfs(data_dir: str) -> list:
    docs = []
    for pdf_path in Path(data_dir).glob("*.pdf"):
        print(f"Loading: {pdf_path.name}")
        loader = PyMuPDFLoader(str(pdf_path))
        docs.extend(loader.load())
    return docs


def split_documents(docs: list) -> list:
    # chunk_size: tokens per chunk. chunk_overlap: shared tokens between chunks.
    # Overlap prevents losing context at chunk boundaries — like Venn diagrams.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    return splitter.split_documents(docs)


def ingest():
    docs = load_pdfs(DATA_PATH)
    if not docs:
        print("No PDFs found in ./data — add some and retry.")
        sys.exit(1)

    chunks = split_documents(docs)
    print(f"Split into {len(chunks)} chunks from {len(docs)} pages.")

    embeddings = OllamaEmbeddings(model=EMBED_MODEL)

    # Chroma.from_documents embeds every chunk and persists to disk.
    # On re-runs you'd want to check for duplicates — for now, wipe and reingest.
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH,
        collection_name="documents",
    )
    print(f"Stored {db._collection.count()} chunks in ChromaDB at {CHROMA_PATH}")


if __name__ == "__main__":
    ingest()