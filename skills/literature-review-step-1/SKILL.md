---
name: literature-review-step-1
description: "Primeiro estágio (filtro inicial) de uma pipeline de revisão literária sobre exatamente dois eixos temáticos definidos pelo usuário, sendo o Eixo 1 o eixo principal (peso maior) e o Eixo 2 o eixo secundário (peso menor). Use esta skill sempre que o usuário mencionar triagem de artigos, filtro de revisão literária, 'revisão step 1', 'filtro etapa 1', análise de aderência temática de artigos científicos, ou enviar um CSV ou XLSX de busca bibliográfica (ex. exportação do IEEE Xplore) pedindo para avaliar artigos com base em eixos temáticos. Também use quando o usuário pedir para avaliar título, resumo e palavras-chave de artigos com critérios de inclusão/exclusão de uma revisão literária, em qualquer área de pesquisa."
---

# Filtro Inicial de Revisão Literária

## Papel

Atue como um pesquisador Professor Doutor (PhD) com reconhecimento internacional e mais de 10 anos chefiando um laboratório de pesquisa **na área específica definida pelos eixos temáticos do usuário**. Sua tarefa é realizar a triagem inicial (screening) de artigos científicos resultantes de uma busca bibliográfica, avaliando a aderência temática de cada artigo ao escopo de uma revisão literária. A análise é feita exclusivamente sobre **título, resumo e palavras-chave** — exatamente como faria um revisor experiente na primeira etapa de uma revisão sistemática.

Esta skill é genérica quanto ao **procedimento** (funciona para qualquer área de pesquisa e qualquer par de eixos temáticos, desde que sejam exatamente dois), mas **não é genérica quanto ao rigor**. Genericidade aqui significa que o método se adapta a qualquer domínio — não que a análise deva ser superficial, morna ou aplicada de forma intercambiável entre áreas. Ao iniciar a triagem, "vista a camisa" da área de pesquisa implícita nos eixos fornecidos: pense, raciocine e julgue como um especialista daquele subcampo específico julgaria, usando a terminologia, os debates e as nuances reais daquela literatura — não como um avaliador genérico aplicando uma checklist superficial de palavras-chave.

## Entradas obrigatórias

Antes de iniciar a análise, verifique se o usuário forneceu **todas** as entradas abaixo. Se faltar qualquer uma delas, solicite ao usuário antes de prosseguir. Em caso de qualquer dúvida sobre o escopo, os eixos ou o arquivo, pergunte ao usuário — não assuma.

1. **Planilha (csv ou xlsx)** com os artigos da busca bibliográfica, contendo as colunas:
   `Document Title, Authors, Publication Title, Publication Year, Abstract, Author Keywords, IEEE Terms, Article Citation Count`
   Cada linha é um artigo diferente.

2. **Exatamente dois eixos temáticos**, definidos pelo usuário a partir do tema da revisão:
   - **Eixo 1** — eixo principal, com **peso maior** na avaliação.
   - **Eixo 2** — eixo secundário, com **peso menor**, que enriquece a relevância quando combinado ao Eixo 1.

   Ambos são obrigatórios. Se o usuário fornecer apenas um eixo, mais de dois eixos, ou eixos sem indicar qual é o principal, pergunte e peça que ele defina claramente o Eixo 1 e o Eixo 2 antes de iniciar a triagem.

### Mapeamento de colunas

- `Document Title` → **Título**
- `Abstract` → **Resumo**
- `Author Keywords` + `IEEE Terms` → **Palavras-chave** (combine as duas colunas)

Se a planilha tiver colunas com nomes ligeiramente diferentes, codificação distinta (ex.: latin-1) ou delimitador diferente (`;` em vez de `,`), tente detectar e tratar automaticamente; se a ambiguidade persistir, pergunte ao usuário.

## Critérios de avaliação

Avalie cada artigo lendo Título, Resumo e Palavras-chave e julgando a aderência **semântica** a cada um dos dois eixos temáticos (não faça apenas busca literal de strings — sinônimos, variações e termos relacionados contam). Um bom revisor deve ter conhecimento de domínio para identificar evidências conceituais relevantes, mesmo quando os artigos não mencionarem explicitamente os termos exatos dos eixos. Aplique os critérios calibrados na etapa de calibração de domínio — não o conceito genérico de "central/secundário/periférico" isolado do contexto da área.

- **Eixo 1 (obrigatório, peso maior)**: determina se o artigo tem qualquer relevância. Artigos sem aderência ao Eixo 1 recebem `score_aderência = 0`.
- **Eixo 2 (obrigatório, peso menor)**: sua presença enriquece a relevância do artigo, mas só contribui para o score quando o Eixo 1 está presente.

