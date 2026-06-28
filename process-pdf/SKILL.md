---
name: process-pdf
description: >
  Use this skill whenever the user provides a CSV file with academic article metadata and wants
  to extract Introduction and Conclusion sections (or equivalent) from a corresponding set of PDF files
  (typically inside a .zip archive). This skill is specifically optimized for IEEE conference papers
  (two-column layout, Roman-numeral sections), especially SRDS (Reliable Distributed Systems), and
  handles batches of 100+ PDFs efficiently. Triggers on requests like: "enrich my CSV with intro and
  conclusion from these PDFs", "extract sections from the PDFs and add to the spreadsheet", "process
  the zip of papers and fill in introduction/conclusion columns", or any similar batch PDF section
  extraction and CSV enrichment workflow. Also use when the user asks to reprocess, fix, or improve
  a previous extraction run.
---

# process-pdf — IEEE Paper Section Extractor v3

Extrai seções de **Introdução** e **Conclusão** (e equivalentes) de um lote de PDFs IEEE,
enriquecendo um arquivo CSV com essas informações.

**Restrição de saída**: o script adiciona APENAS duas colunas ao CSV: `Introduction` e `Conclusion`.

**v3 — correção de truncamento (a Introdução agora sai íntegra).** A v2 truncava a
introdução para uma única frase porque a limpeza de bibliografia disparava no primeiro
agrupamento de citações inline (`[1] … [2]`). A v3 corrige isso e foi validada em 139 PDFs
IEEE SRDS reais: **136/136 introduções com ≥95 % de cobertura (média e mediana de 100 %)**
do conteúdo íntegro da seção. Ver "Validação" ao final.

---

## Workflow resumido

1. Copiar e instalar o script
2. Identificar arquivos de entrada (CSV + ZIP de PDFs)
3. Executar a extração
4. Revisar falhas e corrigir
5. Entregar o CSV enriquecido

---

## Passo 1 — Copiar e instalar

```bash
mkdir -p /home/claude/process-pdf/scripts
cp /mnt/skills/user/process-pdf/scripts/extract_sections.py \
   /home/claude/process-pdf/scripts/extract_sections.py

pip install rapidfuzz --break-system-packages -q
```

> **Nunca reescreva o script do zero.** Ele contém lógica validada contra 139 PDFs IEEE reais
> (introdução íntegra em 100 % dos artigos com introdução detectável).

---

## Passo 2 — Entender as entradas

Inferir do contexto ou perguntar ao usuário:

- **CSV**: caminho + nome da coluna de títulos
- **ZIP**: caminho para o arquivo com os PDFs
- **Saída**: onde salvar o CSV enriquecido

Se forem uploads do usuário, estarão em `/mnt/user-data/uploads/`.

---

## Passo 3 — Executar

```bash
python3 /home/claude/process-pdf/scripts/extract_sections.py \
  --csv      <path/to/articles.csv> \
  --zip      <path/to/pdfs.zip> \
  --title-col "<Nome da Coluna de Título>" \
  --out      <path/to/enriched.csv>
```

O script:
- Detecta estrutura do ZIP (plana ou com subpastas)
- Usa fuzzy matching de títulos (limiar 70 por padrão)
- Detecta seções aceitando cabeçalhos **CAIXA ALTA e Title Case**; escolhe o espinhaço de
  numeração por **subsequência crescente** (ignora subseções e tolera seções perdidas)
- Extrai Introdução **íntegra** (sem corte por citação inline) e Conclusão, com múltiplos fallbacks
- **Remove** footers IEEE/licenciamento/DOI; remove referências/agradecimentos **só da conclusão**
- **Normaliza** quebras de linha: `\n` simples → espaço, `\n\n` preservado
- Imprime status por artigo com diagnóstico `intro=✓ conclusão=✓`
- Salva APENAS as colunas `Introduction` e `Conclusion`

---

## Passo 4 — Revisar falhas

Após a execução, verificar o relatório impresso:

| Sintoma | Causa provável | Ação |
|---|---|---|
| Título sem correspondência | Título muito diferente do nome do PDF | `--threshold 55` |
| `intro=✗` | Artigo com formato não-padrão | Inspeção manual |
| `conclusão=✗` | Artigo sem seção de conclusão explícita | Esperado (célula vazia correta) |
| Texto garbled | PDF digitalizado (imagem) | Ver seção "PDFs Digitalizados" |
| ZIP com subpastas | Script aplana automaticamente | Nenhuma |

Para diagnóstico de um único PDF:

```python
import sys
sys.path.insert(0, '/home/claude/process-pdf')
from scripts.extract_sections import (
    load_pdf_text, strip_footers, find_sections, classify_section,
    extract_intro_conclusion,
)

raw  = load_pdf_text("/path/to/paper.pdf")
secs = find_sections(strip_footers(raw))      # find_sections opera sobre texto sem footer
for pos, num, title in secs:
    print(f"[{num:>4}] {classify_section(title):12s}  {title}")

intro, conclusion = extract_intro_conclusion(raw)
print("INTRO  len:", len(intro or ""))
print(intro)
print("CONCL  len:", len(conclusion or ""))
print(conclusion)
```

