"""Roda todos os experimentos da Seção 3 e grava CSVs em resultados/.

Uso: python src/experimentos.py            # roda para v1 e v2 (as que existirem) e compara
     python src/experimentos.py --versao v1

Arquivos gerados (sufixo _v1/_v2):
  a_semantica_top3      8 perguntas, Top-3, com coluna 'relevante'
  b_lexical_top3        8 perguntas, busca por palavras-chave, até 3 trechos
  metrica               % de perguntas respondíveis com >=1 relevante no Top-3, por abordagem
  c_topk                Top-1/3/5 em duas perguntas
  d_filtro              mesma pergunta com e sem filtro de categoria
  e_limitacoes          distâncias do Top-1/Top-3 por pergunta (evidência para a análise)
  comparacao_antes_depois.csv   v1 x v2 (só se as duas coleções existirem)
"""
import argparse
import csv

import config
from comum import (abrir_colecao, buscar_semantica, carregar_base, carregar_perguntas,
                   configurar_saida_utf8, obter_cliente, obter_embedding_function)
from lexical import buscar_lexical

RESPONDIVEIS = ("direta", "parafrase")


def salvar_csv(nome, linhas):
    config.DIR_RESULTADOS.mkdir(exist_ok=True)
    caminho = config.DIR_RESULTADOS / nome
    if not linhas:
        raise ValueError(f"Nenhuma linha para salvar em {nome}")
    with open(caminho, "w", newline="", encoding="utf-8-sig") as f:  # -sig: o Excel abre com acentos
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)
    print(f"  salvo: {caminho.relative_to(config.RAIZ)}")


def marca_relevante(id_, pergunta):
    if pergunta["tipo"] not in RESPONDIVEIS:
        return "n/a"
    return "sim" if id_ in pergunta["relevantes"] else "nao"


def calcular_acerto(resultados_por_pergunta, perguntas):
    respondiveis = [p for p in perguntas if p["tipo"] in RESPONDIVEIS]
    acertos = sum(
        1 for p in respondiveis
        if any(r["id"] in p["relevantes"] for r in resultados_por_pergunta[p["id"]][:3])
    )
    return acertos, len(respondiveis), round(acertos / len(respondiveis) * 100, 1)


def rodar_versao(versao, cliente, ef, base, cfg):
    print(f"\n=== Versão {versao} ===")
    col = abrir_colecao(versao, cliente, ef)
    perguntas = cfg["perguntas"]
    por_id = {p["id"]: p for p in perguntas}

    # a) semântica Top-3
    sem, linhas_a = {}, []
    for p in perguntas:
        sem[p["id"]] = buscar_semantica(col, p["pergunta"], k=3)
        for r in sem[p["id"]]:
            linhas_a.append({"pergunta_id": p["id"], "tipo": p["tipo"], "pergunta": p["pergunta"],
                             "rank": r["rank"], "id": r["id"], "categoria": r["categoria"],
                             "distancia": r["distancia"], "relevante": marca_relevante(r["id"], p),
                             "fonte": r["fonte"]})
    salvar_csv(f"a_semantica_top3_{versao}.csv", linhas_a)

    # b) lexical, mesma base, sem filtro
    lex, linhas_b = {}, []
    for p in perguntas:
        lex[p["id"]] = buscar_lexical(base, p["pergunta"], k=3, versao=versao)
        if not lex[p["id"]]:
            linhas_b.append({"pergunta_id": p["id"], "tipo": p["tipo"], "pergunta": p["pergunta"],
                             "rank": "", "id": "(nenhum)", "pontuacao": 0, "termos_em_comum": "",
                             "relevante": "nao" if p["tipo"] in RESPONDIVEIS else "n/a"})
        for r in lex[p["id"]]:
            linhas_b.append({"pergunta_id": p["id"], "tipo": p["tipo"], "pergunta": p["pergunta"],
                             "rank": r["rank"], "id": r["id"], "pontuacao": r["pontuacao"],
                             "termos_em_comum": r["termos_em_comum"],
                             "relevante": marca_relevante(r["id"], p)})
    salvar_csv(f"b_lexical_top3_{versao}.csv", linhas_b)

    # métrica
    metrica = []
    for nome, res in (("semantica", sem), ("lexical", lex)):
        acertos, total, pct = calcular_acerto(res, perguntas)
        metrica.append({"versao": versao, "abordagem": nome, "acertos": acertos,
                        "perguntas_respondiveis": total, "taxa_pct": pct})
        print(f"  {nome:9s}: {acertos}/{total} = {pct}%")
    salvar_csv(f"metrica_{versao}.csv", metrica)

    # c) variação do Top-K
    linhas_c = []
    for pid in cfg["top_k_experimento"]:
        p = por_id[pid]
        for k in (1, 3, 5):
            for r in buscar_semantica(col, p["pergunta"], k=k):
                linhas_c.append({"pergunta_id": pid, "top_k": k, "rank": r["rank"], "id": r["id"],
                                 "categoria": r["categoria"], "distancia": r["distancia"],
                                 "relevante": marca_relevante(r["id"], p)})
    salvar_csv(f"c_topk_{versao}.csv", linhas_c)

    # d) com e sem filtro
    f_cfg = cfg["filtro_experimento"]
    p = por_id[f_cfg["pergunta"]]
    linhas_d = []
    for filtro in (None, f_cfg["categoria"]):
        for r in buscar_semantica(col, p["pergunta"], k=3, categoria=filtro):
            linhas_d.append({"pergunta_id": p["id"], "pergunta": p["pergunta"],
                             "filtro": filtro or "(sem filtro)", "rank": r["rank"], "id": r["id"],
                             "categoria": r["categoria"], "distancia": r["distancia"]})
    salvar_csv(f"d_filtro_{versao}.csv", linhas_d)

    # e) evidência para limitações: compare as distâncias de Q7/Q8 com as respondíveis
    linhas_e = []
    for p in perguntas:
        rs = sem[p["id"]]
        linhas_e.append({"pergunta_id": p["id"], "tipo": p["tipo"], "top1_id": rs[0]["id"],
                         "top1_distancia": rs[0]["distancia"],
                         "top3_distancia_media": round(sum(r["distancia"] for r in rs) / len(rs), 4),
                         "top3_ids": " ".join(r["id"] for r in rs)})
    salvar_csv(f"e_limitacoes_{versao}.csv", linhas_e)
    return metrica


def main():
    configurar_saida_utf8()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--versao", choices=[*config.COLECOES, "todas"], default="todas")
    args = parser.parse_args()

    base = carregar_base()
    cfg = carregar_perguntas()
    cliente = obter_cliente()
    ef = obter_embedding_function()

    existentes = {c.name if hasattr(c, "name") else c for c in cliente.list_collections()}
    versoes = list(config.COLECOES) if args.versao == "todas" else [args.versao]
    faltando = [v for v in versoes if config.COLECOES[v] not in existentes]
    if faltando:
        raise SystemExit(f"Coleções não indexadas: {faltando}. Rode: python src/indexar.py")

    todas = []
    for v in versoes:
        todas.extend(rodar_versao(v, cliente, ef, base, cfg))

    if len(versoes) > 1:
        print("\n=== Antes x depois ===")
        salvar_csv("comparacao_antes_depois.csv", todas)


if __name__ == "__main__":
    main()
