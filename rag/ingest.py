# rag\ingest.py

"""
ingest.py
Carrega os docs do Python e MongoDB, faz chunking e salva no ChromaDB.
Execute este arquivo UMA VEZ (ou quando quiser atualizar a base).
"""

from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# ─── URLs da base de conhecimento ───────────────────────────────────────────
URLS = [
    # Python docs
    "https://docs.python.org/3/library/functions.html",
    "https://docs.python.org/3/library/stdtypes.html",
    "https://docs.python.org/3/tutorial/controlflow.html",
    "https://docs.python.org/3/tutorial/datastructures.html",
    "https://docs.python.org/3/tutorial/errors.html",
    "https://docs.python.org/3/tutorial/classes.html",
    # MongoDB docs
    "https://www.mongodb.com/docs/manual/introduction/",
    "https://www.mongodb.com/docs/manual/crud/",
    "https://www.mongodb.com/docs/manual/aggregation/",
    "https://www.mongodb.com/docs/manual/indexes/",
    "https://www.mongodb.com/docs/languages/python/pymongo-driver/current/",
]

CHROMA_PATH = "vectorstore"  # pasta onde o índice será salvo


def load_documents(urls: list[str]):
    print(f"📥 Carregando {len(urls)} páginas...")
    loader = WebBaseLoader(urls)
    docs = loader.load()
    print(f"✅ {len(docs)} documentos carregados.")
    return docs


def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    print(f"✂️  {len(chunks)} chunks gerados.")
    return chunks


def build_vectorstore(chunks):
    print("🔢 Gerando embeddings e salvando no ChromaDB...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH,
    )
    print(f"✅ Vectorstore salvo em '{CHROMA_PATH}'.")
    return vectorstore


if __name__ == "__main__":
    docs = load_documents(URLS)
    chunks = split_documents(docs)
    build_vectorstore(chunks)
    print("\n Ingestão concluída! Agora rode o app.py.")