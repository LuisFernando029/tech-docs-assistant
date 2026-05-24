# 🤖 Guia Completo — Assistente de Documentação Técnica (RAG + LangChain)

> **Tema 9 — Python Software Foundation Docs + MongoDB Docs**  
> Trabalho Prático de PLN — Prof. Vagner Macedo

---

## 📋 Visão Geral do Projeto

O objetivo é construir um sistema RAG (Retrieval-Augmented Generation) que responde perguntas técnicas sobre Python e MongoDB em linguagem natural, retornando respostas contextualizadas com trechos das documentações oficiais — incluindo **code snippets automáticos**.

**Stack principal:**
- LangChain (pipeline RAG)
- ChromaDB (vector store)
- Sentence Transformers (embeddings locais, sem custo de API)
- Streamlit (interface web)
- BeautifulSoup4 (scraping das docs)

---

## 🗂️ Estrutura de Pastas do Projeto

```
rag-docs-assistant/
│
├── .env                        # Chaves de API (se usar OpenAI)
├── requirements.txt
├── README.md
│
├── ingestion/
│   ├── scraper_python_docs.py  # Coleta docs do Python
│   ├── scraper_mongo_docs.py   # Coleta docs do MongoDB
│   └── ingest_pipeline.py      # Orquestra ingestão completa
│
├── rag/
│   ├── embeddings.py           # Configuração dos embeddings
│   ├── vectorstore.py          # Criação/carregamento do ChromaDB
│   ├── retriever.py            # Configuração do retriever
│   └── chain.py                # Chain RAG principal
│
├── app/
│   └── streamlit_app.py        # Interface web
│
├── data/
│   └── chroma_db/              # Banco vetorial persistido (gerado)
│
└── tests/
    └── test_queries.py         # Testes de perguntas e respostas
```

---

## 🔢 Etapas do Projeto (do começo ao fim)

---

### ETAPA 1 — Configuração do Ambiente

**1.1 — Criar o arquivo `.env`**

```env
# Se for usar OpenAI (opcional)
OPENAI_API_KEY=sua_chave_aqui

# Se for usar outro LLM via API
# GROQ_API_KEY=...
```

**1.2 — Criar o `requirements.txt`** (subconjunto do que você já tem instalado, para documentar):

```
langchain
langchain-core
chromadb
sentence-transformers
beautifulsoup4
streamlit
python-dotenv
requests
```

**1.3 — Verificar instalações críticas**

```python
# Rode este script para checar se tudo está ok
import langchain, chromadb, sentence_transformers, streamlit, bs4
print("Todas as dependências OK!")
```

---

### ETAPA 2 — Coleta de Dados (Scraping / Ingestão)

O objetivo desta etapa é **baixar o conteúdo das documentações** e transformá-los em texto puro para processamento.

#### 2.1 — `ingestion/scraper_python_docs.py`

```python
import requests
from bs4 import BeautifulSoup
from langchain.schema import Document

# URLs relevantes da documentação oficial do Python
PYTHON_DOC_URLS = [
    "https://docs.python.org/3/library/functions.html",
    "https://docs.python.org/3/library/stdtypes.html",
    "https://docs.python.org/3/library/os.html",
    "https://docs.python.org/3/library/pathlib.html",
    "https://docs.python.org/3/library/re.html",
    "https://docs.python.org/3/library/collections.html",
    "https://docs.python.org/3/tutorial/index.html",
    # Adicione mais URLs conforme necessário
]

def scrape_python_docs(urls: list[str]) -> list[Document]:
    documents = []
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove menus, scripts, estilos
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            
            # Foca no conteúdo principal
            main = soup.find("div", {"class": "body"}) or soup.find("main") or soup.body
            text = main.get_text(separator="\n", strip=True)
            
            documents.append(Document(
                page_content=text,
                metadata={"source": url, "base": "Python Docs"}
            ))
            print(f"✅ Coletado: {url}")
        except Exception as e:
            print(f"❌ Erro em {url}: {e}")
    
    return documents

if __name__ == "__main__":
    docs = scrape_python_docs(PYTHON_DOC_URLS)
    print(f"\nTotal de documentos Python coletados: {len(docs)}")
```

#### 2.2 — `ingestion/scraper_mongo_docs.py`

