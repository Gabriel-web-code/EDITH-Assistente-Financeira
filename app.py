import os
from datetime import date, datetime

import streamlit as st
from dotenv import load_dotenv
from groq import APIError

import agent
import db
import sessao

load_dotenv()

try:
    if not os.getenv("GROQ_API_KEY") and "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = str(st.secrets["GROQ_API_KEY"])
    if not os.getenv("GROQ_MODEL") and "GROQ_MODEL" in st.secrets:
        agent.MODELO = str(st.secrets["GROQ_MODEL"])
except Exception:
    pass

MESES = [
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
]

ROTULOS = {
    "registrar_gasto": "Registrando lançamento...",
    "listar_gastos": "Consultando lançamentos...",
    "resumo_mensal": "Consultando o resumo do mês...",
    "excluir_gasto": "Excluindo lançamento...",
    "salvar_memoria": "Salvando memória...",
    "pesquisar_web": "Pesquisando na internet...",
    "abrir_pagina": "Lendo página...",
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Inter", "Segoe UI", sans-serif;
    -webkit-font-smoothing: antialiased;
}

.stApp {
    background:
        radial-gradient(1100px 620px at 50% -12%, rgba(78, 78, 86, 0.30) 0%, rgba(0, 0, 0, 0) 62%),
        linear-gradient(180deg, #000000 0%, #0b0b0d 48%, #050506 100%);
    color: #f5f5f7;
}

header[data-testid="stHeader"] {
    background: transparent;
}

#MainMenu, footer {
    visibility: hidden;
}

[data-testid="stAppDeployButton"] {
    display: none !important;
}

.block-container {
    max-width: 1080px;
    padding: 2.5rem 1.5rem 8.5rem 1.5rem;
}

[data-testid="stBottom"] {
    background: linear-gradient(180deg, rgba(5, 5, 6, 0) 0%, #050506 42%, #050506 100%);
}

[data-testid="stBottom"] > div {
    background: transparent;
}

.hero {
    position: relative;
    overflow: hidden;
    background: linear-gradient(135deg, #0b0b0d 0%, #1b1b1e 52%, #2c2c31 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 28px;
    padding: 2.4rem 2.6rem;
    box-shadow: 0 30px 70px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.05);
    margin-bottom: 2rem;
}

.hero::after {
    content: "";
    position: absolute;
    inset: 0;
    background:
        radial-gradient(520px 220px at 88% -18%, rgba(255, 255, 255, 0.14) 0%, rgba(255, 255, 255, 0) 70%),
        radial-gradient(420px 220px at 4% 122%, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0) 70%);
    pointer-events: none;
}

.hero .rotulo {
    position: relative;
    z-index: 1;
    color: #9a9aa0;
    font-size: 0.76rem;
    font-weight: 600;
    letter-spacing: 0.24em;
    text-transform: uppercase;
}

.hero h1 {
    position: relative;
    z-index: 1;
    font-size: 3rem;
    line-height: 1.03;
    font-weight: 700;
    letter-spacing: -0.035em;
    margin: 0.5rem 0 0.75rem 0;
    color: #ffffff;
}

.hero p {
    position: relative;
    z-index: 1;
    font-size: 1.08rem;
    color: #b8b8be;
    margin: 0;
    max-width: 620px;
}

[data-testid="stChatMessage"] {
    background: linear-gradient(135deg, #101012 0%, #1e1e21 55%, #2a2a2f 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 20px;
    padding: 1rem 1.25rem;
    box-shadow: 0 18px 42px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.04);
    margin-bottom: 0.85rem;
    color: #f5f5f7;
}

[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] strong,
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3,
[data-testid="stChatMessage"] h4,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] em,
[data-testid="stChatMessage"] blockquote {
    color: #f5f5f7;
}

[data-testid="stChatMessage"] a {
    color: #ffffff;
    text-decoration: underline;
    text-decoration-color: rgba(255, 255, 255, 0.35);
}

[data-testid="stChatMessage"] code {
    background: rgba(255, 255, 255, 0.09);
    color: #f5f5f7;
    border-radius: 6px;
    padding: 0.1rem 0.35rem;
}

