# AI Paper Screening

Conjunto de **skills para Claude** (Anthropic) que automatiza a triagem e avaliação de artigos científicos em revisões literárias. O pipeline reproduz, com auxílio de IA, as etapas que um revisor humano realizaria, da triagem inicial por título/resumo até a leitura integral dos artigos, e entrega como resultado uma planilha consolidada com ranking final dos artigos mais relevantes.

## Contexto acadêmico

O projeto foi desenvolvido no âmbito da disciplina **TÓPICOS AVANÇADOS EM SISTEMAS INTEGRADOS E DISTRIBUÍDOS II** do **PROGRAMA DE PÓS-GRADUAÇÃO EM SISTEMAS E COMPUTAÇÃO (PPgSC)**. A disciplina não é de revisão literária em si, mas o pipeline foi criado como ferramenta de apoio para realizar a revisão literária dos temas abordados na disciplina, lidando com o volume de artigos retornado por buscas em bases como o IEEE Xplore.

A avaliação é estruturada em torno de **dois eixos temáticos** definidos pelo pesquisador (Eixo 1: principal/peso maior; Eixo 2: secundário/peso menor), que guiam os critérios de inclusão/exclusão em todas as etapas.

## Estrutura do pipeline

O repositório é um **conjunto de skills** (arquivos `SKILL.md`) que instruem o Claude a atuar como revisor científico em quatro estágios sequenciais:

| Skill | Função |
|---|---|
| `literature-review-step-1` | Filtro inicial por **aderência temática**, a partir de título, resumo e palavras-chave. |
| `process-pdf` | Extração automatizada das seções **Introdução** e **Conclusão** de PDFs, enriquecendo a planilha. |
| `literature-review-step-2` | Refinamento por **qualidade de introdução/conclusão** (critérios de exclusão E1–E5) e classificação conceitual dos artigos aprovados. |
| `literature-review-step-3` | Avaliação de **qualidade metodológica e reprodutibilidade** com leitura do PDF íntegro, gerando o **ranking final** (Score Geral 0–10). |
| `literature-review-orchestrator` | Conduz as três etapas em sequência, lendo e salvando os arquivos em uma única pasta do Google Drive, sem exigir que o usuário repita informações entre etapas. |

## Funcionamento

1. **Etapa 1: Filtro inicial.** Avalia cada artigo por título, resumo e palavras-chave. Aplica checagem de presença do Eixo 1 (zeragem total se ausente) e, se presente, pontua aderência temática (0–10) combinada com impacto bibliométrico (citações/ano, por quartil), gerando `Score Stage 1 (0–1)`. Saída: `filtro_etapa_1.xlsx`.

2. **Extração de seções (`process-pdf`).** Script Python que extrai texto de PDFs via `pdftotext` (com fallback em `PyPDF2`), aplica heurísticas de limpeza para layout IEEE de duas colunas e localiza os artigos por correspondência *fuzzy* de título (`rapidfuzz`), enriquecendo a planilha com as colunas `Introduction` e `Conclusion`.

3. **Etapa 2: Refinamento.** Lê Abstract/Introdução/Conclusão dos artigos aprovados na Etapa 1, aplica cinco critérios binários de exclusão (E1–E5), pontua os não excluídos em cinco critérios de qualidade (P1–P5) e classifica em quatro dimensões conceituais. Combina com o `Score Stage 1` em um `Score Combinado` e `Quartil`. Saída: `filtro_etapa_2.xlsx`.

4. **Etapa 3: Qualidade metodológica.** Para os artigos aprovados na Etapa 2, lê o PDF íntegro e pontua quatro critérios (clareza metodológica, reprodutibilidade, comparação com o estado da arte, confiabilidade: 0/1/2,5 cada). Normaliza por min-max e combina com as etapas anteriores em um `Score Geral (0–10)`, gerando o **ranking final**.

5. **Orquestrador (opcional).** Executa as três etapas de forma encadeada, perguntando uma única vez os eixos temáticos e a pasta do Google Drive, e o parâmetro de poda em cada transição.

## Tecnologias

- **Claude (Anthropic)** como mecanismo de avaliação semântica, orientado por skills em Markdown com critérios, tabelas de pontuação e fórmulas explícitas.
- **Python 3** para extração de PDFs (`process-pdf/scripts/extract_sections.py`): `pdftotext`/`PyPDF2`, `rapidfuzz`, `ProcessPoolExecutor`, `pandas`, `openpyxl`.
- **Google Drive** (opcional, via integração do Claude) como repositório dos insumos e resultados no fluxo orquestrado.

## Estrutura do repositório

```
ai-paper-screening/
├── literature-review-step-1/SKILL.md          # Filtro inicial (aderência temática)
├── process-pdf/
│   ├── SKILL.md                                # Extração de Introdução/Conclusão
│   └── scripts/extract_sections.py             # Script de extração de PDFs
├── literature-review-step-2/SKILL.md          # Refinamento (qualidade de intro/conclusão)
├── literature-review-step-3/SKILL.md          # Qualidade metodológica e ranking final
├── literature-review-orchestrator/SKILL.md    # Orquestração das três etapas via Google Drive
└── README.md
```

## Como usar

Os arquivos `SKILL.md` são usados como **skills do Claude** (claude.ai, Claude Code ou API). Cada skill define em seu cabeçalho os gatilhos que levam o Claude a acioná-la automaticamente. Para o pipeline completo, use o orquestrador informando os dois eixos temáticos e o link da pasta do Google Drive com os insumos.
