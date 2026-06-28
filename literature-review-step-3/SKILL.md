---
name: literature-review-step-3
description: "Terceiro e último estágio de uma pipeline de revisão literária. Use sempre que o usuário mencionar 'revisão step 3', 'etapa 3 da revisão', 'ranking final de artigos', 'qualidade metodológica', 'avaliação de reprodutibilidade', ou fornecer a planilha da Etapa 2 (`filtro_etapa_2.xlsx`, com `Score Stage 1`, `Score Stage 2`, `Score Combinado`) junto com os PDFs íntegros dos artigos (`.zip` ou pasta do Google Drive) pedindo avaliar a qualidade metodológica e a reprodutibilidade ainda não cobertas, gerando o ranking final 0–10. NUNCA reprova ou remove artigos — aplica a poda da Etapa 2, localiza o PDF íntegro de cada artigo aprovado e lê o artigo completo (não só Abstract/Introduction/Conclusion) para pontuar quatro critérios (0, 1 ou 2,5 cada, soma 0–10): clareza metodológica, reprodutibilidade, comparação com o estado da arte e confiabilidade/disponibilidade. Normaliza por min-max sobre o lote, combina com `Score Stage 1`/`Score Stage 2` em um `Score Geral (0-10)` e ranqueia os artigos aprovados."
---

# Qualidade Metodológica e Reprodutibilidade — Estágio 3 de Revisão da Literatura

## Papel

Atue como um pesquisador Professor Doutor (PhD) com reconhecimento internacional e mais de 10 anos chefiando um laboratório de pesquisa **na área específica definida pelos eixos temáticos do usuário** (a mesma área já identificada nos Estágios 1 e 2). Sua tarefa é julgar a **qualidade metodológica e a reprodutibilidade** de cada artigo aprovado no Estágio 2 — não mais aderência temática, problemática ou originalidade/lacuna (já avaliadas nas Etapas 1 e 2), mas se o método descrito é claro, reprodutível, comparado com o estado da arte e validado de forma consistente em termos de confiabilidade/disponibilidade. Esta etapa não reavalia os critérios E1–E5 ou P1–P5 da Etapa 2: um artigo pode estar perfeitamente formulado (nota alta na Etapa 2) e ainda ter uma metodologia rasa ou pouco reprodutível (nota baixa nesta etapa), e vice-versa — são lentes diferentes sobre o artigo.

A lente desta etapa, porém, exige mais material do que as anteriores: clareza metodológica, reprodutibilidade, comparação com o estado da arte e confiabilidade/disponibilidade não podem ser julgadas com segurança apenas por `Abstract`, `Introduction` e `Conclusion` (o material já lido nas Etapas 1–2) — dependem do corpo completo do artigo (Metodologia/Proposta, Modelo de Falhas/Premissas do Sistema, Experimentos/Avaliação, Trabalhos Relacionados). Por isso esta etapa recebe o PDF íntegro de cada artigo aprovado — seja dentro de um `.zip` enviado pelo usuário, seja em uma pasta do Google Drive cujo link foi informado — e o lê por completo antes de pontuar — não se apoia só nas três seções já extraídas nas etapas anteriores.

Esta etapa **não filtra**: todo artigo aprovado no Estágio 2 (linha com `Score Combinado` preenchido) recebe pontuação e aparece no ranking final. Não há critério de exclusão nesta skill — divergir desse princípio é o erro mais grave que esta skill pode cometer.

---

## Visão geral do processo