```python
import requests
from bs4 import BeautifulSoup
from langchain.schema import Document

MONGO_DOC_URLS = [
    "https://www.mongodb.com/docs/manual/introduction/",
    "https://www.mongodb.com/docs/manual/crud/",
    "https://www.mongodb.com/docs/manual/aggregation/",
    "https://www.mongodb.com/docs/manual/indexes/",
    "https://www.mongodb.com/docs/drivers/python/current/",
    # Adicione mais URLs conforme necessário
]

def scrape_mongo_docs(urls: list[str]) -> list[Document]:
    documents = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for url in urls:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            
            for tag in soup(["script", "style", "nav", "footer"]):
                tag.decompose()
            
            main = soup.find("main") or soup.find("article") or soup.body
            text = main.get_text(separator="\n", strip=True)
            
            documents.append(Document(
                page_content=text,
                metadata={"source": url, "base": "MongoDB Docs"}
            ))
            print(f"✅ Coletado: {url}")
        except Exception as e:
            print(f"❌ Erro em {url}: {e}")
    
    return documents
```

**💡 Dica:** Se o scraping de algum site bloquear, você pode baixar as páginas manualmente como `.html` e fazer parse local.

---

### ETAPA 3 — Pré-processamento e Chunking

Depois de coletar os textos, é necessário **dividi-los em pedaços menores** (chunks) para que o sistema possa recuperar trechos relevantes com precisão.

#### 3.1 — `ingestion/ingest_pipeline.py`

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from scraper_python_docs import scrape_python_docs, PYTHON_DOC_URLS
from scraper_mongo_docs import scrape_mongo_docs, MONGO_DOC_URLS

def load_and_chunk_all():
    print("📥 Coletando documentação Python...")
    python_docs = scrape_python_docs(PYTHON_DOC_URLS)
    
    print("\n📥 Coletando documentação MongoDB...")
    mongo_docs = scrape_mongo_docs(MONGO_DOC_URLS)
    
    all_docs = python_docs + mongo_docs
    print(f"\n📄 Total de documentos brutos: {len(all_docs)}")
    
    # Splitter: divide em chunks de ~800 chars com sobreposição de 100
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " "]
    )
    
    chunks = splitter.split_documents(all_docs)
    print(f"✂️  Total de chunks gerados: {len(chunks)}")
    
    return chunks

if __name__ == "__main__":
    chunks = load_and_chunk_all()
```

**Por que chunk_size=800?** Documentações técnicas têm parágrafos densos. 800 caracteres é um bom equilíbrio entre contexto e precisão. Você pode experimentar entre 500 e 1200.

---

### ETAPA 4 — Vetorização (Embeddings)

Esta etapa transforma os chunks de texto em **vetores numéricos** que representam o significado semântico do conteúdo.

#### 4.1 — `rag/embeddings.py`

```python
from langchain_community.embeddings import HuggingFaceEmbeddings

def get_embeddings():
    """
    Usa sentence-transformers localmente (sem custo de API).
    O modelo 'all-MiniLM-L6-v2' é leve e funciona bem para inglês
    (as docs do Python e MongoDB são em inglês).
    """
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"},  # Troque para "cuda" se tiver GPU
        encode_kwargs={"normalize_embeddings": True}
    )
    return embeddings
```

**Alternativa:** Se as perguntas serão predominantemente em **português**, use `"sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"` que suporta múltiplos idiomas.

---

### ETAPA 5 — Armazenamento Vetorial (ChromaDB)

Os embeddings gerados são armazenados no ChromaDB, que permite buscas por similaridade eficientes.

#### 5.1 — `rag/vectorstore.py`

```python
import os
from langchain_community.vectorstores import Chroma
from rag.embeddings import get_embeddings

CHROMA_PATH = "./data/chroma_db"

def build_vectorstore(chunks):
    """Cria o banco vetorial a partir dos chunks. Executar apenas uma vez."""
    print("🧠 Gerando embeddings e construindo ChromaDB...")
    embeddings = get_embeddings()
    
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    print(f"✅ ChromaDB salvo em '{CHROMA_PATH}' com {vectorstore._collection.count()} vetores.")
    return vectorstore


def load_vectorstore():
    """Carrega um banco vetorial já existente."""
    if not os.path.exists(CHROMA_PATH):
        raise FileNotFoundError(
            f"ChromaDB não encontrado em '{CHROMA_PATH}'. "
            "Execute primeiro o script de ingestão."
        )
    embeddings = get_embeddings()
    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )
    print(f"✅ ChromaDB carregado: {vectorstore._collection.count()} vetores.")
    return vectorstore
```

---

### ETAPA 6 — Retriever (Mecanismo de Busca)

O retriever é responsável por **buscar os chunks mais relevantes** para uma pergunta.

#### 6.1 — `rag/retriever.py`

```python
def get_retriever(vectorstore, k=5):
    """
    k=5: retorna os 5 chunks mais relevantes por pergunta.
    search_type="mmr": Maximum Marginal Relevance — evita chunks repetitivos.
    """
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": 15}
    )
    return retriever
