import os
import sqlite3
import threading
from datetime import date

BASE = os.path.dirname(os.path.abspath(__file__))
CAMINHO_PADRAO = os.getenv("EDITH_DB") or os.path.join(BASE, "edith.db")

# Cada sessão do Streamlit roda em uma thread própria. Guardar o caminho do
# banco na thread impede que um visitante leia os dados de outro.
_estado = threading.local()


def caminho_banco():
    return getattr(_estado, "caminho", CAMINHO_PADRAO)


def usar_banco(caminho):
    """Aponta as operações desta sessão para um arquivo SQLite próprio."""
    if not caminho:
        raise ValueError("Caminho de banco inválido.")
    _estado.caminho = os.path.abspath(caminho)
    return _estado.caminho


def conectar():
    conexao = sqlite3.connect(caminho_banco())
    conexao.row_factory = sqlite3.Row
    return conexao


def inicializar():
    conexao = conectar()
    try:
        conexao.executescript(
            """
            CREATE TABLE IF NOT EXISTS conversas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                atualizado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            );

            CREATE TABLE IF NOT EXISTS mensagens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversa_id INTEGER,
                papel TEXT NOT NULL,
                conteudo TEXT NOT NULL,
                criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            );

            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descricao TEXT NOT NULL,
                valor REAL NOT NULL,
                categoria TEXT NOT NULL,
                data TEXT NOT NULL,
                criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            );

            CREATE TABLE IF NOT EXISTS memorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conteudo TEXT NOT NULL UNIQUE,
                criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            );
            """
        )

        colunas = [linha["name"] for linha in conexao.execute("PRAGMA table_info(mensagens)")]
        if "conversa_id" not in colunas:
            conexao.execute("ALTER TABLE mensagens ADD COLUMN conversa_id INTEGER")
            total = conexao.execute("SELECT COUNT(*) AS total FROM mensagens").fetchone()["total"]
            if total:
                cursor = conexao.execute(
                    "INSERT INTO conversas (titulo) VALUES (?)", ("Conversa anterior",)
                )
                conexao.execute(
                    "UPDATE mensagens SET conversa_id = ? WHERE conversa_id IS NULL",
                    (cursor.lastrowid,),
                )

        conexao.commit()
    finally:
        conexao.close()


def _consultar(sql, parametros=()):
    conexao = conectar()
    try:
        return conexao.execute(sql, parametros).fetchall()
    finally:
        conexao.close()


def _gravar(sql, parametros=()):
    conexao = conectar()
    try:
        cursor = conexao.execute(sql, parametros)
        conexao.commit()
        return cursor.lastrowid
    finally:
        conexao.close()


def criar_conversa(titulo="Nova conversa"):
    return _gravar("INSERT INTO conversas (titulo) VALUES (?)", (titulo,))


def listar_conversas():
    linhas = _consultar(
        """
        SELECT c.id, c.titulo, c.criado_em, c.atualizado_em,
               (SELECT COUNT(*) FROM mensagens m WHERE m.conversa_id = c.id) AS total
        FROM conversas c
        ORDER BY c.atualizado_em DESC, c.id DESC
        """
    )
    return [dict(linha) for linha in linhas]


def conversa_vazia():
    linhas = _consultar(
        """
        SELECT c.id
        FROM conversas c
        WHERE NOT EXISTS (SELECT 1 FROM mensagens m WHERE m.conversa_id = c.id)
        ORDER BY c.id DESC
        LIMIT 1
        """
    )
    return linhas[0]["id"] if linhas else None


def renomear_conversa(conversa_id, titulo):
    _gravar(
        "UPDATE conversas SET titulo = ?, atualizado_em = datetime('now', 'localtime') "
        "WHERE id = ?",
        (titulo.strip()[:60], conversa_id),
    )


def excluir_conversa(conversa_id):
    _gravar("DELETE FROM mensagens WHERE conversa_id = ?", (conversa_id,))
    _gravar("DELETE FROM conversas WHERE id = ?", (conversa_id,))


def contar_mensagens(conversa_id):
    linha = _consultar(
        "SELECT COUNT(*) AS total FROM mensagens WHERE conversa_id = ?", (conversa_id,)
    )[0]
    return linha["total"]


def salvar_mensagem(papel, conteudo, conversa_id):
    conexao = conectar()
    try:
        conexao.execute(
            "INSERT INTO mensagens (conversa_id, papel, conteudo) VALUES (?, ?, ?)",
            (conversa_id, papel, conteudo),
        )
        conexao.execute(
            "UPDATE conversas SET atualizado_em = datetime('now', 'localtime') WHERE id = ?",
            (conversa_id,),
        )
        conexao.commit()
    finally:
        conexao.close()


def carregar_mensagens(conversa_id, limite=40):
    linhas = _consultar(
        "SELECT papel, conteudo FROM mensagens WHERE conversa_id = ? "
        "ORDER BY id DESC LIMIT ?",
        (conversa_id, limite),
    )
    return [
        {"role": linha["papel"], "content": linha["conteudo"]}
        for linha in reversed(linhas)
    ]


def limpar_mensagens(conversa_id):
    _gravar("DELETE FROM mensagens WHERE conversa_id = ?", (conversa_id,))


def registrar_gasto(descricao, valor, categoria, data_gasto=None):
    data_gasto = data_gasto or date.today().isoformat()
    return _gravar(
        "INSERT INTO gastos (descricao, valor, categoria, data) VALUES (?, ?, ?, ?)",
        (descricao.strip(), float(valor), categoria.strip(), data_gasto),
    )


def listar_gastos(mes=None, ano=None):
    if mes and ano:
        inicio = date(ano, mes, 1)
        fim = date(ano + (1 if mes == 12 else 0), 1 if mes == 12 else mes + 1, 1)
        linhas = _consultar(
            "SELECT id, descricao, valor, categoria, data FROM gastos "
            "WHERE data >= ? AND data < ? ORDER BY data, id",
            (inicio.isoformat(), fim.isoformat()),
        )
    else:
        linhas = _consultar(
            "SELECT id, descricao, valor, categoria, data FROM gastos ORDER BY data, id"
        )
    return [dict(linha) for linha in linhas]


def resumo_mensal(mes, ano):
    gastos = listar_gastos(mes, ano)
    por_categoria = {}
    for gasto in gastos:
        por_categoria[gasto["categoria"]] = round(
            por_categoria.get(gasto["categoria"], 0) + gasto["valor"], 2
        )
    return {
        "mes": mes,
        "ano": ano,
        "total": round(sum(gasto["valor"] for gasto in gastos), 2),
        "quantidade": len(gastos),
        "por_categoria": dict(
            sorted(por_categoria.items(), key=lambda item: item[1], reverse=True)
        ),
        "gastos": gastos,
    }


def excluir_gasto(gasto_id):
    _gravar("DELETE FROM gastos WHERE id = ?", (gasto_id,))
    return True


def salvar_memoria(conteudo):
    conteudo = conteudo.strip()
    if not conteudo:
        return False
    _gravar("INSERT OR IGNORE INTO memorias (conteudo) VALUES (?)", (conteudo,))
    return True


def listar_memorias():
    return [dict(linha) for linha in _consultar("SELECT id, conteudo FROM memorias ORDER BY id")]


def excluir_memoria(memoria_id):
    _gravar("DELETE FROM memorias WHERE id = ?", (memoria_id,))


def limpar_memorias():
    _gravar("DELETE FROM memorias")
