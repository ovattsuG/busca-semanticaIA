# Busca semântica sobre conceitos de IA com ChromaDB + preparação de RAG

**Autor:** Gustavo (trabalho individual)
**Execução:** ChromaDB **local** (PersistentClient).

## 1. Problema
Estudantes de Engenharia de Software que começam a estudar IA aplicada (embeddings, bancos vetoriais, RAG, LLMs) perdem tempo procurando definições espalhadas em papers e documentações. O protótipo responde perguntas em linguagem natural recuperando trechos curtos e com fonte de uma base curada, e já prepara o prompt para um modelo gerador responder citando essas fontes.
**Quem usaria:** alunos e monitores de disciplinas de IA, como material de consulta rápida.

## 2. Base de conhecimento (`dados/base.json`)
- **36 trechos**, **4 categorias** (9 cada): `embeddings`, `bancos_vetoriais`, `rag`, `llm`.
- Campos: `id` (prefixo da categoria + número, ex. `EMB-01`), `categoria`, `titulo`, `texto`, `fonte`.
- **Seleção:** um conceito por trecho, escolhido a partir do material de apoio (documentação do Chroma, model card do modelo, paper de RAG) e de papers clássicos citados nele (Word2Vec, Sentence-BERT, Transformer, HNSW…).
- **Autoria:** os textos foram escritos pelo autor com as próprias palavras; o campo `fonte` indica o material de base.
- **Divisão (chunking):** cada trecho tem uma ideia só e até 45 palavras. O modelo trunca entradas acima de **128 tokens**; `src/validar_base.py` mede cada trecho com o tokenizer do próprio modelo e grava `resultados/tokens_por_trecho.csv`.

## 3. Decisões técnicas
| Item | Valor |
|---|---|
| Modelo de embeddings | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (multilíngue, inclui português) |
| Dimensão | 384 (o `indexar.py` confere ao iniciar) |
| Limite de entrada | 128 tokens |
| Métrica | `cosine` (`configuration={"hnsw": {"space": "cosine"}}`; o padrão do Chroma é `l2`) |
| Distância exibida | distância cosseno = 1 − similaridade (menor = mais parecido) |
| Mesmo modelo p/ docs e perguntas | sim: a embedding function fica ligada à coleção e `query_texts` usa ela |

**Onde roda cada parte:** o código Python, o modelo de embeddings (baixado do Hugging Face na 1ª execução e depois usado offline, em CPU) e o banco (pasta `chroma_db/`) rodam todos na máquina local.

## 4. Como executar
Testado com Python 3.12.10 (chromadb 1.5.9, sentence-transformers 6.3.0). No Windows, se o `pip` falhar ao instalar o `torch`, use Python 3.12.

> **Importante:** o banco (`chroma_db/`) **não vem no repositório**. É preciso rodar `src/indexar.py` uma vez antes de `buscar.py`, `experimentos.py` ou `rag.py`.
> A 1ª execução precisa de **internet** para instalar as dependências e baixar o modelo (~470 MB do Hugging Face). Depois disso, tudo roda offline.

### Opção rápida (Windows)
```powershell
git clone https://github.com/ovattsuG/busca-semanticaIA.git
cd busca-semanticaIA
rodar_tudo.bat
```
O script cria o `.venv`, instala as dependências, valida a base, indexa no Chroma, roda os experimentos e gera os casos de RAG em `resultados/`.

### Passo a passo (qualquer sistema)
```powershell
git clone https://github.com/ovattsuG/busca-semanticaIA.git
cd busca-semanticaIA
python -m venv .venv
.venv\Scripts\activate            # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

python src/validar_base.py         # 1) checa base e tokens (1ª vez baixa o modelo)
python src/indexar.py              # 2) cria as coleções v1 e v2 (só insere se estiverem vazias)
python src/buscar.py "O que é um embedding?" --k 3
python src/buscar.py "Como funciona a busca?" --k 3 --categoria bancos_vetoriais
python src/buscar.py               # modo interativo (:k 5, :cat rag, :cat, :sair)
python src/lexical.py "O que é um embedding?"
python src/experimentos.py         # 3) gera todos os CSVs em resultados/
python src/rag.py --casos          # 4) gera os 3 casos de RAG em resultados/*.md
```

