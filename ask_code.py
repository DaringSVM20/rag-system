import sys
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document

CHROMA_PATH = "./chroma_db"
EMBED_MODEL = "nomic-embed-text"
LLM_MODEL   = "phi3:mini"

PROMPT_TEMPLATE = """
You are a senior engineer helping a developer understand a codebase.
Answer using only the code context provided. Always mention the source file.
If the answer isn't in the context, say so.

Context:
{context}

Question: {question}

Answer:"""


def format_docs(docs):
    return "\n\n---\n\n".join(
        f"# {doc.metadata.get('source', 'unknown')}\n{doc.page_content}"
        for doc in docs
    )


def _get_retriever(collection_name: str, k: int):
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)
    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name=collection_name,
    )
    return db.as_retriever(search_kwargs={"k": k})


def get_sources(question: str, collection_name: str = "codebase", k: int = 5) -> list[Document]:
    return _get_retriever(collection_name, k).invoke(question)


def build_chain(collection_name: str = "codebase", temperature: float = 0.0, k: int = 5):
    retriever = _get_retriever(collection_name, k)
    llm = ChatOllama(model=LLM_MODEL, temperature=temperature)
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    return (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )


if __name__ == "__main__":
    question = " ".join(sys.argv[1:])
    if not question:
        print("Usage: uv run python ask_code.py \"how does auth work?\"")
        sys.exit(1)
    print(f"\nQ: {question}\n")
    print(build_chain().invoke(question))