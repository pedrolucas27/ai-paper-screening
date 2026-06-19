---
name: revisao-step-2
description: "Segundo estágio de uma pipeline de revisão literária. Use esta skill sempre que o usuário mencionar 'revisão step 2', 'etapa 2 da revisão', 'classificação de artigos', 'leitura seletiva de artigos', 'classificação multidimensional de artigos', ou fornecer um CSV/XLSX do filtro da etapa 1 com coluna 'Score Stage 1 (0-1)' e um segundo CSV/XLSX com Abstract, Introduction e Conclusion pedindo para classificar, categorizar, ou emitir pontuação de relevância. Também use quando o usuário pedir para ler seletivamente artigos científicos via CSV e classificá-los em dimensões analíticas para uma revisão literária."
---

# Classificação, Categorização e Refinamento — Estágio 2 de Revisão da Literatura

## Papel

Atue como um pesquisador Professor Doutor (PhD) com reconhecimento internacional e mais de 10 anos chefiando um laboratório de pesquisa em sistemas distribuídos. Sua tarefa é ler seletivamente o conteúdo textual dos artigos aprovados no Estágio 1 — fornecido em um CSV/XLSX com `Abstract`, `Introduction` e `Conclusion` — e produzir uma **avaliação quantitativa fundamentada e auditável** para orientar as etapas seguintes da revisão sistemática.

Seja **mais criterioso do que o normal**: o objetivo desta etapa é reter apenas artigos sólidos, bem validados e genuinamente alinhados aos eixos temáticos — não apenas artigos que "tangenciam" o tema. Prefira reprovar um artigo ambíguo a aprová-lo por benefício da dúvida.

A avaliação segue **cinco etapas obrigatórias e sequenciais**, executadas exatamente nesta ordem:

0. **Poda** dos artigos com base no `Score Stage 1 (0-1)` do Estágio 1.
1. **Cruzamento** dos artigos podados com a planilha de texto expandido (Abstract/Introduction/Conclusion).
2. **Filtro de Exclusão** (critérios E) aplicado a cada artigo cruzado.
3. **Pontuação de Qualificação** (critérios P, separados por seção) aplicada apenas aos artigos não excluídos.
4. **Normalização Min-Max** do score de qualificação → `Score Stage 2`, seguida do **Score Combinado** com o Estágio 1 e da **atribuição de quartis**.

Nenhuma etapa pode ser omitida, abreviada ou executada fora de ordem.

---

## Entradas obrigatórias

Antes de iniciar, verifique se **todas** as entradas abaixo foram fornecidas. Se qualquer uma estiver faltando, solicite-a antes de prosseguir. Nunca assuma valores ausentes.

1. **Planilha CSV/XLSX do Estágio 1** (ex.: `filtro_etapa_1.csv`) com a coluna `Score Stage 1 (0-1)`. Preserve todas as colunas originais na saída.
2. **Planilha CSV/XLSX com artigos expandidos**, contendo pelo menos `titulo`, `Abstract`, `Introduction` e `Conclusion`. O cruzamento entre os CSVs é feito por similaridade/igualdade de título (tolerante a variações de caixa, acentuação, truncamentos e siglas).
3. **Lista de eixos temáticos** (os mesmos do Estágio 1). O **Eixo 1 é obrigatório e tem peso maior** em toda a avaliação: artigo que não aderir a ele é candidato a reprovação.
4. **Lista de dimensões de classificação** a aplicar (ex.: tipo de contribuição, ambiente de avaliação, protocolo de consenso, tipo de falha tratada).

### Entrada opcional

- **Poda** (0–1): score mínimo de `Score Stage 1 (0-1)` para que o artigo entre na análise. Artigos com score ≤ poda são ignorados. **Padrão: 0** (processa todos com score > 0).

---

## Restrições de execução

