import streamlit as st

#  PAGE CONFIG
st.set_page_config(
    page_title="Tech Docs Assistant",
    page_icon="public/logo.png",
    layout="centered", # Layout centralizado e focado, estilo ChatGPT/Search
    initial_sidebar_state="collapsed",
)

#  CUSTOM CSS (Baseado nas cores e estética da sua Logo)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@400;500;600;700&display=swap');

/* ── Root tokens baseados na Logo ───────────────────────────── */
:root {
    --bg:         #06090e;      /* Preto profundo do fundo da logo */
    --surface:    #121824;      /* Azul escuro sutil para os cards */
    --surface2:   #1b2436;      /* Variação para inputs e hover */
    --border:     #1f2e4d;      /* Borda azulada discreta */
    --accent:     #00d2ff;      /* Azul Neon brilhante (Olhos/Luz do Robô) */
    --accent-grad: linear-gradient(135deg, #00d2ff 0%, #7928ca 100%); /* Gradiente do arco */
    --text:       #e6edf3;
    --muted:      #6e7681;
    --font-mono:  'JetBrains Mono', monospace;
    --font-ui:    'Inter', sans-serif;
}

/* ── Global reset ──────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: var(--font-ui) !important;
}

/* Esconder completamente elementos desnecessários da sidebar */
[data-testid="stSidebar"] {
    display: none;
}

/* ── Header Principal (Inspirado na Logo) ────────────────────── */
.app-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 3rem 0 1.5rem;
    position: relative;
}

.logo-wrapper {
    position: relative;
    width: 100px;
    height: 100px;
    margin-bottom: 1rem;
    display: flex;
    justify-content: center;
    align-items: center;
}

/* Recriação do arco luminoso da logo em CSS */
.logo-wrapper::before {
    content: '';
    position: absolute;
    width: 120px;
    height: 120px;
    border-radius: 50%;
    border: 3px solid transparent;
    background: linear-gradient(var(--bg), var(--bg)) padding-box,
                linear-gradient(135deg, #00d2ff 0%, #9b51e0 100%) border-box;
    mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
    -webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
    -webkit-mask-composite: destination-out;
    mask-composite: exclude;
}

.app-header .logo-emoji {
    font-size: 3rem;
    z-index: 2;
    filter: drop-shadow(0 0 10px rgba(0, 210, 255, 0.5));
}

.app-header h1 {
    font-family: var(--font-ui);
    font-size: 2.2rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    background: linear-gradient(120deg, #fff 40%, var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}

.app-header p {
    color: var(--muted);
    font-size: 1rem;
    margin-top: 0.5rem;
}

/* ── Tags de Fontes de Dados ───────────────────────────────── */
.source-pills {
    display: flex;
    justify-content: center;
    gap: 10px;
    margin-bottom: 2.5rem;
}
.pill {
    font-size: 12px;
    font-family: var(--font-mono);
    padding: 6px 16px;
    border-radius: 30px;
    background: #121824;
    border: 1px solid var(--border);
    color: #fff;
    display: flex;
    align-items: center;
    gap: 6px;
}
.pill-active::before {
    content: '';
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 8px var(--accent);
}

/* ── Container de Inputs e Botões ──────────────────────────── */
[data-testid="stTextInput"] > div > div > input {
    background-color: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 12px !important;
    color: var(--text) !important;
    font-size: 16px !important;
    padding: 16px 20px !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
    transition: all 0.3s ease;
}
[data-testid="stTextInput"] > div > div > input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(0, 210, 255, 0.2), 0 4px 20px rgba(0,0,0,0.3) !important;
}
[data-testid="stTextInput"] label {
    display: none; /* Remove label padrão do streamlit para visual mais limpo */
}

/* Botão de Busca Estilo RAG Moderno */
[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #00b4d8 0%, #0077b6 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #fff !important;
    font-family: var(--font-ui) !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    padding: 12px 28px !important;
    box-shadow: 0 4px 14px rgba(0, 180, 216, 0.3) !important;
    transition: all 0.2s ease;
}
[data-testid="stButton"] > button[kind="primary"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 180, 216, 0.5) !important;
}

/* Botão Secundário (Limpar) */
[data-testid="stButton"] > button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--muted) !important;
    padding: 12px 20px !important;
}
[data-testid="stButton"] > button[kind="secondary"]:hover {
    border-color: var(--text) !important;
    color: var(--text) !important;
}

/* ── Bloco Uniforme de Resposta ────────────────────────────── */
.response-block {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.5rem;
    margin-top: 2rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}
.response-block .block-title {
    font-family: var(--font-mono);
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--accent);
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.response-block .block-title::before {
    content: '●';
    font-size: 10px;
}

/* ── Fontes Consultadas ───────────────────────────────────── */
.source-container {
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border);
}
.source-item {
    background: var(--surface2);
    border-radius: 8px;
    padding: 10px 14px;
    margin-bottom: 8px;
    font-size: 13px;
}
.source-item a {
    color: var(--accent);
    text-decoration: none;
    font-family: var(--font-mono);
}
.source-item a:hover { text-decoration: underline; }

