"""Cofre privado por visitante.

Na internet, cada aba do navegador recebe um banco SQLite novo, criado em uma
pasta temporária e ligado apenas àquela sessão do Streamlit. O `edith.db` do
repositório nunca é aberto, então o site sempre começa vazio e cada pessoa
constrói os próprios gastos, memórias e conversas.

No seu computador (localhost) o comportamento continua o de sempre: o app usa
o `edith.db` da pasta do projeto e os dados sobrevivem ao fechar o navegador.
"""

import os
import shutil
import tempfile
import time

import streamlit as st

import db

PREFIXO = "edith_cofre_"
VALIDADE_SEGUNDOS = 12 * 60 * 60
CHAVE = "edith_banco"
CHAVE_MODO = "edith_modo_local"
HOSTS_LOCAIS = {"localhost", "127.0.0.1", "0.0.0.0", "::1"}


def _host_da_requisicao():
    try:
        host = st.context.headers.get("Host", "") or ""
    except Exception:
        return ""
    host = host.strip().lower()
    if host.startswith("["):
        return host[1 : host.find("]")] if "]" in host else host
    return host.split(":")[0]


def _detectar_modo_local():
    if os.getenv("EDITH_DB"):
        return True
    if os.getenv("EDITH_LOCAL", "").strip().lower() in {"1", "true", "sim", "yes"}:
        return True
    # Sem cabeçalho de requisição (testes, chamadas internas), assume o modo
    # seguro: banco temporário por sessão.
    return _host_da_requisicao() in HOSTS_LOCAIS


def modo_local():
    """True quando o app roda na própria máquina do dono."""
    if CHAVE_MODO not in st.session_state:
        st.session_state[CHAVE_MODO] = _detectar_modo_local()
    return bool(st.session_state[CHAVE_MODO])


def _limpar_antigos():
    """Remove cofres de sessões encerradas há mais de 12 horas."""
    raiz = tempfile.gettempdir()
    limite = time.time() - VALIDADE_SEGUNDOS
    try:
        entradas = os.listdir(raiz)
    except OSError:
        return

    for nome in entradas:
        if not nome.startswith(PREFIXO):
            continue
        caminho = os.path.join(raiz, nome)
        try:
            if os.path.getmtime(caminho) < limite:
                shutil.rmtree(caminho, ignore_errors=True)
        except OSError:
            continue


def _marcar_ativo(caminho):
    """Atualiza a data da pasta para o faxineiro não apagar uma sessão em uso."""
    try:
        os.utime(os.path.dirname(caminho), None)
    except OSError:
        pass


def banco_da_sessao():
    """Devolve o banco desta sessão, criando um cofre vazio na primeira visita."""
    if modo_local():
        db.usar_banco(db.CAMINHO_PADRAO)
        if not os.path.isfile(db.CAMINHO_PADRAO):
            db.inicializar()
        return db.CAMINHO_PADRAO

    caminho = st.session_state.get(CHAVE)

    if caminho and os.path.isdir(os.path.dirname(caminho)):
        db.usar_banco(caminho)
        if not os.path.isfile(caminho):
            db.inicializar()
        _marcar_ativo(caminho)
        return caminho

    _limpar_antigos()
    pasta = tempfile.mkdtemp(prefix=PREFIXO)
    caminho = os.path.join(pasta, "edith.db")
    st.session_state[CHAVE] = caminho
    db.usar_banco(caminho)
    db.inicializar()
    return caminho


def apagar_banco_da_sessao():
    """Apaga o cofre desta sessão e já prepara um novo, vazio."""
    caminho = st.session_state.pop(CHAVE, None)
    if caminho:
        shutil.rmtree(os.path.dirname(caminho), ignore_errors=True)
    return banco_da_sessao()