[data-testid="stChatMessage"] pre {
    background: rgba(0, 0, 0, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
}

[data-testid="stChatMessage"] hr {
    border-color: rgba(255, 255, 255, 0.12);
}

[data-testid="stChatMessage"] th,
[data-testid="stChatMessage"] td {
    border-color: rgba(255, 255, 255, 0.14);
    color: #f5f5f7;
}

[data-testid="stChatMessage"] thead tr th {
    background: rgba(255, 255, 255, 0.06);
}

[data-testid="stChatMessage"] tbody tr:nth-child(even) {
    background: rgba(255, 255, 255, 0.03);
}

[data-testid="stChatMessageAvatarAssistant"],
[data-testid="stChatMessageAvatarCustom"] {
    display: none;
}

[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: linear-gradient(135deg, #242428 0%, #323237 55%, #3f3f45 100%);
    border-color: rgba(255, 255, 255, 0.12);
}

[data-testid="stChatInput"] {
    background: #17171a !important;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 18px;
    box-shadow: 0 22px 55px rgba(0, 0, 0, 0.7), inset 0 1px 0 rgba(255, 255, 255, 0.04);
    padding: 0.45rem 0.5rem 0.45rem 0.75rem;
}

[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] div[data-baseweb="textarea"],
[data-testid="stChatInput"] div[data-baseweb="base-input"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
}

[data-testid="stChatInput"] div {
    background-color: transparent !important;
    border-color: transparent !important;
}

[data-testid="stChatInputTextArea"] {
    background: transparent !important;
    color: #f5f5f7 !important;
    font-size: 1rem;
    caret-color: #ffffff;
}

[data-testid="stChatInputTextArea"]::placeholder {
    color: #7c7c82 !important;
}

[data-testid="stChatInputSubmitButton"] {
    background: #f5f5f7 !important;
    border-radius: 12px !important;
    color: #0a0a0c !important;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.45);
}

[data-testid="stChatInputSubmitButton"]:hover {
    background: #ffffff !important;
}

[data-testid="stChatInputSubmitButton"] svg,
[data-testid="stChatInputSubmitButton"] path {
    fill: #0a0a0c !important;
    color: #0a0a0c !important;
}

[data-testid="stChatInputFileUploadButton"],
[data-testid="stChatInputMicButton"] {
    background: transparent !important;
    color: #a1a1a6 !important;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #101013 0%, #08080a 100%);
    border-right: 1px solid rgba(255, 255, 255, 0.07);
}

[data-testid="stSidebar"] .block-container {
    padding-top: 2rem;
}

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #c7c7cc;
}

[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] {
    color: #8e8e93;
}

.marca {
    font-size: 1.35rem;
    font-weight: 700;
    letter-spacing: 0.22em;
    color: #ffffff;
}

.marca-sub {
    color: #8e8e93;
    font-size: 0.85rem;
    margin-top: -0.2rem;
    margin-bottom: 0.5rem;
}

.secao {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #8e8e93;
    margin: 1.3rem 0 0.5rem 0;
}

.cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 0.7rem;
    margin: 0.5rem 0 1.2rem 0;
}