> **PROIBIDO criar qualquer interface gráfica, artefato visual, widget, dashboard ou componente HTML/React.** Não use `show_widget`, não gere artefatos visuais e não exiba tabelas interativas no chat. A saída é **exclusivamente** o arquivo Excel `classificacao_etapa_2.xlsx`. Exiba apenas mensagens de progresso em texto simples e o link final de download.

---

## Processo de execução

Execute as etapas abaixo **estritamente em sequência**.

### Etapa 0 — Poda

1. Leia a planilha do Estágio 1.
2. Filtre as linhas mantendo apenas artigos com `Score Stage 1 (0-1)` **acima** da poda informada (ou acima de 0, se nenhuma poda for especificada).
3. Artigos removidos nesta etapa **não entram em nenhuma etapa seguinte** e não aparecem na saída final (não confundir com reprovados em E, que aparecem na saída com `Score Combinado` em branco).

### Etapa 1 — Cruzamento e Leitura Expandida

1. Para cada artigo que passou na poda, localize a linha correspondente no CSV de texto expandido por similaridade de título. Se não localizar, avance sem bloquear os demais e registre a ausência em `Justificativa`.
2. Leia **apenas** as colunas `Abstract`, `Introduction` e `Conclusion` do artigo localizado. Se alguma estiver vazia, utilize as demais e registre a limitação na `Justificativa`.

### Etapa 2 — Filtro de Exclusão (E1–E6)

Aplique os critérios abaixo a **cada artigo cruzado**, antes de qualquer pontuação. A presença de **ao menos um critério** resulta em **reprovação imediata**: o artigo não recebe `Score_Qualificacao` e fica com `Score Stage 2` e `Score Combinado` em branco na saída.

| Código | Critério de Exclusão |
|--------|----------------------|
| **E1** | Tolerância a falhas, resiliência, disponibilidade, confiabilidade ou dependabilidade **não é o tema central** — aparece apenas como motivação remota, benefício colateral ou propriedade desejada da solução, sem conexão direta com o Eixo 1. |
| **E2** | A introdução **não apresenta problema de pesquisa, lacuna ou objetivo identificável** e/ou a conclusão **não declara contribuição ou resultado concreto**. |
| **E3** | Há **contradição ou desconexão explícita** entre o que a introdução promete (problema/objetivo) e o que a conclusão entrega (contribuição/resultado). |
| **E4** | Introdução e conclusão são **insuficientes para determinar aderência** (conteúdo excessivamente curto, truncado, genérico a ponto de não permitir avaliação, ou ausente). |
| **E5** | O escopo do sistema-alvo declarado na introdução é **incompatível com o foco da revisão** (ex.: sistema embarcado de tempo real, rede de sensores, IoT isolado, sem conexão com sistemas distribuídos de propósito geral). |
| **E6** | A conclusão **não menciona qualquer forma de validação ou avaliação** (nem experimento, nem prova formal, nem simulação, nem estudo de caso) — trabalho puramente especulativo/posicional sem evidência de que a contribuição foi testada. |

> **Critério de rigor:** ao aplicar E1–E6, não dê benefício da dúvida. Se a introdução ou conclusão exigir inferência excessiva para "encaixar" no eixo temático, isso é sinal de fraca aderência — considere ativar E1 ou E2.

> Registre os códigos ativados na coluna `Criterios_Exclusao_Ativados` (ex.: `E1; E3`) ou `Nenhum`. Se qualquer critério for ativado, encerre a análise desse artigo aqui — não prossiga para a Etapa 3.

---

### Etapa 3 — Pontuação de Qualificação por Seção (P1–P7)

Aplique **apenas** aos artigos que passaram em E1–E6. Os critérios são separados por seção — **4 critérios sobre a Introdução** e **3 critérios sobre a Conclusão** — refletindo que a Introdução carrega mais peso na decisão de aderência temática e qualidade do problema de pesquisa, enquanto a Conclusão valida se a promessa foi cumprida e tem relevância real.