1. **Filtragem** — mantém apenas artigos com `Score Combinado` preenchido na Etapa 2 (aplica poda opcional, se houver). Feita só com a planilha, antes de tocar no `.zip` — não vale a pena descompactar/ler PDFs de artigos que nem chegam a entrar nesta etapa.
2. **Cruzamento com o PDF íntegro** — para cada artigo que passou pela poda, localiza o PDF correspondente — dentro do `.zip` enviado ou na pasta do Google Drive informada (conforme a fonte usada) — por similaridade de título (mesma tolerância de cruzamento usada na Etapa 2) e extrai o texto completo do artigo. Ver "Cruzamento e leitura do PDF íntegro".
3. **Pontuação (C1–C4)** — quatro critérios independentes de qualidade metodológica, cada um aceitando apenas 0, 1 ou 2,5: Clareza Metodológica (C1), Reprodutibilidade (C2), Comparação com o Estado da Arte (C3) e Avaliação de Confiabilidade/Disponibilidade (C4), julgados sobre o texto integral do PDF (e não mais só Abstract/Introduction/Conclusion).
4. **Score Bruto 3 e normalização** — soma direta de C1–C4 (escala 0–10), depois normalizada por min-max **sobre o lote inteiro** (mesma lógica usada no `Score Stage 2` da Etapa 2) para gerar `Score Stage 3 (0-1)`.
5. **Score Geral (0-10) e Ranking** — combina `Score Stage 3` (peso maior) com `Score Stage 1` e `Score Stage 2`, herdados das duas etapas anteriores, converte o resultado para a escala 0–10 e ordena o ranking final.

---

## Entradas obrigatórias

1. **Planilha de saída do Estágio 2** (`filtro_etapa_2.xlsx`, aba "Resultado"), com as colunas `Score Stage 1 (0-1)`, `Score Stage 2`, `Score Combinado` e `Quartil` preenchidas para os artigos aprovados. Artigos com essas colunas em branco (reprovados em E1–E5) **não entram** nesta etapa — o critério de entrada continua sendo `Score Combinado` preenchido, mas o cálculo final desta etapa usa `Score Stage 1` e `Score Stage 2` diretamente (ver "Cálculo"), não o `Score Combinado` já agregado.
2. **Os PDFs íntegros dos artigos**, em uma das duas formas (qualquer uma serve; se ambas forem fornecidas, use o que estiver disponível primeiro e mencione na conversa qual fonte foi usada):
   - **Arquivo `.zip`** com os PDFs íntegros dos artigos. Pode conter mais artigos do que os aprovados (o cruzamento é por título, então PDFs extras no zip são simplesmente ignorados) e pode ter subpastas.
   - **Link de uma pasta do Google Drive** (ex.: `https://drive.google.com/drive/folders/<ID_DA_PASTA>`) contendo os PDFs íntegros. Mesma tolerância: pode ter mais arquivos do que os aprovados, e pode ter subpastas dentro da pasta informada.

   Em ambos os casos, cada artigo que passa pela poda precisa, idealmente, ter seu PDF localizável na fonte indicada — quando não localizar, não bloqueie o lote (ver "Cruzamento e leitura do PDF íntegro" para o fallback).
3. **Lista de eixos temáticos** (os mesmos dos Estágios 1 e 2) — apenas como contexto de área; não são repontuados aqui.

### Entrada opcional

- **Poda** por `Score Combinado` ou `Quartil` do Estágio 2 (ex.: processar só `Quartil` Q1/Q2). **Padrão: nenhuma** — processa todos os artigos aprovados.

Se qualquer entrada obrigatória faltar, pergunte antes de prosseguir.

---

## Cruzamento e leitura do PDF íntegro

Antes de tudo, identifique qual fonte de PDFs foi fornecida (zip, Drive, ou ambas — ver "Entradas obrigatórias") e siga a ramificação correspondente abaixo para obter a lista de arquivos disponíveis e seus conteúdos.

### Obtendo a lista de arquivos

**Fonte = `.zip`:** descompacte o arquivo em uma pasta de trabalho local e liste os PDFs (recursivamente, incluindo subpastas).

