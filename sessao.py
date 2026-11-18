"""Cofre privado por visitante.

Cada aba do navegador recebe um banco SQLite novo, criado em uma pasta
temporária e ligado apenas àquela sessão do Streamlit. O `edith.db` do
repositório nunca é aberto, então o site sempre começa vazio e cada pessoa
constrói os próprios gastos, memórias e conversas.
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
    """Devolve o banco exclusivo desta sessão, criando-o na primeira visita."""
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
