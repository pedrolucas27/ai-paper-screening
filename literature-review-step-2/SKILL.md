---
name: literature-review-step-2
description: "Segundo estágio de uma pipeline de revisão literária. Use esta skill sempre que o usuário mencionar 'revisão step 2', 'etapa 2 da revisão', 'pontuação de artigos', 'filtro de qualidade de artigos', 'leitura seletiva de artigos', ou fornecer um CSV/XLSX do filtro da etapa 1 com coluna 'Score Stage 1 (0-1)' e um segundo CSV/XLSX com Abstract, Introduction e Conclusion pedindo para aplicar critérios de exclusão e emitir pontuação de qualidade/relevância. Também use quando o usuário pedir para avaliar a qualidade de redação e de execução científica (introdução e conclusão) de artigos já aprovados na triagem temática, em qualquer área de pesquisa. Além da pontuação, esta skill também classifica os artigos não excluídos em quatro dimensões conceituais (Tipo de Domínio, Técnicas/Abordagens Utilizadas, Tipo de Falha/Problema Abordado e Métricas de Avaliação), com base exclusivamente em Abstract/Introduction/Conclusion."
---

# Refinamento — Estágio 2 de Revisão da Literatura

## Papel

Atue como um pesquisador Professor Doutor (PhD) com reconhecimento internacional e mais de 10 anos chefiando um laboratório de pesquisa na área definida pelos eixos temáticos do usuário (a mesma área já identificada no Estágio 1). A aderência temática já foi decidida no Estágio 1 — não a recalcule aqui. Sua tarefa agora é julgar, como revisor de periódico de alto impacto, se a Introdução e a Conclusão de cada artigo têm o nível de execução e rigor de um artigo **excelente** desta subárea específica, não apenas "aceitável". Leia `Abstract`, `Introduction` e `Conclusion` dos artigos aprovados no Estágio 1 e produza uma avaliação quantitativa auditável.

Os eixos temáticos só reaparecem nesta etapa de duas formas, nunca como repontuação: como checagem confirmatória de domínio (critério E4) e como rótulo descritivo na Dimensão 3 da classificação.

---

## Visão geral do processo

1. **Poda** — filtra artigos pelo `Score Stage 1 (0-1)` do Estágio 1.
2. **Cruzamento** — localiza o texto expandido (Abstract/Introduction/Conclusion) de cada artigo podado.
3. **Filtro de Exclusão (E1–E5)** — binário, reprovação imediata se qualquer critério ativar.
4. **Classificação + Pontuação (P1–P5)** — só para artigos não excluídos.
5. **Cálculo final** — normalização, `Score Combinado` com o Estágio 1, `Quartil`.

---

## Entradas obrigatórias

1. **Planilha do Estágio 1** (ex.: `filtro_etapa_1.csv`) com a coluna `Score Stage 1 (0-1)`. Preserve todas as colunas originais na saída.
2. **Planilha de artigos expandidos**, com pelo menos `titulo`, `Abstract`, `Introduction` e `Conclusion`. Cruzamento por similaridade de título (tolerante a caixa, acentuação, truncamentos, siglas).
3. **Eixos temáticos** (os mesmos do Estágio 1) — usados apenas no critério E4 e na marcação da Dimensão 3.

**Poda (opcional, 0–1):** score mínimo de `Score Stage 1 (0-1)` para entrar na análise. Padrão: 0 (processa todos com score > 0).

---

## Etapa 1 — Poda e Cruzamento

1. Filtre os artigos do Estágio 1 mantendo apenas `Score Stage 1 (0-1)` acima da poda. Os removidos não entram em nenhuma etapa seguinte e não aparecem na saída final (diferente dos reprovados em E, que aparecem com colunas de score em branco).
2. Para cada artigo restante, localize a linha correspondente no CSV de texto expandido por similaridade de título. Não localizou? Avance sem bloquear os demais e registre a ausência na `Justificativa`.
3. Leia `Abstract`, `Introduction` e `Conclusion` como um conjunto único de evidência — não isole as seções ao buscar validação (ver E5 e P4). Seção vazia: use as demais e registre a limitação.

---

## Etapa 2 — Filtro de Exclusão (E1–E5)

Critérios binários — **ativado** ou **não ativado** — aplicados a cada artigo cruzado, antes de qualquer classificação ou pontuação. Nunca são somados ou convertidos em número. Na incerteza sobre se um critério se aplica, reprove pelo lado mais rigoroso.

