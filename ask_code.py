import sys
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

CHROMA_PATH = "./chroma_db"
EMBED_MODEL = "nomic-embed-text"
LLM_MODEL = "phi3:mini"

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


def build_chain(collection_name: str = "codebase"):
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)
    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name=collection_name,
    )
    retriever = db.as_retriever(search_kwargs={"k": 5})
    llm = ChatOllama(model=LLM_MODEL, temperature=0)
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain


if __name__ == "__main__":
    question = " ".join(sys.argv[1:])
    if not question:
        print("Usage: uv run python ask_code.py \"how does auth work?\"")
        sys.exit(1)
    print(f"\nQ: {question}\n")
    print(build_chain().invoke(question))