"""Busca semântica na coleção persistida. Só lê o banco — nunca insere.

Uso:
  python src/buscar.py "O que é um embedding?"
  python src/buscar.py "Como funciona a busca?" --k 5 --categoria bancos_vetoriais
  python src/buscar.py                      # modo interativo (comandos: :k N, :cat nome, :cat, :sair)
"""
import argparse

import config
from comum import abrir_colecao, buscar_semantica, configurar_saida_utf8, imprimir_resultados


def categorias_da_colecao(col):
    metas = col.get(include=["metadatas"])["metadatas"]
    return sorted({m["categoria"] for m in metas})


def executar(col, pergunta, k, categoria):
    filtro = f" | filtro categoria={categoria}" if categoria else " | sem filtro"
    print(f"\nPergunta: {pergunta}\nTop-K={k}{filtro}")
    imprimir_resultados(buscar_semantica(col, pergunta, k, categoria))


def main():
    configurar_saida_utf8()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pergunta", nargs="?", help="pergunta em linguagem natural")
    parser.add_argument("--k", type=int, default=3, help="quantidade de resultados (Top-K)")
    parser.add_argument("--categoria", help="filtra por categoria")
    parser.add_argument("--versao", choices=list(config.COLECOES), default="v1")
    args = parser.parse_args()

    col = abrir_colecao(args.versao)
    categorias = categorias_da_colecao(col)
    print(f"Coleção '{col.name}' carregada do disco ({config.CAMINHO_CHROMA}) "
          f"com {col.count()} registros — nenhum documento foi reinserido.")
    print(f"Modelo: {config.MODELO_EMBEDDINGS} | métrica: {config.METRICA} | categorias: {categorias}")

    if args.categoria and args.categoria not in categorias:
        parser.error(f"categoria '{args.categoria}' não existe. Opções: {categorias}")
    if args.k < 1:
        parser.error("--k precisa ser >= 1")

    if args.pergunta:
        executar(col, args.pergunta, args.k, args.categoria)
        return

    k, categoria = args.k, args.categoria
    print("\nModo interativo. Comandos: ':k 5', ':cat rag', ':cat' (remove filtro), ':sair'")
    while True:
        try:
            entrada = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not entrada:
            continue
        if entrada == ":sair":
            break
        if entrada.startswith(":k"):
            partes = entrada.split()
            if len(partes) == 2 and partes[1].isdigit() and int(partes[1]) >= 1:
                k = int(partes[1])
                print(f"Top-K = {k}")
            else:
                print("Uso: :k N  (N inteiro >= 1)")
            continue
        if entrada.startswith(":cat"):
            partes = entrada.split()
            if len(partes) == 1:
                categoria = None
                print("Filtro removido.")
            elif partes[1] in categorias:
                categoria = partes[1]
                print(f"Filtro: categoria = {categoria}")
            else:
                print(f"Categoria inválida. Opções: {categorias}")
            continue
        executar(col, entrada, k, categoria)


if __name__ == "__main__":
    main()
