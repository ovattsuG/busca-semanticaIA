"""Busca por palavras-chave (baseline lexical para comparar com a semântica).

REGRA (documentada no README):
 1. Minúsculas.
 2. Remove acentos (NFKD) — "métrica" e "metrica" viram o mesmo termo.
 3. Troca tudo que não é letra/dígito por espaço (remove pontuação) e separa por espaços.
 4. Remove stopwords do português (lista STOPWORDS abaixo). Sem isso, "o", "que", "é"
    casariam com quase todos os trechos e o placar viraria ruído.
 5. Pontuação de um trecho = nº de termos DISTINTOS da consulta presentes no trecho.
 6. Retorna até K trechos com pontuação >= 1, ordenados por pontuação (desc) e id (asc) no empate.

Uso: python src/lexical.py "O que é um embedding?" [--k 3] [--versao v1]
"""
import argparse
import re
import unicodedata

from comum import carregar_base, configurar_saida_utf8, texto_para_indexar

STOPWORDS = {
    "a", "o", "as", "os", "um", "uma", "uns", "umas", "de", "do", "da", "dos", "das", "e", "ou",
    "que", "qual", "quais", "quanto", "quantos", "como", "por", "para", "pra", "com", "sem", "em",
    "no", "na", "nos", "nas", "ao", "aos", "se", "sua", "seu", "suas", "seus", "ele", "ela", "eles",
    "elas", "isso", "isto", "este", "esta", "esse", "essa", "ser", "sao", "foi", "sobre", "mais",
    "mas", "nao", "ja", "pelo", "pela", "pelos", "pelas", "cada", "entre", "ate", "me", "eu",
    "voce", "lhe", "la", "ha", "tem",
}


def normalizar(texto):
    sem_acento = unicodedata.normalize("NFKD", texto.lower())
    sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c))
    tokens = re.sub(r"[^a-z0-9]+", " ", sem_acento).split()
    return [t for t in tokens if t not in STOPWORDS]


def buscar_lexical(base, pergunta, k=3, versao="v1"):
    termos_consulta = set(normalizar(pergunta))
    pontuados = []
    for t in base:
        termos_trecho = set(normalizar(texto_para_indexar(t, versao)))
        comuns = termos_consulta & termos_trecho
        if comuns:
            pontuados.append((len(comuns), t, sorted(comuns)))
    pontuados.sort(key=lambda x: (-x[0], x[1]["id"]))
    return [
        {
            "rank": pos,
            "id": t["id"],
            "categoria": t["categoria"],
            "fonte": t["fonte"],
            "pontuacao": n,
            "termos_em_comum": " ".join(comuns),
            "texto": t["texto"],
        }
        for pos, (n, t, comuns) in enumerate(pontuados[:k], start=1)
    ]


def main():
    configurar_saida_utf8()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pergunta")
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--versao", choices=["v1", "v2"], default="v1")
    args = parser.parse_args()

    print(f"Termos da consulta após normalização: {sorted(set(normalizar(args.pergunta)))}")
    resultados = buscar_lexical(carregar_base(), args.pergunta, args.k, args.versao)
    if not resultados:
        print("Nenhum trecho com termos em comum.")
    for r in resultados:
        print(f"  #{r['rank']} [{r['id']}] pontos={r['pontuacao']} termos={r['termos_em_comum']}")
        print(f"      {r['texto']}")


if __name__ == "__main__":
    main()