**Fonte = link de pasta do Google Drive:**
1. Extraia o ID da pasta a partir do link informado pelo usuário — é o trecho após `/folders/` (ex.: em `https://drive.google.com/drive/folders/1AbCdEfGhIjKlMnOp`, o ID é `1AbCdEfGhIjKlMnOp`; ignore qualquer parâmetro `?usp=...` no final).
2. Use a ferramenta `Google Drive:search_files` com a query `parentId = '<ID_DA_PASTA>' and mimeType contains 'pdf'` para listar os PDFs diretamente dentro da pasta. Se o usuário mencionar que há subpastas, repita a busca trocando `parentId` pelo ID de cada subpasta encontrada (liste subpastas com `parentId = '<ID_DA_PASTA>' and mimeType = 'application/vnd.google-apps.folder'`).
3. Pagine com `pageToken`/`next_page_token` se a pasta tiver muitos arquivos.
4. Se a busca não retornar nada (pasta vazia, ID errado, ou sem permissão de acesso), avise o usuário e pergunte se o link/permissões estão corretos antes de tratar todo o lote como fallback.

Se **ambas** as fontes foram fornecidas, monte a lista de candidatos a partir das duas (zip + Drive) antes de cruzar por título — um título pode estar em qualquer uma das duas.

### Cruzamento e extração (comum às duas fontes)

Depois da filtragem (poda), para cada artigo restante:

1. **Localizar o PDF.** Compare o título do artigo (coluna `Document Title` ou equivalente herdada da Etapa 1) com os nomes de arquivo disponíveis (no zip descompactado e/ou na listagem do Drive), tolerando diferenças de caixa, acentuação, truncamento e siglas — a mesma lógica de tolerância usada no cruzamento por título da Etapa 2. Em caso de ambiguidade entre dois arquivos candidatos, abra ambos e confirme pelo título/autores na primeira página antes de decidir.
2. **Obter o arquivo localmente.**
   - Zip: o PDF já está extraído na pasta de trabalho local.
   - Drive: baixe o conteúdo com `Google Drive:download_file_content` usando o `fileId` do candidato escolhido (retorna base64) e salve como PDF na pasta de trabalho local antes de extrair o texto.
3. **Extrair o texto integral.** Siga `/mnt/skills/public/pdf-reading/SKILL.md` para a estratégia de extração — `pdftotext -raw` é a primeira opção para artigos em duas colunas (IEEE/ACM), com `pypdf` como alternativa. Leia o artigo **completo**: Metodologia/Proposta, Modelo de Falhas/Premissas do Sistema, Experimentos/Avaliação e Trabalhos Relacionados costumam ser as seções mais relevantes para julgar os critérios C1–C4, além de Abstract/Introduction/Conclusion já conhecidos.
4. **PDF digitalizado ou sem camada de texto.** Se `pdftotext`/`pypdf` retornar vazio ou texto ilegível, siga a rota de OCR descrita em `pdf-reading` ("Scanned documents"). Se mesmo assim o texto não for recuperável, trate como "não localizado" (item 5).
5. **PDF não localizado (ou não recuperável em nenhuma das fontes).** Não bloqueie o lote: avance para o próximo artigo. Pontue os critérios C1–C4 com o material disponível na planilha (`Abstract`, `Introduction`, `Conclusion` herdados da Etapa 2) e registre a limitação na `Justificativa` (ex.: "PDF não localizado no zip/Drive — pontuação baseada apenas em Abstract/Introdução/Conclusão da Etapa 2"). Marque `PDF Íntegro Lido = Não` para esse artigo na saída (ver "Saída").

Esse cruzamento e leitura acontecem **só** sobre os artigos que sobreviveram à filtragem do passo 1 do processo — nunca descompacte/baixe/leia PDFs de artigos já podados.

---

## Critérios de Pontuação (0, 1 ou 2,5 por critério)

