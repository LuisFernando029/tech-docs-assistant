"""
chain.py - Compatível com langchain >= 1.0 / langchain-core
"""

import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

CHROMA_PATH = "vectorstore"

SYSTEM_PROMPT = """Você é um assistente técnico especializado em Python e MongoDB.
Use os trechos de documentação abaixo para responder à pergunta do usuário.
Sempre que relevante, inclua exemplos de código.
Se a resposta não estiver nos documentos fornecidos, diga que não encontrou a informação na base.

Documentação relevante:
{context}

Pergunta: {question}"""


def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
    )


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def build_chain():
    if not os.getenv("GROQ_API_KEY"):
        raise EnvironmentError("GROQ_API_KEY não encontrada. Defina no arquivo .env")

    vectorstore = load_vectorstore()
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5},
    )

    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.2)
    prompt = ChatPromptTemplate.from_template(SYSTEM_PROMPT)

    # Salva os docs recuperados para retornar junto com a resposta
    retrieved_docs = {}

    def retrieve_and_store(question):
        docs = retriever.invoke(question)
        retrieved_docs["docs"] = docs
        return {"context": format_docs(docs), "question": question}

    chain = (
        RunnableLambda(retrieve_and_store)
        | prompt
        | llm
        | StrOutputParser()
    )

    class RAGChain:
        def invoke(self, question: str):
            answer = chain.invoke(question)
            return {
                "answer": answer,
                "source_documents": retrieved_docs.get("docs", []),
            }

    return RAGChain()