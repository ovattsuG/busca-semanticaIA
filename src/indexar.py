"""Cria a coleção no ChromaDB e insere a base. Roda UMA vez.

Uso:
  python src/indexar.py                 # indexa v1 e v2
  python src/indexar.py --versao v1
  python src/indexar.py --recriar       # apaga e recria (use só se mudou a base)

Se a coleção já existir com dados, o script NÃO reinsere — isso é o que separa
indexação (escrita) de consulta (buscar.py, só leitura).
"""
import argparse

import config
from comum import (carregar_base, configurar_saida_utf8, obter_cliente,
                   obter_embedding_function, texto_para_indexar)


def indexar(versao, recriar, cliente, ef, base):
    nome = config.COLECOES[versao]
    existentes = [c.name if hasattr(c, "name") else c for c in cliente.list_collections()]

    if nome in existentes and recriar:
        cliente.delete_collection(nome)
        print(f"[{versao}] coleção '{nome}' apagada (--recriar).")
    elif nome in existentes:
        col = cliente.get_collection(name=nome, embedding_function=ef)
        if col.count() > 0:
            print(f"[{versao}] coleção '{nome}' já existe com {col.count()} registros. Nada inserido.")
            return col

    col = cliente.get_or_create_collection(
        name=nome,
        embedding_function=ef,
        configuration={"hnsw": {"space": config.METRICA}},
        metadata={"modelo": config.MODELO_EMBEDDINGS, "versao": versao},
    )
    col.add(
        ids=[t["id"] for t in base],
        documents=[texto_para_indexar(t, versao) for t in base],
        metadatas=[{"categoria": t["categoria"], "titulo": t["titulo"], "fonte": t["fonte"]} for t in base],
    )
    print(f"[{versao}] {col.count()} registros inseridos em '{nome}'.")
    return col


def main():
    configurar_saida_utf8()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--versao", choices=[*config.COLECOES, "todas"], default="todas")
    parser.add_argument("--recriar", action="store_true", help="apaga a coleção antes de inserir")
    args = parser.parse_args()

    base = carregar_base()
    cliente = obter_cliente()
    ef = obter_embedding_function()

    dimensao = len(ef(["teste de dimensão"])[0])
    if dimensao != config.DIMENSAO_ESPERADA:
        raise RuntimeError(f"Dimensão {dimensao} diferente da esperada ({config.DIMENSAO_ESPERADA}).")
    print(f"Modelo: {config.MODELO_EMBEDDINGS} | dimensão: {dimensao} | métrica: {config.METRICA}")
    print(f"Banco local: {config.CAMINHO_CHROMA}")

    versoes = list(config.COLECOES) if args.versao == "todas" else [args.versao]
    for v in versoes:
        indexar(v, args.recriar, cliente, ef, base)


if __name__ == "__main__":
    main()