Avalie por significado, com a mesma terminologia e nível de exigência da subárea identificada nos eixos temáticos. Cada critério aceita **apenas três valores possíveis: 0, 1 ou 2,5** — não há notas intermediárias (sem 0,5, 1,5, 2 etc.). As tabelas abaixo são âncoras de julgamento, não uma escala lexical fina: a avaliação é deliberadamente grossa (ausente / parcial / pleno) para que o julgamento seja rápido e consistente entre artigos, sem forçar distinções sutis difíceis de defender. Toda nota se baseia em texto efetivamente presente no artigo — o PDF íntegro lido nesta etapa (Metodologia/Proposta, Modelo de Falhas/Premissas do Sistema, Experimentos/Avaliação, Trabalhos Relacionados, além de Abstract/Introduction/Conclusion já conhecidos; ou, no fallback sem PDF localizado em nenhuma das fontes, apenas estas três últimas seções) —, com a seção de origem identificada na `Justificativa` — nunca infira pelo título ou por suposição de prestígio do veículo/autores. Na dúvida entre 1 e 2,5, escolha 1: esta etapa existe para diferenciar os artigos mais fortes dentro de um lote já aprovado, e pontuação genericamente alta para todos anula a utilidade do ranking.

Os quatro critérios têm **peso igual** entre si — nenhum domina os demais, diferente do esquema de pesos desiguais usado nas Etapas anteriores, porque aqui avalia-se uma única dimensão (qualidade metodológica) sob quatro ângulos complementares, não dimensões concorrentes. O peso igual é garantido pelo próprio teto de cada critério (máximo 2,5 cada): a soma direta dos quatro, sem necessidade de ponderação por pesos percentuais, já resulta numa escala 0–10 (ver "Cálculo do Score Geral e Ranking").

### Critério C1 — Clareza Metodológica

*Pergunta orientadora: o artigo descreve o modelo de falhas, as premissas do sistema e o ambiente experimental de forma suficientemente detalhada?*

| Nota | Critério |
|---|---|
| 2,5 | Modelo de falhas, premissas do sistema (rede, sincronia, adversário, etc.) e ambiente experimental (hardware, software, parâmetros) descritos de forma explícita e completa — um leitor da subárea entende sob quais condições o sistema foi projetado e avaliado |
| 1 | Descrição parcial — presente, mas com lacunas relevantes (ex.: premissa de sincronia implícita, ambiente experimental apenas parcialmente especificado, ou descrição dispersa exigindo inferência do leitor) |
| 0 | Modelo de falhas, premissas ou ambiente experimental ausentes ou não identificáveis no texto |

### Critério C2 — Reprodutibilidade

*Pergunta orientadora: as provas, algoritmos ou pseudocódigos são detalhados o suficiente para permitir reimplementação independente — ou o artigo referencia um repositório de armazenamento (código/dados) que comprove a disponibilidade dos artefatos?*

Não é necessário que o código apareça explicitamente no corpo do artigo: uma referência clara a um repositório de armazenamento (ex.: link para GitHub, GitLab, Zenodo, Figshare, Open Science Framework, ou nota de "código disponível em...") já conta a favor desta nota, mesmo sem pseudocódigo ou prova detalhada no texto. As duas vias — detalhamento textual do método e disponibilização via repositório — são alternativas, não cumulativas: a presença de qualquer uma das duas, isoladamente, já sustenta a nota correspondente.

| Nota | Critério |
|---|---|
| 2,5 | Provas, algoritmos ou pseudocódigos completos e detalhados (passo a passo, complexidade, parâmetros), suficientes para reimplementação independente sem contato com os autores; **OU** o artigo indica um link/repositório de armazenamento (código e/ou dados) que comprove a disponibilidade dos artefatos do próprio trabalho |
| 1 | Algoritmo/prova presente, mas apenas parcialmente detalhado ou esboçado em alto nível — passos ou parâmetros omitidos, insuficiente para reimplementação confiável sem decisões adicionais do leitor; **OU** há menção a repositório/artefatos, mas sem confirmação clara de que cobre o código/dados específicos do artigo (ex.: link genérico do laboratório/grupo de pesquisa, link quebrado ou inacessível, ou menção vaga sem URL/identificador concreto) |
| 0 | Nenhum algoritmo, pseudocódigo ou prova fornecido no texto, **e** nenhum link/repositório de código ou dados indicado — método descrito apenas em prosa, sem evidência de disponibilização de artefatos |