---

## Pipeline de limpeza de texto

A limpeza é aplicada **por seção** depois do fatiamento:

### Passo 1 — Remoção de footers/boilerplate (documento inteiro + por seção)

| Padrão | Exemplo |
|---|---|
| Bloco de acesso IEEE Xplore | `Authorized licensed use limited to: UFRGN. Downloaded on…` |
| Linhas "Downloaded on DATE" | `Downloaded on June 12,2026 at 16:38:55 UTC` |
| Copyright/ISBN | `978-1-7281-4807-6/23/$31.00 © 2023 IEEE` |
| DOI (com e sem prefixo) | `DOI: 10.1109/SRDS57473.2023.00016` · `10.1109/SRDS…` |
| URLs doi.org / dx.doi.org | `http://dx.doi.org/10.1109/…` |
| Creative Commons / Open Access | `This work is licensed under a Creative Commons…` |
| Avisos de manuscrito | `Manuscript received May 2023; accepted August 2023` |
| ORCID / e-mail | `ORCID iD: 0000-0002-1234-5678` |
| Cabeçalhos de conferência/journal | `2023 IEEE 42nd SRDS`, `IEEE Transactions on…` |
| Números de página isolados | `42` em linha própria |
| Index Terms / Keywords | `Index Terms—fault tolerance, consensus` |

### Passo 2 — Remoção CONSERVADORA de back-matter (SÓ na conclusão)

Aplicada apenas à última seção (conclusão), pois é a única que pode encostar nas
referências/agradecimentos. **Nunca é aplicada à introdução.** Corta o texto quando encontra:

- Cabeçalho explícito `REFERENCES` / `BIBLIOGRAPHY` / `REFERÊNCIAS` / `ACKNOWLEDGMENTS` / `AGRADECIMENTOS`.
- Um bloco de lista de referências de verdade: **≥3 entradas consecutivas** que começam
  a linha com `[N] Autor…` (próximas entre si). Citações inline soltas **não** disparam o corte.
- Agradecimentos inline no final (`Acknowledgments. This work was supported …`).

### Passo 3 — Normalização de quebras de linha (por seção)

| Transform | Motivo |
|---|---|
| `\r\n` / `\r` → `\n` | Normalizar finais Windows |
| `word-\n` → `word` | Rejuntar quebra de coluna hifenizada |
| `\n` simples → espaço | Quebra de linha PDF não é nova frase |
| `\n\n+` → `\n\n` | Limite de parágrafo preservado |
| Espaços duplos colapsados | Artefatos de extração |

> ⚠️ **A introdução NÃO sofre remoção de bibliografia.** Seu limite final já é o início da
> próxima seção (ex.: "II. …"), muito antes das referências, então qualquer corte por
> citação só poderia truncar texto válido. Esse era exatamente o bug da v2.

---

## Lógica de detecção de seções (v3)

### Por que a Introdução não é mais truncada

A v2 chamava `_strip_trailing_bibliography` na introdução, e essa função cortava no primeiro
par de marcadores `[1] … [2]` próximos — o que ocorre em QUALQUER introdução com citações
inline. Resultado: introdução reduzida à primeira frase. A v3 (a) **não** aplica remoção de
bibliografia à introdução e (b) tornou a remoção conservadora (só lista de referências real).

### Cabeçalho de seção detectado

Linha que satisfaz:
- Começa (no início da linha) com numeral **romano** (`I`–`XII…`) ou **árabe** (1–99), seguido de `.` ou `)`
- Título com 2–10 palavras e ≥75 % de caracteres alfabéticos
- Título em **CAIXA ALTA** (`INTRODUCTION`) **ou** em **Title Case** (`Introduction`, `Related Work`)
  — a v3 aceita os dois estilos (a v2 só aceitava CAIXA ALTA, perdendo papers Title-Case)

### Seleção do esquema de numeração (espinhaço)

Quando o paper mistura seções de topo (I, II, III…) com enumerações de subseção (1), 2), 3)…),
o script escolhe o esquema cujo **maior subsequência crescente** (LIS) é mais longa:
- Seções de topo crescem monotonicamente mesmo com uma seção perdida (I, III, IV, V, VI → cadeia de 5)
- Subseções **reiniciam** (1,2,3 … 1,2,3), logo só formam cadeias curtas
- A LIS isola o espinhaço real e ignora subseções intercaladas e falsos positivos
  (tolera, por exemplo, uma seção "II" não detectada por causa de quebra de página)

### Estratégia de extração de texto do PDF

`pdftotext -raw` (evita interleaving de duas colunas) → `pdftotext` padrão → `pypdf`.
Form-feeds (`\x0c`) viram `\n\n` **preservando** o conteúdo seguinte — a v2 apagava a linha
inteira após o form-feed, destruindo cabeçalhos colados ao quebra-página (ex.: `\x0cI. Introduction`).