.card {
    background: linear-gradient(140deg, #1c1c20 0%, #141416 55%, #101012 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 0.85rem 0.95rem;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.05);
}

.card span {
    display: block;
    font-size: 0.72rem;
    color: #8e8e93;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.3rem;
}

.card strong {
    display: block;
    font-size: 1.05rem;
    font-weight: 600;
    color: #ffffff;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

[data-testid="stDataFrame"] {
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    overflow: hidden;
    background: #131315;
}

[data-testid="stDataFrame"] * {
    border-color: rgba(255, 255, 255, 0.08) !important;
}

[data-testid="stExpander"] {
    background: linear-gradient(140deg, #17171a 0%, #101012 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    overflow: hidden;
}

[data-testid="stExpander"] summary,
[data-testid="stExpander"] details {
    background: transparent;
    color: #f5f5f7;
}

[data-testid="stExpander"] summary:hover {
    background: rgba(255, 255, 255, 0.04);
}

[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background: #17171a;
    border-radius: 12px;
    border-color: rgba(255, 255, 255, 0.12);
    color: #f5f5f7;
}

[data-testid="stSelectbox"] svg {
    color: #c7c7cc;
}

[data-baseweb="popover"] div[role="listbox"],
[data-baseweb="popover"] ul {
    background: #17171a;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
}

[data-baseweb="popover"] li {
    color: #f5f5f7;
}

[data-baseweb="popover"] li:hover {
    background: rgba(255, 255, 255, 0.08);
}

[data-baseweb="tooltip"],
[data-testid="stTooltipContent"] {
    background: #1c1c1f !important;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    color: #f5f5f7 !important;
}

[data-baseweb="tooltip"] *,
[data-testid="stTooltipContent"] * {
    color: #f5f5f7 !important;
}

.stButton button {
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    background: linear-gradient(180deg, rgba(255, 255, 255, 0.10) 0%, rgba(255, 255, 255, 0.04) 100%);
    color: #f5f5f7;
    font-weight: 500;
    padding: 0.5rem 1.1rem;
    transition: all 0.2s ease;
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.45);
}

.stButton button:hover {
    background: rgba(255, 255, 255, 0.16);
    color: #ffffff;
    border-color: rgba(255, 255, 255, 0.22);
}

.stButton button p {
    color: inherit;
}

.st-key-historico .stButton button {
    background: transparent;
    color: #c7c7cc;
    border: 1px solid transparent;
    box-shadow: none;
    text-align: left;
    justify-content: flex-start;
    font-weight: 400;
    padding: 0.45rem 0.7rem;
    border-radius: 12px;
}

.st-key-historico .stButton button:hover {
    background: rgba(255, 255, 255, 0.07);
    color: #ffffff;
}

.st-key-historico .stButton button[kind="primary"] {
    background-color: transparent;
    background-image: linear-gradient(135deg, rgba(255, 255, 255, 0.16) 0%, rgba(255, 255, 255, 0.07) 100%);
    border-color: rgba(255, 255, 255, 0.16);
    color: #ffffff;
    font-weight: 500;
}

.st-key-historico .stButton button p {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    text-align: left;
    width: 100%;
}

.st-key-acoes .stButton button {
    background: transparent;
    color: #c7c7cc;
    border: 1px solid rgba(255, 255, 255, 0.14);
    box-shadow: none;
}

.st-key-acoes .stButton button:hover {
    background: rgba(255, 255, 255, 0.08);
    color: #ffffff;
}

[data-testid="stSidebar"] h3 {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #8e8e93;
}

[data-testid="stAlert"] {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 14px;
    color: #f5f5f7;
}

[data-testid="stAlert"] p {
    color: #f5f5f7;
}

::-webkit-scrollbar {
    width: 10px;
    height: 10px;
}

::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.18);
    border-radius: 999px;
}

::-webkit-scrollbar-track {
    background: transparent;
}

@media (max-width: 640px) {
    .block-container {
        padding: 1rem 0.9rem 8rem 0.9rem;
    }
    .hero {
        padding: 1.7rem 1.5rem;
        border-radius: 22px;
        margin-bottom: 1.4rem;
    }
    .hero h1 {
        font-size: 2.1rem;
    }
    .hero p {
        font-size: 0.98rem;
    }
    [data-testid="stChatMessage"] {
        padding: 0.85rem 1rem;
        border-radius: 18px;
    }
    [data-testid="stChatInput"] {
        border-radius: 16px;
    }
    .cards {
        grid-template-columns: 1fr 1fr;
    }
}
</style>
"""


def moeda(valor):
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def data_curta(valor):
    try:
        return datetime.fromisoformat(valor).strftime("%d/%m %H:%M")
    except (TypeError, ValueError):
        return ""


st.set_page_config(
    page_title="EDITH",
    layout="wide",
    initial_sidebar_state="expanded",
)

sessao.banco_da_sessao()

st.markdown(CSS, unsafe_allow_html=True)

hoje = date.today()
conversas = db.listar_conversas()
ids = [conversa["id"] for conversa in conversas]

if not ids:
    conversa_id = db.criar_conversa()
    conversas = db.listar_conversas()
    ids = [conversa["id"] for conversa in conversas]
else:
    conversa_id = st.session_state.get("conversa_id")
    if conversa_id not in ids:
        conversa_id = ids[0]

st.session_state.conversa_id = conversa_id
historico = db.carregar_mensagens(conversa_id, 40)

st.markdown(
    """
    <div class="hero">
        <div class="rotulo">EDITH</div>
        <h1>Assistente Financeira</h1>
        <p>Gestão de gastos, memória permanente e análise de mercado em um único ambiente.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not historico:
    with st.chat_message("assistant"):
        st.markdown(
            "Bem-vindo. Sou a EDITH, sua assistente financeira. Posso registrar despesas, "
            "organizar o resumo do mês e acompanhar o mercado. Como posso ajudar?"
        )

for mensagem in historico:
    with st.chat_message(mensagem["role"]):
        st.markdown(mensagem["content"])

pergunta = st.chat_input("Registre um gasto ou pergunte sobre o mercado...")

