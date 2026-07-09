import sys
from pathlib import Path

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

CHROMA_PATH = "./chroma_db"
EMBED_MODEL = "nomic-embed-text"


def load_pdfs(data_dir: str) -> list:
    docs = []
    for pdf_path in Path(data_dir).glob("*.pdf"):
        loader = PyMuPDFLoader(str(pdf_path))
        docs.extend(loader.load())
    return docs


def split_documents(docs: list) -> list:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    return splitter.split_documents(docs)


def ingest(collection_name: str = "documents"):
    docs = load_pdfs("./data")
    if not docs:
        print("No PDFs found in ./data")
        sys.exit(1)

    chunks = split_documents(docs)
    print(f"Split into {len(chunks)} chunks.")

    embeddings = OllamaEmbeddings(model=EMBED_MODEL)
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH,
        collection_name=collection_name,
    )
    print(f"Stored {db._collection.count()} chunks in '{collection_name}'.")


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "documents"
    ingest(name)