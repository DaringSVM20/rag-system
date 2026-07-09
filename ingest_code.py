import sys
from pathlib import Path
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

CHROMA_PATH = "./chroma_db"
EMBED_MODEL = "nomic-embed-text"

LANGUAGE_MAP = {
    ".py":   Language.PYTHON,
    ".js":   Language.JS,
    ".ts":   Language.TS,
    ".jsx":  Language.JS,
    ".tsx":  Language.TS,
    ".md":   Language.MARKDOWN,
    ".html": Language.HTML,
    ".cpp":  Language.CPP,
    ".c":    Language.C,
    ".go":   Language.GO,
    ".rs":   Language.RUST,
    ".rb":   Language.RUBY,
    ".java": Language.JAVA,
}

SKIP_DIRS = {".git", ".venv", "node_modules", "__pycache__", "dist", "build", ".next"}


def load_code_files(repo_path: str) -> list[Document]:
    docs = []
    for path in Path(repo_path).rglob("*"):
        if any(skip in path.parts for skip in SKIP_DIRS):
            continue
        if path.suffix not in LANGUAGE_MAP:
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            if not content.strip():
                continue
            docs.append(Document(
                page_content=content,
                metadata={"source": str(path), "language": path.suffix}
            ))
        except Exception as e:
            print(f"Skipped {path}: {e}")
    return docs


def split_documents(docs: list[Document]) -> list[Document]:
    chunks = []
    for doc in docs:
        lang = LANGUAGE_MAP[doc.metadata["language"]]
        splitter = RecursiveCharacterTextSplitter.from_language(
            language=lang,
            chunk_size=800,
            chunk_overlap=100,
        )
        chunks.extend(splitter.split_documents([doc]))
    return chunks


def ingest(repo_path: str, collection_name: str = "codebase"):
    docs = load_code_files(repo_path)
    if not docs:
        print(f"No supported code files found in {repo_path}")
        sys.exit(1)
    print(f"Loaded {len(docs)} files.")

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
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    name = sys.argv[2] if len(sys.argv) > 2 else Path(path).name
    ingest(path, name)