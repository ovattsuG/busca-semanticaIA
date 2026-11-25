# Análise dos resultados

Execução com o modelo **real** (`paraphrase-multilingual-MiniLM-L12-v2`) em 24/11/2026, via `rodar_tudo.bat`
(Python 3.12.10, chromadb 1.5.9, sentence-transformers 6.3.0, CPU).
Todos os números abaixo foram copiados de `resultados/*.csv`. Distância = distância cosseno (menor = mais parecido).

## 0. Base e tokens (`tokens_por_trecho.csv`)
- 36 trechos, todos com `dentro_do_limite = sim`.
- Maior trecho: **66 tokens** na v1 (EMB-04 e RAG-04) e **76 tokens** na v2 (EMB-04, já com o título).
  Nenhum chega perto do limite de 128 tokens, então nenhum trecho foi truncado.

## 1. Métrica: semântica × lexical (`metrica_v1.csv`)

| Abordagem | Acertos (Q1–Q6) | Taxa |
|---|---|---|
| Semântica Top-3 | 6/6 | **100,0%** |
| Lexical (até 3) | 5/6 | **83,3%** |

**Onde a lexical falhou: Q6 (paráfrase).** A pergunta "De quantos números é formado o vetor..." devolveu
EMB-04 (3 termos: *frase gera modelo*), EMB-07 (3: *frase modelo vetor*) e EMB-01 (2: *numeros vetor*). Nenhum dos três é relevante.
O trecho certo (EMB-05) diz "converte **frases** e parágrafos em **vetores** de 384 dimensões". A regra não reduz
as palavras ao radical, então "frase" ≠ "frases" e "vetor" ≠ "vetores", e a pergunta não usa "dimensões". A semântica pôs EMB-05
no Top-3 (rank 3, dist. 0,4458), porque compara o sentido e não a grafia.
*(Verificação extra, reproduzível: `python src/lexical.py "<Q6>" --k 5` mostra que, na v1, EMB-05 não aparece nem no Top-5.)*

**Mesmo quando acerta, a lexical ordena mal:**
- Q4 "O que significa RAG?": todos os três trechos casam só "rag" (pontuação 1). O desempate é pelo id, então
  LLM-06 e LLM-08 ficam na frente e o relevante RAG-01 cai para o **3º lugar**. A semântica põe RAG-01 em 1º (0,5482).
- Q1: os três resultados lexicais têm pontuação 1 (*embedding*). O relevante (EMB-01) só vem em 1º porque o id dele é o menor na ordem alfabética.
- Q5 (paráfrase): a lexical acerta com RAG-02 (*documentos respostas*), mas o 2º lugar é VET-01 (*documentos ia*),
  que fala do ChromaDB. A semântica trouxe **3 relevantes em 3** (RAG-06, RAG-02, LLM-07).

**Precisão no Top-3 (relevantes encontrados / 3), semântica v1:** Q1 1/3, Q2 1/3, Q3 1/3, Q4 1/3, Q5 3/3, Q6 1/3.
A métrica oficial ("≥1 relevante no Top-3") esconde que, na maioria das perguntas, 2 dos 3 trechos são ruído.

## 2. Top-K: Q1 e Q5 (`c_topk_v1.csv`)

| Pergunta | K=1 | K=3 | K=5 |
|---|---|---|---|
| Q1 (1 relevante no gabarito) | EMB-01 ✔ (0,3691) | +RAG-05, LLM-04 ✘ | +LLM-09, RAG-01 ✘ |
| relevantes / K | 1/1 | 1/3 | 1/5 |
| Q5 (4 relevantes no gabarito) | RAG-06 ✔ (0,6138) | +RAG-02 ✔, LLM-07 ✔ | +EMB-09 ✘, RAG-07 ✘ |
| relevantes / K | 1/1 | 3/3 | 3/5 |
| cobertura do gabarito Q5 | 1/4 | 3/4 | 3/4 |

- **Q1 (direta):** K=1 já basta. Aumentar o K só acrescenta trechos não relevantes, e a precisão cai de 1/1 para 1/5.
  O 1º lugar se destaca: 0,3691 contra 0,5367 do 2º.
- **Q5 (paráfrase):** a resposta está espalhada em vários trechos, então K=3 traz 3 dos 4 relevantes. K=5 não acrescenta nenhum
  (RAG-01 não aparece nem no Top-5) e põe dois irrelevantes. As distâncias ficam muito próximas
  (0,6138 a 0,6691 no Top-5), sinal de que o modelo não separa bem o certo do errado nessa pergunta.
- Conclusão: o K ideal depende da pergunta. K=3 foi um bom meio-termo nos dois casos. Num RAG, um K maior também
  gasta mais da janela de contexto do gerador (LLM-06).

## 3. Filtro por categoria: Q7 "Como funciona a busca?" (`d_filtro_v1.csv`)

| Rank | Sem filtro | `categoria = bancos_vetoriais` |
|---|---|---|
| 1 | RAG-08 (rag) 0,4836 | VET-07 0,5937 |
| 2 | VET-07 (bancos_vetoriais) 0,5937 | VET-06 0,6292 |
| 3 | RAG-07 (rag) 0,6173 | VET-08 0,7217 |