| Código | Critério |
|--------|----------|
| **E1** | A introdução não apresenta problema de pesquisa, lacuna ou objetivo identificável, e/ou a conclusão não declara contribuição ou resultado concreto. |
| **E2** | Há contradição ou desconexão explícita entre o que a introdução promete (problema/objetivo) e o que a conclusão entrega (contribuição/resultado). |
| **E3** | Introdução e conclusão são insuficientes para avaliar qualidade (conteúdo excessivamente curto, truncado, genérico ao ponto de impedir avaliação, ou ausente). |
| **E4** | O domínio/escopo revelado pelo texto completo é incompatível com o Eixo 2 da revisão, de um jeito que não era visível no resumo avaliado no Estágio 1 (ex.: o abstract sugeria sistemas distribuídos multi-nó, mas a introdução revela um experimento single-node). |
| **E5** | Nenhuma das três seções, lidas em conjunto, menciona qualquer forma concreta de validação (experimento, prova formal, simulação, estudo de caso, prototipagem avaliada) — trabalho puramente especulativo. **Menção a limitações e/ou trabalhos futuros na conclusão nunca, por si só, ativa E5.** Releia as três seções por completo antes de ativar; só ative se nenhuma evidência de validação aparecer em nenhuma delas. |

**Registro:**
1. Códigos ativados em `Criterios_Exclusao_Ativados` (ex.: `E1; E2`) ou `Nenhum`.
2. Para cada código ativado, cite na `Justificativa` a evidência textual concreta (termo, afirmação ou ausência específica) e a seção de origem. Para E5, declare explicitamente que as três seções foram revisadas em conjunto e nenhuma evidência de validação foi encontrada — não basta dizer "a conclusão não valida".
3. Qualquer critério ativado encerra a análise do artigo: não prossiga para a Etapa 3. Nas colunas `Tipo_Dominio`, `Tecnicas_Abordadas`, `Tipo_Falha_Problema`, `Metricas_Avaliacao`, registre `NÃO PROCESSADO — artigo excluído (<códigos>)`.

---

## Etapa 3 — Classificação Conceitual Multidimensional

Aplicada apenas aos artigos não excluídos na Etapa 2, com base no texto já lido na Etapa 1. Vá além da superfície semântica: um artigo que usa Raft para coordenação de réplicas trata de "consenso", "replicação" e "tolerância a partições" mesmo sem citar esses termos literalmente. Toda categoria atribuída exige evidência textual concreta, registrada na `Justificativa` com a seção de origem.

#### Dimensão 1 — Tipo de Domínio

(multivalorado; domínio(s) concreto(s), não descrição genérica)

| Categoria | Descrição |
|---|---|
| `Sistemas Distribuídos/Cloud` | Sistemas distribuídos genéricos, computação em nuvem, datacenters |
| `Edge/Fog Computing` | Processamento descentralizado próximo aos dispositivos/usuários |
| `IoT/Sistemas Embarcados` | Dispositivos de baixo poder computacional, sensores, redes de sensores |
| `Blockchain/Sistemas Descentralizados` | Ledgers distribuídos, criptomoedas, contratos inteligentes |
| `Microsserviços/Containers` | Arquiteturas de microsserviços, orquestração de containers |
| `Redes de Computadores` | Protocolos de rede, infraestrutura de comunicação, SDN |
| `Armazenamento/Bancos de Dados` | Storage distribuído, bancos de dados, sistemas de arquivos |
| `Sistemas Críticos/Tempo Real` | Sistemas com requisitos rígidos de tempo ou segurança crítica |
| `Computação de Alto Desempenho (HPC)` | Clusters, supercomputação, processamento paralelo massivo |
| `Infraestrutura de IA/ML` | Pipelines, plataformas ou infraestrutura para treinamento/inferência de modelos |

Categoria nova e descritiva se nenhuma capturar o domínio com fidelidade.

#### Dimensão 2 — Técnicas/Abordagens Utilizadas

(multivalorado)

| Categoria | Descrição |
|---|---|
| `Algoritmos de Consenso` | Raft, Paxos, PBFT e variantes |
| `Replicação` | Réplicas de dados/estado, replicação ativa/passiva |
| `Checkpointing/Rollback-Recovery` | Salvamento periódico de estado para recuperação posterior |
| `Detecção de Falhas (Failure Detectors)` | Heartbeats, timeouts, gossip para detectar falhas |
| `Redundância de Hardware/Software` | N-versão, replicação tripla modular (TMR), redundância de componentes |
| `Machine Learning/IA Aplicada` | Modelos preditivos, detecção de anomalias, otimização via aprendizado |
| `Particionamento/Sharding` | Divisão de dados ou carga entre nós |
| `Balanceamento de Carga` | Distribuição dinâmica de requisições/carga entre recursos |
| `Criptografia/Mecanismos de Segurança` | Assinaturas digitais, criptografia, autenticação, controle de acesso |
| `Migração/Orquestração de Containers` | Live migration, escalonamento automático (auto-scaling) |
| `Escalonamento de Recursos (Scheduling)` | Algoritmos de alocação de recursos ou tarefas |

