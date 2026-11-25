# Caso RAG 2 — Q5 (parafrase)

**Pergunta:** Como impedir que a IA invente respostas, apoiando-a em documentos externos?  
**Top-K:** 3 | **Filtro:** nenhum | **Coleção:** conceitos_ia_v1

## 1. Resultados da busca

| # | id | categoria | distância | fonte |
|---|---|---|---|---|
| 1 | RAG-06 | rag | 0.6138 | Texto elaborado pelo autor com base em: Lewis et al. (2020), arXiv:2005.11401 |
| 2 | RAG-02 | rag | 0.6423 | Texto elaborado pelo autor com base em: Lewis et al. (2020), arXiv:2005.11401 |
| 3 | LLM-07 | llm | 0.6433 | Texto elaborado pelo autor com base em: Ji et al. (2023), arXiv:2202.03629 |

## 2. Contexto montado

```text
[RAG-06] (categoria: rag | fonte: Texto elaborado pelo autor com base em: Lewis et al. (2020), arXiv:2005.11401)
O prompt de um sistema RAG deve conter a pergunta do usuário, os trechos recuperados com suas fontes e instruções para que o modelo responda apenas com base nesse contexto, cite as fontes e avise quando a informação for insuficiente.

[RAG-02] (categoria: rag | fonte: Texto elaborado pelo autor com base em: Lewis et al. (2020), arXiv:2005.11401)
No artigo de Lewis e colegas (2020), o conhecimento guardado nos pesos do modelo é chamado de memória paramétrica, e o índice de documentos consultado é a memória não paramétrica. Unir as duas gerou respostas mais específicas e factuais.

[LLM-07] (categoria: llm | fonte: Texto elaborado pelo autor com base em: Ji et al. (2023), arXiv:2202.03629)
Alucinação é quando um modelo de linguagem gera um conteúdo fluente e convincente, mas falso ou sem apoio nas fontes. Fornecer documentos confiáveis como contexto é uma das estratégias usadas para reduzir esse problema.
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
[RAG-06] (categoria: rag | fonte: Texto elaborado pelo autor com base em: Lewis et al. (2020), arXiv:2005.11401)
O prompt de um sistema RAG deve conter a pergunta do usuário, os trechos recuperados com suas fontes e instruções para que o modelo responda apenas com base nesse contexto, cite as fontes e avise quando a informação for insuficiente.

[RAG-02] (categoria: rag | fonte: Texto elaborado pelo autor com base em: Lewis et al. (2020), arXiv:2005.11401)
No artigo de Lewis e colegas (2020), o conhecimento guardado nos pesos do modelo é chamado de memória paramétrica, e o índice de documentos consultado é a memória não paramétrica. Unir as duas gerou respostas mais específicas e factuais.

[LLM-07] (categoria: llm | fonte: Texto elaborado pelo autor com base em: Ji et al. (2023), arXiv:2202.03629)
Alucinação é quando um modelo de linguagem gera um conteúdo fluente e convincente, mas falso ou sem apoio nas fontes. Fornecer documentos confiáveis como contexto é uma das estratégias usadas para reduzir esse problema.

PERGUNTA: Como impedir que a IA invente respostas, apoiando-a em documentos externos?

RESPOSTA:
```
