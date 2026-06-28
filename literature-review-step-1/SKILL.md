---
name: literature-review-step-1
description: "Primeiro estágio (filtro inicial) de uma pipeline de revisão literária sobre exatamente dois eixos temáticos definidos pelo usuário, sendo o Eixo 1 o eixo principal (peso maior) e o Eixo 2 o eixo secundário (peso menor). Use esta skill sempre que o usuário mencionar triagem de artigos, filtro de revisão literária, 'revisão step 1', 'filtro etapa 1', análise de aderência temática de artigos científicos, ou enviar um CSV ou XLSX de busca bibliográfica (ex. exportação do IEEE Xplore) pedindo para avaliar artigos com base em eixos temáticos. Também use quando o usuário pedir para avaliar título, resumo e palavras-chave de artigos com critérios de inclusão/exclusão de uma revisão literária, em qualquer área de pesquisa."
---

# Filtro Inicial de Revisão Literária

## Papel

Atue como um pesquisador Professor Doutor (PhD) com reconhecimento internacional e mais de 10 anos chefiando um laboratório de pesquisa **na área específica definida pelos eixos temáticos do usuário**. Sua tarefa é realizar a triagem inicial (screening) de artigos científicos resultantes de uma busca bibliográfica, avaliando a aderência temática de cada artigo ao escopo de uma revisão literária. A análise é feita exclusivamente sobre **título, resumo e palavras-chave** — exatamente como faria um revisor experiente na primeira etapa de uma revisão sistemática.

---

## Premissas Iniciais

**Leia e internalize estas premissas antes de tocar em qualquer artigo ou cálculo.** Elas valem para o lote inteiro, do primeiro ao último artigo, e não serão repetidas nas seções seguintes — todo procedimento e toda fórmula abaixo já as assume como verdadeiras.

**P1. Entradas obrigatórias.** Antes de iniciar, confirme que o usuário forneceu:
- Uma planilha (csv ou xlsx) com as colunas `Document Title, Authors, Publication Title, Publication Year, Abstract, Author Keywords, IEEE Terms, Article Citation Count` (uma linha por artigo).
- **Exatamente dois eixos temáticos**: Eixo 1 (principal, peso maior) e Eixo 2 (secundário, peso menor).

Se faltar qualquer entrada, se vier só um eixo, mais de dois eixos, ou eixos sem indicação clara de qual é o principal — pergunte ao usuário antes de prosseguir. Não assuma.

**P2. Mapeamento de colunas.**
| Coluna da planilha | Campo usado na análise |
|---|---|
| `Document Title` | Título |
| `Abstract` | Resumo |
| `Author Keywords` + `IEEE Terms` | Palavras-chave (combine as duas) |

Se a planilha tiver nomes de coluna ligeiramente diferentes, codificação distinta (ex.: latin-1) ou delimitador diferente (`;`), detecte e trate automaticamente; se a ambiguidade persistir, pergunte.

**P3. Relação entre os eixos é hierárquica, não paralela.** Eixo 2 nunca é avaliado como tema independente do artigo. Ele é avaliado apenas como: *o tema do Eixo 1, tratado pelo artigo, está situado dentro do contexto do Eixo 2?* É uma verificação **binária** (sim/não), não uma escala de centralidade própria.
> Exemplo: revisão sobre "tolerância a falhas" (Eixo 1) "em sistemas distribuídos" (Eixo 2). O que importa não é se o artigo menciona sistemas distribuídos isoladamente, mas se a tolerância a falhas tratada no artigo está situada nesse contexto (réplicas, nós, consenso, cluster, microsserviços etc.) e não em outro (hardware de nó único, sistema embarcado isolado, dispositivo de borda solitário).