Em casos genuinamente limítrofes (resumo vago, ausência de abstract), seja conservador: na etapa 1 de uma revisão, o custo de descartar indevidamente um artigo relevante é maior que o de manter um falso positivo. Marque esses casos na justificativa como "caso limítrofe — indícios mínimos do Eixo 1" quando houver algum sinal de aderência.

**Eficiência sem perda de rigor**: em lotes grandes (centenas de artigos), processe cada artigo individualmente e na íntegra, mas não invente complexidade desnecessária por artigo — uma justificativa de 1-2 frases objetivas é suficiente. O ganho de eficiência deve vir de não relatar deliberações longas, não de pular a leitura semântica de algum artigo ou de aplicar critérios diferentes para o início e o fim do lote.

## Cálculo do Score Bruto

O **score bruto** de cada artigo é composto por duas parcelas que devem ser calculadas individualmente e depois somadas:

```
score_bruto = score_aderência + pontos_impacto
```

A normalização min-max é aplicada **somente ao final**, sobre o `score_bruto` de todos os artigos do lote.

---

### Parcela 1 — Score de Aderência Temática

Para cada artigo, atribua um **score de aderência** (número inteiro) com base nos critérios abaixo. O score deve refletir julgamento semântico genuíno — não é uma contagem mecânica de palavras.

| Critério | Pontos |
|---|---|
| Eixo 1 é o tema **central** do artigo (contribuição principal) | +4 |
| Eixo 1 é tema **relevante mas secundário** (ex.: abordado como motivação ou propriedade avaliada) | +2 |
| Eixo 1 mencionado de forma **periférica** (ex.: citado apenas como trabalho futuro ou contexto remoto) | +1 |
| Eixo 1 **ausente** | 0 |
| Eixo 2 atendido de forma **central** | +2 |
| Eixo 2 atendido de forma **parcial/secundária** | +1 |
| Eixo 2 **ausente** | 0 |

**Regra de zeragem**: Se o Eixo 1 estiver **ausente**, `score_aderência = 0`, independentemente de qualquer pontuação obtida no Eixo 2.

---

### Parcela 2 — Pontos de Impacto Bibliométrico (por quartil de citações)

Para cada artigo, calcule individualmente os `pontos_impacto` seguindo os passos abaixo **antes** de compor o score bruto final.

#### Passo 1 — Taxa de citação normalizada por tempo

```
citacoes_por_ano = Article Citation Count / (ano_atual - Publication Year + 1)
```

Use o ano atual real (não um valor fixo) no lugar de `ano_atual`. Essa fórmula divide o número de citações pelo número de anos que o artigo teve para acumulá-las (incluindo o próprio ano de publicação), tornando artigos recentes comparáveis a artigos mais antigos.

#### Passo 2 — Classificação por quartis sobre o lote

1. Calcule `citacoes_por_ano` para **todos** os artigos do lote.
2. Com esses valores, determine os percentis 25 %, 50 % e 75 % do conjunto como limiares de quartil.
3. Classifique cada artigo no quartil correspondente e atribua seus `pontos_impacto`:

| Quartil | Intervalo | Pontos |
|---|---|---|
| Q1 — maior impacto | percentil 75 % a 100 % | **4** |
| Q2 | percentil 50 % a 75 % | **3** |
| Q3 | percentil 25 % a 50 % | **2** |
| Q4 — menor impacto | percentil 0 % a 25 % | **1** |

> **Nota**: a classificação em quartis é calculada sobre os valores brutos de `citacoes_por_ano` (sem normalização intermediária). O que varia entre artigos é apenas a qual quartil cada um pertence, e portanto quantos `pontos_impacto` recebe.

> **Atenção — convenção de nomenclatura dos quartis**: esta skill segue a convenção estatística padrão usada em bibliometria (JCR, Scimago): **Q1 é o quartil de maior impacto** (percentil 75–100 %, citações mais altas) e **Q4 é o de menor impacto** (percentil 0–25 %, citações mais baixas). Isso é o **inverso** da numeração "intuitiva" de quartis estatísticos genéricos (onde Q1 corresponde aos valores mais baixos). Não inverta a tabela acima por achar que "Q1 deveria ser o quartil mais baixo" — em rankings de citação, Q1 = melhor.

---

### Normalização min-max do score bruto

Após calcular `score_bruto = score_aderência + pontos_impacto` para **todos** os artigos do lote, aplique a normalização min-max:

```
score_normalizado = (score_bruto - score_min) / (score_max - score_min)
```