Categoria nova e descritiva se nenhuma capturar a técnica com fidelidade.

#### Dimensão 3 — Tipo de Falha/Problema Abordado

(multivalorado; tipo de falha/problema efetivamente discutido)

| Categoria | Descrição |
|---|---|
| `Falhas de Colapso (Crash Failures)` | Nó/processo para de responder por completo |
| `Falhas Bizantinas` | Comportamento arbitrário, incorreto ou malicioso |
| `Partição de Rede` | Perda de conectividade entre subconjuntos de nós |
| `Falhas de Omissão` | Perda de mensagens, requisições não atendidas |
| `Falhas Temporais (Timing)` | Violação de prazos, atrasos além do tolerável |
| `Ataques de Segurança` | DDoS, injeção, exploração de vulnerabilidades, acesso não autorizado |
| `Degradação de Desempenho` | Lentidão, gargalos, baixa vazão sob carga |
| `Inconsistência de Dados/Estado` | Estados divergentes entre réplicas ou nós |
| `Esgotamento de Recursos` | Falta de memória, CPU, energia ou banda |
| `Falhas de Software (Bugs/Exceções)` | Erros de programação, exceções não tratadas |

Categoria nova e descritiva se nenhuma capturar o tipo de falha/problema com fidelidade.

> **Marcação de eixo (só nesta dimensão, só como rótulo):** identifique entre parênteses a qual eixo cada categoria se relaciona — `(Eixo 1)`, `(Eixo 2)` ou `(Ambos)`. Ex.: `Falhas Bizantinas (Eixo 1)`; `Partição de Rede (Eixo 2)`; `Falhas de Colapso em Sistemas Distribuídos (Ambos)`.

#### Dimensão 4 — Métrica de Avaliação

(multivalorado; métricas efetivamente citadas, não apenas a categoria)

| Categoria | Exemplos |
|---|---|
| `Latência/Tempo de Resposta` | ms, tempo médio, percentis (p95/p99) |
| `Throughput/Vazão` | requisições/s, transações/s, MB/s |
| `Disponibilidade` | uptime %, SLA, tempo médio até falha (MTBF) |
| `Overhead de Recursos` | uso de CPU, memória, rede, energia |
| `Escalabilidade` | desempenho vs. número de nós/usuários/réplicas |
| `Recuperação de Falhas` | MTTR, tempo de detecção/recuperação |
| `Acurácia/Precisão` | accuracy, precision, recall, F1 (quando aplicável) |
| `Custo Computacional` | complexidade assintótica, custo monetário |
| `Métrica Qualitativa` | satisfação do usuário, facilidade de uso, percepção |
| `Nenhuma Métrica Quantitativa` | avaliação puramente qualitativa/descritiva |

Trabalho teórico puro, sem métricas: registre `Nenhuma Métrica Quantitativa` e justifique.

**Casos especiais:** dimensão não determinável a partir do texto disponível → `Não identificado`. Exige leitura mais profunda do que as três seções permitem → `REVISAR` + nota na `Justificativa`. Artigo não localizado no cruzamento → `NÃO PROCESSADO — artigo não cruzado`. Múltiplos valores na mesma dimensão: separe com `;`.

Registre os resultados em `Tipo_Dominio`, `Tecnicas_Abordadas`, `Tipo_Falha_Problema` e `Metricas_Avaliacao` (ver "Saída").

---

## Etapa 4 — Pontuação de Excelência (P1–P5)

Aplique apenas aos artigos que passaram em E1–E5. Cada critério vai de **0 a 2**. Em todos os cinco, o padrão de comparação é "isso está no nível de um artigo **excelente** desta subárea?" — não "isso está presente?". Na incerteza entre dois níveis, atribua o mais baixo. P1–P3 avaliam a Introdução; P4–P5 avaliam a Conclusão (P4 pode usar evidência de qualquer uma das três seções).

**P1 — Especificidade e Contextualização do Problema**
- **2**: Problema técnico específico, cenário concreto e escopo delimitado — não uma reformulação genérica do campo de pesquisa.
- **1**: Problema e cenário identificáveis, mas genéricos em algum aspecto ou exigindo inferência para fechar o escopo.
- **0**: Problema ausente, vago, ou indistinguível de uma descrição genérica da área.

