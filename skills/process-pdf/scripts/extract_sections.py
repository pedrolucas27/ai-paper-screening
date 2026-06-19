#!/usr/bin/env python3
"""
extract_sections.py v2 — IEEE Paper Section Extractor
Optimized for SRDS / IEEE Xplore two-column PDFs.
"""

import argparse
import csv
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
import zipfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional, Tuple

# ─── Dependências opcionais ──────────────────────────────────────────────────

try:
    from rapidfuzz import fuzz, process as fuzz_process
    FUZZY_LIB = "rapidfuzz"
except ImportError:
    try:
        from thefuzz import fuzz, process as fuzz_process
        FUZZY_LIB = "thefuzz"
    except ImportError:
        fuzz_process = None
        FUZZY_LIB = None

try:
    import pypdf
    HAS_PYPDF = True
except ImportError:
    try:
        import PyPDF2 as pypdf  # type: ignore
        HAS_PYPDF = True
    except ImportError:
        HAS_PYPDF = False


# ═══════════════════════════════════════════════════════════════════════════════
# DETECÇÃO DE SEÇÕES — índice unificado (um único regex → ID e limites)
# ═══════════════════════════════════════════════════════════════════════════════

# Cabeçalho de seção de alto nível para papers IEEE:
#   numeral romano OU árabe de 1-2 dígitos, ponto ou parêntese,
#   seguido de título em CAIXA ALTA na mesma linha.
# Usando ^ com MULTILINE: .start() retorna posição exata do início da linha.
_SECTION_HDR_RAW = re.compile(
    r'^[ \t]*(?P<num>[IVX]{1,6}|\d{1,2})[\.\)]\s{1,6}(?P<title>[^\n\r]{2,100})[ \t]*$',
    re.MULTILINE,
)

# Marcador de Referências / Bibliografia (com ou sem numeral)
_REFS_HDR = re.compile(
    r'^[ \t]*(?:[IVX]{1,6}|\d{1,2})?[\.\)]?\s*'
    r'(?:REFERENCES?|BIBLIOGRAPHY|REFERÊNCIAS?|REFERENCIAS?)[ \t]*(?:\n|$)',
    re.MULTILINE | re.IGNORECASE,
)

# ── Conjuntos de palavras-chave para classificação ──────────────────────────

_INTRO_KW = re.compile(
    r'^(?:'
    r'INTRODUCTION|INTRODUÇÃO|INTRODUCAO|INTRODUC[AÃ]O'
    r'|OVERVIEW|MOTIVATION[S]?|BACKGROUND'
    r'|PROBLEM STATEMENT|PROBLEM DESCRIPTION|PROBLEM FORMULATION|PROBLEM OVERVIEW'
    r'|CONTEXT(?: AND MOTIVATION)?|RESEARCH CONTEXT|RESEARCH MOTIVATION'
    r'|PLANNED CONTRIBUTION[S]?(?: AND RELEVANCE)?'
    r'|PROPOSED APPROACH|PROPOSED SOLUTION|PROPOSED METHOD'
    r'|CONTRIBUTION[S]?|SCOPE(?: AND MOTIVATION)?'
    r'|SETTING THE STAGE|GETTING STARTED|SETTING UP'
    r')$',
    re.IGNORECASE,
)

_CONCLUSION_KW = re.compile(
    r'^(?:'
    r'CONCLUSION[S]?|CONCLUS[AÃ]O|CONCLUSÕES|CONCLUS[OÕ]ES'
    r'|CONCLUDING REMARKS?|FINAL REMARKS?|CLOSING REMARKS?'
    r'|CONCLUSION[S]? AND FUTURE WORK[S]?'
    r'|CONCLUSION[S]? AND FUTURE DIRECTIONS?'
    r'|CONCLUSION[S]? AND OUTLOOK'
    r'|CONCLUSION[S]? AND DISCUSSION'
    r'|CONCLUSION[S]? AND OPEN ISSUES?'
    r'|CONCLUSION[S]? AND PERSPECTIVES?'
    r'|CONCLUSION[S]? AND CONTRIBUTIONS?'
    r'|SUMMARY(?: AND CONCLUSION[S]?)?'
    r'|SUMMARY AND FUTURE WORK[S]?'
    r'|DISCUSSION(?: AND CONCLUSION[S]?)?'
    r'|DISCUSSION(?: AND FUTURE WORK[S]?)?'
    r'|FINAL CONSIDERATIONS?|CONSIDERAÇÕES FINAIS?|CONSIDERACOES FINAIS?'
    r'|PERSPECTIVES?(?: AND CONCLUSION[S]?)?'
    r'|LESSONS LEARNED(?: AND CONCLUSION[S]?)?'
    r'|WRAP[- ]?UP|EPILOG(?:UE)?'
    r')$',
    re.IGNORECASE,
)

_BACK_MATTER_KW = re.compile(
    r'^(?:'
    r'REFERENCES?|BIBLIOGRAPHY|REFERÊNCIAS?|REFERENCIAS?'
    r'|ACKNOWLEDGMENTS?|ACKNOWLEDGEMENTS?|AGRADECIMENTOS?'
    r'|APPENDIX|APPENDICES|APÊNDICE[S]?|APENDICE[S]?'
    r'|BIOGRAPHIES?|AUTHORS?(?: BIOGRAPHIES?)?|ABOUT THE AUTHORS?'
    r'|AUTHOR BIOGRAPHIES?|BIOS?'
    r'|FUNDING|DECLARATIONS?|CONFLICTS? OF INTEREST|COMPETING INTERESTS?'
    r'|DATA AVAILABILITY|SUPPLEMENTARY MATERIAL[S]?|SUPPLEMENTAL MATERIAL[S]?'
    r'|NOTES?|ENDNOTES?|FOOTNOTES?'
    r')$',
    re.IGNORECASE,
)


