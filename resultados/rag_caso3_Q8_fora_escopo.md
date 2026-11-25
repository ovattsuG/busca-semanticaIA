# Caso RAG 3 — Q8 (fora_escopo)

**Pergunta:** Quanto custa por mês o plano pago do Chroma Cloud?  
**Top-K:** 3 | **Filtro:** nenhum | **Coleção:** conceitos_ia_v1

## 1. Resultados da busca

| # | id | categoria | distância | fonte |
|---|---|---|---|---|
| 1 | VET-04 | bancos_vetoriais | 0.4523 | Texto elaborado pelo autor com base em: https://docs.trychroma.com/reference/python/client |
| 2 | VET-01 | bancos_vetoriais | 0.6353 | Texto elaborado pelo autor com base em: https://www.trychroma.com/ |
| 3 | VET-08 | bancos_vetoriais | 0.6661 | Texto elaborado pelo autor com base em: https://docs.trychroma.com/docs/querying-collections/metadata-filtering |

## 2. Contexto montado

```text
[VET-04] (categoria: bancos_vetoriais | fonte: Texto elaborado pelo autor com base em: https://docs.trychroma.com/reference/python/client)
O Chroma Cloud é a versão gerenciada do ChromaDB. A conexão é feita pelo CloudClient, que exige tenant, database e uma chave de API, normalmente lidos de variáveis de ambiente.

[VET-01] (categoria: bancos_vetoriais | fonte: Texto elaborado pelo autor com base em: https://www.trychroma.com/)
O ChromaDB é um banco de dados vetorial de código aberto voltado para aplicações de IA. Ele armazena documentos, seus embeddings e metadados, e permite buscar os registros mais próximos de uma consulta.

[VET-08] (categoria: bancos_vetoriais | fonte: Texto elaborado pelo autor com base em: https://docs.trychroma.com/docs/querying-collections/metadata-filtering)
O parâmetro where do ChromaDB filtra os registros pelos metadados. Por exemplo, um where com categoria igual a rag restringe a busca aos trechos dessa categoria. Há operadores como $eq, $in, $and e $or.
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
[VET-04] (categoria: bancos_vetoriais | fonte: Texto elaborado pelo autor com base em: https://docs.trychroma.com/reference/python/client)
O Chroma Cloud é a versão gerenciada do ChromaDB. A conexão é feita pelo CloudClient, que exige tenant, database e uma chave de API, normalmente lidos de variáveis de ambiente.

[VET-01] (categoria: bancos_vetoriais | fonte: Texto elaborado pelo autor com base em: https://www.trychroma.com/)
O ChromaDB é um banco de dados vetorial de código aberto voltado para aplicações de IA. Ele armazena documentos, seus embeddings e metadados, e permite buscar os registros mais próximos de uma consulta.

[VET-08] (categoria: bancos_vetoriais | fonte: Texto elaborado pelo autor com base em: https://docs.trychroma.com/docs/querying-collections/metadata-filtering)
O parâmetro where do ChromaDB filtra os registros pelos metadados. Por exemplo, um where com categoria igual a rag restringe a busca aos trechos dessa categoria. Há operadores como $eq, $in, $and e $or.

PERGUNTA: Quanto custa por mês o plano pago do Chroma Cloud?

RESPOSTA:
```
