import os
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

st.set_page_config(
    page_title="Tech Docs Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500&family=Syne:wght@600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg:           #0f1117;
    --bg2:          #161b27;
    --surface:      #1e2336;
    --surface2:     #252b3b;
    --border:       rgba(255,255,255,0.08);
    --border-focus: rgba(138,180,248,0.45);
    --accent:       #8ab4f8;
    --accent2:      #c58af9;
    --accent3:      #78d0b3;
    --text:         #e8eaed;
    --text2:        #9aa0ac;
    --text3:        #4e545c;
    --font:         'DM Sans', sans-serif;
    --font-h:       'Syne', sans-serif;
    --font-mono:    'JetBrains Mono', monospace;
}

*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font) !important;
}

.main .block-container {
    max-width: 700px !important;
    margin: 0 auto !important;
    padding: 0 1.25rem 160px !important;
}

[data-testid="stSidebar"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
#MainMenu,
footer,
header {
    display: none !important;
}

/* Hero */
.hero {
    text-align: center;
    padding: 2.5rem 0 1.2rem;
}

.gem-star {
    font-size: 2rem;
    display: block;
    margin-bottom: 0.8rem;
    background: linear-gradient(135deg, #8ab4f8, #c58af9, #78d0b3);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero h1 {
    font-family: var(--font-h);
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    line-height: 1.2;
    margin: 0 0 0.4rem;

    background: linear-gradient(
        135deg,
        #8ab4f8 0%,
        #c58af9 55%,
        #78d0b3 100%
    );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero p {
    color: var(--text2);
    font-size: 0.9rem;
    font-weight: 300;
    margin: 0;
}

/* Badges */
.badges {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin: 0.9rem 0 2rem;
    flex-wrap: wrap;
}

.badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;

    font-size: 11px;
    font-family: var(--font-mono);

    padding: 4px 12px;
    border-radius: 20px;

    border: 1px solid var(--border);
    background: var(--surface);
    color: var(--text2);
}

.bdot {
    width: 5px;
    height: 5px;
    border-radius: 50%;
    background: var(--accent3);
    box-shadow: 0 0 5px var(--accent3);
    flex-shrink: 0;
}

/* Chips */
.chips-label {
    font-size: 10.5px;
    font-family: var(--font-mono);
    color: var(--text3);
    letter-spacing: 0.09em;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}

div[data-testid="stHorizontalBlock"] [data-testid="stButton"] > button {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text2) !important;

    border-radius: 18px !important;
    font-size: 12.5px !important;
    font-family: var(--font) !important;
    font-weight: 400 !important;

    padding: 7px 14px !important;
    width: 100% !important;

    box-shadow: none !important;
    text-align: left !important;
    transform: none !important;

    transition:
        border-color 0.15s,
        color 0.15s !important;
}

div[data-testid="stHorizontalBlock"] [data-testid="stButton"] > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    background: rgba(138,180,248,0.05) !important;
}

/* Chat */
.turn {
    margin-bottom: 1.2rem;
}

.user-row {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 0.85rem;
}

.user-bubble {
    background: var(--surface2);
    border: 1px solid var(--border);

    border-radius: 18px 18px 4px 18px;

    padding: 10px 16px;
    max-width: 75%;

    font-size: 14px;
    color: var(--text);
    line-height: 1.55;

    word-break: break-word;
}

.ai-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 0.5rem;
}