# Seções claramente não-conclusivas — excluir do fallback de conclusão
_SKIP_FALLBACK_CONCLUSION = re.compile(
    r'^(?:'
    r'RELATED WORK(?:S)?(?:\s+AND\s+[A-Z ]+)?|'
    r'BACKGROUND|PRELIMINARIES|MOTIVATION(?:\s+AND\s+[A-Z ]+)?|'
    r'EVALUATION|EXPERIMENTS?|EXPERIMENTAL(?:\s+RESULTS?)?|'
    r'IMPLEMENTATION[S]?|PERFORMANCE(?:\s+EVALUATION)?|'
    r'NUMERICAL RESULTS?|SIMULATION[S]?|'
    r'SYSTEM (?:OVERVIEW|DESIGN|ARCHITECTURE|MODEL)|'
    r'THREAT MODEL|SECURITY (?:MODEL|ANALYSIS)|'
    r'PROBLEM (?:FORMULATION|DESCRIPTION|STATEMENT|OVERVIEW|MODEL)|'
    r'APPROACH(?:ES)?|ALGORITHM[S]?|DESIGN|ARCHITECTURE|METHODOLOGY|'
    r'PROTOCOL[S]?|SCHEME[S]?|FRAMEWORK[S]?|'
    r'PROPOSED (?:SCHEME|PROTOCOL|SYSTEM|APPROACH|METHOD)'
    r')$',
    re.IGNORECASE,
)


# Palavras "pequenas" que não precisam estar capitalizadas em um título Title-Case
_TITLE_STOPWORDS = {
    'a', 'an', 'and', 'or', 'of', 'the', 'for', 'to', 'in', 'on', 'with', 'via',
    'from', 'at', 'by', 'as', 'vs', 'using', 'based', 'over', 'under', 'into',
    'among', 'between', 'toward', 'towards', 'no', 'its', 'it', 'is', 'are',
}


def _is_heading_title(title: str) -> bool:
    """
    Verifica se a string é um *cabeçalho de seção* — aceita DOIS estilos comuns
    em papers IEEE/ACM:

      (A) CAIXA ALTA:   'INTRODUCTION', 'RELATED WORK'      (≥80 % maiúsculas)
      (B) Title Case:   'Introduction', 'Related Work'      (palavras de conteúdo
                        capitalizadas, ignorando stopwords)

    Rejeita frases de corpo (ex.: '1) we propose a new method that …') porque
    nelas as palavras de conteúdo começam em minúscula.
    """
    title = title.strip()
    letters = [c for c in title if c.isalpha()]
    if len(letters) < 2:
        return False

    words = re.findall(r"[A-Za-z][A-Za-z'\-]*", title)
    if not words or len(words) > 10:        # cabeçalhos são curtos (≤10 palavras)
        return False

    # Regra A — predominantemente em CAIXA ALTA
    upper_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
    if upper_ratio >= 0.80:
        return True

    # Regra B — Title Case: ≥80 % das palavras de conteúdo iniciam em maiúscula
    content = [w for w in words if w.lower() not in _TITLE_STOPWORDS]
    if not content:
        return False
    cap_ratio = sum(1 for w in content if w[0].isupper()) / len(content)
    return cap_ratio >= 0.80


def _roman_to_int(s: str) -> int:
    vals = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    total, prev = 0, 0
    for ch in reversed(s.upper()):
        v = vals.get(ch, 0)
        total += -v if v < prev else v
        prev = max(prev, v)
    return total


def find_sections(text: str) -> List[Tuple[int, str, str]]:
    """
    Detecta todos os cabeçalhos de seção de alto nível no texto.
    Retorna lista de (pos_início_linha, numeral, título_em_maiúsculas).
    Posições são inícios exatos de linha — sem deslocamento de \\n.

    Estratégia (v3):
      1. Coleta candidatos: linha que começa com numeral romano/árabe + '.'/'(' +
         título que passa em `_is_heading_title` (aceita CAIXA ALTA e Title Case).
      2. Escolhe UM esquema de numeração dominante (romano OU árabe) — o que tiver
         mais cabeçalhos; desempate pelo que contém a seção de valor 1. Isso
         elimina falsos positivos (marcadores de lista '1)', números de equação).
    """
    candidates: List[Tuple[int, str, str, int, bool]] = []
    for m in _SECTION_HDR_RAW.finditer(text):
        raw_title = m.group('title').strip().rstrip('.')
        if len(raw_title) < 3:
            continue
        if not _is_heading_title(raw_title):
            continue
        numeral = m.group('num').upper()
        is_roman = bool(re.fullmatch(r'[IVXLCDM]+', numeral))
        value = _roman_to_int(numeral) if is_roman else int(numeral)
        candidates.append((m.start(), numeral, raw_title.upper(), value, is_roman))

    if not candidates:
        return []

    roman = [c for c in candidates if c[4]]
    arabic = [c for c in candidates if not c[4]]

    def spine(group):
        """
        Maior subsequência ESTRITAMENTE CRESCENTE (por valor) em ordem de
        posição no documento — tolera lacunas.

        Por quê: as seções de TOPO crescem monotonicamente (I, II, III, …) mesmo
        que uma ou outra não seja detectada (ex.: 'II' perdida por formatação →
        I, III, IV, V, VI ainda é crescente). Já as enumerações de SUBSEÇÃO
        REINICIAM (1,2,3 … 1,2,3 …), então sua maior cadeia crescente é curta.
        A LIS isola o verdadeiro espinhaço de seções e ignora subseções
        intercaladas e falsos positivos.
        """
        group = sorted(group, key=lambda c: c[0])
        n = len(group)
        if n == 0:
            return []
        # LIS (O(n²) — n é pequeno) com reconstrução
        length = [1] * n
        prev = [-1] * n
        for i in range(n):
            for j in range(i):
                if group[j][3] < group[i][3] and length[j] + 1 > length[i]:
                    length[i] = length[j] + 1
                    prev[i] = j
        end = max(range(n), key=lambda i: length[i])
        chain = []
        while end != -1:
            chain.append(group[end])
            end = prev[end]
        return list(reversed(chain))

    roman_spine = spine(roman)
    arabic_spine = spine(arabic)
    chosen = roman_spine if len(roman_spine) >= len(arabic_spine) else arabic_spine

    # Fallback: se nenhuma cadeia sequencial limpa (≥2), usar todos os candidatos
    # do esquema mais numeroso (papers com numeração irregular).
    if len(chosen) < 2:
        pool = roman if len(roman) >= len(arabic) else arabic
        chosen = sorted(pool, key=lambda c: c[0])

    chosen = sorted(chosen, key=lambda c: c[0])
    return [(pos, num, title) for pos, num, title, _, _ in chosen]


