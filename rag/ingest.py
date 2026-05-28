"""
ingest.py
Carrega os docs do Python e MongoDB, faz chunking e salva no ChromaDB.
"""

from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import shutil
import os

# ─── URLs da base de conhecimento ────────────────────────────────────────────
URLS = [
    # ── Python: Built-ins e tipos ──────────────────────────────────────────
    "https://docs.python.org/3/library/functions.html",       # funções built-in (map, filter, zip, enumerate...)
    "https://docs.python.org/3/library/stdtypes.html",        # tipos padrão (str, list, dict, set...)
    "https://docs.python.org/3/library/string.html",          # string — format, templates
    "https://docs.python.org/3/library/re.html",              # regex
    "https://docs.python.org/3/library/datetime.html",        # datas e horas
    "https://docs.python.org/3/library/collections.html",     # Counter, defaultdict, deque, namedtuple
    "https://docs.python.org/3/library/itertools.html",       # itertools — chain, product, groupby
    "https://docs.python.org/3/library/functools.html",       # functools — reduce, lru_cache, partial
    "https://docs.python.org/3/library/pathlib.html",         # pathlib — manipulação de arquivos
    "https://docs.python.org/3/library/os.html",              # os — sistema operacional
    "https://docs.python.org/3/library/json.html",            # json — serialização
    "https://docs.python.org/3/library/typing.html",          # type hints

    # ── Python: Tutoriais ──────────────────────────────────────────────────
    "https://docs.python.org/3/tutorial/controlflow.html",    # if, for, while, match
    "https://docs.python.org/3/tutorial/datastructures.html", # listas, dicts, sets, comprehensions
    "https://docs.python.org/3/tutorial/errors.html",         # exceções e tratamento de erros
    "https://docs.python.org/3/tutorial/classes.html",        # OOP — classes, herança
    "https://docs.python.org/3/tutorial/modules.html",        # módulos e pacotes
    "https://docs.python.org/3/tutorial/inputoutput.html",    # I/O — leitura/escrita de arquivos
    "https://docs.python.org/3/tutorial/venv.html",           # ambientes virtuais

    # ── Python: Howtos e referências ───────────────────────────────────────
    "https://docs.python.org/3/howto/functional.html",        # programação funcional
    "https://docs.python.org/3/howto/logging.html",           # logging
    "https://docs.python.org/3/howto/sorting.html",           # ordenação — sorted, key, reverse
    "https://docs.python.org/3/reference/expressions.html",   # expressões — lambda, comprehensions
    "https://docs.python.org/3/library/exceptions.html",      # lista completa de exceções

    # ── MongoDB: Manual principal ──────────────────────────────────────────
    "https://www.mongodb.com/docs/manual/introduction/",
    "https://www.mongodb.com/docs/manual/crud/",
    "https://www.mongodb.com/docs/manual/aggregation/",
    "https://www.mongodb.com/docs/manual/indexes/",
    "https://www.mongodb.com/docs/manual/data-modeling/",
    "https://www.mongodb.com/docs/manual/transactions/",
    "https://www.mongodb.com/docs/manual/replication/",
    "https://www.mongodb.com/docs/manual/sharding/",
    "https://www.mongodb.com/docs/manual/security/",

    # ── MongoDB: Operadores de query ───────────────────────────────────────
    "https://www.mongodb.com/docs/manual/reference/operator/query/",
    "https://www.mongodb.com/docs/manual/reference/operator/update/",
    "https://www.mongodb.com/docs/manual/reference/operator/aggregation-pipeline/",

    # ── MongoDB: PyMongo (driver Python) ──────────────────────────────────
    "https://www.mongodb.com/docs/languages/python/pymongo-driver/current/",
    "https://www.mongodb.com/docs/languages/python/pymongo-driver/current/connect/",
    "https://www.mongodb.com/docs/languages/python/pymongo-driver/current/crud/",
    "https://www.mongodb.com/docs/languages/python/pymongo-driver/current/aggregation/",
    "https://www.mongodb.com/docs/languages/python/pymongo-driver/current/indexes/",
]

CHROMA_PATH = "vectorstore"


def load_documents(urls: list[str]):
    print(f"📥 Carregando {len(urls)} páginas...")
    # Carrega em lotes para evitar timeout
    all_docs = []
    batch_size = 8
    for i in range(0, len(urls), batch_size):
        batch = urls[i:i + batch_size]
        print(f"   → Lote {i // batch_size + 1}: {len(batch)} páginas...")
        try:
            loader = WebBaseLoader(batch)
            loader.requests_kwargs = {"timeout": 20}
            docs = loader.load()
            all_docs.extend(docs)
        except Exception as e:
            print(f"   ⚠️  Erro no lote {i // batch_size + 1}: {e}")
    print(f"✅ {len(all_docs)} documentos carregados.")
    return all_docs


def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150,           # overlap maior = melhor contexto entre chunks
        separators=["\n\n", "\n", ".", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    print(f"✂️  {len(chunks)} chunks gerados.")
    return chunks


def build_vectorstore(chunks):
    # Remove o vectorstore antigo para recriar do zero
    if os.path.exists(CHROMA_PATH):
        print(f"🗑️  Removendo vectorstore antigo...")
        shutil.rmtree(CHROMA_PATH)

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
    docs   = load_documents(URLS)
    chunks = split_documents(docs)
    build_vectorstore(chunks)
    print(f"\n🎉 Ingestão concluída! {len(chunks)} chunks indexados.")
    print("   Agora rode: streamlit run app.py")