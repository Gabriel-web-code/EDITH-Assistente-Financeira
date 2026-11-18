import sys
from datetime import date

import agent
import db

ROTULOS = {
    "registrar_gasto": "Registrando lançamento...",
    "listar_gastos": "Consultando lançamentos...",
    "resumo_mensal": "Consultando o resumo do mês...",
    "excluir_gasto": "Excluindo lançamento...",
    "salvar_memoria": "Salvando memória...",
    "pesquisar_web": "Pesquisando na internet...",
    "abrir_pagina": "Lendo página...",
}


def moeda(valor):
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")


def imprimir_resumo(mes, ano):
    resumo = db.resumo_mensal(mes, ano)
    if not resumo["gastos"]:
        print("Nenhum lançamento neste mês.")
        return

    print(f"{'Data':<12}{'Descrição':<30}{'Categoria':<16}{'Valor':>14}")
    print("-" * 72)
    for gasto in resumo["gastos"]:
        descricao = gasto["descricao"][:28]
        print(
            f"{gasto['data']:<12}{descricao:<30}{gasto['categoria']:<16}"
            f"{moeda(gasto['valor']):>14}"
        )
    print("-" * 72)
    print(f"{'Total do mês':<58}{moeda(resumo['total']):>14}")
    print("")
    print("Total por categoria:")
    for categoria, valor in resumo["por_categoria"].items():
        print(f"  {categoria:<24}{moeda(valor):>14}")


def main():
    hoje = date.today()
    conversas = db.listar_conversas()
    conversa_id = conversas[0]["id"] if conversas else db.criar_conversa()

    print("EDITH - Assistente Financeira")
    print("Comandos: /mes, /limpar, /ajuda, /sair\n")

    while True:
        try:
            entrada = input("Você: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nAté logo.")
            break

        if not entrada:
            continue

        comando = entrada.lower()

        if comando in {"/sair", "sair", "exit", "quit"}:
            print("Até logo.")
            break

        if comando == "/ajuda":
            print(
                "/mes      mostra a tabela de gastos do mês atual\n"
                "/limpar   apaga o histórico da conversa atual\n"
                "/sair     encerra o programa\n"
            )
            continue

        if comando == "/limpar":
            db.limpar_mensagens(conversa_id)
            db.renomear_conversa(conversa_id, "Nova conversa")
            print("Histórico apagado.\n")
            continue

        if comando == "/mes":
            imprimir_resumo(hoje.month, hoje.year)
            print("")
            continue

        if db.contar_mensagens(conversa_id) == 0:
            db.renomear_conversa(conversa_id, entrada[:48])

        db.salvar_mensagem("user", entrada, conversa_id)

        try:
            resposta = agent.responder(
                db.carregar_mensagens(conversa_id, 40),
                lambda nome, argumentos: print(
                    f"  [{ROTULOS.get(nome, 'Processando...')}]"
                ),
            )
        except Exception as erro:
            print(f"[Erro] {erro}\n")
            continue

        print(f"EDITH: {resposta}\n")
        db.salvar_mensagem("assistant", resposta, conversa_id)


if __name__ == "__main__":
    main()