def find_refs_boundary(text: str) -> Optional[int]:
    """
    Retorna posição da seção REFERENCES/BIBLIOGRAPHY, ou None.
    Detecta tanto o cabeçalho explícito quanto o início de bloco de citações [1].
    """
    m = _REFS_HDR.search(text)
    pos_header = m.start() if m else None

    # Fallback: detectar início do bloco de citações numeradas "[1] Autor..."
    # (papers que omitem o cabeçalho "REFERENCES")
    m2 = re.search(r'\n[ \t]*\[1\]\s+[A-Z][a-z]', text)
    pos_citations = m2.start() if m2 else None

    candidates = [p for p in [pos_header, pos_citations] if p is not None]
    return min(candidates) if candidates else None


def classify_section(title: str) -> str:
    """
    Classifica um título de seção.
    Retorna: 'intro' | 'conclusion' | 'backmatter' | 'body'
    """
    t = title.strip().upper()
    if _BACK_MATTER_KW.match(t):
        return 'backmatter'
    if _INTRO_KW.match(t):
        return 'intro'
    if _CONCLUSION_KW.match(t):
        return 'conclusion'
    return 'body'


# ═══════════════════════════════════════════════════════════════════════════════
# REMOÇÃO DE FOOTERS / BOILERPLATE
# ═══════════════════════════════════════════════════════════════════════════════