/* ── Sugestões/Exemplos abaixo do input ────────────────────── */
.suggestions-title {
    font-size: 12px;
    color: var(--muted);
    font-family: var(--font-mono);
    margin: 1.5rem 0 0.5rem 2px;
}
div.stButton > button.suggestion-btn {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
    border-radius: 20px !important;
    padding: 6px 14px !important;
    font-size: 13px !important;
    text-align: left !important;
}
div.stButton > button.suggestion-btn:hover {
    border-color: var(--accent) !important;
    background: var(--surface2) !important;
}

/* Código customizado */
code {
    background: #06090e !important;
    color: #ff79c6 !important;
}
</style>
""", unsafe_allow_html=True)


#  MAIN HEADER (Centralizado, baseado na Logo)
st.markdown("""
<div class='app-header'>
    <div class='logo-wrapper'>
        <div class='logo-emoji'>🤖</div>
    </div>
    <h1>Tech Docs Assistant</h1>
    <p>Sua IA para consulta de documentações técnicas em tempo real</p>
</div>
""", unsafe_allow_html=True)

# Fontes ativas centralizadas
st.markdown("""
<div class='source-pills'>
    <span class='pill pill-active'>🐍 Python Docs</span>
    <span class='pill pill-active'>🍃 MongoDB Docs</span>
</div>
""", unsafe_allow_html=True)


#  QUERY INPUT
prefill = st.session_state.pop("prefill", "")
pergunta = st.text_input(
    "Label invisível via CSS",
    value=prefill,
    placeholder="Pergunte qualquer coisa... (Ex: Como usar o aggregation pipeline no MongoDB?)",
    key="query_input",
)

# Botões de Ação alinhados de forma moderna
col_btn, col_clear, _ = st.columns([1.5, 1.2, 5])
with col_btn:
    buscar = st.button("⚡ Buscar Resposta", type="primary", use_container_width=True)
with col_clear:
    if st.button("✕ Limpar", type="secondary", use_container_width=True):
        st.session_state.last_result = None
        st.rerun()


#  SUGESTÕES RÁPIDAS (Substitui os botões feios que ficavam na sidebar)
st.markdown("<div class='suggestions-title'>Sugestões de busca:</div>", unsafe_allow_html=True)

# Grid de botões de sugestão elegantes
sugestoes = [
    "Como usar a função map() em Python?",
    "Como fazer insert no MongoDB?",
    "O que é list comprehension?",
    "Como usar o aggregation pipeline?"
]

col_sug1, col_sug2 = st.columns(2)
with col_sug1:
    if st.button(f"💡 {sugestoes[0]}", key="sug_1", use_container_width=True):
        st.session_state["prefill"] = sugestoes[0]
        st.rerun()
    if st.button(f"💡 {sugestoes[1]}", key="sug_2", use_container_width=True):
        st.session_state["prefill"] = sugestoes[1]
        st.rerun()
with col_sug2:
    if st.button(f"💡 {sugestoes[2]}", key="sug_3", use_container_width=True):
        st.session_state["prefill"] = sugestoes[2]
        st.rerun()
    if st.button(f"💡 {sugestoes[3]}", key="sug_4", use_container_width=True):
        st.session_state["prefill"] = sugestoes[3]
        st.rerun()


#  MOCK RAG PIPELINE
def run_rag(query: str) -> dict:
    return {
        "result": (
            "A função `enumerate()` retorna um objeto enumerado que produz tuplas "
            "contendo um índice e o valor do iterável correspondente.\n\n"
            "É especialmente útil quando você precisa do índice e do valor ao "
            "mesmo tempo dentro de um `for` loop."
        ),
        "snippet": (
            "fruits = ['apple', 'banana', 'cherry']\n\n"
            "for index, fruit in enumerate(fruits):\n"
            "    print(f'{index}: {fruit}')"
        ),
        "source_documents": [
            type("Doc", (), {
                "page_content": "enumerate(iterable, start=0) — Returns an enumerate object...",
                "metadata": {"source": "https://docs.python.org/3/library/functions.html#enumerate", "base": "Python Docs"},
            })(),
        ],
    }


#  EXECUTE QUERY
if buscar and pergunta.strip():
    with st.spinner("Varrendo bases de conhecimento..."):
        result = run_rag(pergunta.strip())
    st.session_state.last_result = {"query": pergunta.strip(), **result}


#  DISPLAY RESULT (Interface limpa em Bloco Único)
if st.session_state.get("last_result"):
    res = st.session_state.last_result
    answer = res.get("result", "")
    snippet = res.get("snippet", "")
    sources = res.get("source_documents", [])

    # Bloco único unificado contendo o output estruturado da IA
    st.markdown("""
    <div class='response-block'>
        <div class='block-title'>Resposta do Assistente</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(answer)

    if snippet:
        st.markdown("<br>", unsafe_allow_html=True)
        st.code(snippet, language="python")

    if sources:
        st.markdown("<div class='source-container'><div style='font-size:12px; color:#6e7681; font-family:JetBrains Mono; margin-bottom:8px;'>FONTES CONSULTADAS:</div></div>", unsafe_allow_html=True)
        for doc in sources:
            url = doc.metadata.get("source", "#")
            base = doc.metadata.get("base", "")
            st.markdown(f"""
            <div class='source-item'>
                🔹 <strong>{base}</strong> — <a href='{url}' target='_blank'>{url}</a>
            </div>
            """, unsafe_allow_html=True)