```

---

### ETAPA 7 — Chain RAG (Geração de Resposta)

Esta é a peça central: combina os documentos recuperados com um LLM para gerar a resposta final.

#### 7.1 — `rag/chain.py`

```python
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from rag.retriever import get_retriever

# Prompt customizado para um assistente de documentação técnica
PROMPT_TEMPLATE = """Você é um assistente técnico especializado em Python e MongoDB.
Use APENAS os trechos de documentação abaixo para responder à pergunta.
Se a resposta incluir código, formate-o em blocos de código Python ou JavaScript.
Se não souber a resposta com base no contexto, diga "Não encontrei essa informação na documentação disponível."

Contexto da documentação:
{context}

Pergunta: {question}

Resposta técnica (inclua exemplos de código quando relevante):"""

def get_rag_chain(vectorstore, llm):
    retriever = get_retriever(vectorstore)
    
    prompt = PromptTemplate(
        template=PROMPT_TEMPLATE,
        input_variables=["context", "question"]
    )
    
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )
    return chain
```

#### 7.2 — Escolha do LLM

Você tem algumas opções dependendo do que preferir:

**Opção A — OpenAI (paga, melhor qualidade):**
```python
from langchain_openai import ChatOpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
```

**Opção B — Groq (gratuito com limite generoso):**
```python
from langchain_groq import ChatGroq
llm = ChatGroq(model="llama3-8b-8192", temperature=0)
# Instalar: pip install langchain-groq
```

**Opção C — Ollama (100% local, sem API):**
```python
from langchain_community.llms import Ollama
llm = Ollama(model="llama3")
# Instalar Ollama: https://ollama.com/ e rodar: ollama pull llama3
```

**Recomendação:** Use **Groq** (gratuito) ou **Ollama** (local) para não ter custos.

---

### ETAPA 8 — Interface Web com Streamlit

#### 8.1 — `app/streamlit_app.py`

```python
import streamlit as st
from rag.vectorstore import load_vectorstore
from rag.chain import get_rag_chain

