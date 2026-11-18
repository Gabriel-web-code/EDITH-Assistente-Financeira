"""Tabelas Markdown legíveis no celular.

O agente responde com tabelas em Markdown. Em telas estreitas elas estouram a
largura da conversa. Este módulo troca cada tabela por HTML próprio: tabela
normal no computador e cartões empilhados no celular.
"""

import html
import re
import unicodedata

_SEPARADOR = re.compile(r"^:?-+:?$")
_NEGRITO = re.compile(r"\*\*(.+?)\*\*")
_CODIGO = re.compile(r"`([^`]+)`")


def _sem_acento(texto):
    decomposto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in decomposto if unicodedata.category(c) != "Mn")


def _inline(texto):
    texto = html.escape(texto.strip(), quote=False)
    texto = _NEGRITO.sub(r"<strong>\1</strong>", texto)
    texto = _CODIGO.sub(r"<code>\1</code>", texto)
    return texto


def _celulas(linha):
    linha = linha.strip()
    if linha.startswith("|"):
        linha = linha[1:]
    if linha.endswith("|"):
        linha = linha[:-1]
    return [celula.strip() for celula in linha.split("|")]


def _e_separador(linha):
    if "-" not in linha:
        return False
    celulas = _celulas(linha)
    return bool(celulas) and all(_SEPARADOR.match(c.replace(" ", "")) for c in celulas)


def _classe(cabecalho):
    chave = _sem_acento(cabecalho).lower()
    if re.search(r"\b(valor|total|preco|gasto|montante|custo|media)\b", chave):
        return "valor"
    if re.search(r"\b(data|dia|mes|ano|periodo)\b", chave):
        return "data"
    return ""


def _indice_titulo(cabecalho, classes):
    regras = [
        (2, r"\b(descricao|item|lancamento|nome|conta|produto|servico|estabelecimento)\b"),
        (1, r"\bcategoria\b"),
    ]
    escolhido = None
    for peso, padrao in regras:
        for indice, nome in enumerate(cabecalho):
            if classes[indice]:
                continue
            if re.search(padrao, _sem_acento(nome).lower()):
                if escolhido is None or peso > escolhido[0]:
                    escolhido = (peso, indice)
    return escolhido[1] if escolhido else None


def _alinhamentos(separador, total):
    lista = []
    for celula in separador:
        if celula.startswith(":") and celula.endswith(":"):
            lista.append("center")
        elif celula.endswith(":"):
            lista.append("right")
        else:
            lista.append("left")
    while len(lista) < total:
        lista.append("left")
    return lista[:total]


def _ajustar(linha, total):
    return (list(linha) + [""] * total)[:total]


def _montar(cabecalho, separador, corpo):
    total = len(cabecalho)
    classes = [_classe(nome) for nome in cabecalho]
    alinhamentos = _alinhamentos(separador, total)
    indice_valor = next((i for i, c in enumerate(classes) if c == "valor"), None)
    indice_titulo = _indice_titulo(cabecalho, classes)
    if indice_titulo is None:
        indice_titulo = 0 if indice_valor != 0 else (1 if total > 1 else 0)
    if not classes[indice_titulo]:
        classes[indice_titulo] = "titulo"

    larguras = {"data": "18%", "valor": "20%", "titulo": "34%"}

    partes = ['<div class="tabela-edith"><table><colgroup>']
    for indice in range(total):
        largura = larguras.get(classes[indice], "")
        partes.append(f'<col style="width:{largura}">' if largura else "<col>")
    partes.append("</colgroup><thead><tr>")
    for indice, nome in enumerate(cabecalho):
        classe = f' class="col-{classes[indice]}"' if classes[indice] else ""
        estilo = (
            f' style="text-align:{alinhamentos[indice]}"'
            if alinhamentos[indice] != "left"
            else ""
        )
        partes.append(f"<th{classe}{estilo}>{_inline(nome)}</th>")
    partes.append("</tr></thead><tbody>")

    for linha in corpo:
        linha = _ajustar(linha, total)
        partes.append("<tr>")
        for indice, celula in enumerate(linha):
            classe = f' class="col-{classes[indice]}"' if classes[indice] else ""
            estilo = (
                f' style="text-align:{alinhamentos[indice]}"'
                if alinhamentos[indice] != "left"
                else ""
            )
            partes.append(f"<td{classe}{estilo}>{_inline(celula)}</td>")
        partes.append("</tr>")
    partes.append("</tbody></table>")

    partes.append('<div class="cartoes">')
    for linha in corpo:
        linha = _ajustar(linha, total)
        titulo = linha[indice_titulo]
        valor = linha[indice_valor] if indice_valor is not None else ""
        meta = []
        for indice, celula in enumerate(linha):
            if indice in (indice_titulo, indice_valor) or not celula:
                continue
            if classes[indice] == "data":
                meta.append(_inline(celula))
            else:
                meta.append(f"{_inline(cabecalho[indice])}: {_inline(celula)}")

        partes.append('<div class="cartao-edith">')
        partes.append('<div class="cartao-edith-topo">')
        partes.append(f'<span class="cartao-edith-titulo">{_inline(titulo)}</span>')
        if valor:
            partes.append(f'<span class="cartao-edith-valor">{_inline(valor)}</span>')
        partes.append("</div>")
        if meta:
            partes.append(f'<div class="cartao-edith-meta">{" · ".join(meta)}</div>')
        partes.append("</div>")

    partes.append("</div></div>")
    return "".join(partes)


def blocos(texto):
    """Divide a resposta em trechos de Markdown e trechos de tabela em HTML."""
    if not texto:
        return []

    linhas = texto.splitlines()
    saida = []
    buffer = []
    indice = 0

    while indice < len(linhas):
        proxima = indice + 1
        if (
            "|" in linhas[indice]
            and proxima < len(linhas)
            and _e_separador(linhas[proxima])
        ):
            cabecalho = _celulas(linhas[indice])
            separador = _celulas(linhas[proxima])
            if len(cabecalho) >= 2 and len(cabecalho) == len(separador):
                corpo = []
                fim = proxima + 1
                while fim < len(linhas) and "|" in linhas[fim] and linhas[fim].strip():
                    corpo.append(_celulas(linhas[fim]))
                    fim += 1
                if buffer:
                    trecho = "\n".join(buffer).strip()
                    if trecho:
                        saida.append(("md", trecho))
                    buffer = []
                saida.append(("html", _montar(cabecalho, separador, corpo)))
                indice = fim
                continue

        buffer.append(linhas[indice])
        indice += 1

    if buffer:
        trecho = "\n".join(buffer).strip()
        if trecho:
            saida.append(("md", trecho))

    return saida