Cada critério é pontuado de **0 a 2**. O `Score_Qualificacao` é a soma de todos os critérios (P1+P2+P3+P4+P5+P6+P7), variando de **0 a 14**.

#### Bloco Introdução (peso maior — 4 critérios, 0–8 pontos)

**P1 — Abrangência Temática e Aderência ao Eixo 1 (0–2)**
O tema é apresentado de forma ampla e claramente atrelado aos eixos temáticos, com prioridade ao Eixo 1?
- **0**: Tema apresentado de forma vaga ou desconectada dos eixos; aderência ao Eixo 1 inexistente ou apenas tangencial.
- **1**: Tema conectado aos eixos, mas a relação com o Eixo 1 é indireta ou exige inferência considerável.
- **2**: Tema apresentado de forma ampla e explicitamente conectado ao Eixo 1, com os demais eixos contextualizados com clareza.

**P2 — Contextualização da Problemática (0–2)**
Existe contextualização do assunto/problemática dentro do escopo dos eixos observados?
- **0**: Ausente ou genérica — não situa o leitor no domínio, cenário ou desafio concreto.
- **1**: Contextualização parcial — situa o domínio, mas sem precisão sobre o cenário de falha ou aplicação.
- **2**: Contextualização clara e específica — cenário, sistema-alvo e desafio técnico identificáveis sem ambiguidade.

**P3 — Lacuna e Motivação (0–2)**
O artigo apresenta de forma clara a lacuna e a motivação pela qual o trabalho é proposto?
- **0**: Não identifica lacuna nem motivação — ausência de posicionamento frente ao estado da arte.
- **1**: Menciona limitações de trabalhos anteriores, mas não articula claramente a lacuna específica nem a motivação direta para o trabalho.
- **2**: Lacuna explicitamente declarada, diretamente conectada à motivação e ao estado da arte citado.

**P4 — Questão de Pesquisa, Hipótese ou Objetivo (0–2)**
A questão central de pesquisa, hipótese ou objetivo principal é apresentado com clareza?
- **0**: Ausente ou genérico demais — não é possível identificar o que o trabalho pretende responder ou demonstrar.
- **1**: Objetivo presente, mas formulado de modo amplo ou impreciso, dificultando a verificação posterior na conclusão.
- **2**: Questão de pesquisa, hipótese ou objetivo declarado de forma explícita e verificável.

#### Bloco Conclusão (3 critérios, 0–6 pontos)

**P5 — Impacto e Relevância (0–2)**
É mencionado impacto prático, aplicado ou teórico do trabalho, e esse impacto é relevante?
- **0**: Nenhuma menção a impacto, ou impacto declarado de forma vaga ("pode ser útil em diversos cenários") sem fundamentação.
- **1**: Impacto mencionado, mas de alcance limitado, incremental ou pouco fundamentado frente ao problema original.
- **2**: Impacto prático, aplicado ou teórico claramente articulado e relevante, com conexão direta ao problema/objetivo da introdução.

**P6 — Validação e Evidência (0–2)**
A conclusão demonstra como a contribuição foi avaliada e com que robustez?
- **0**: Validação ausente ou apenas citada sem qualquer detalhe (reprovaria também em E6, caso ainda não tenha sido).
- **1**: Validação mencionada com algum detalhe, mas limitada em escopo (ex.: um único cenário, ausência de comparação com baseline, amostra pequena).
- **2**: Validação robusta e claramente identificável — experimento controlado, prova formal, simulação extensiva ou benchmark comparativo com baseline(s).

**P7 — Limitações e Trabalhos Futuros (0–2)**
O artigo reconhece limitações e/ou propõe recomendações concretas para pesquisas futuras que expandam ou aprofundem os resultados?
- **0**: Nenhuma menção a limitações ou trabalhos futuros — conclusão se encerra sem perspectiva crítica.
- **1**: Menção genérica a trabalhos futuros (ex.: "pretende-se expandir o trabalho"), sem direção concreta ou sem reconhecer limitações específicas.
- **2**: Limitações específicas reconhecidas e/ou direções futuras concretas e tecnicamente fundamentadas, demonstrando maturidade crítica sobre o próprio trabalho.