# --- Configuração da página ---
st.set_page_config(
    page_title="Assistente de Docs Técnicas",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Assistente de Documentação Técnica")
st.markdown("Tire dúvidas sobre **Python** e **MongoDB** com base nas documentações oficiais.")

# --- LLM (escolha um) ---
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

from langchain_community.llms import Ollama
llm = Ollama(model="llama3")

# --- Carregamento (com cache para não recarregar a cada pergunta) ---
@st.cache_resource
def init_chain():
    vectorstore = load_vectorstore()
    chain = get_rag_chain(vectorstore, llm)
    return chain

chain = init_chain()

# --- Interface de perguntas ---
st.divider()

# Exemplos de perguntas
with st.expander("💡 Exemplos de perguntas"):
    st.markdown("""
    - Como usar a função `map()` em Python?
    - Como fazer uma query de busca no MongoDB?
    - Como usar `pathlib` para manipular arquivos?
    - Como criar um índice no MongoDB?
    - Como usar list comprehension em Python?
    - Como funciona o aggregation pipeline do MongoDB?
    """)

# Input do usuário
query = st.text_input(
    "🔍 Digite sua pergunta técnica:",
    placeholder="Ex: Como usar a função enumerate() em Python?"
)

if st.button("Perguntar", type="primary") and query:
    with st.spinner("Buscando na documentação..."):
        result = chain({"query": query})
    
    st.markdown("### 📝 Resposta")
    st.markdown(result["result"])
    
    # Exibir fontes utilizadas
    st.divider()
    st.markdown("### 📌 Fontes Consultadas")
    sources = result.get("source_documents", [])
    for i, doc in enumerate(sources, 1):
        with st.expander(f"Fonte {i}: {doc.metadata.get('source', 'Desconhecida')}"):
            st.text(doc.page_content[:500] + "...")

# Histórico de perguntas
if "history" not in st.session_state:
    st.session_state.history = []

if query and st.button:
    st.session_state.history.append(query)

if st.session_state.history:
    st.divider()
    st.markdown("### 🕘 Histórico de Perguntas")
    for q in reversed(st.session_state.history[-5:]):
        st.text(f"• {q}")
```

---

### ETAPA 9 — Script de Execução Inicial (`build_db.py`)

Crie este script na raiz para rodar **uma única vez** e construir o banco vetorial:

```python
# build_db.py — Execute apenas uma vez para popular o ChromaDB
import sys
sys.path.append(".")

from ingestion.ingest_pipeline import load_and_chunk_all
from rag.vectorstore import build_vectorstore

if __name__ == "__main__":
    print("🚀 Iniciando pipeline de ingestão...")
    chunks = load_and_chunk_all()
    vectorstore = build_vectorstore(chunks)
    print("\n🎉 Base vetorial construída com sucesso! Agora rode o Streamlit.")
    print("   streamlit run app/streamlit_app.py")
```

---

### ETAPA 10 — README.md do Projeto

Crie um `README.md` para a entrega:

```markdown
# Assistente de Documentação Técnica — RAG com LangChain

Sistema RAG para consulta inteligente das documentações do Python e MongoDB.

## Como executar

### 1. Instalar dependências
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 2. Configurar variáveis de ambiente
Copie `.env.example` para `.env` e preencha as chaves necessárias.

### 3. Construir a base vetorial (apenas uma vez)
\`\`\`bash
python build_db.py
\`\`\`

### 4. Iniciar a interface web
\`\`\`bash
streamlit run app/streamlit_app.py
\`\`\`

## Exemplos de perguntas
- "Como usar a função `zip()` em Python?"
- "Como fazer uma query com filtros no MongoDB?"
- "Como funciona o decorador `@property`?"

## Arquitetura
Scraping → Chunking → Embeddings (MiniLM) → ChromaDB → Retriever (MMR) → LLM → Streamlit
```

---

## 🧪 Etapa 11 — Testes e Validação

Crie um arquivo `tests/test_queries.py` para registrar exemplos de perguntas e respostas para o relatório:

```python
# tests/test_queries.py
import sys
sys.path.append(".")

from rag.vectorstore import load_vectorstore
from rag.chain import get_rag_chain

TEST_QUERIES = [
    "Como usar a função map() em Python?",
    "Como usar enumerate() em Python?",
    "Como inserir documentos no MongoDB?",
    "Como criar um índice no MongoDB?",
    "Como usar list comprehension em Python?",
    "Como fazer uma busca com filtros no MongoDB?",
]

if __name__ == "__main__":
    # Configure seu LLM aqui
    from langchain_community.llms import Ollama
    llm = Ollama(model="llama3")
    
    vectorstore = load_vectorstore()
    chain = get_rag_chain(vectorstore, llm)
    
    for query in TEST_QUERIES:
        print(f"\n{'='*60}")
        print(f"PERGUNTA: {query}")
        result = chain({"query": query})
        print(f"RESPOSTA:\n{result['result']}")
        print(f"\nFONTES: {[d.metadata['source'] for d in result['source_documents']]}")
```

---

## 📊 Ordem de Execução (Resumo Final)

```
1. Configurar .env com chaves de API (se necessário)
2. Verificar dependências instaladas
3. Implementar scrapers (scraper_python_docs.py e scraper_mongo_docs.py)
4. Implementar o pipeline de ingestão (ingest_pipeline.py)
5. Implementar embeddings (rag/embeddings.py)
6. Implementar vectorstore (rag/vectorstore.py)
7. Implementar retriever (rag/retriever.py)
8. Implementar chain RAG (rag/chain.py)
9. Implementar interface Streamlit (app/streamlit_app.py)
10. Rodar build_db.py → constrói o ChromaDB
11. Rodar streamlit run app/streamlit_app.py → testa o sistema
12. Rodar tests/test_queries.py → coleta exemplos para o relatório
13. Gravar vídeo de demonstração
14. Escrever relatório técnico com os resultados
```

---

## ⚠️ Armadilhas Comuns e Como Evitar

| Problema | Solução |
|----------|---------|
| Scraping bloqueado por rate limiting | Adicione `time.sleep(1)` entre requisições |
| ChromaDB lento na primeira vez | Normal — geração de embeddings é demorada |
| Resposta fora de contexto | Ajuste o `chunk_size` ou o `k` do retriever |
| Imports quebrados | Sempre rode scripts da pasta raiz do projeto |
| LLM sem API key | Use Ollama (local) ou Groq (gratuito) |

---

## 📄 Estrutura do Relatório Técnico

1. **Introdução** — O que é RAG e por que é útil para documentações técnicas
2. **Objetivo** — O que o assistente resolve (pesquisa de funções, code snippets)
3. **Base de Dados** — Python Docs + MongoDB Docs, justificativa da escolha
4. **Metodologia** — Descrever cada etapa do pipeline (ingestão → geração)
5. **Resultados** — Screenshots + exemplos de perguntas e respostas do `test_queries.py`
6. **Conclusão** — Limitações encontradas e possíveis melhorias

---

*Guia gerado para o Trabalho Prático de PLN — Sistema RAG com LangChain*