- O filtro **muda a interpretação da pergunta**: sem filtro, o resultado favorece "busca lexical × semântica" (RAG-08).
  Com o filtro, aparecem a consulta Top-K (VET-07) e o índice HNSW (VET-06), duas das interpretações previstas em
  `perguntas.json`. O VET-06 nem aparecia no Top-3 sem filtro.
- A distância de VET-07 é a mesma nos dois casos (0,5937). O filtro **só restringe os candidatos**, não muda o embedding
  nem a distância.
- Efeito colateral: para completar 3 resultados, o filtro inclui VET-08 com 0,7217, **a maior distância de todos
  os experimentos v1**. O filtro garante a categoria, mas não a relevância.

## 4. Limitações: Q7 (ambígua) e Q8 (fora de escopo) (`e_limitacoes_v1.csv`)

| Pergunta | tipo | Top-1 | dist. Top-1 | média Top-3 |
|---|---|---|---|---|
| Q1 | direta | EMB-01 | 0,3691 | 0,5135 |
| Q2 | direta | VET-01 | 0,2624 | 0,3742 |
| Q3 | direta | VET-05 | 0,1672 | 0,3020 |
| Q4 | direta | RAG-01 | 0,5482 | 0,5939 |
| Q5 | paráfrase | RAG-06 | 0,6138 | 0,6331 |
| Q6 | paráfrase | EMB-04 | 0,4326 | 0,4396 |
| **Q7** | ambígua | RAG-08 | **0,4836** | 0,5649 |
| **Q8** | fora de escopo | VET-04 | **0,4523** | 0,5846 |

- **O Top-K sempre devolve algo.** A Q8 pergunta o preço do Chroma Cloud, informação que não existe na base, e mesmo assim
  recebeu 3 trechos. O 1º (VET-04, "Chroma Cloud") é do assunto certo, mas só fala de `CloudClient`, tenant,
  database e chave de API, **sem nenhum preço**. Ser o trecho mais próximo não significa ter a informação.
- **A distância não separa o que tem resposta do que não tem.** A distância Top-1 da Q8 (0,4523) é **menor** que a das
  perguntas respondíveis Q4 (0,5482) e Q5 (0,6138), e quase igual à da Q6 (0,4326). Para que Q4 e Q5 passassem,
  um limiar fixo teria de aceitar distâncias de até 0,6138, e aí a Q8 também passaria. Com estes dados, **nenhum limiar
  separa Q8 das respondíveis**. Por isso o prompt do RAG manda o gerador dizer quando o contexto é insuficiente.
- **Q7 (ambígua):** recebe uma resposta "confiante" (0,4836, melhor que Q4 e Q5) sobre **uma** das interpretações
  (lexical × semântica), mas o usuário podia querer saber do HNSW ou da consulta Top-K. O sistema não percebe que a
  pergunta é ambígua. Na prática ele só escolhe uma leitura, e o filtro (seção 3) é uma forma de o usuário indicar qual quer.
- A lexical tem a mesma falha na Q8: devolveu VET-04 por causa de *chroma cloud* (`b_lexical_top3_v1.csv`), embora
  o trecho também não tenha preço.

## 5. Antes × depois da melhoria v2 (título prefixado) (`comparacao_antes_depois.csv`, `*_v2.csv`)

**Métrica oficial: sem mudança.** Semântica 6/6 = 100,0% e lexical 5/6 = 83,3% nas duas versões.
A métrica já estava no teto na v1 e não consegue mostrar ganho. Abaixo dela, porém, a v2 mudou bastante:

| Pergunta | Top-1 v1 (dist.) | Top-1 v2 (dist.) | Efeito |
|---|---|---|---|
| Q1 | EMB-01 ✔ 0,3691 | EMB-01 ✔ 0,2939 | melhor (mais próximo) |
| Q2 | VET-01 ✔ 0,2624 | VET-01 ✔ 0,1683 | melhor, e **VET-02 ✔ entrou no Top-3** (1/3 → 2/3) |
| Q3 | VET-05 ✔ 0,1672 | VET-05 ✔ 0,1718 | praticamente igual |
| Q4 | RAG-01 ✔ 0,5482 | RAG-01 ✔ 0,3814 | melhor |
| Q5 | RAG-06 ✔ 0,6138 | **EMB-09 ✘** 0,6156 | **pior**: Top-3 cai de 3/3 para 1/3 |
| Q6 | EMB-04 ✘ 0,4326 | **EMB-05 ✔** 0,4381 | melhor: o relevante sobe do 3º para o 1º lugar |

- **Ganho nas perguntas diretas, como a hipótese previa.** Q1, Q2 e Q4 ficaram mais próximas do trecho certo, porque o
  título repete o termo da pergunta ("O que é um embedding", "O que é o ChromaDB", "Definição de RAG").
  Q6 também melhorou: o título "Dimensão do modelo multilíngue MiniLM" aproximou EMB-05 da pergunta.