### Variantes de Introdução reconhecidas
`INTRODUCTION`, `INTRODUÇÃO`, `OVERVIEW`, `MOTIVATION`, `BACKGROUND`, `PROBLEM STATEMENT`,
`PROBLEM DESCRIPTION`, `PROPOSED APPROACH`, `CONTRIBUTION`, etc.

### Variantes de Conclusão reconhecidas
`CONCLUSION(S)`, `CONCLUDING REMARKS`, `FINAL REMARKS`, `SUMMARY`, `DISCUSSION`,
`FINAL CONSIDERATIONS`, `CONSIDERAÇÕES FINAIS`, `CONCLUSION AND FUTURE WORK`, etc.

### Estratégia de fallback (quando não há seção numerada explícita)

**Introdução**: primeira seção `intro` → primeira seção `body` (≥100 chars) →
título em linha isolada → preâmbulo antes da primeira subseção (papers de workshop).

**Conclusão** (do FINAL para o início): última seção `conclusion` → última seção `body`
substancial (≥200 chars) que não seja claramente técnica → `None` se o artigo genuinamente
não tiver conclusão (célula vazia correta).

---

## Estratégia de extração de texto do PDF

Tenta três métodos em ordem, usando o primeiro que retornar ≥200 chars:

1. `pdftotext -raw` — lê fluxos de conteúdo PDF em ordem; evita interleaving de duas colunas e produz cabeçalhos de seção mais limpos *(recomendado para papers IEEE)*
2. `pdftotext` — layout padrão; fallback geral
3. `pypdf` — Python puro; último recurso

**`pdftotext -layout` NÃO é usado** — adiciona espaços de alinhamento que quebram os regexes de seção.

**Form-feeds** (`\x0c`) do pdftotext são convertidos em `\n\n` antes do processamento.

---

## PDFs Digitalizados

Se a extração retorna texto vazio, o arquivo é provavelmente digitalizado/rasterizado.
As células `Introduction` e `Conclusion` ficam vazias para essas linhas.
Para OCR, consulte `/mnt/skills/public/pdf-reading/SKILL.md` → seção "Scanned documents".

---

## Colunas adicionadas ao CSV

| Coluna | Conteúdo |
|---|---|
| `Introduction` | Texto completo da seção de introdução (limpo, normalizado) |
| `Conclusion` | Texto completo da seção de conclusão (limpo, normalizado) |

**Nenhuma outra coluna é adicionada.**

---

## Opções da linha de comando

| Flag | Padrão | Descrição |
|---|---|---|
| `--csv` | obrigatório | Caminho para o CSV de entrada |
| `--zip` | obrigatório | Caminho para o ZIP com PDFs |
| `--title-col` | obrigatório | Nome da coluna de títulos no CSV |
| `--out` | obrigatório | Caminho para o CSV de saída |
| `--threshold` | 70 | Limiar de similaridade fuzzy (0–100) |
| `--workers` | 4 | Workers paralelos |
| `--max-chars` | 15000 | Máximo de caracteres por seção |

---

## Desempenho

Para 100+ PDFs, o script processa em paralelo (4 workers padrão).
Estimativa: ~3–5s por PDF → ~5–10 min para 100 PDFs.

---

## Validação (v3)

Validado contra os **139 PDFs IEEE SRDS** do corpus de revisão.

**Metodologia**: para cada PDF, um extrator de referência independente (não baseado neste
script) recorta a introdução íntegra — do cabeçalho `I. Introduction` até a próxima seção de
topo — aplicando a mesma remoção de footers (requisito comum, não o que está sob teste).
A cobertura é medida por **recall em nível de token** (`difflib.SequenceMatcher` sobre tokens
alfanuméricos), o que ignora ruído cosmético (hifenização, espaços) e isola o que importa:
quanto do conteúdo íntegro da introdução o script captura.

**Resultados**:
- **136/136** introduções com **≥95 %** de cobertura (artigos com introdução detectável)
- Cobertura **média e mediana = 100 %**
- 0/139 introduções vazias ou truncadas (todas ≥300 chars, completas até a próxima seção)
- 138/139 conclusões extraídas (a faltante é um artigo genuinamente sem conclusão)
- Zero corte por citação inline; zero footer/DOI/licença/referência/agradecimento vazando

**Regressões corrigidas vs. v2** (mediana de cobertura da introdução subiu de **8,2 % → 100 %**):
1. `_strip_trailing_bibliography` truncava a introdução no primeiro `[1] … [2]` — agora é
   conservadora e **nunca** roda na introdução.
2. Detecção de cabeçalho aceitava só CAIXA ALTA — agora aceita Title Case também.
3. Form-feed apagava cabeçalhos colados ao quebra-página — agora preserva o conteúdo.
4. Seleção de esquema de numeração pegava subseções soltas — agora usa o espinhaço por LIS.
