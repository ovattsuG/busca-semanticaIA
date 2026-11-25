# Caso RAG 1 — Q1 (direta)

**Pergunta:** O que é um embedding?  
**Top-K:** 3 | **Filtro:** nenhum | **Coleção:** conceitos_ia_v1

## 1. Resultados da busca

| # | id | categoria | distância | fonte |
|---|---|---|---|---|
| 1 | EMB-01 | embeddings | 0.3691 | Texto elaborado pelo autor com base em: https://www.sbert.net/ |
| 2 | RAG-05 | rag | 0.5367 | Texto elaborado pelo autor com base em: https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 |
| 3 | LLM-04 | llm | 0.6346 | Texto elaborado pelo autor com base em: Kudo e Richardson (2018), arXiv:1808.06226 |

## 2. Contexto montado

```text
[EMB-01] (categoria: embeddings | fonte: Texto elaborado pelo autor com base em: https://www.sbert.net/)
Um embedding é uma representação numérica de um texto na forma de um vetor de números reais. Textos com significados parecidos ficam próximos nesse espaço vetorial, o que permite comparar frases pelo sentido e não apenas pelas palavras usadas.

[RAG-05] (categoria: rag | fonte: Texto elaborado pelo autor com base em: https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)
Chunking é a divisão dos documentos em trechos menores antes da indexação. Trechos muito longos misturam assuntos e podem ser truncados pelo modelo; trechos muito curtos perdem contexto. O ideal é que cada trecho trate de uma única ideia.

[LLM-04] (categoria: llm | fonte: Texto elaborado pelo autor com base em: Kudo e Richardson (2018), arXiv:1808.06226)
Tokenização é a divisão do texto em unidades menores, os tokens, que podem ser palavras inteiras ou pedaços de palavras. Ferramentas como o SentencePiece aprendem esse vocabulário de subpalavras diretamente do texto bruto.
```

## 3. Prompt para o modelo gerador

```text
Você é um assistente que responde perguntas sobre conceitos de Inteligência Artificial.

INSTRUÇÕES:
1. Responda usando SOMENTE as informações do CONTEXTO abaixo. Não use conhecimento próprio.
2. Fundamente cada afirmação em pelo menos um trecho do contexto.
3. Cite as fontes usadas com o identificador do trecho entre colchetes, por exemplo [EMB-01].
4. Se o contexto não tiver informação suficiente para responder, escreva exatamente:
   "O contexto fornecido não contém informação suficiente para responder a esta pergunta."
   e não invente uma resposta.

CONTEXTO:
[EMB-01] (categoria: embeddings | fonte: Texto elaborado pelo autor com base em: https://www.sbert.net/)
Um embedding é uma representação numérica de um texto na forma de um vetor de números reais. Textos com significados parecidos ficam próximos nesse espaço vetorial, o que permite comparar frases pelo sentido e não apenas pelas palavras usadas.

[RAG-05] (categoria: rag | fonte: Texto elaborado pelo autor com base em: https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)
Chunking é a divisão dos documentos em trechos menores antes da indexação. Trechos muito longos misturam assuntos e podem ser truncados pelo modelo; trechos muito curtos perdem contexto. O ideal é que cada trecho trate de uma única ideia.

[LLM-04] (categoria: llm | fonte: Texto elaborado pelo autor com base em: Kudo e Richardson (2018), arXiv:1808.06226)
Tokenização é a divisão do texto em unidades menores, os tokens, que podem ser palavras inteiras ou pedaços de palavras. Ferramentas como o SentencePiece aprendem esse vocabulário de subpalavras diretamente do texto bruto.

PERGUNTA: O que é um embedding?

RESPOSTA:
```