### Critério C3 — Comparação com o Estado da Arte

*Pergunta orientadora: há comparação quantitativa ou qualitativa com soluções existentes?*

| Nota | Critério |
|---|---|
| 2,5 | Comparação explícita e sistemática com soluções existentes (baselines), quantitativa (métricas, tabelas, gráficos) ou qualitativa (tabela comparativa de propriedades/garantias), com discussão das diferenças |
| 1 | Comparação presente, mas limitada — um único baseline, comparação qualitativa breve sem dados de suporte, ou apenas menção ao estado da arte sem comparação direta de desempenho/propriedades |
| 0 | Nenhuma comparação com soluções existentes — trabalho apresentado isoladamente |

### Critério C4 — Avaliação de Confiabilidade e Disponibilidade

*Pergunta orientadora: o artigo analisa o comportamento do sistema diante de falhas, avaliando métricas como disponibilidade, continuidade de serviço e confiabilidade?*

| Nota | Critério |
|---|---|
| 2,5 | Avaliação explícita do comportamento sob falhas, com métricas concretas de disponibilidade, continuidade de serviço e/ou confiabilidade (ex.: tempo de recuperação, taxa de sucesso sob injeção de falhas, MTTF/MTTR, % de uptime) |
| 1 | Avaliação sob falhas presente, mas limitada — discussão qualitativa sem métricas quantitativas robustas, ou métricas presentes em escopo muito restrito (um único cenário de falha) |
| 0 | Nenhuma avaliação do comportamento do sistema diante de falhas |

---

## Cálculo do Score Geral e Ranking

Cada fórmula abaixo é definida **uma única vez**; as seções seguintes ("Processo de execução", "Saída") apenas referenciam estes nomes.

**Etapa 1 — Score Bruto 3 (por artigo, soma direta de C1–C4)**
```
Score Bruto 3 = C1 + C2 + C3 + C4
```
Escala 0–10 (cada critério ∈ {0, 1, 2,5}, máximo 4 × 2,5 = 10). Soma direta, sem necessidade de pesos percentuais — o teto de 2,5 por critério já garante peso igual entre os quatro (ver justificativa em "Critérios de Pontuação"). Ainda **não normalizado** — é o equivalente, nesta etapa, ao `Score Bruto 2` da Etapa 2 (soma/combinação direta antes de qualquer normalização sobre o lote).

**Etapa 2 — Score Stage 3 (min-max sobre o lote)**
```
Score Stage 3 (0-1) = (Score Bruto 3 − min) / (max − min)
```
`min` e `max` calculados sobre os `Score Bruto 3` de **todos** os artigos do lote — mesma lógica de normalização usada no `Score Stage 2` da Etapa 2. Só pode ser calculado depois que todo o lote tiver `Score Bruto 3` definido.

**Caso de borda:** `max == min` (inclui o caso de um único artigo aprovado, ou empate total entre todos): `Score Stage 3 (0-1) = Score Bruto 3 / 10` para todos — não divida por zero.

**Etapa 3 — Score Geral (combinação dos três estágios, convertido para escala 0–10)**
```
Score Geral (0-1)  = round(0.20 × Score Stage 1 (0-1) + 0.30 × Score Stage 2 + 0.50 × Score Stage 3 (0-1), 4)
Score Geral (0-10) = round(Score Geral (0-1) × 10, 2)
```
Usa os três scores **individuais** das três etapas (todos normalizados 0–1 antes da combinação) — não o `Score Combinado` (que já é uma agregação só de Stage 1+2). Peso crescente da etapa mais recente para a mais antiga (Stage 1 = 0,20 < Stage 2 = 0,30 < Stage 3 = 0,50): a qualidade metodológica avaliada nesta etapa é o sinal mais forte para o ranking final, mas o histórico das duas etapas anteriores continua presente e pesando no resultado, mantendo a mesma lógica de cascata já usada para combinar Stage 1 → Stage 2. A conversão final para 0–10 existe só para tornar o `Score Geral` legível como nota de ranking — não altera a ordem relativa dos artigos. `Score Combinado` permanece na planilha apenas como referência/auditoria (e como critério de desempate, ver Etapa 4), não entra na fórmula do `Score Geral`.