**P2 — Solidez da Lacuna e Posicionamento na Literatura**
- **2**: Lacuna específica, articulada com referência concreta e verificável ao estado da arte da subárea — mostra a limitação real de abordagens existentes, não apenas "poucos trabalhos abordam X".
- **1**: Lacuna e motivação presentes, mas com posicionamento frente à literatura genérico, incompleto ou pouco específico.
- **0**: Lacuna ausente, implícita, ou puramente genérica (ex.: "o tema é importante e pouco estudado", sem referência concreta ao que já existe).

**P3 — Clareza e Relevância da Contribuição/Questão de Pesquisa**
- **2**: Questão/objetivo declarado com precisão verificável **e** a conclusão entrega uma contribuição cujo impacto (prático, teórico ou aplicado) é claramente articulado e relevante, não trivial.
- **1**: Questão/objetivo e contribuição presentes e conectados, mas imprecisos, modestos, ou com impacto pouco detalhado.
- **0**: Questão/objetivo ausente, genérico, ou contribuição não declarada / sem conexão clara de impacto com o problema original.

**P4 — Rigor e Robustez da Validação**
- **2**: Validação robusta no padrão da subárea — experimento controlado com baseline(s) relevante(s), prova formal completa, ou simulação/estudo extensivo com variação de cenário.
- **1**: Validação presente, mas de escopo abaixo do padrão de excelência (um único baseline, um único cenário, amostra pequena, sem variação).
- **0**: Nenhuma evidência de validação em nenhuma das três seções (geralmente coincide com E5 — se atingir 0 aqui sem o artigo ter sido excluído por E5, revise se E5 não deveria ter sido ativado).

**P5 — Maturidade Crítica: Limitações e Trabalhos Futuros**
Independente da nota em P4 — mede reflexão crítica sobre os próprios limites, não validação.
- **2**: Limitações específicas e tecnicamente fundamentadas e/ou direções futuras concretas, no nível de maturidade crítica de um artigo de referência na subárea.
- **1**: Menção a limitações ou trabalhos futuros presente, mas genérica ou pouco fundamentada.
- **0**: Nenhuma menção a limitações ou trabalhos futuros, ou menção tão genérica que equivale à ausência (ex.: "pretende-se expandir o trabalho", sem direção concreta).

**Registro:** resuma os cinco valores em `Score P1-P5`, formato `P1=2; P2=0; P3=1; P4=2; P5=1` (sempre as cinco chaves, ordem P1→P5). Some em `Score Bruto 2` (0–10). Na `Justificativa`, cite evidência textual concreta para cada critério, com a seção de origem; para notas intermediárias, explique objetivamente por que o atendimento fica abaixo do nível pleno.

---

## Etapa 5 — Cálculo Final: do Score Bruto 2 ao Quartil

Depois de pontuar todo o lote, aplique a cascata **nesta ordem exata**:

| Passo | Coluna | Fórmula | Escala | Sobre quê opera |
|-------|--------|---------|--------|------------------|
| 1 | `Score Bruto 2` | `P1+P2+P3+P4+P5` | 0–10 | Cada artigo (Etapa 4) |
| 2 | `Score Stage 2` | `(Score Bruto 2 − min) / (max − min)` | 0–1 | `min`/`max` sobre todos os artigos não excluídos do lote |
| 3 | `Score Combinado` | `0,40 × Score Stage 1 + 0,60 × Score Stage 2` | 0–1 | Cada artigo, usando `Score Stage 1 (0-1)` do Estágio 1 (vírgula → ponto se necessário) |
| 4 | `Quartil` | Faixa fixa de `Score Combinado` (tabela abaixo) | Q1–Q4 | Cada artigo |

**Casos de borda:**
- `max == min` (inclui o caso de um único artigo aprovado): `Score Stage 2 = Score Bruto 2 / 10` para todos — não divida por zero.
- Nenhum artigo passou em E1–E5: pule os passos 2–4; `Score Bruto 2`, `Score Stage 2`, `Score Combinado` e `Quartil` ficam em branco para todo o lote; registre essa condição na aba "Resumo".
- Artigos reprovados em E1–E5 nunca entram no cálculo de `min`/`max` e seguem para a saída com essas quatro colunas em branco.
- Arredonde só no momento de registrar (4 casas decimais para `Score Stage 2` e `Score Combinado`) — nunca arredonde um valor intermediário antes de usá-lo no próximo passo.

**Faixas fixas de Quartil** (valor absoluto do `Score Combinado`, não percentil):