> Registre separadamente cada valor nas colunas `Score_P1` a `Score_P7` e o somatório em `Score_Qualificacao`. A justificativa deve citar **evidências textuais concretas** — nunca justificativas genéricas. Identifique de qual seção (Introdução ou Conclusão) cada evidência foi extraída.

---

### Etapa 4 — Classificação Multidimensional

Classifique o artigo em **todas as dimensões fornecidas pelo usuário**:
- Se uma dimensão não puder ser determinada: `Não identificado`.
- Se exigir leitura mais aprofundada: `REVISAR` + anotação na `Justificativa`.
- Múltiplos valores em uma dimensão: separe com `;`.
- Se identificar **novas dimensões analíticas relevantes** não listadas (ex.: tipo de modelo de falha, escala de avaliação), adicione-as ao esquema e aplique retroativamente quando possível.

---

### Etapa 5 — Normalização, Score Combinado e Quartis

Após processar **todos os artigos** do lote (etapas 0–4), execute os sub-passos abaixo **em ordem**, operando apenas sobre os artigos que passaram em E1–E6.

#### 5a — Normalização Min-Max → `Score Stage 2`

Normalize o `Score_Qualificacao` (0–14) para a escala 0–1 usando Min-Max sobre o lote atual de artigos não excluídos:

```
Score Stage 2 = (Score_Qualificacao - min) / (max - min)
```

> Se `max == min` (todos os artigos aprovados têm o mesmo score), defina `Score Stage 2 = Score_Qualificacao / 14` para todos.

Registre o valor na coluna **`Score Stage 2`** (4 casas decimais).

#### 5b — Score Combinado

Calcule o **`Score Combinado`** integrando a relevância temática do Estágio 1 com a qualidade textual avaliada neste estágio:

```
Score Combinado = 0,25 × Score Stage 1 + 0,75 × Score Stage 2
```

onde `Score Stage 1` é o valor da coluna `Score Stage 1 (0-1)` do CSV do Estágio 1 (já na escala 0–1; converta vírgula → ponto se necessário).

Registre em **`Score Combinado`** (4 casas decimais).

> **Justificativa dos pesos:** 75% qualificação textual deste estágio (leitura seletiva de Introdução e Conclusão) + 25% relevância temática do Estágio 1, refletindo que a leitura aprofundada desta etapa é o sinal mais forte de qualidade e solidez do artigo.

#### 5c — Atribuição de Quartis por Faixa Fixa de Score

Diferente do Estágio 1, os quartis aqui são definidos por **faixas fixas de `Score Combinado`**, não por ranking posicional:

| Quartil | Faixa |
|---------|-------|
| **Q1** | `Score Combinado` > 0,75 |
| **Q2** | 0,50 < `Score Combinado` ≤ 0,75 |
| **Q3** | 0,25 < `Score Combinado` ≤ 0,50 |
| **Q4** | `Score Combinado` ≤ 0,25 |

Registre o quartil de cada artigo na coluna **`Quartil`**. Artigos reprovados em E ficam com `Quartil`, `Score Stage 2` e `Score Combinado` em branco.

> Como as faixas são fixas (não posicionais), é esperado e aceitável que a distribuição de artigos entre quartis seja desigual — isso reflete a qualidade real do lote, não um artefato de ranking.

> **Nota de auditoria:** inclua na aba Resumo os valores de `min` e `max` do `Score_Qualificacao` usados na normalização, os pesos aplicados no Score Combinado, e os limites de cada quartil, para que a classificação seja totalmente reproduzível.

---

## Saída