- **Resultado inesperado: Q5 piorou.** Na v2, o 1º lugar é EMB-09, título "Mesmo modelo para **documentos** e perguntas",
  que casa com "documentos externos" da pergunta, mas fala de outro assunto. RAG-06 ganhou o título "Prompt em um sistema RAG",
  que não lembra a pergunta, e caiu para o 5º lugar (0,6553 em `c_topk_v2.csv`). No Top-3 da v2 sobrou só LLM-07.
  Prefixar o título ajuda quando ele repete as palavras da pergunta e atrapalha nas paráfrases, que usam outras palavras.
- **Top-K na v2 (`c_topk_v2.csv`):** na Q5, K=1 erra (0/1) e K=3 dá 1/3. Com K=5 voltam RAG-02 e RAG-06 (3/5). Na v2, um K
  maior compensa a perda de ordenação.
- **Filtro na v2 (`d_filtro_v2.csv`):** mesmo comportamento da v1. Com o filtro, aparecem VET-07, VET-06 e VET-08 (0,6009 / 0,6384 / 0,7028).
- **Limitação continua na v2 (`e_limitacoes_v2.csv`):** Q8 Top-1 = 0,4520, ainda mais próximo que o Top-1 da
  respondível Q5 (0,6156). Continua sem limiar possível, e a melhoria não resolve o "sempre devolve algo".
- **Lexical v2:** mesmos resultados nos CSVs. Na Q6, o título acrescenta "multilingue" e EMB-05 sobe para 2 pontos,
  mas empata com EMB-01 e perde no desempate pelo id (fica em 5º lugar segundo `src/lexical.py --k 5 --versao v2`).

**Conclusão da melhoria:** taxa igual (100% → 100%), distâncias menores nas perguntas diretas, um relevante a mais em Q2,
Q6 corrigida no Top-1, Q5 piorou. É uma troca, não um ganho garantido. Para avaliar de verdade, seria preciso
uma métrica mais fina (precisão@3 ou posição do 1º relevante) e mais perguntas.

## 6. Casos RAG: o que cada prompt deveria gerar (`resultados/rag_caso*.md`, coleção v1, K=3)

### Caso 1: Q1 direta, "O que é um embedding?"
Contexto: EMB-01 (0,3691), RAG-05 (0,5367), LLM-04 (0,6346).
**Resposta esperada:** um embedding é uma representação numérica de um texto em forma de vetor de números reais.
Textos com significados parecidos ficam próximos nesse espaço, o que permite comparar frases pelo sentido
e não só pelas palavras **[EMB-01]**. RAG-05 (chunking) e LLM-04 (tokenização) não respondem à pergunta e não deveriam
ser citados. Isso mostra que o gerador precisa ignorar o ruído do Top-3.

### Caso 2: Q5 paráfrase, "Como impedir que a IA invente respostas, apoiando-a em documentos externos?"
Contexto: RAG-06 (0,6138), RAG-02 (0,6423), LLM-07 (0,6433), os 3 do gabarito.
**Resposta esperada:** o problema se chama alucinação, quando o modelo gera conteúdo convincente mas sem apoio
nas fontes, e uma das formas de reduzi-lo é fornecer documentos confiáveis como contexto **[LLM-07]**. Num RAG,
o prompt traz a pergunta, os trechos recuperados com as fontes e instruções para responder só com base neles,
citar as fontes e avisar quando a informação for insuficiente **[RAG-06]**. Lewis et al. (2020) mostraram que juntar
a memória paramétrica com um índice de documentos (memória não paramétrica) gera respostas mais específicas e
factuais **[RAG-02]**. A recuperação funcionou mesmo sem a pergunta usar as palavras "RAG" ou "alucinação".

### Caso 3: Q8 fora de escopo, "Quanto custa por mês o plano pago do Chroma Cloud?"
Contexto: VET-04 (0,4523), VET-01 (0,6353), VET-08 (0,6661).
**Resposta esperada:** exatamente *"O contexto fornecido não contém informação suficiente para responder a esta pergunta."*
O VET-04 fala do Chroma Cloud, mas não tem preço. Um gerador que inventasse um valor estaria alucinando, e este é
o caso que testa a instrução nº 4 do prompt. Vale notar que o VET-04 tem distância menor que a do 1º lugar de Q4 e Q5
(seção 4), então o recuperador sozinho não percebe que não há resposta.

## 7. Resumo
1. A semântica superou a lexical (100% × 83,3%). A diferença apareceu na paráfrase Q6 e na ordenação de Q4.
2. A métrica "≥1 relevante no Top-3" bateu no teto e esconde diferenças de precisão e de ordenação.
3. Top-K: K=1 basta para a pergunta direta, e a paráfrase precisa de K≥3.
4. O filtro troca a interpretação da pergunta ambígua, mas pode forçar trechos distantes (0,7217).
5. A distância não indica se há resposta: a Q8 (0,4523) fica mais próxima que perguntas respondíveis.
6. A melhoria v2 deixou a taxa igual, melhorou as diretas e Q6 e piorou Q5.