_FOOTER_PATTERNS: List[re.Pattern] = [
    # ── Blocos de controle de acesso IEEE Xplore ──────────────────────────────
    re.compile(
        r'Authorized licensed use limited to:.*?(?=\n\n|\Z)',
        re.DOTALL | re.IGNORECASE,
    ),
    re.compile(
        r'Downloaded (?:from|on)\s+[^\n]{0,120}',
        re.IGNORECASE,
    ),
    # ── Linhas de Copyright / ISBN ────────────────────────────────────────────
    re.compile(
        r'\d{3}[-\u2013]\d[-\u2013]\d{4}[-\u2013]\d{4}[-\u2013]'
        r'\d[\d]?/\d{2}/\$[\d.]+[^\n]*',
        re.IGNORECASE,
    ),
    re.compile(r'[©\u00A9Cc]\s*\d{4}\s+IEEE\b[^\n]*', re.IGNORECASE),
    re.compile(r'[©\u00A9]\s*Copyright\s+\d{4}[^\n]*', re.IGNORECASE),
    re.compile(r'Copyright\s+[©\u00A9]?\s*\d{4}[^\n]*', re.IGNORECASE),
    # ── Creative Commons / Acesso Aberto ─────────────────────────────────────
    re.compile(
        r'This (?:work|article|paper) is licensed under\s+a?\s*Creative Commons[^\n]*',
        re.IGNORECASE,
    ),
    re.compile(r'CC\s*[-–]?\s*BY(?:-[A-Z]{2})?\s+[\d.]+[^\n]*', re.IGNORECASE),
    re.compile(r'Creative Commons Attribution[^\n]*', re.IGNORECASE),
    re.compile(r'Open Access[^\n]*', re.IGNORECASE),
    # ── Avisos "Aceito para publicação" / manuscrito ──────────────────────────
    re.compile(
        r'This (?:article|paper|manuscript|work) has been accepted for '
        r'(?:inclusion|publication)[^\n]*',
        re.IGNORECASE,
    ),
    re.compile(
        r'Manuscript received[^\n]*',
        re.IGNORECASE,
    ),
    re.compile(r'Date of (?:publication|current version|receipt)[^\n]*', re.IGNORECASE),
    re.compile(r'IEEE Xplore[^\n]*', re.IGNORECASE),
    re.compile(r'(?:Personal|Personal use of this material)[^\n]*permitted[^\n]*', re.IGNORECASE),
    # ── DOI ──────────────────────────────────────────────────────────────────
    re.compile(r'Digital Object Identifier[^\n]*', re.IGNORECASE),
    re.compile(r'DOI:?\s*10\.\d{4,}/[^\s\n]+', re.IGNORECASE),   # 'DOI:' ou 'DOI '
    re.compile(r'(?<![\w/])10\.\d{4,}/[^\s\n]{4,}', re.IGNORECASE),  # DOI nu
    re.compile(r'https?://doi\.org/\S+', re.IGNORECASE),
    # ── Cabeçalhos de rodapé de conferência / journal ─────────────────────────
    re.compile(
        r'(?m)^(?:Proceedings of|IEEE Transactions on|IEEE Conference on|'
        r'IEEE (?:International )?Symposium on|Proc\. of|Journal of|'
        r'ACM Transactions on|USENIX|In Proceedings)[^\n]{0,150}$',
        re.IGNORECASE | re.MULTILINE,
    ),
    re.compile(
        r'(?m)^\d{4}\s+(?:IEEE|ACM|USENIX|IFIP)[^\n]{0,150}$',
        re.IGNORECASE | re.MULTILINE,
    ),
    re.compile(
        r'(?m)^(?:SRDS|DSN|SOSP|OSDI|NSDI|EuroSys|FAST|ATC|ICDCS|DISC|'
        r'PODC|OPODIS|Middleware|CLOUD|SYSTOR)\s*[^\n]{0,150}$',
        re.IGNORECASE | re.MULTILINE,
    ),
    # ── Números de página isolados ────────────────────────────────────────────
    re.compile(
        r'(?m)^[ \t]*[-\u2013\u2014]?\s*\d{1,4}\s*[-\u2013\u2014]?[ \t]*$',
        re.MULTILINE,
    ),
    # ── Códigos ISBN / ISSN ───────────────────────────────────────────────────
    re.compile(r'\b\d{3}[-\u2013]\d[-\u2013]\d{4}[-\u2013]\d{4}[-\u2013]\d/\d{2}\b[^\n]*', re.IGNORECASE),
    re.compile(r'ISSN[:\s]+\d{4}[-\u2013]\d{4}[^\n]*', re.IGNORECASE),
    re.compile(r'ISBN[:\s]+[\d\-]{10,17}[^\n]*', re.IGNORECASE),
    # ── Linhas de Autor / ORCID / e-mail ─────────────────────────────────────
    re.compile(
        r'ORCID\s*(?:iD)?[:\s]+\d{4}-\d{4}-\d{4}-\d{3}[\dXx][^\n]*',
        re.IGNORECASE,
    ),
    re.compile(r'(?:e[-\u2013]?mail|email)[:\s]+\S+@\S+[^\n]*', re.IGNORECASE),
    re.compile(
        r'(?m)^[A-Z][a-z]+(?: [A-Z][a-z]+)+,\s+(?:Member|Senior Member|Fellow),?\s+IEEE[^\n]*$',
        re.MULTILINE,
    ),
    # ── arXiv / preprint ─────────────────────────────────────────────────────
    re.compile(r'arXiv:\d{4}\.\d{4,}v?\d*[^\n]*', re.IGNORECASE),
    re.compile(r'Preprint submitted to[^\n]*', re.IGNORECASE),
    re.compile(r"Publisher[''\u2019]s Version[^\n]*", re.IGNORECASE),
    re.compile(r'(?:Technical Report|Tech\. Report|TR)[-:\s]+[^\n]{0,80}', re.IGNORECASE),
    # ── Index Terms / Keywords (às vezes antes/dentro do abstract) ───────────
    re.compile(
        r'Index Terms?[—\-:\u2014\s]+[^\n]{0,400}',
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(r'Keywords?[—\-:\u2014\s]+[^\n]{0,300}', re.IGNORECASE),
    re.compile(r'Key ?[Ww]ords?[—\-:\u2014\s]+[^\n]{0,300}', re.IGNORECASE),
    # ── Prefixo Abstract (pode vazar para o intro) ────────────────────────────
    re.compile(r'(?m)^[ \t]*Abstract[—\-:\u2014\s]+', re.IGNORECASE | re.MULTILINE),
    # ── Cabeçalhos de página após form-feed ──────────────────────────────────
    # (pdftotext insere \x0c; já convertido para \n\n no pré-processamento,
    # mas o nome da conferência pode ficar como linha isolada)
    re.compile(
        r'(?m)^[ \t]*\d{4}(?:st|nd|rd|th)?\s+(?:IEEE|ACM|USENIX|IFIP|Annual)[^\n]{0,200}$',
        re.MULTILINE | re.IGNORECASE,
    ),
    # ── Linhas com apenas pontuação / símbolos ────────────────────────────────
    re.compile(r'(?m)^[ \t]*[^\w\s]{3,}[ \t]*$', re.MULTILINE),
]


def strip_footers(text: str) -> str:
    """Remove boilerplate IEEE/licenciamento do texto (múltiplas passagens regex)."""
    for pat in _FOOTER_PATTERNS:
        text = pat.sub(' ', text)
    # Colapsar espaços/linhas em branco criados pelas remoções
    text = re.sub(r'[ \t]{2,}', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text


# ═══════════════════════════════════════════════════════════════════════════════
# NORMALIZAÇÃO DE QUEBRAS DE LINHA  (aplicada por seção após extração)
# ═══════════════════════════════════════════════════════════════════════════════

def normalize_linebreaks(text: str) -> str:
    """
    Normaliza quebras de linha dentro de uma seção já extraída:
      1. Finais Windows/Mac → Unix
      2. Quebras de linha hifenizadas rejoined (artefato de coluna PDF)
      3. \\n simples → espaço (quebra de linha intraparágrafo)
      4. 2+ \\n → \\n\\n (limite de parágrafo preservado)
      5. Múltiplos espaços colapsados
      6. Cada parágrafo aparado
    """
    # Normalizar finais de linha
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Rejuntar quebras de linha hifenizadas: "distrib-\nuted" → "distributed"
    text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)

    # Proteger quebras de parágrafo
    text = re.sub(r'\n{2,}', '\x00PARA\x00', text)

    # \\n simples → espaço (quebra de coluna PDF)
    text = text.replace('\n', ' ')

    # Restaurar parágrafos
    text = text.replace('\x00PARA\x00', '\n\n')

    # Colapsar múltiplos espaços
    text = re.sub(r' {2,}', ' ', text)

    # Limpar espaços ao redor dos limites de parágrafo
    text = re.sub(r'[ \t]*\n\n[ \t]*', '\n\n', text)

    # Aparar cada parágrafo, remover vazios e linhas órfãs muito curtas
    paragraphs = [p.strip() for p in text.split('\n\n')]
    paragraphs = [p for p in paragraphs if len(p) >= 4]

    return '\n\n'.join(paragraphs).strip()


# ═══════════════════════════════════════════════════════════════════════════════
# EXTRAÇÃO DE TEXTO DO PDF
# ═══════════════════════════════════════════════════════════════════════════════

def _run_pdftotext(pdf_path: str, *flags: str) -> str:
    """Executa pdftotext com flags dadas. Retorna stdout ou '' em caso de erro."""
    try:
        result = subprocess.run(
            ['pdftotext', *flags, pdf_path, '-'],
            capture_output=True, text=True, timeout=60,
        )
        return result.stdout
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return ''


def _preprocess(text: str) -> str:
    """
    Pré-processamento antes da detecção de seções:
    - Form-feeds (\\x0c, marcadores de página do pdftotext) → quebra dupla,
      PRESERVANDO o conteúdo que vier na sequência.

    ⚠️  Correção: a versão anterior fazia `\\x0c[^\\n]{0,200}\\n?` → '\\n\\n',
    apagando TODO o resto da linha após o form-feed. Quando um cabeçalho de
    seção real ficava colado ao quebra-página (ex.: '\\x0cI. Introduction'),
    o cabeçalho era destruído e a Introdução não era detectada. Agora apenas
    inserimos a quebra de parágrafo e mantemos o texto seguinte — cabeçalhos
    de página genuínos (nome da conferência, número de página) são removidos
    depois por `strip_footers`.
    """
    # Form-feed → quebra de parágrafo, sem comer a linha seguinte.
    # Se houver espaços logo após o \x0c (antes de texto), normaliza para \n\n.
    text = re.sub(r'\x0c[ \t]*', '\n\n', text)
    return text


def load_pdf_text(pdf_path: str) -> str:
    """
    Extrai texto bruto usando o melhor método disponível:
      1. pdftotext -raw     — evita interleaving de duas colunas; melhor para IEEE
      2. pdftotext          — layout padrão; fallback
      3. pypdf              — Python puro; último recurso
    Retorna string vazia para PDFs digitalizados/baseados em imagem.
    """
    MIN_CHARS = 200

    text = _preprocess(_run_pdftotext(pdf_path, '-raw'))
    if len(text.strip()) >= MIN_CHARS:
        return text

    text = _preprocess(_run_pdftotext(pdf_path))
    if len(text.strip()) >= MIN_CHARS:
        return text

    if HAS_PYPDF:
        try:
            reader = pypdf.PdfReader(pdf_path)
            pages = []
            for page in reader.pages:
                try:
                    pages.append(page.extract_text() or '')
                except Exception:
                    pages.append('')
            text = _preprocess('\n'.join(pages))
            if len(text.strip()) >= MIN_CHARS:
                return text
        except Exception:
            pass

    return ''


# ═══════════════════════════════════════════════════════════════════════════════
# FATIAMENTO DE SEÇÕES — usa índice na lista (não posição bruta)
# ═══════════════════════════════════════════════════════════════════════════════

def _strip_trailing_bibliography(text: str) -> str:
    """
    Remove APENAS uma lista de referências bibliográficas genuína que tenha
    vazado para o final de uma seção — NUNCA trunca em citações inline.

    ┌─ Diferença crítica vs. versão antiga ────────────────────────────────────┐
    │ A versão antiga cortava no primeiro par de marcadores '[1] … [2]'        │
    │ próximos — o que ocorre em QUALQUER introdução com citações inline,      │
    │ truncando o texto para uma única frase. Esta versão exige um *bloco de   │
    │ lista de referências de verdade*: ≥3 entradas consecutivas, cada uma     │
    │ iniciando uma linha com '[N]' seguida de texto tipo-autor.               │
    └──────────────────────────────────────────────────────────────────────────┘
    """
    if not text:
        return text

    # Cabeçalho explícito REFERENCES/BIBLIOGRAPHY/ACKNOWLEDGMENTS dentro da seção
    # → corta ali (back-matter sempre vem DEPOIS do conteúdo da conclusão).
    mh = re.search(
        r'(?im)^[ \t]*(?:[IVXLCDM]{1,6}|\d{1,2})?[\.\)]?\s*'
        r'(?:REFERENCES?|BIBLIOGRAPHY|REFER[EÊ]NCIAS?'
        r'|ACKNOWLEDG?MENTS?|ACKNOWLEDGEMENTS?|AGRADECIMENTOS?)[ \t]*$',
        text,
    )
    if mh:
        text = text[:mh.start()]

    # Acknowledgments inline ('Acknowledgment. This work was supported …') —
    # comum em papers ACM/IEEE sem cabeçalho numerado. Sempre no FINAL.
    ma = re.search(
        r'(?:^|\n|\.\s)\s*(?:Acknowledg?ments?|Acknowledgements?|Agradecimentos?)'
        r'[\.\:\—\-\s]',
        text,
    )
    if ma and ma.start() > len(text) * 0.4:   # só se estiver na metade final
        text = text[:ma.start()]

    # Bloco de lista de referências: ≥3 linhas consecutivas '[N] Autor...'
    # (cada entrada inicia a própria linha — característica de lista, não de
    #  citação inline, que aparece no MEIO de uma frase).
    entry = re.compile(r'(?m)^[ \t]*\[\d{1,3}\]\s+\S')
    starts = [m.start() for m in entry.finditer(text)]
    if len(starts) >= 3:
        # Verifica consecutividade: as 3+ primeiras entradas estão próximas
        # umas das outras (lista densa), não espalhadas pelo corpo.
        block_start = starts[0]
        consecutive = 1
        for a, b in zip(starts, starts[1:]):
            if b - a < 600:                      # entradas de ref são curtas/próximas
                consecutive += 1
                if consecutive >= 3:
                    text = text[:block_start]
                    break
            else:
                block_start = b
                consecutive = 1

    return text.strip()


def _slice_section(
    text: str,
    sections: List[Tuple[int, str, str]],
    idx: int,
    refs_pos: Optional[int],
    max_chars: int,
    strip_bib: bool = False,
) -> str:
    """
    Extrai o corpo de sections[idx] do texto.
    Limite final = início de sections[idx+1], ou refs_pos, ou EOF.
    Garante consistência: limites sempre vêm da mesma lista → sem desalinhamento.

    `strip_bib`: só ative para a ÚLTIMA seção (conclusão), que pode encostar na
    lista de referências. Para a introdução fica SEMPRE desligado — o limite já
    é a próxima seção, muito antes das referências, então qualquer remoção de
    bibliografia ali só poderia truncar texto válido com citações inline.
    """
    start = sections[idx][0]

    # Determinar limite final
    candidates: List[int] = []
    if idx + 1 < len(sections):
        nxt = sections[idx + 1][0]
        if nxt > start:
            candidates.append(nxt)
    if refs_pos is not None and refs_pos > start:
        candidates.append(refs_pos)

    end = min(candidates) if candidates else None
    body = (text[start:end] if end else text[start:])[:max_chars]

    # Remover linha do cabeçalho (tudo até e incluindo o primeiro \\n)
    nl = body.find('\n')
    body = body[nl + 1:].strip() if nl >= 0 else ''

    # Duas passagens de remoção de footer (cabeçalhos de página embutidos na seção)
    body = strip_footers(body)

    # Remoção CONSERVADORA de lista de referências — só na seção final (conclusão),
    # e somente sobre o texto bruto (linhas '[N] Autor'). Nunca na introdução.
    if strip_bib:
        body = _strip_trailing_bibliography(body)

    # Normalizar quebras de linha
    body = normalize_linebreaks(body)

    return body


# ═══════════════════════════════════════════════════════════════════════════════
# FALLBACK DE TEXTO LIVRE  (quando nenhum cabeçalho numerado é encontrado)
# ═══════════════════════════════════════════════════════════════════════════════

# Padrões de fallback: título em linha própria, sem exigir numeral
_FREE_INTRO = re.compile(
    r'(?m)^[ \t]*(?:[IVX]{1,6}[\.\)]\s+)?'
    r'(?:INTRODUCTION|INTRODUÇÃO|OVERVIEW|MOTIVATION|BACKGROUND|INTRODUÇÃO)'
    r'(?:\s+(?:AND|&|OF|TO|E)\s+[\w][\w\s&/,-]{0,50})?[ \t]*$',
    re.IGNORECASE,
)

_FREE_CONCLUSION = re.compile(
    r'(?m)^[ \t]*(?:[IVX]{1,6}[\.\)]\s+)?'
    r'(?:CONCLUSION[S]?|CONCLUDING REMARKS?|FINAL REMARKS?|SUMMARY|DISCUSSION|'
    r'CONSIDERAÇÕES FINAIS?|CONCLUSÕES?)'
    r'(?:\s+(?:AND|&|OF|E)\s+[\w][\w\s&/,-]{0,50})?[ \t]*$',
    re.IGNORECASE,
)

_FREE_HEADING = re.compile(
    r'(?m)^[ \t]*(?:[IVX\d]{1,6}[\.\)]\s*)?[A-Z][A-Z ]{2,60}[ \t]*$',
    re.MULTILINE,
)


def _text_fallback(text: str, refs_pos: Optional[int], max_chars: int):
    """
    Fallback quando nenhum cabeçalho de seção numerado é detectado.
    Busca por palavras-chave como título em linha isolada.
    """
    limit = refs_pos if refs_pos else len(text)

    def extract_from_match(m: re.Match) -> Optional[str]:
        body_start = m.end()
        rest = text[body_start:limit]
        # Próximo cabeçalho similar
        nh = _FREE_HEADING.search(rest)
        end = body_start + nh.start() if nh else limit
        body = text[body_start:end][:max_chars].strip()
        body = strip_footers(body)
        body = normalize_linebreaks(body)
        return body if len(body) >= 100 else None

    # Introdução: primeiro match
    intro = None
    m = _FREE_INTRO.search(text[:limit])
    if m:
        intro = extract_from_match(m)

    # Conclusão: ÚLTIMO match
    conclusion = None
    matches = list(_FREE_CONCLUSION.finditer(text[:limit]))
    if matches:
        conclusion = extract_from_match(matches[-1])

    # Fallback final: abstract como introdução para artigos sem seção INTRODUCTION
    # (ex: papers de workshop com formato não-padrão IEEE)
    if not intro:
        # Procura bloco de texto substancial antes da primeira subseção (A., B.)
        first_subsec = re.search(r'(?m)^[A-Z][\.)\s]+\w', text)
        first_sec_re = re.search(r'(?m)^[IVX]{1,5}[\.)\s]+\w', text)
        cutoff = min(
            first_subsec.start() if first_subsec else len(text),
            first_sec_re.start() if first_sec_re else len(text),
            limit,
        )
        preamble = text[:cutoff].strip()
        # Remover linhas muito curtas (título, autores, afiliações)
        lines = [l.strip() for l in preamble.split('\n') if len(l.strip()) > 40]
        preamble_body = ' '.join(lines)
        preamble_body = normalize_linebreaks(preamble_body)
        if len(preamble_body) >= 200:
            intro = preamble_body[:max_chars]

    return intro, conclusion


# ═══════════════════════════════════════════════════════════════════════════════
# LÓGICA DE EXTRAÇÃO PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════

def extract_intro_conclusion(raw_text: str, max_chars: int = 15000):
    """
    Extrai (introdução, conclusão) do texto bruto do PDF.

    Pipeline:
      1. Strip de footers no documento completo (mantém \\n para detecção de seções)
      2. Detecção unificada de seções (um regex → posições exatas de linha)
      3. Limite de referências detectado separadamente
      4. Introdução: primeira seção classificada como 'intro'
         Fallback: primeira seção 'body' não vazia (≥100 chars)
      5. Conclusão: ÚLTIMA seção classificada como 'conclusion'
         Fallback: última seção 'body' substancial (≥200 chars) antes das refs
      6. Se nenhuma seção numerada encontrada: fallback de texto livre

    Retorna (intro: str | None, conclusion: str | None).
    """
    if not raw_text or len(raw_text.strip()) < 100:
        return None, None

    # ── 1. Strip de footer no documento completo ──────────────────────────────
    text = strip_footers(raw_text)

    # ── 2. Detecção unificada de seções ───────────────────────────────────────
    sections = find_sections(text)          # [(pos, numeral, título)]
    refs_pos = find_refs_boundary(text)

    # Seções válidas = antes do limite de referências
    def before_refs(pos: int) -> bool:
        return refs_pos is None or pos < refs_pos

    valid = [
        (i, pos, num, title)
        for i, (pos, num, title) in enumerate(sections)
        if before_refs(pos) and classify_section(title) != 'backmatter'
    ]

    # ── 3. Introdução: primeira seção 'intro' ─────────────────────────────────
    intro: Optional[str] = None
    for i, pos, num, title in valid:
        if classify_section(title) == 'intro':
            candidate = _slice_section(text, sections, i, refs_pos, max_chars)
            if len(candidate.strip()) >= 50:
                intro = candidate
                break

    if not intro:
        # Fallback: primeira seção 'body' com conteúdo suficiente
        for i, pos, num, title in valid:
            if classify_section(title) == 'body':
                candidate = _slice_section(text, sections, i, refs_pos, max_chars)
                if len(candidate.strip()) >= 100:
                    intro = candidate
                    break

    # ── 4. Conclusão: ÚLTIMA seção 'conclusion' ───────────────────────────────
    conclusion: Optional[str] = None
    for i, pos, num, title in reversed(valid):
        if classify_section(title) == 'conclusion':
            candidate = _slice_section(text, sections, i, refs_pos, max_chars, strip_bib=True)
            if len(candidate.strip()) >= 50:
                conclusion = candidate
                break

    if not conclusion:
        # Fallback: última seção 'body' substancial antes das refs
        # que NÃO seja seção claramente técnica/não-conclusiva
        for i, pos, num, title in reversed(valid):
            if classify_section(title) == 'body' and not _SKIP_FALLBACK_CONCLUSION.match(title):
                candidate = _slice_section(text, sections, i, refs_pos, max_chars, strip_bib=True)
                stripped = candidate.strip()
                # Rejeitar se começa com cabeçalho de subseção (A. B. C.) — conteúdo errado
                if len(stripped) >= 200 and not re.match(r'^[A-Z]\.\s+[A-Z]', stripped):
                    conclusion = candidate
                    break

    # ── 5. Fallback de texto livre quando nenhuma seção numerada encontrada ───
    if not intro or not conclusion:
        fb_intro, fb_conclusion = _text_fallback(text, refs_pos, max_chars)
        if not intro and fb_intro:
            intro = fb_intro
        if not conclusion and fb_conclusion:
            conclusion = fb_conclusion

    return intro or None, conclusion or None


# ═══════════════════════════════════════════════════════════════════════════════
# CORRESPONDÊNCIA FUZZY: Título → nome do arquivo PDF
# ═══════════════════════════════════════════════════════════════════════════════

def _slugify(text: str) -> str:
    """Normaliza texto para comparação fuzzy: remove acentos, lowercase, espaços."""
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = re.sub(r'[^a-z0-9\s]', ' ', text.lower())
    return re.sub(r'\s+', ' ', text).strip()


def match_title_to_pdf(title: str, pdf_names: List[str], threshold: int = 70) -> Optional[str]:
    """Corresponde um título de artigo ao nome de arquivo PDF mais próximo."""
    if not pdf_names:
        return None
    slug_title = _slugify(title)
    slug_map = {n: _slugify(Path(n).stem) for n in pdf_names}

    if fuzz_process:
        choices = list(slug_map.values())
        result = fuzz_process.extractOne(
            slug_title, choices, scorer=fuzz.token_sort_ratio
        )
        if result and result[1] >= threshold:
            matched_slug = result[0]
            for orig, slug in slug_map.items():
                if slug == matched_slug:
                    return orig
        return None
    else:
        # Fallback sem biblioteca fuzzy: correspondência por proporção de palavras
        words = slug_title.split()
        if not words:
            return None
        best_name: Optional[str] = None
        best_ratio = 0.0
        for orig, slug in slug_map.items():
            ratio = sum(1 for w in words if w in slug) / len(words)
            if ratio > best_ratio:
                best_ratio = ratio
                best_name = orig
        return best_name if best_ratio >= 0.6 else None


# ═══════════════════════════════════════════════════════════════════════════════
# EXTRAÇÃO DE PDFs DO ZIP
# ═══════════════════════════════════════════════════════════════════════════════

def extract_zip_pdfs(zip_path: str, dest_dir: str) -> List[str]:
    """Extrai todos os PDFs do arquivo ZIP para dest_dir (achata subpastas)."""
    extracted: List[str] = []
    with zipfile.ZipFile(zip_path, 'r') as zf:
        for member in zf.infolist():
            if member.filename.lower().endswith('.pdf'):
                flat_name = Path(member.filename).name
                dest_path = os.path.join(dest_dir, flat_name)
                with zf.open(member) as src, open(dest_path, 'wb') as dst:
                    dst.write(src.read())
                extracted.append(dest_path)
    return extracted


# ═══════════════════════════════════════════════════════════════════════════════
# WORKER (pool de subprocessos)
# ═══════════════════════════════════════════════════════════════════════════════

def _process_one(args: tuple):
    """Processa um único PDF. Retorna (título, intro, conclusão, erro)."""
    title, pdf_path, max_chars = args
    try:
        raw_text = load_pdf_text(pdf_path)
        intro, conclusion = extract_intro_conclusion(raw_text, max_chars=max_chars)
        return title, intro or '', conclusion or '', None
    except Exception as exc:
        return title, '', '', str(exc)


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='Extrai Introdução & Conclusão de PDFs IEEE e enriquece um CSV.'
    )
    parser.add_argument('--csv', required=True, help='Caminho para o CSV de entrada')
    parser.add_argument('--zip', required=True, help='Caminho para o ZIP com PDFs')
    parser.add_argument('--title-col', required=True, help='Nome da coluna de títulos no CSV')
    parser.add_argument('--out', required=True, help='Caminho para o CSV de saída enriquecido')
    parser.add_argument('--threshold', type=int, default=70,
                        help='Limiar de similaridade fuzzy para correspondência de título (padrão: 70)')
    parser.add_argument('--workers', type=int, default=4,
                        help='Número de workers paralelos (padrão: 4)')
    parser.add_argument('--max-chars', type=int, default=15000,
                        help='Máximo de caracteres por seção (padrão: 15000)')
    args = parser.parse_args()

    # Auto-instalar rapidfuzz se necessário
    if FUZZY_LIB is None:
        print('[setup] Instalando rapidfuzz …')
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', 'rapidfuzz',
             '--break-system-packages', '-q'],
            check=True,
        )
        print('[setup] Por favor, execute o script novamente (rapidfuzz instalado).')
        sys.exit(0)

    print(f'[info] Biblioteca fuzzy: {FUZZY_LIB}')

    # ── Ler CSV ───────────────────────────────────────────────────────────────
    with open(args.csv, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])

    if args.title_col not in fieldnames:
        sys.exit(
            f"[error] Coluna '{args.title_col}' não encontrada. "
            f"Disponíveis: {fieldnames}"
        )

    # ── Extrair e processar PDFs ───────────────────────────────────────────────
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f'[info] Extraindo PDFs de {args.zip} …')
        pdf_paths = extract_zip_pdfs(args.zip, tmpdir)
        pdf_names = [Path(p).name for p in pdf_paths]
        print(f'[info] {len(pdf_paths)} PDFs encontrados.')

        # Corresponder títulos a PDFs
        work_items: List[tuple] = []
        unmatched: List[str] = []
        for row in rows:
            title = row.get(args.title_col, '').strip()
            matched = match_title_to_pdf(title, pdf_names, threshold=args.threshold)
            if matched:
                work_items.append((title, os.path.join(tmpdir, matched), args.max_chars))
            else:
                unmatched.append(title)
                work_items.append((title, None, args.max_chars))

        matched_count = len(work_items) - len(unmatched)
        print(f'[info] Correspondidos {matched_count}/{len(rows)} artigos.')
        if unmatched:
            for t in unmatched[:10]:
                print(f'  [warn] sem correspondência: {t[:80]}')
            if len(unmatched) > 10:
                print(f'  ... e mais {len(unmatched) - 10}')

        # Processar em paralelo
        filterable = [(t, p, mc) for t, p, mc in work_items if p]
        results: dict = {}

        print(f'[info] Processando {len(filterable)} PDFs ({args.workers} workers) …')
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(_process_one, item): item[0] for item in filterable}
            for idx, future in enumerate(as_completed(futures), 1):
                title, intro, conclusion, err = future.result()
                results[title] = (intro, conclusion)

                # Diagnóstico por artigo
                has_intro = '✓' if intro else '✗'
                has_conc  = '✓' if conclusion else '✗'
                status = (
                    f'intro={has_intro} conclusão={has_conc}'
                    if not err
                    else f'ERR: {err}'
                )
                print(f'  [{idx:>3}/{len(filterable)}] {title[:55]!r}  → {status}')

        # ── Escrever CSV de saída ─────────────────────────────────────────────
        out_fieldnames = list(fieldnames)
        for col in ('Introduction', 'Conclusion'):
            if col not in out_fieldnames:
                out_fieldnames.append(col)

        with open(args.out, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=out_fieldnames, extrasaction='ignore')
            writer.writeheader()
            for row in rows:
                title = row.get(args.title_col, '').strip()
                intro, conclusion = results.get(title, ('', ''))
                row['Introduction'] = intro
                row['Conclusion'] = conclusion
                writer.writerow(row)

        # Sumário final
        total = len(rows)
        ok_intro = sum(1 for t, p, _ in work_items if p and results.get(t, ('', ''))[0])
        ok_conc  = sum(1 for t, p, _ in work_items if p and results.get(t, ('', ''))[1])
        print(f'\n[done] Salvo em: {args.out}')
        print(f'[sumário] Introdução extraída: {ok_intro}/{matched_count} | '
              f'Conclusão extraída: {ok_conc}/{matched_count}')


if __name__ == '__main__':
    main()