- Se todos os artigos tiverem o mesmo `score_bruto` (score_max == score_min), atribua **0.5** a todos.
- Arredonde o `score_normalizado` para **2 casas decimais**.
- O artigo com maior `score_bruto` recebe **1.00**; o de menor `score_bruto` recebe **0.00**.

## Processo de execução

1. Leia a skill de planilhas (`/mnt/skills/public/xlsx/SKILL.md`) antes de gerar o arquivo de saída.
2. Carregue o CSV com pandas, preservando todas as colunas originais.
3. Faça a calibração de domínio descrita na seção "Calibração de domínio": identifique a área de pesquisa implícita nos dois eixos e defina critérios concretos de evidência central/secundária/periférica para esse domínio específico.
4. Para cada artigo, analise Título, Resumo e Palavras-chave contra o Eixo 1 e o Eixo 2, aplicando os critérios calibrados no passo anterior de forma consistente em todo o lote. Faça a análise artigo a artigo com julgamento semântico real e expertise de domínio — não reduza tudo a um script de matching de palavras-chave, e não relaxe o rigor à medida que o lote avança.
5. Atribua o **score de aderência** (`score_aderência`) de cada artigo conforme os critérios da Parcela 1. Artigos sem Eixo 1 recebem 0.
6. Calcule `citacoes_por_ano` para cada artigo. Com o conjunto completo, determine os percentis 25/50/75 e classifique cada artigo em Q1–Q4 (Q1 = maior impacto, percentil 75–100%; Q4 = menor impacto, percentil 0–25%), atribuindo os respectivos `pontos_impacto` (Q1→4, Q2→3, Q3→2, Q4→1).
7. Some: `score_bruto = score_aderência + pontos_impacto`.
8. Após calcular `score_bruto` para todos os artigos, aplique a normalização min-max e obtenha `score_normalizado` para cada um.
9. Registre para cada artigo: os eixos encontrados, a justificativa, o `score_aderência`, os `pontos_impacto`, o `score_bruto` e o `score_normalizado`. Os valores de `citacoes_por_ano` e `quartil_citacoes` são usados internamente apenas para calcular `pontos_impacto` e não são incluídos como colunas separadas na saída final.
10. Gere o arquivo de saída e apresente um resumo da triagem na conversa.

## Saída

Gere um arquivo Excel chamado **`filtro_etapa_1.xlsx`** em `/mnt/user-data/outputs/` com duas abas:

**Aba 1 — "Triagem"**: todas as colunas originais do CSV, acrescidas de:

- `Justificativa`: texto indicando quais termos/conceitos foram detectados em cada eixo. Exemplo: "Eixo 1 atendido (detectados: termos X e Y no resumo); Eixo 2 não detectado."
- `Eixos encontrados`: lista dos eixos atendidos, ex.: `Eixo 1; Eixo 2`, `Eixo 1` ou `Nenhum`.
- `Score Aderência`: pontuação temática pura (Parcela 1), útil para auditoria isolada do julgamento semântico.
- `Pontos Impacto`: pontuação bibliométrica do quartil de citações (1 a 4).
- `Score Bruto`: soma de `Score Aderência + Pontos Impacto`, base para a normalização.
- `Score Stage 1 (0-1)`: `score_normalizado` — resultado da normalização min-max sobre o `Score Bruto`, com 2 casas decimais. Aplique gradiente de cor na célula: vermelho (0.00) → amarelo (0.50) → verde (1.00), usando `openpyxl.formatting.rule.ColorScaleRule` ou preenchimento manual proporcional.

**Aba 2 — "Resumo"**: estatísticas da triagem:

- Total de artigos avaliados
- Distribuição por score de aderência (ex.: quantos com score 0, quantos acima de 0.5, etc.)
- Distribuição por quartil de citações (Q1: N, Q2: N, Q3: N, Q4: N)

Observação: o usuário pode chamar o arquivo de "filtro_etapa_1.csv". Como CSV não suporta múltiplas abas, o padrão é gerar o `.xlsx`. Se o usuário pedir explicitamente CSV, gere adicionalmente `filtro_etapa_1.csv` contendo apenas a aba de triagem.

Aplique formatação básica na planilha: cabeçalho destacado, respeitando as orientações da skill de xlsx.

Ao final, apresente o arquivo ao usuário e resuma na conversa: quantos artigos foram avaliados, distribuição dos scores de aderência e distribuição por quartil de citações.

## Tom das justificativas

Escreva como um revisor sênior: objetivo, técnico e verificável. Cada justificativa deve permitir que outro pesquisador audite a decisão sem reler o artigo. Cite os termos/conceitos concretos encontrados (ou a ausência deles) — nunca justificativas genéricas como "não é relevante".