**P4. Regra de zeragem — checagem rigorosa e curto-circuito total.** A checagem de presença do Eixo 1 é o primeiro e mais crítico julgamento de todo o processo, e deve ser feita com o mesmo rigor de especialista descrito em "Papel" — não é uma varredura superficial de palavras-chave. Antes de pontuar qualquer linha da Tabela A, pergunte-se explicitamente: *o tema do Eixo 1 aparece no artigo (ainda que de forma periférica, P5) ou está genuinamente ausente?* Só classifique como ausente se, após leitura semântica completa de título, resumo e palavras-chave, nenhum indício real do Eixo 1 puder ser apontado — e mesmo indícios mínimos contam a favor da presença (ver P6, que trata desse limite).

Se, e somente se, essa checagem rigorosa concluir que o Eixo 1 está **ausente**, então:
- `score_aderência = 0` diretamente, sem somar nenhuma pontuação de Eixo 2 (a verificação do Eixo 2, P3, nem chega a ser feita);
- **nenhum outro cálculo é realizado para esse artigo** — não se calcula `citações_por_ano` (Etapa 2), não se calcula `pontos_impacto` (Etapa 3, Tabela B); esses campos ficam em branco/N/A na planilha de saída, e não apenas "calculados mas ignorados";
- `Score Stage 1 = 0.00` é atribuído diretamente, sem passar pela fórmula de pesos da Etapa 4;
- o artigo é marcado como **excluído** no filtro (ver "Saída") e destacado visualmente na planilha, para que fique evidente à primeira vista quais artigos foram eliminados nesta etapa por ausência total do Eixo 1.

Esse curto-circuito é uma decisão de execução (poupar trabalho desnecessário), não apenas uma decisão de pontuação — não execute as etapas seguintes "por garantia" para esses artigos.

**P5. Julgamento semântico, não lexical.** Avalie por significado (sinônimos, variações, termos relacionados contam), não por matching literal de string. Estabeleça o padrão de rigor da subárea (ver "Papel") **antes** de avaliar o primeiro artigo, e aplique esse mesmo padrão de forma idêntica do primeiro ao último artigo do lote — não relaxe o rigor à medida que o lote avança.

**P6. Casos limítrofes são conservadores.** Resumo vago ou ausência de abstract com algum indício de Eixo 1: mantenha o artigo (não zere) e marque na justificativa como "caso limítrofe — indícios mínimos do Eixo 1". Na etapa 1, descartar indevidamente custa mais que manter um falso positivo.

**P7. Convenção de quartil bibliométrico.** Q1 = **maior** impacto (citações/ano mais altas), Q4 = **menor** impacto. Esta é a convenção padrão de bibliometria (JCR, Scimago) — o inverso da numeração "intuitiva" de quartis estatísticos genéricos. Nunca inverta.

**P8. Cálculos em duas camadas.** `score_aderência` (Tabela A) é sempre por artigo, escala fixa 0–10. O quartil de citações (Tabela B) depende do **lote inteiro** — calcule `citações_por_ano` de todos os artigos antes de determinar os percentis. O `Score Stage 1` final (Etapa 4) usa apenas escalas fixas, não min-max do lote — só o `Quartil` final (Etapa 5) volta a depender do lote, por faixa fixa de valor.

**P9. Eficiência sem perda de rigor.** Em lotes grandes, processe cada artigo individualmente e por completo, mas a justificativa de cada um deve ser objetiva (1-2 frases). O ganho de eficiência vem de relatar menos, nunca de avaliar menos ou de pular a leitura semântica de qualquer artigo.

**P10. Peso fixo entre aderência e impacto (70/30), com curto-circuito total se Eixo 1 ausente.** Para artigos com `score_aderência > 0`, o `Score Stage 1` combina aderência temática (70%) e impacto bibliométrico (30%). Mas se a checagem rigorosa de P4 concluir que o Eixo 1 está ausente (`score_aderência = 0`), o `Score Stage 1` é **zerado por completo** e **`citações_por_ano` e `pontos_impacto` não são calculados** para esse artigo — diferentemente de uma simples exclusão da fórmula, o cálculo nem é executado, e os campos correspondentes ficam vazios/N/A na planilha de saída. Impacto bibliométrico nunca compensa a ausência total do tema central da revisão, e não há razão para computá-lo quando o artigo já está fora do escopo.

---

## Tabelas de Pontuação (fonte única de referência)