### Prova de persistência
1. `python src/indexar.py` → "36 registros inseridos".
2. Feche o terminal.
3. Abra outro terminal e rode `python src/buscar.py "O que é RAG?"`. A primeira linha mostra a coleção carregada do disco com 36 registros, **sem reinserção**. `buscar.py` não tem nenhum `add`. Rodar `indexar.py` de novo também não duplica: ele informa "já existe… Nada inserido".

## 5. Experimentos (`dados/perguntas.json`)
8 perguntas: Q1–Q4 diretas, Q5–Q6 paráfrases, Q7 ambígua, Q8 fora de escopo. **O gabarito de relevantes de Q1–Q6 foi definido antes da execução** e fica no próprio JSON.

| Exp. | Arquivo |
|---|---|
| a) semântica Top-3 | `a_semantica_top3_v1.csv` |
| b) lexical | `b_lexical_top3_v1.csv` |
| Métrica (% com ≥1 relevante no Top-3, Q1–Q6) | `metrica_v1.csv` |
| c) Top-1/3/5 (Q1 e Q5) | `c_topk_v1.csv` |
| d) com/sem filtro (Q7, `bancos_vetoriais`) | `d_filtro_v1.csv` |
| e) limitações: distâncias por pergunta | `e_limitacoes_v1.csv` |
| Antes × depois da melhoria | `comparacao_antes_depois.csv` |

**Métrica:** acertos = nº de perguntas (entre as 6 respondíveis) com pelo menos um trecho relevante no Top-3; taxa = acertos / 6 × 100.

### Regra da busca por palavras-chave (`src/lexical.py`)
1. Converte para minúsculas e remove acentos.
2. Remove pontuação: tudo que não é letra ou dígito vira espaço.
3. Remove stopwords do português (lista no código). Sem isso, palavras como "o", "que" e "é" casam com quase todos os trechos.
4. A pontuação de cada trecho é o número de termos **distintos** da consulta que aparecem nele.
5. Retorna até 3 trechos com pontuação ≥ 1. Empates são desfeitos pelo id.

### Melhoria: título prefixado ao texto (v2)
**Hipótese:** cada trecho fala de um conceito, mas nem sempre repete o nome dele (ex.: o trecho do mean pooling não diz "vetor da frase" no começo). Indexar `"<título>. <texto>"` põe o termo-chave no embedding, o que deve aproximar perguntas diretas do trecho certo.
**Como avaliar:** a coleção `conceitos_ia_v2` usa a mesma base, o mesmo modelo e as mesmas 8 perguntas. As duas abordagens recebem o mesmo texto. O resultado está em `comparacao_antes_depois.csv`, e vale também se não houver melhora.

## 6. Conexão com RAG (`src/rag.py`)
O programa recupera os trechos, monta o **contexto** (texto + id + categoria + fonte) e o **prompt** com: pergunta; trechos; instrução para responder só com base no contexto; citar fontes pelo id; e escrever uma frase fixa quando o contexto for insuficiente. Casos gerados: Q1 (direta), Q5 (paráfrase), Q8 (fora de escopo). O envio a um LLM não é feito (é opcional na atividade). Diagrama do fluxo em `docs/fluxo.md`.

## 7. Limitações conhecidas
- A busca vetorial **sempre** devolve K resultados. Na Q8 (preço do Chroma Cloud) ela traz trechos sobre o Chroma Cloud que **não** têm preço. Por isso o prompt instrui o gerador a reconhecer falta de informação.
- Não há limiar de distância para descartar resultados. Um limiar fixo precisaria ser calibrado com mais perguntas do que as 8 do experimento.
- Base pequena (36 trechos): as métricas servem para comparar abordagens, não para estimar o desempenho em produção.
- `PersistentClient` é indicado pela documentação do Chroma para desenvolvimento e testes. Em produção, a recomendação é um servidor Chroma ou o Chroma Cloud.

## 8. Estrutura
```
dados/        base.json, perguntas.json
src/          config, comum, validar_base, indexar, buscar, lexical, experimentos, rag
resultados/   CSVs e casos de RAG (gerados)
docs/         fluxo.md, analise_resultados.md
chroma_db/    banco local (gerado; fora do Git)
```

## Referências
- Chroma — https://docs.trychroma.com/
- Modelo — https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- Lewis et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*. arXiv:2005.11401