if pergunta:
    if db.contar_mensagens(conversa_id) == 0:
        db.renomear_conversa(conversa_id, pergunta.strip().replace("\n", " ")[:48])

    db.salvar_mensagem("user", pergunta, conversa_id)

    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.chat_message("assistant"):
        aviso = st.empty()
        aviso.caption("Analisando a solicitação...")
        resposta = None
        try:
            resposta = agent.responder(
                db.carregar_mensagens(conversa_id, 40),
                lambda nome, argumentos: aviso.caption(
                    ROTULOS.get(nome, "Processando...")
                ),
            )
        except APIError as erro:
            if erro.status_code == 401:
                st.error(
                    "Chave de API inválida. Gere uma nova em "
                    "https://console.groq.com/keys e atualize o arquivo .env."
                )
            elif erro.status_code == 429:
                st.error("Limite de requisições atingido. Aguarde alguns segundos.")
            else:
                st.error(f"Erro na API Groq ({erro.status_code}): {erro.message}")
        except Exception as erro:
            st.error(f"Não foi possível concluir a solicitação: {erro}")

        aviso.empty()
        if resposta:
            st.markdown(resposta)

    if resposta:
        db.salvar_mensagem("assistant", resposta, conversa_id)
        st.rerun()

with st.sidebar:
    st.markdown('<div class="marca">EDITH</div>', unsafe_allow_html=True)
    st.markdown('<div class="marca-sub">Painel financeiro</div>', unsafe_allow_html=True)
    st.caption("Sessão privada: seus lançamentos, memórias e conversas ficam apenas nesta aba.")

    st.markdown('<div class="secao">Histórico</div>', unsafe_allow_html=True)

    with st.container(key="nova"):
        if st.button("Nova conversa", width="stretch"):
            vazia = db.conversa_vazia()
            st.session_state.conversa_id = vazia if vazia else db.criar_conversa()
            st.rerun()

    with st.container(key="historico", height=220):
        visiveis = [
            conversa
            for conversa in conversas
            if conversa["total"] > 0 or conversa["id"] == conversa_id
        ]
        for conversa in visiveis:
            ativa = conversa["id"] == conversa_id
            if st.button(
                conversa["titulo"] or "Nova conversa",
                key=f"conversa_{conversa['id']}",
                type="primary" if ativa else "secondary",
                width="stretch",
                help=f"Atualizada em {data_curta(conversa['atualizado_em'])}",
            ):
                st.session_state.conversa_id = conversa["id"]
                st.rerun()

    st.markdown('<div class="secao">Painel financeiro</div>', unsafe_allow_html=True)

    mes_nome = st.selectbox("Mês", MESES, index=hoje.month - 1)
    mes = MESES.index(mes_nome) + 1
    anos = [hoje.year - 2, hoje.year - 1, hoje.year, hoje.year + 1]
    ano = st.selectbox("Ano", anos, index=anos.index(hoje.year))

    resumo = db.resumo_mensal(mes, ano)
    categorias = list(resumo["por_categoria"].items())
    maior_categoria = categorias[0][0] if categorias else "Sem lançamentos"

    st.markdown(
        f"""
        <div class="cards">
            <div class="card"><span>Total do mês</span><strong>{moeda(resumo['total'])}</strong></div>
            <div class="card"><span>Lançamentos</span><strong>{resumo['quantidade']}</strong></div>
            <div class="card"><span>Maior categoria</span><strong>{maior_categoria}</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if resumo["gastos"]:
        st.dataframe(
            [
                {
                    "Data": gasto["data"],
                    "Descrição": gasto["descricao"],
                    "Categoria": gasto["categoria"],
                    "Valor": gasto["valor"],
                }
                for gasto in resumo["gastos"]
            ],
            column_config={
                "Valor": st.column_config.NumberColumn("Valor", format="R$ %.2f")
            },
            hide_index=True,
            width="stretch",
            height=220,
        )
    else:
        st.caption("Nenhum lançamento neste mês.")

    with st.expander("Memória", expanded=False):
        memorias = db.listar_memorias()
        if memorias:
            for memoria in memorias:
                st.markdown(f"- {memoria['conteudo']}")
        else:
            st.caption("Nenhuma memória registrada.")

    with st.container(key="acoes"):
        if st.button("Excluir conversa", width="stretch"):
            db.excluir_conversa(conversa_id)
            restantes = db.listar_conversas()
            st.session_state.conversa_id = (
                restantes[0]["id"] if restantes else db.criar_conversa()
            )
            st.rerun()

        if st.button("Limpar memórias", width="stretch"):
            db.limpar_memorias()
            st.rerun()

        if st.button(
            "Apagar meus dados",
            width="stretch",
            help="Remove desta sessão as conversas, os gastos e as memórias.",
        ):
            sessao.apagar_banco_da_sessao()
            st.session_state.pop("conversa_id", None)
            st.rerun()