Estas duas tabelas são a única fonte de pontos do sistema. Toda fórmula na próxima seção apenas referencia estas tabelas — os valores não são redefinidos em nenhum outro lugar deste documento.

### Tabela A — Score de Aderência Temática (por artigo)

| Linha | Critério | Pontos |
|---|---|---|
| Eixo 1 | Tema **central** do artigo (contribuição principal) | 7 |
| Eixo 1 | Tema **relevante mas secundário** (ex.: motivação, propriedade avaliada) | 4 |
| Eixo 1 | Mencionado de forma **periférica** (ex.: trabalho futuro, contexto remoto) | 2 |
| Eixo 1 | **Ausente** → aplica P4 (zeragem); ignore a linha de Eixo 2 | 0 |
| Eixo 2 | **Aplicado** dentro do contexto do Eixo 1 (ver P3) | 3 |
| Eixo 2 | **Não aplicado** dentro do contexto do Eixo 1 (ou ausente) | 0 |

Escolha exatamente uma linha de Eixo 1 e, se a regra de zeragem (P4) não se aplicou, exatamente uma linha de Eixo 2. Escala resultante: 0 a 10, com o Eixo 1 como componente dominante (até 70% do total possível).

### Tabela B — Pontos de Impacto Bibliométrico (por quartil, sobre o lote)

| Quartil | Percentil de `citações_por_ano` | Pontos |
|---|---|---|
| Q1 — maior impacto | 75–100% | 4 |
| Q2 | 50–75% | 3 |
| Q3 | 25–50% | 2 |
| Q4 — menor impacto | 0–25% | 1 |

(Convenção de Q1/Q4 conforme P7.)

---

## Cálculo do Score — ordem fixa

Cada fórmula abaixo é definida **uma única vez**. As seções seguintes ("Processo de execução", "Saída") apenas referenciam estes nomes — não os recalculam nem os redefinem.

**Etapa 1 — Score de Aderência (por artigo, usa Tabela A)**
```
score_aderência = pontos_eixo1 + pontos_eixo2
```
(`pontos_eixo2 = 0` sempre que P4 zerar o artigo.)

**Checkpoint de curto-circuito (P4).** Se `score_aderência == 0` nesta etapa, **pare aqui para este artigo**: não execute as Etapas 2 e 3 para ele. Vá direto para `Score Stage 1 = 0.00` (Etapa 4) e marque o artigo como excluído (ver "Saída"). Só siga para as Etapas 2 e 3 os artigos com `score_aderência > 0`.

**Etapa 2 — Taxa de citação normalizada por tempo (por artigo, só para `score_aderência > 0`)**
```
citações_por_ano = Article Citation Count / (ano_atual - Publication Year + 1)
```
Use o ano atual real. Isso torna artigos recentes comparáveis a artigos antigos. **Não calcule esta etapa para artigos já zerados no checkpoint acima** — deixe o campo vazio/N/A na saída.

**Etapa 3 — Pontos de Impacto (sobre o lote, usa Tabela B; só para `score_aderência > 0`)**
Calcule `citações_por_ano` (Etapa 2) para **todos os artigos com `score_aderência > 0`** do lote primeiro. Só então determine os percentis 25/50/75 desse subconjunto (artigos zerados não entram no cálculo de percentis), classifique cada um em Q1–Q4 e atribua `pontos_impacto` pela Tabela B. Artigos zerados ficam com `pontos_impacto` vazio/N/A.

**Etapa 4 — Score Stage 1 (por artigo, pesos fixos — ver P10)**
```
se score_aderência == 0:
    Score Stage 1 = 0.00   (curto-circuito total — Etapas 2 e 3 nem foram executadas para este artigo)
senão:
    aderência_norm = score_aderência / 10
    impacto_norm   = (pontos_impacto - 1) / 3
    Score Stage 1  = round(0.70 × aderência_norm + 0.30 × impacto_norm, 2)
```
Escalas fixas (0–10 e 1–4): fora do caso de zeragem, o resultado já nasce em 0–1, sem depender de min-max do lote — pode ser calculado artigo a artigo assim que `pontos_impacto` (Etapa 3) estiver definido para ele.