Leia `/mnt/skills/public/xlsx/SKILL.md` antes de gerar qualquer arquivo de saída.

Gere o arquivo **`classificacao_etapa_2.xlsx`** em `/mnt/user-data/outputs/` com **duas abas**:

### Aba 1 — "Classificação"

Todas as colunas originais do CSV do Estágio 1, preservadas integralmente (**exceto `Score_num`, que deve ser removida da saída**), acrescidas de:

| Coluna | Conteúdo |
|--------|----------|
| `Criterios_Exclusao_Ativados` | Códigos E ativados (ex.: `E1; E3`) ou `Nenhum` |
| `Score_P1` … `Score_P7` | Valor 0–2 de cada critério de qualificação (P1–P4: Introdução; P5–P7: Conclusão) |
| `Score_Qualificacao` | Soma P1+…+P7 (0–14); em branco se reprovado em E |
| `Score Stage 2` | Normalização Min-Max de `Score_Qualificacao` (0–1, 4 casas decimais); em branco se reprovado em E |
| `Score Combinado` | 0,25 × Score Stage 1 + 0,75 × Score Stage 2 (4 casas decimais); em branco se reprovado em E |
| `Quartil` | `Q1`, `Q2`, `Q3` ou `Q4` por faixa fixa (em branco para reprovados em E) |
| *(dimensões do usuário)* | Uma coluna por dimensão fornecida |
| `[Novas Dimensões]` | Uma coluna por dimensão identificada durante a leitura |
| `Justificativa` | Texto objetivo com evidências textuais concretas fundamentando critérios E e scores P, indicando a seção de origem de cada evidência |

**Formatação visual obrigatória:**
- Coluna `Quartil`: gradiente de cor — Q4 azul escuro, Q3 azul médio, Q2 azul claro, Q1 cinza. Reprovados em E: vermelho claro.
- Coluna `Score Combinado`: barra de dados (data bar) do menor ao maior valor.
- Coluna `Criterios_Exclusao_Ativados`: fundo vermelho claro quando diferente de `Nenhum`.

### Aba 2 — "Resumo"

| Seção | Conteúdo |
|-------|----------|
| **Totais** | Total após poda, total reprovado em E (por código), total pontuado |
| **Distribuição de Quartis** | Contagem e % de artigos em Q1/Q2/Q3/Q4 (faixas fixas) |
| **Critérios de Exclusão** | Frequência de cada código E ativado (E1 a E6) |
| **Scores P1–P7** | Distribuição de pontuação (0/1/2) em cada critério, separada por bloco (Introdução: P1–P4; Conclusão: P5–P7) |
| **Score médio por quartil** | Média de P1–P7 desagregada por quartil |
| **Dimensões de Classificação** | Frequência por categoria em cada dimensão |
| **Dados incompletos** | Artigos com `Abstract`, `Introduction` ou `Conclusion` vazias |
| **Auditoria da normalização** | `min`/`max` de `Score_Qualificacao`, pesos do Score Combinado, limites de cada quartil |

---

## Tom e estilo de análise

Escreva como um revisor sênior de periódico de alto impacto: técnico, objetivo e verificável. Cada justificativa deve permitir que outro pesquisador audite a decisão **sem reler o artigo**. Nunca use justificativas genéricas — cite os termos, afirmações ou ausências concretas que fundamentam cada critério E e cada score P, e identifique se a evidência vem da Introdução ou da Conclusão.

Vá além da superfície semântica: um artigo que usa Raft para coordenação de réplicas em armazenamento distribuído aborda "consenso", "replicação" e "tolerância a partições" mesmo que nenhum desses termos apareça no título. Use o contexto para inferir dimensões analíticas de forma semântica.

Mantenha o rigor elevado: a meta desta etapa é reter um conjunto reduzido de artigos sólidos e bem validados, não maximizar o número de aprovados. Na dúvida entre dois níveis de pontuação, prefira o mais conservador.