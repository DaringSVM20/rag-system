# retrieve.py
# Loads ChromaDB, retrieves relevant chunks, sends to local LLM.

from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

CHROMA_PATH = "./chroma_db"
EMBED_MODEL = "nomic-embed-text"
LLM_MODEL = "phi3:mini"

PROMPT_TEMPLATE = """
You are an assistant answering questions based only on the provided context.
If the context doesn't contain the answer, say so — don't make things up.

Context:
{context}

Question: {question}

Answer:"""


def format_docs(docs: list) -> str:
    # Joins retrieved chunks into one string block for the prompt.
    return "\n\n---\n\n".join(doc.page_content for doc in docs)


def build_chain():
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)
    db = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name="documents",
    )

    # k=4: retrieve top 4 most similar chunks. Tune up for broader context,
    # down for precision (and fewer hallucination opportunities).
    retriever = db.as_retriever(search_kwargs={"k": 4})

    llm = ChatOllama(model=LLM_MODEL, temperature=0)
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

    # LangChain Expression Language (LCEL) chain:
    # question → retriever fetches docs → format → into prompt → LLM → parse
    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain


def ask(question: str) -> str:
    chain = build_chain()
    return chain.invoke(question)


if __name__ == "__main__":
    import sys
    question = " ".join(sys.argv[1:]) or "Summarize the main topics in these documents."
    print(f"\nQ: {question}\n")
    print(ask(question))