import requests
from bs4 import BeautifulSoup
from ddgs import DDGS

CABECALHOS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}


def pesquisar_web(consulta, max_resultados=5):
    try:
        with DDGS() as buscador:
            resultados = list(
                buscador.text(consulta, region="br-pt", max_results=max_resultados)
            )
    except Exception as erro:
        return {"erro": f"Não foi possível concluir a busca: {erro}"}

    if not resultados:
        return {"consulta": consulta, "resultados": []}

    itens = [
        {
            "titulo": item.get("title", ""),
            "url": item.get("href", ""),
            "resumo": item.get("body", ""),
        }
        for item in resultados
    ]
    return {"consulta": consulta, "resultados": itens}


def abrir_pagina(url, limite=6000):
    if not url.startswith(("http://", "https://")):
        return {"erro": "Endereço inválido."}
    try:
        resposta = requests.get(url, headers=CABECALHOS, timeout=15)
        resposta.raise_for_status()
    except Exception as erro:
        return {"erro": f"Não foi possível abrir a página: {erro}"}

    sopa = BeautifulSoup(resposta.text, "html.parser")
    for tag in sopa(["script", "style", "noscript", "header", "footer", "nav", "aside", "form"]):
        tag.decompose()

    texto = " ".join(sopa.get_text(" ").split())
    return {"url": url, "conteudo": texto[:limite]}
