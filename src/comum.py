"""Funções compartilhadas: leitura da base, conexão com o Chroma e busca semântica."""
import json
import sys

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

import config

CAMPOS_OBRIGATORIOS = ("id", "categoria", "titulo", "texto", "fonte")


def configurar_saida_utf8():
    # O terminal do Windows às vezes usa cp1252 e quebra com acentos.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def carregar_base():
    with open(config.ARQ_BASE, encoding="utf-8") as f:
        base = json.load(f)
    erros = []
    vistos = set()
    for i, trecho in enumerate(base):
        faltando = [c for c in CAMPOS_OBRIGATORIOS if not str(trecho.get(c, "")).strip()]
        if faltando:
            erros.append(f"trecho na posição {i}: campos vazios ou ausentes {faltando}")
        if trecho.get("id") in vistos:
            erros.append(f"id duplicado: {trecho.get('id')}")
        vistos.add(trecho.get("id"))
    if erros:
        raise ValueError("Base inválida:\n  " + "\n  ".join(erros))
    return base


def carregar_perguntas():
    with open(config.ARQ_PERGUNTAS, encoding="utf-8") as f:
        return json.load(f)


def texto_para_indexar(trecho, versao):
    """O que vira embedding. v2 prefixa o título: é a melhoria avaliada no experimento."""
    if versao == "v1":
        return trecho["texto"]
    if versao == "v2":
        return f"{trecho['titulo']}. {trecho['texto']}"
    raise ValueError(f"versão desconhecida: {versao!r} (use v1 ou v2)")


def obter_cliente():
    return chromadb.PersistentClient(path=str(config.CAMINHO_CHROMA))


def obter_embedding_function():
    return SentenceTransformerEmbeddingFunction(
        model_name=config.MODELO_EMBEDDINGS,
        device=config.DISPOSITIVO,
    )


def abrir_colecao(versao, cliente=None, ef=None):
    """Abre uma coleção JÁ EXISTENTE. Nunca insere nada: é o que prova a persistência."""
    if versao not in config.COLECOES:
        raise ValueError(f"versão desconhecida: {versao!r} (use {list(config.COLECOES)})")
    cliente = cliente or obter_cliente()
    nome = config.COLECOES[versao]
    existentes = [c.name if hasattr(c, "name") else c for c in cliente.list_collections()]
    if nome not in existentes:
        raise RuntimeError(
            f"A coleção '{nome}' não existe em {config.CAMINHO_CHROMA}. "
            f"Rode antes: python src/indexar.py --versao {versao}"
        )
    return cliente.get_collection(name=nome, embedding_function=ef or obter_embedding_function())


def buscar_semantica(colecao, pergunta, k=3, categoria=None):
    if k < 1:
        raise ValueError("Top-K precisa ser >= 1")
    filtro = {"categoria": categoria} if categoria else None
    res = colecao.query(
        query_texts=[pergunta],
        n_results=k,
        where=filtro,
        include=["documents", "metadatas", "distances"],
    )
    resultados = []
    for pos, (id_, doc, meta, dist) in enumerate(
        zip(res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0]), start=1
    ):
        resultados.append({
            "rank": pos,
            "id": id_,
            "categoria": meta.get("categoria", ""),
            "titulo": meta.get("titulo", ""),
            "fonte": meta.get("fonte", ""),
            "distancia": round(float(dist), 4),
            "texto": doc,
        })
    return resultados


def imprimir_resultados(resultados, mostrar_texto=True):
    if not resultados:
        print("  (nenhum resultado — verifique o filtro de categoria)")
        return
    for r in resultados:
        print(f"  #{r['rank']}  [{r['id']}]  dist={r['distancia']:.4f}  categoria={r['categoria']}")
        print(f"      fonte: {r['fonte']}")
        if mostrar_texto:
            print(f"      {r['texto']}")
