"""
chain.py - Com histórico de conversa (multi-turn)
"""

import os
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import HumanMessage, AIMessage

CHROMA_PATH = "vectorstore"

# Prompt que recebe histórico + contexto + pergunta atual
SYSTEM_PROMPT = """Você é um assistente técnico especializado em Python e MongoDB.
Use os trechos de documentação abaixo para responder à pergunta do usuário.
Sempre que relevante, inclua exemplos de código em blocos ```python```.
Se a resposta não estiver nos documentos fornecidos, diga que não encontrou a informação na base.
Seja direto e objetivo.

Documentação relevante:
{context}"""

# Prompt auxiliar: reformula a pergunta levando em conta o histórico
CONDENSE_PROMPT = """Dado o histórico de conversa abaixo e a pergunta mais recente do usuário,
reformule a pergunta para ser autocontida (sem depender do histórico).
Se a pergunta já for clara, retorne ela exatamente como está.

Histórico:
{chat_history}

Pergunta: {question}
Pergunta reformulada:"""


def load_vectorstore():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
    )


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def format_history(messages: list) -> str:
    """Converte lista de mensagens em texto para o prompt de condensação."""
    lines = []
    for m in messages:
        role = "Usuário" if isinstance(m, HumanMessage) else "Assistente"
        lines.append(f"{role}: {m.content}")
    return "\n".join(lines)


def build_chain():
    if not os.getenv("GROQ_API_KEY"):
        raise EnvironmentError("GROQ_API_KEY não encontrada. Defina no arquivo .env")

    vectorstore = load_vectorstore()
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5},
    )

    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.2)

    # Prompt principal com suporte a histórico
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ])

    # Prompt para reformular a pergunta com base no histórico
    condense_prompt = ChatPromptTemplate.from_template(CONDENSE_PROMPT)

    retrieved_docs = {}

    def retrieve_with_history(inputs: dict):
        question     = inputs["question"]
        chat_history = inputs.get("chat_history", [])

        # Se há histórico, reformula a pergunta para ser autocontida
        if chat_history:
            history_text = format_history(chat_history)
            condensed = (condense_prompt | llm | StrOutputParser()).invoke({
                "chat_history": history_text,
                "question": question,
            })
        else:
            condensed = question

        docs = retriever.invoke(condensed)
        retrieved_docs["docs"] = docs
        return {
            "context":      format_docs(docs),
            "question":     question,
            "chat_history": chat_history,
        }

    chain = (
        RunnableLambda(retrieve_with_history)
        | prompt
        | llm
        | StrOutputParser()
    )

    class RAGChain:
        def invoke(self, question: str, chat_history: list = None):
            answer = chain.invoke({
                "question":     question,
                "chat_history": chat_history or [],
            })
            return {
                "answer":           answer,
                "source_documents": retrieved_docs.get("docs", []),
            }

    return RAGChain()