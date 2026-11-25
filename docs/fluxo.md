# Fluxo da solução

```mermaid
flowchart LR
    subgraph Indexação["Indexação (src/indexar.py, roda 1 vez)"]
        A[dados/base.json<br/>36 trechos + metadados] --> B[Modelo de embeddings<br/>paraphrase-multilingual-MiniLM-L12-v2<br/>384 dimensões, CPU local]
        B --> C[(ChromaDB local<br/>PersistentClient ./chroma_db<br/>HNSW, métrica cosine)]
    end
    subgraph Consulta["Consulta (src/buscar.py, src/rag.py)"]
        P[Pergunta do usuário] --> B2[Mesmo modelo de embeddings]
        B2 --> Q[query: Top-K + filtro where categoria]
        C --> Q
        Q --> R[Trechos recuperados<br/>id, fonte, distância]
        R --> CT[Montagem do contexto<br/>texto + fonte]
        CT --> PR[Prompt: pergunta + contexto<br/>+ fundamentar, citar fontes,<br/>avisar se insuficiente]
        PR --> G[Modelo gerador LLM<br/>opcional, fora do escopo obrigatório]
    end
```

Versão em texto (para o slide do vídeo, se o Mermaid não renderizar):

```
base.json ─► [embeddings] ─► ChromaDB (disco)
                                   │
pergunta ─► [mesmo modelo] ─► query Top-K (+ filtro) ─► trechos + fontes
                                                          │
                                             contexto + instruções ─► PROMPT ─► (LLM gerador)
```

Para gerar uma imagem: cole o bloco mermaid em https://mermaid.live e exporte PNG.