**Etapa 5 — Quartil final (sobre o lote, faixa fixa do Score Stage 1)**
Só depois de ter `Score Stage 1` de **todos** os artigos, classifique cada um por faixa fixa de valor absoluto (não confundir com o quartil de citações da Etapa 3, que é percentil sobre `citações_por_ano`):

| Quartil | Faixa de `Score Stage 1` |
|---|---|
| Q1 | > 0,75 |
| Q2 | > 0,50 e ≤ 0,75 |
| Q3 | > 0,25 e ≤ 0,50 |
| Q4 | ≤ 0,25 |

> Faixas fixas, não posicionais: é esperado e aceitável que a distribuição entre quartis seja desigual — reflete a qualidade real do lote, não um artefato de ranking.

> **Por que essa ordem importa**: Etapas 1, 2 e 4 são por artigo. Etapas 3 e 5 dependem do **lote inteiro** e só podem ser calculadas depois que todos os artigos passaram pelas etapas anteriores.

---

## Processo de execução

1. Leia a skill de planilhas (`/mnt/skills/public/xlsx/SKILL.md`) antes de gerar o arquivo de saída.
2. Carregue o CSV/XLSX com pandas, preservando todas as colunas originais (P1, P2).
3. Identifique a subárea de pesquisa implícita nos dois eixos e fixe o padrão de rigor central/secundário/periférico para essa subárea (P5), antes de avaliar o primeiro artigo.
4. Para cada artigo, leia Título, Resumo e Palavras-chave e aplique a Tabela A: pontue Eixo 1 com a checagem rigorosa de P4 (presença real vs. ausência genuína), depois Eixo 2 se aplicável (respeitando P3), obtendo `score_aderência` (Etapa 1). Em casos limítrofes, aplique P6.
5. **Checkpoint por artigo**: se `score_aderência == 0`, marque o artigo como **excluído**, atribua `Score Stage 1 = 0.00` e **não calcule** `citações_por_ano` nem `pontos_impacto` para ele — pule direto para o passo 9 deste artigo. Só os artigos com `score_aderência > 0` seguem para os passos 6 e 7.
6. Para os artigos não excluídos, calcule `citações_por_ano` (Etapa 2).
7. Com `citações_por_ano` do subconjunto de artigos não excluídos já calculado, determine os percentis e atribua `pontos_impacto` via Tabela B (Etapa 3), depois calcule `Score Stage 1` pela fórmula de pesos fixos (Etapa 4).
8. Com `Score Stage 1` de todo o lote já calculado (zerados e não-zerados), atribua o `Quartil` final por faixa fixa (Etapa 5) — artigos excluídos caem automaticamente em Q4.
9. Registre para cada artigo: eixos encontrados, justificativa, `score_aderência`, `pontos_impacto` (ou N/A se excluído), `Score Stage 1`, `Quartil` e `Status` (Incluído/Excluído).
10. Gere o arquivo de saída (cabeçalho fixo, autofiltro e destaque visual dos excluídos — ver "Saída") e apresente um resumo da triagem na conversa, destacando quantos artigos foram excluídos por ausência do Eixo 1.

---

## Saída

Gere um arquivo Excel chamado **`filtro_etapa_1.xlsx`** em `/mnt/user-data/outputs/` com duas abas:

**Aba 1 — "Triagem"**: todas as colunas originais do CSV, acrescidas de:

- `Justificativa`: texto curto e verificável indicando os termos/conceitos detectados em cada eixo e se o Eixo 2 foi considerado aplicado no contexto do Eixo 1 (P3). Exemplo: "Eixo 1 central (termos X e Y no resumo, 7 pts); Eixo 2 aplicado no contexto — réplicas e consenso discutidos (3 pts); score_aderência = 10." Para artigos excluídos, registre por que o Eixo 1 foi considerado ausente (ex.: "Eixo 1 ausente — nenhum indício de [tema] no título, resumo ou palavras-chave; score_aderência = 0; demais cálculos não realizados.").
- `Eixos encontrados`: `Eixo 1; Eixo 2`, `Eixo 1` ou `Nenhum`.
- `Status`: `Incluído` ou `Excluído (Eixo 1 ausente)`. Esta coluna torna explícito, sem precisar abrir a Justificativa, quais artigos foram eliminados nesta etapa por curto-circuito de P4.
- `Score Aderência`: resultado da Etapa 1 (0–10).
- `Pontos Impacto`: resultado da Etapa 3 (1–4), ou vazio/N/A para artigos com `Status = Excluído` (ver P4/P10 — o cálculo nem é realizado para esses artigos).
- `Score Stage 1 (0-1)`: resultado da Etapa 4 (pesos fixos 70/30, ver P10), ou `0.00` direto para excluídos. Gradiente de cor vermelho (0.00) → amarelo (0.50) → verde (1.00), via `openpyxl.formatting.rule.ColorScaleRule`.
- `Quartil`: resultado da Etapa 5 (Q1–Q4, faixa fixa do `Score Stage 1`). Use o mesmo esquema de cor da Skill 2 (Q4 azul escuro → Q1 cinza), para manter leitura visual consistente entre as etapas.

**Destaque visual dos excluídos**: aplique preenchimento de fundo (cor sólida, ex. vermelho claro `FFC7CE`, via `openpyxl.styles.PatternFill`) em toda a linha de cada artigo com `Status = Excluído (Eixo 1 ausente)`. Esse destaque tem prioridade visual sobre o `ColorScaleRule` da coluna `Score Stage 1` (aplique o `ColorScaleRule` normalmente, mas o preenchimento de linha deixa claro de imediato, ao rolar a planilha, quais artigos saíram do filtro nesta etapa — não dependa só da cor de uma única coluna para essa leitura).

**Aba 2 — "Resumo"**: estatísticas da triagem:

- Total de artigos avaliados.
- Total e percentual de artigos **excluídos** por ausência do Eixo 1 (`Status = Excluído`) vs. **incluídos**.
- Distribuição por score de aderência entre os incluídos (ex.: quantos acima de 0.5 em `Score Stage 1`).
- Distribuição por status do Eixo 2 entre os incluídos (aplicado no contexto do Eixo 1 / não aplicado).
- Distribuição por quartil de citações entre os incluídos (Q1: N, Q2: N, Q3: N, Q4: N) — não se aplica aos excluídos, já que `pontos_impacto` não foi calculado para eles.
- Distribuição pelo `Quartil` final (Q1–Q4, faixa fixa do `Score Stage 1`) — note que todo artigo excluído cai automaticamente em Q4 por ter `Score Stage 1 = 0.00`.

Observação: se o usuário pedir o arquivo em CSV, gere adicionalmente `filtro_etapa_1.csv` (apenas a aba de triagem), já que CSV não suporta múltiplas abas — mas o padrão é gerar o `.xlsx`. No CSV, mantenha a coluna `Status` como forma de identificar os excluídos, já que o preenchimento de cor não é exportável para esse formato.

Aplique formatação básica (cabeçalho destacado, primeira linha congelada) e ative autofiltro na linha de cabeçalho (`worksheet.auto_filter.ref`), para que o usuário possa filtrar e ordenar livremente ao abrir no Excel ou Google Sheets — seguindo as orientações da skill de xlsx.

Ao final, apresente o arquivo ao usuário e resuma na conversa: quantos artigos foram avaliados, quantos foram **excluídos** por ausência do Eixo 1 (e por quê, em linhas gerais), distribuição dos scores de aderência entre os incluídos, distribuição por quartil de citações e distribuição pelo `Quartil` final.

## Tom das justificativas

Escreva como um revisor sênior: objetivo, técnico e verificável. Cada justificativa deve permitir que outro pesquisador audite a decisão sem reler o artigo. Cite os termos/conceitos concretos encontrados (ou a ausência deles) — nunca justificativas genéricas como "não é relevante".