**Etapa 4 — Ranking (sobre o lote)**
Depois de calcular `Score Geral (0-10)` de **todos** os artigos, ordene em ordem decrescente. Critério de desempate, nesta ordem: (1) maior `C2_Reprodutibilidade` (reprodutibilidade é o critério mais diretamente verificável e, por isso, o desempate mais defensável entre os quatro); (2) maior `Score Combinado` do Estágio 2 (resume, só para fins de desempate, o desempenho combinado das duas etapas anteriores). Atribua `Posição Ranking` (1 = melhor) sem pular números, mesmo em empate completo (atribua a mesma posição e prossiga a numeração normalmente a partir da próxima linha distinta).

> **Por que essa ordem importa**: a Etapa 1 é por artigo. As Etapas 2, 3 e 4 dependem do **lote inteiro** (min/max do lote para a Etapa 2; todos os `Score Geral` calculados para a Etapa 4) e só podem ser calculadas depois que todos os artigos tiverem passado pela etapa anterior.

---

## Processo de execução

1. Leia `/mnt/skills/public/xlsx/SKILL.md` e `/mnt/skills/public/pdf-reading/SKILL.md` antes de prosseguir.
2. Carregue a planilha do Estágio 2 e filtre apenas linhas com `Score Combinado` preenchido (e a poda opcional, se houver) — só com a planilha, sem tocar no zip/Drive ainda.
3. Obtenha a lista de PDFs disponíveis na fonte fornecida (descompacte o `.zip` e/ou liste a pasta do Google Drive via `Google Drive:search_files`, conforme "Cruzamento e leitura do PDF íntegro") e, para cada artigo filtrado, localize o PDF correspondente por título, baixe-o se vier do Drive (`Google Drive:download_file_content`) e extraia o texto integral; registre o fallback para os artigos sem PDF localizado em nenhuma das fontes.
4. Para cada artigo, leia o texto obtido no passo 3 (PDF íntegro ou, no fallback, `Abstract`/`Introduction`/`Conclusion` da planilha).
5. Pontue os critérios C1–C4 (0, 1 ou 2,5 cada) e calcule `Score Bruto 3` (Etapa 1 do cálculo), registrando evidência textual por critério, com a seção de origem.
6. Com `Score Bruto 3` de **todo** o lote calculado, determine `min`/`max` e calcule `Score Stage 3` (Etapa 2 do cálculo) para cada artigo — aplique o caso de borda se `max == min`.
7. Calcule `Score Geral (0-10)` combinando `Score Stage 1`, `Score Stage 2` e `Score Stage 3` (Etapa 3 do cálculo).
8. Com `Score Geral (0-10)` de todo o lote calculado, monte o `Ranking` (Etapa 4 do cálculo).
9. Gere o arquivo de saída e apresente um resumo na conversa, incluindo quantos PDFs foram localizados/lidos integralmente vs. quantos caíram no fallback.

---

## Saída

Não gere artefatos visuais, widgets, dashboards ou componentes HTML/React (`show_widget` proibido). A única saída desta skill é o arquivo `.xlsx` abaixo. Leia `/mnt/skills/public/xlsx/SKILL.md` antes de gerá-lo.

Gere o arquivo **`raking_selecao_final.xlsx`** em `/mnt/user-data/outputs/`, com **duas abas**:

### Aba 1 — "Ranking"

Todas as colunas da planilha do Estágio 2, preservadas (inclusive `Score Stage 1 (0-1)`, `Score Stage 2` e `Score Combinado`), acrescidas de — **já ordenada por `Posição Ranking` crescente**:

