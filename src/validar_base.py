"""Valida a base e mede o tamanho de cada trecho em tokens do próprio modelo de embeddings.

Uso: python src/validar_base.py
Sai com código 1 se algum trecho passar do limite (seria truncado em silêncio pelo modelo).
"""
import csv
import sys
from collections import Counter

from sentence_transformers import SentenceTransformer

import config
from comum import carregar_base, configurar_saida_utf8, texto_para_indexar


def main():
    configurar_saida_utf8()
    base = carregar_base()
    categorias = Counter(t["categoria"] for t in base)
    print(f"Trechos: {len(base)}  |  Categorias: {dict(categorias)}")
    if len(base) < 30 or len(categorias) < 3:
        print("ERRO: a atividade exige >= 30 trechos e >= 3 categorias.")
        sys.exit(1)

    modelo = SentenceTransformer(config.MODELO_EMBEDDINGS, device=config.DISPOSITIVO)
    tokenizer = modelo.tokenizer
    limite = modelo.max_seq_length
    print(f"Modelo: {config.MODELO_EMBEDDINGS}  |  max_seq_length: {limite}")

    config.DIR_RESULTADOS.mkdir(exist_ok=True)
    saida = config.DIR_RESULTADOS / "tokens_por_trecho.csv"
    excedidos = []
    with open(saida, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "categoria", "palavras", "tokens_v1", "tokens_v2", "dentro_do_limite"])
        for t in base:
            # input_ids inclui os tokens especiais <s> e </s>, que também contam no limite.
            tok_v1 = len(tokenizer(texto_para_indexar(t, "v1"))["input_ids"])
            tok_v2 = len(tokenizer(texto_para_indexar(t, "v2"))["input_ids"])
            ok = max(tok_v1, tok_v2) <= limite
            if not ok:
                excedidos.append(t["id"])
            w.writerow([t["id"], t["categoria"], len(t["texto"].split()), tok_v1, tok_v2, "sim" if ok else "NAO"])

    print(f"Relatório salvo em {saida.relative_to(config.RAIZ)}")
    if excedidos:
        print(f"ERRO: trechos acima de {limite} tokens: {excedidos}")
        sys.exit(1)
    print("OK: todos os trechos cabem no limite do modelo.")


if __name__ == "__main__":
    main()