.ai-av {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    flex-shrink: 0;

    background: linear-gradient(135deg, #4285f4, #7c4dff);

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 9px;
    font-weight: 700;
    color: #fff;

    font-family: var(--font-mono);
}

.ai-label {
    font-size: 11px;
    font-family: var(--font-mono);
    color: var(--text3);

    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.ai-content {
    padding-left: 36px;
    animation: fadeUp 0.22s ease;
}

@keyframes fadeUp {
    from {
        opacity: 0;
        transform: translateY(4px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Fontes */
.src-wrap {
    margin-top: 0.8rem;
    padding-top: 0.8rem;
    border-top: 1px solid var(--border);
}

.src-label {
    font-size: 10px;
    font-family: var(--font-mono);
    color: var(--text3);

    letter-spacing: 0.08em;
    text-transform: uppercase;

    margin-bottom: 0.4rem;
}

.src-chip {
    display: inline-flex;
    align-items: center;
    gap: 4px;

    background: var(--surface);
    border: 1px solid var(--border);

    border-radius: 5px;
    padding: 3px 9px;
    margin: 0 4px 4px 0;

    font-size: 11px;
    font-family: var(--font-mono);
    color: var(--text2);

    text-decoration: none;

    transition:
        border-color 0.12s,
        color 0.12s;
}

.src-chip:hover {
    border-color: var(--accent);
    color: var(--accent);
}

.turn-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.2rem 0;
}

/* Loading */
.loading-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    padding: 4rem 0 2rem;
    gap: 1.2rem;
}

.loading-dots {
    display: flex;
    gap: 8px;
    align-items: center;
}

.loading-dots span {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    animation: bounce 1.3s infinite ease-in-out;
}

.loading-dots span:nth-child(1) {
    background: #8ab4f8;
    animation-delay: 0s;
}

.loading-dots span:nth-child(2) {
    background: #c58af9;
    animation-delay: 0.22s;
}

.loading-dots span:nth-child(3) {
    background: #78d0b3;
    animation-delay: 0.44s;
}

@keyframes bounce {
    0%, 80%, 100% {
        transform: scale(0.55);
        opacity: 0.35;
    }

    40% {
        transform: scale(1.1);
        opacity: 1;
    }
}

.loading-text {
    font-size: 13px;
    color: var(--text2);
    font-weight: 300;
    letter-spacing: 0.02em;
}

/* INPUT AJUSTADO */
[data-testid="stTextInput"] {
    width: 100%;
}

[data-testid="stTextInput"] > div {
    width: 100%;
}

[data-testid="stTextInput"] div[data-baseweb="input"] {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 26px !important;

    overflow: hidden !important;

    min-height: 50px !important;

    display: flex !important;
    align-items: center !important;

    padding: 0 6px !important;

    transition:
        border-color 0.2s,
        box-shadow 0.2s !important;
}

[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
    border-color: var(--border-focus) !important;

    box-shadow:
        0 0 0 3px rgba(138,180,248,0.1) !important;

    background: var(--surface2) !important;
}

[data-testid="stTextInput"] input {
    background: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;

    color: var(--text) !important;
    font-family: var(--font) !important;
    font-size: 14.5px !important;

    padding: 0 14px !important;
    height: 48px !important;
}

[data-testid="stTextInput"] input::placeholder {
    color: var(--text3) !important;
}

[data-testid="stTextInput"] label {
    display: none !important;
}

/* Botões */
[data-testid="stButton"] > button {
    font-family: var(--font) !important;
    font-weight: 500 !important;

    border-radius: 22px !important;

    transition: all 0.16s ease !important;
}

[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #4285f4, #7c4dff) !important;
    border: none !important;
    color: #fff !important;

    font-size: 13.5px !important;
    padding: 10px 20px !important;

    box-shadow:
        0 2px 10px rgba(66,133,244,0.3) !important;
}

[data-testid="stButton"] > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;

    box-shadow:
        0 4px 16px rgba(66,133,244,0.45) !important;
}

[data-testid="stButton"] > button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid var(--border) !important;

    color: var(--text2) !important;

    font-size: 13px !important;
    padding: 10px 16px !important;
}

[data-testid="stButton"] > button[kind="secondary"]:hover {
    border-color: rgba(255,255,255,0.18) !important;
    color: var(--text) !important;
}

/* Code */
[data-testid="stCode"] {
    border-radius: 10px !important;
    border: 1px solid var(--border) !important;
    overflow: hidden !important;
    margin-top: 0.6rem !important;
}

[data-testid="stCode"] pre {
    background: #0b0f18 !important;
    font-family: var(--font-mono) !important;
    font-size: 12.5px !important;
    line-height: 1.6 !important;
}

/* Esconde spinner padrão */
[data-testid="stSpinner"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# ── CHAIN ─────────────────────────────────────────────────────────────────────
if not os.getenv("GROQ_API_KEY"):
    st.error("⚠️ GROQ_API_KEY não encontrada.")
    st.stop()

@st.cache_resource(show_spinner="Carregando base de conhecimento...")
def get_chain():
    from rag.chain import build_chain
    return build_chain()

chain = get_chain()

def run_rag(question: str, history: list) -> dict:
    result = chain.invoke(question, chat_history=history)

    answer = result.get("answer", "Sem resposta.")
    source_docs = result.get("source_documents", [])

    snippet = ""

    if "```" in answer:
        parts = answer.split("```")

        code_blocks = [
            p for i, p in enumerate(parts)
            if i % 2 == 1
        ]

        snippet = "\n\n".join(
            b.split("\n", 1)[1] if "\n" in b else b
            for b in code_blocks
        )

        answer = parts[0].strip()

    return {
        "answer": answer,
        "snippet": snippet,
        "source_documents": source_docs,
    }

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "chat_display" not in st.session_state:
    st.session_state.chat_display = []

if "pending_q" not in st.session_state:
    st.session_state.pending_q = None

if "query_input" not in st.session_state:
    st.session_state.query_input = ""

if "clear_input" not in st.session_state:
    st.session_state.clear_input = False

# ── PROCESSA PERGUNTA ─────────────────────────────────────────────────────────
if st.session_state.pending_q:

    question = st.session_state.pending_q
    st.session_state.pending_q = None

    st.markdown("""
    <div class="loading-wrap">
      <div class="loading-dots">
        <span></span>
        <span></span>
        <span></span>
      </div>

      <div class="loading-text">
        Consultando a base de conhecimento...
      </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        result = run_rag(
            question,
            st.session_state.chat_history
        )

        st.session_state.chat_history.append(
            HumanMessage(content=question)
        )

        st.session_state.chat_history.append(
            AIMessage(content=result["answer"])
        )

        st.session_state.chat_display.append({
            "question": question,
            "answer": result["answer"],
            "snippet": result.get("snippet", ""),
            "sources": result.get("source_documents", []),
        })

    except Exception as e:
        st.error(f"Erro: {e}")

    st.rerun()

# ── HERO ──────────────────────────────────────────────────────────────────────
if not st.session_state.chat_display:

    st.markdown("""
    <div class="hero">
      <span class="gem-star">✶</span>

      <h1>Olá, desenvolvedor</h1>

      <p>
        Consulte a documentação do Python e MongoDB com IA
      </p>
    </div>

    <div class="badges">
      <span class="badge">
        <span class="bdot"></span>
        🐍 Python Docs
      </span>

      <span class="badge">
        <span class="bdot"></span>
        🍃 MongoDB Docs
      </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<div class='chips-label'>Sugestões</div>",
        unsafe_allow_html=True
    )

    sugestoes = [
        "Como usar map() em Python?",
        "Insert de documentos no MongoDB",
        "O que é list comprehension?",
        "Aggregation pipeline — como funciona?",
    ]

    col1, col2 = st.columns(2)

    with col1:
        for i in [0, 1]:

            if st.button(
                sugestoes[i],
                key=f"sug_{i}",
                use_container_width=True
            ):

                st.session_state.pending_q = sugestoes[i]
                st.session_state.clear_input = True

                st.rerun()

    with col2:
        for i in [2, 3]:

            if st.button(
                sugestoes[i],
                key=f"sug_{i}",
                use_container_width=True
            ):

                st.session_state.pending_q = sugestoes[i]
                st.session_state.clear_input = True

                st.rerun()

# ── HISTÓRICO ─────────────────────────────────────────────────────────────────
for idx, turn in enumerate(st.session_state.chat_display):

    if idx > 0:
        st.markdown(
            "<hr class='turn-divider'>",
            unsafe_allow_html=True
        )

    st.markdown(f"""
    <div class="turn">

      <div class="user-row">
        <div class="user-bubble">
          {turn['question']}
        </div>
      </div>

      <div class="ai-row">
        <div class="ai-av">AI</div>
        <div class="ai-label">Assistente</div>
      </div>

    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<div class='ai-content'>",
        unsafe_allow_html=True
    )

    st.markdown(turn["answer"])

    if turn.get("snippet"):
        st.code(turn["snippet"], language="python")

    if turn.get("sources"):

        seen = set()

        chips = '<div class="src-wrap"><div class="src-label">Fontes</div>'

        for doc in turn["sources"]:

            url = doc.metadata.get("source", "#")

            if url in seen:
                continue

            seen.add(url)

            icon = "🐍" if "python.org" in url else "🍃"

            p = url.rstrip("/").split("/")
            label = p[-1] if p[-1] else p[-2]

            chips += (
                f'<a class="src-chip" '
                f'href="{url}" '
                f'target="_blank">'
                f'{icon} {label}'
                f'</a>'
            )

        chips += "</div>"

        st.markdown(
            chips,
            unsafe_allow_html=True
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

# ── INPUT ─────────────────────────────────────────────────────────────────────
if st.session_state.clear_input:
    st.session_state.query_input = ""
    st.session_state.clear_input = False

col_input, col_send = st.columns([6, 1])

with col_input:

    pergunta = st.text_input(
        "query",
        placeholder="Pergunte sobre Python ou MongoDB...",
        key="query_input",
        label_visibility="collapsed",
    )

with col_send:

    buscar = st.button(
        "Enviar",
        type="primary",
        use_container_width=True
    )

# ── NOVA CONVERSA ─────────────────────────────────────────────────────────────
if st.session_state.chat_display:

    if st.button(
        "↺  Nova conversa",
        type="secondary",
        use_container_width=True
    ):

        st.session_state.chat_history = []
        st.session_state.chat_display = []

        st.session_state.clear_input = True

        st.rerun()

# ── ENVIA PERGUNTA ────────────────────────────────────────────────────────────
if buscar and pergunta.strip():

    st.session_state.pending_q = pergunta.strip()

    st.session_state.clear_input = True

    st.rerun()