| Coluna | Conteúdo |
|---|---|
| `PDF Íntegro Lido` | `Sim` (PDF localizado no zip ou na pasta do Drive e lido por completo) ou `Não` (fallback — pontuado só com `Abstract`/`Introduction`/`Conclusion` da Etapa 2) |
| `C1_Clareza_Metodologica` | Nota: 0, 1 ou 2,5 |
| `C2_Reprodutibilidade` | Nota: 0, 1 ou 2,5 |
| `C3_Comparacao_Estado_Arte` | Nota: 0, 1 ou 2,5 |
| `C4_Confiabilidade_Disponibilidade` | Nota: 0, 1 ou 2,5 |
| `Score Bruto 3` | Etapa 1 do cálculo (soma direta de C1–C4, escala 0–10, antes da normalização) |
| `Score Stage 3 (0-1)` | Etapa 2 do cálculo (min-max sobre o lote, ou caso de borda `max == min`) |
| `Score Geral (0-10)` | Etapa 3 do cálculo (combinação de `Score Stage 1` + `Score Stage 2` + `Score Stage 3`, pesos 0,20/0,30/0,50, convertida para escala 0–10, 2 casas decimais) |
| `Posição Ranking` | Etapa 4 do cálculo (1 = melhor) |
| `Justificativa` | Evidência textual concreta para cada um dos quatro critérios, identificando a seção de origem (qualquer seção do PDF íntegro — ex. Metodologia, Experimentos, Modelo de Falhas — ou Abstract/Introdução/Conclusão no caso de fallback). Para C2, quando a nota vier (total ou parcialmente) de um link/repositório de código ou dados, cite o link/identificador encontrado e a seção onde ele aparece (ex. nota de rodapé, "Disponibilidade de Dados", Abstract) |

**Formatação obrigatória:**
- `Score Geral (0-10)`: gradiente de cor vermelho (0) → amarelo (5) → verde (10), via `ColorScaleRule`.
- `C1_Clareza_Metodologica`, `C2_Reprodutibilidade`, `C3_Comparacao_Estado_Arte`, `C4_Confiabilidade_Disponibilidade`: barra de dados (data bar) 0–2,5.
- Cabeçalho com primeira linha congelada e autofiltro ativo (`worksheet.auto_filter.ref`), para filtrar e ordenar livremente no Excel ou Google Sheets.

### Aba 2 — "Resumo"

- Fonte dos PDFs íntegros usada (`.zip`, pasta do Google Drive, ou ambas).
- Total de artigos pontuados.
- Quantos artigos tiveram `PDF Íntegro Lido = Sim` vs. `Não` (fallback), e a lista dos títulos em fallback (não localizados em nenhuma das fontes ou não recuperáveis).
- Top 10 do `Ranking` (título + `Score Geral (0-10)`).
- Média e desvio padrão de `C1`, `C2`, `C3`, `C4`, `Score Bruto 3`, `Score Stage 3` e `Score Geral (0-10)`, sobre o lote.
- Auditoria: escala usada em cada critério (`0, 1 ou 2,5`, soma direta sem pesos percentuais), `min`/`max` de `Score Bruto 3` usados na normalização (e se o caso de borda `max == min` foi aplicado), pesos da combinação final entre os três estágios (`Score Stage 1=0,20; Score Stage 2=0,30; Score Stage 3=0,50`) e critério de desempate aplicado.

Ao final, apresente o arquivo ao usuário e resuma na conversa: quantos artigos foram pontuados, quantos tiveram o PDF íntegro lido (vs. fallback) e o top 5 do ranking.

## Tom das justificativas

Escreva como um revisor sênior de periódico de alto impacto: técnico, objetivo e verificável. Cada justificativa deve permitir que outro pesquisador audite a nota de cada critério sem reler o artigo — cite os termos, técnicas, algoritmos, métricas ou métodos de validação concretos que fundamentam cada nota, nunca generalidades como "parece relevante".