| Quartil | Faixa |
|---------|-------|
| **Q1** | > 0,75 |
| **Q2** | > 0,50 e ≤ 0,75 |
| **Q3** | > 0,25 e ≤ 0,50 |
| **Q4** | ≤ 0,25 |

Faixas fixas, não posicionais — distribuição desigual entre quartis é esperada.

Peso 60/40: a leitura aprofundada desta etapa (qualidade de execução, julgada pelo padrão de excelência da subárea) é o sinal mais forte; a aderência temática do Estágio 1 mantém peso relevante no resultado final.

---

## Saída

Não gere artefatos visuais, widgets, dashboards ou componentes HTML/React (`show_widget` proibido). A única saída desta skill é o arquivo `.xlsx` abaixo. Leia `/mnt/skills/public/xlsx/SKILL.md` antes de gerá-lo.

Gere **`filtro_etapa_2.xlsx`** em `/mnt/user-data/outputs/`, com três abas:

### Aba 1 — "Resultado"

Todas as colunas originais do CSV do Estágio 1, acrescidas de:

| Coluna | Conteúdo |
|--------|----------|
| `Tipo_Dominio` | Categoria(s) da Dimensão 1, separadas por `;`; reprovados em E: `NÃO PROCESSADO — artigo excluído (<códigos>)` |
| `Tecnicas_Abordadas` | Categoria(s) da Dimensão 2; mesma regra |
| `Tipo_Falha_Problema` | Categoria(s) da Dimensão 3, com marcação de eixo entre parênteses; mesma regra |
| `Metricas_Avaliacao` | Categoria(s)/métricas da Dimensão 4; mesma regra |
| `Criterios_Exclusao_Ativados` | Códigos E ativados (ex.: `E1; E3`) ou `Nenhum` |
| `Score P1-P5` | `P1=2; P2=0; ...; P5=2`; em branco se reprovado em E |
| `Score Bruto 2` | Soma direta `P1+...+P5` (0–10); em branco se reprovado em E |
| `Score Stage 2` | Normalização Min-Max (0–1, 4 casas decimais); em branco se reprovado em E |
| `Score Combinado` | `0,40 × Score Stage 1 + 0,60 × Score Stage 2` (4 casas decimais); em branco se reprovado em E |
| `Quartil` | `Q1`–`Q4` (em branco para reprovados em E) |
| `Justificativa` | Evidências textuais concretas para cada critério E (motivo de cada exclusão), cada critério P e cada categoria das quatro dimensões, com a seção de origem (Abstract, Introdução ou Conclusão) |

**Formatação:**
- `Quartil`: gradiente Q4 azul escuro → Q1 cinza. Reprovados em E: vermelho claro.
- `Score Bruto 2` e `Score Combinado`: barra de dados (data bar), menor ao maior valor (`Score Bruto 2` em escala 0–10).
- `Criterios_Exclusao_Ativados`: fundo vermelho claro quando diferente de `Nenhum`.
- `Tipo_Dominio`, `Tecnicas_Abordadas`, `Tipo_Falha_Problema`, `Metricas_Avaliacao`: cor de fundo distinta por dimensão.
- Cabeçalho congelado, autofiltro ativo (`worksheet.auto_filter.ref`).

### Aba 2 — "Resumo"

| Seção | Conteúdo |
|-------|----------|
| **Totais** | Total após poda, total reprovado em E (por código), total pontuado |
| **Distribuição de Quartis** | Contagem e % por Q1/Q2/Q3/Q4 |
| **Critérios de Exclusão** | Frequência de cada código E1–E5 |
| **Distribuição P1–P5** | Contagem e % dos valores 0/1/2 em cada critério, sobre os artigos pontuados |
| **Score Bruto 2 médio por quartil** | Média de `Score Bruto 2`, por quartil |
| **Distribuição — Tipo de Domínio / Técnicas / Falha-Problema / Métricas** | Frequência de cada categoria das Dimensões 1–4, sobre os artigos não excluídos |
| **Dados incompletos** | Artigos com `Abstract`, `Introduction` ou `Conclusion` vazias |
| **Auditoria da normalização** | `min`/`max` usados, pesos do Score Combinado, limites de quartil; se nenhum artigo passou em E1–E5, registre "Nenhum artigo aprovado — normalização não aplicável" |

---

## Tom

Escreva como revisor sênior de periódico de alto impacto: técnico, objetivo, verificável — cada justificativa deve permitir auditoria sem reler o artigo. Cite termos, afirmações ou ausências concretas, nunca justificativas genéricas, e identifique a seção de origem de cada evidência.
