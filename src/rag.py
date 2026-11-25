"""Monta o contexto e o prompt de RAG a partir dos trechos recuperados.

Uso:
  python src/rag.py "O que é um embedding?" [--k 3] [--categoria rag] [--versao v1]
  python src/rag.py --casos     # gera os 3 casos da atividade (direta, paráfrase, fora de escopo)

O envio ao modelo de linguagem é opcional na atividade e NÃO é feito aqui.
"""
import argparse

import config
from comum import abrir_colecao, buscar_semantica, carregar_perguntas, configurar_saida_utf8

MENSAGEM_INSUFICIENTE = "O contexto fornecido não contém informação suficiente para responder a esta pergunta."

MODELO_PROMPT = """Você é um assistente que responde perguntas sobre conceitos de Inteligência Artificial.

INSTRUÇÕES:
1. Responda usando SOMENTE as informações do CONTEXTO abaixo. Não use conhecimento próprio.
2. Fundamente cada afirmação em pelo menos um trecho do contexto.
3. Cite as fontes usadas com o identificador do trecho entre colchetes, por exemplo [EMB-01].
4. Se o contexto não tiver informação suficiente para responder, escreva exatamente:
   "{insuficiente}"
   e não invente uma resposta.

CONTEXTO:
{contexto}

PERGUNTA: {pergunta}

RESPOSTA:"""


def montar_contexto(resultados):
    blocos = [
        f"[{r['id']}] (categoria: {r['categoria']} | fonte: {r['fonte']})\n{r['texto']}"
        for r in resultados
    ]
    return "\n\n".join(blocos) if blocos else "(nenhum trecho recuperado)"


def montar_prompt(pergunta, resultados):
    return MODELO_PROMPT.format(insuficiente=MENSAGEM_INSUFICIENTE,
                                contexto=montar_contexto(resultados), pergunta=pergunta)


def relatorio_markdown(titulo, pergunta, resultados, k, categoria, versao):
    linhas = [f"# {titulo}", "", f"**Pergunta:** {pergunta}  ",
              f"**Top-K:** {k} | **Filtro:** {categoria or 'nenhum'} | **Coleção:** {config.COLECOES[versao]}", "",
              "## 1. Resultados da busca", "", "| # | id | categoria | distância | fonte |", "|---|---|---|---|---|"]
    linhas += [f"| {r['rank']} | {r['id']} | {r['categoria']} | {r['distancia']:.4f} | {r['fonte']} |"
               for r in resultados]
    linhas += ["", "## 2. Contexto montado", "", "```text", montar_contexto(resultados), "```",
               "", "## 3. Prompt para o modelo gerador", "", "```text", montar_prompt(pergunta, resultados), "```", ""]
    return "\n".join(linhas)


def gerar(col, pergunta, k, categoria, versao, titulo, arquivo=None):
    resultados = buscar_semantica(col, pergunta, k, categoria)
    md = relatorio_markdown(titulo, pergunta, resultados, k, categoria, versao)
    print(md)
    if arquivo:
        config.DIR_RESULTADOS.mkdir(exist_ok=True)
        caminho = config.DIR_RESULTADOS / arquivo
        caminho.write_text(md, encoding="utf-8")
        print(f"\n>> salvo em {caminho.relative_to(config.RAIZ)}\n")


def main():
    configurar_saida_utf8()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("pergunta", nargs="?")
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--categoria")
    parser.add_argument("--versao", choices=list(config.COLECOES), default="v1")
    parser.add_argument("--casos", action="store_true", help="gera os 3 casos exigidos na atividade")
    args = parser.parse_args()

    if not args.casos and not args.pergunta:
        parser.error("informe uma pergunta ou use --casos")
    if args.k < 1:
        parser.error("--k precisa ser >= 1")

    col = abrir_colecao(args.versao)
    if args.casos:
        cfg = carregar_perguntas()
        por_id = {p["id"]: p for p in cfg["perguntas"]}
        for n, pid in enumerate(cfg["rag_casos"], start=1):
            p = por_id[pid]
            gerar(col, p["pergunta"], args.k, None, args.versao,
                  f"Caso RAG {n} — {p['id']} ({p['tipo']})", f"rag_caso{n}_{p['id']}_{p['tipo']}.md")
    else:
        gerar(col, args.pergunta, args.k, args.categoria, args.versao, "Consulta RAG")


if __name__ == "__main__":
    main()
