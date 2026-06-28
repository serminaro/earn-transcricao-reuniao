"""Grader do eval — SPEC-005 §4.

Métricas de qualidade da transcrição em Python puro (sem ``jiwer``):

- :func:`normalize` — normalização do protocolo (SPEC-005 §4.4): minúsculas,
  remoção de pontuação, colapso de espaços e normalização de numerais
  (por extenso <-> dígitos). **Acentuação é preservada** (em PT-BR o acento é
  distintivo). Esta função é parte fixa do protocolo: mudá-la muda as métricas
  e exige nota no Histórico da SPEC-005.
- :func:`wer` — Word Error Rate por distância de edição (SPEC-005 §4.1).
- :func:`ter` — Term Error Rate sobre o vocabulário ancorado (SPEC-005 §4.2).

Nenhuma dependência externa: apenas a stdlib.
"""

from __future__ import annotations

import re
import unicodedata

__all__ = ["normalize", "wer", "ter"]


# --------------------------------------------------------------------------- #
# Numerais por extenso (PT-BR) -> valor inteiro                                #
# --------------------------------------------------------------------------- #
# A normalização leva tudo a uma forma canônica em dígitos: "vinte e três" e
# "23" colapsam ambos para "23", evitando que a métrica puna diferenças
# meramente ortográficas de numeral.

_UNIDADES = {
    "zero": 0,
    "um": 1, "uma": 1,
    "dois": 2, "duas": 2,
    "tres": 3,
    "quatro": 4,
    "cinco": 5,
    "seis": 6,
    "sete": 7,
    "oito": 8,
    "nove": 9,
    "dez": 10,
    "onze": 11,
    "doze": 12,
    "treze": 13,
    "catorze": 14, "quatorze": 14,
    "quinze": 15,
    "dezesseis": 16,
    "dezessete": 17,
    "dezoito": 18,
    "dezenove": 19,
    "vinte": 20,
    "trinta": 30,
    "quarenta": 40,
    "cinquenta": 50,
    "sessenta": 60,
    "setenta": 70,
    "oitenta": 80,
    "noventa": 90,
    "cem": 100, "cento": 100,
    "duzentos": 200, "duzentas": 200,
    "trezentos": 300, "trezentas": 300,
    "quatrocentos": 400, "quatrocentas": 400,
    "quinhentos": 500, "quinhentas": 500,
    "seiscentos": 600, "seiscentas": 600,
    "setecentos": 700, "setecentas": 700,
    "oitocentos": 800, "oitocentas": 800,
    "novecentos": 900, "novecentas": 900,
}

# Multiplicadores de escala.
_ESCALAS = {
    "mil": 1000,
    "milhao": 1_000_000, "milhoes": 1_000_000,
    "bilhao": 1_000_000_000, "bilhoes": 1_000_000_000,
}


def _strip_accents(token: str) -> str:
    """Forma SEM acento de um token, só para casar chaves dos dicionários de
    numeral (que são guardadas sem acento). NÃO altera a saída de
    :func:`normalize`, que preserva acentuação."""
    nfkd = unicodedata.normalize("NFKD", token)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def _is_number_word(token: str) -> bool:
    key = _strip_accents(token)
    return key in _UNIDADES or key in _ESCALAS


def _compose_number(values: list[int]) -> int:
    """Compõe uma sequência de valores de numeral por extenso num inteiro.

    Algoritmo aditivo-multiplicativo padrão: unidades/dezenas/centenas somam no
    segmento corrente; ``mil``/``milhão`` fecham o segmento multiplicando-o pela
    escala. Ex.: [20, 3] -> 23; [100, 50] -> 150; [2, 1000] -> 2000;
    [1, 1_000_000] -> 1_000_000.
    """
    result = 0
    current = 0
    for v in values:
        if v >= 1000:  # escala (mil, milhão, ...)
            current = current if current != 0 else 1
            result += current * v
            current = 0
        else:
            current += v
    return result + current


def _normalize_numerals(tokens: list[str]) -> list[str]:
    """Colapsa execuções de numeral por extenso em um único token de dígitos.

    Um ``e`` entre dois numerais por extenso é tratado como conector (ignorado);
    em qualquer outra posição é palavra comum e preservado.
    """
    out: list[str] = []
    run: list[int] = []  # valores do numeral em construção

    def flush() -> None:
        if run:
            out.append(str(_compose_number(run)))
            run.clear()

    i = 0
    n = len(tokens)
    while i < n:
        tok = tokens[i]
        if _is_number_word(tok):
            key = _strip_accents(tok)
            run.append(_UNIDADES.get(key, _ESCALAS.get(key, 0)))
            i += 1
            continue
        if tok == "e" and run and i + 1 < n and _is_number_word(tokens[i + 1]):
            # conector dentro de um numeral composto ("vinte e três")
            i += 1
            continue
        flush()
        out.append(tok)
        i += 1
    flush()
    return out


# --------------------------------------------------------------------------- #
# Normalização (SPEC-005 §4.4)                                                 #
# --------------------------------------------------------------------------- #
# Mantém letras (incl. acentuadas) e dígitos; tudo o mais vira separador.
# ``\w`` em modo unicode (padrão para str) já casa acentuadas, então removemos
# o que NÃO é palavra nem espaço.
_PUNCT_RE = re.compile(r"[^\w\s]", flags=re.UNICODE)
_DIGIT_LETTER_BOUNDARY = re.compile(r"(?<=\d)(?=[^\W\d_])|(?<=[^\W\d_])(?=\d)",
                                    flags=re.UNICODE)


def normalize(text: str) -> list[str]:
    """Normaliza ``text`` conforme SPEC-005 §4.4 e retorna a lista de tokens.

    Passos: minúsculas -> pontuação vira espaço -> colapso de espaços ->
    normalização de numerais (por extenso <-> dígitos). Acentuação preservada.
    """
    if text is None:
        return []
    # minúsculas (casefold cobre PT-BR sem destruir acento)
    text = text.casefold()
    # pontuação (e underscore, que \w incluiria) vira espaço
    text = _PUNCT_RE.sub(" ", text)
    text = text.replace("_", " ")
    # separa fronteiras dígito/letra coladas ("23h" -> "23 h")
    text = _DIGIT_LETTER_BOUNDARY.sub(" ", text)
    # colapso de espaços + tokenização
    tokens = text.split()
    # numerais por extenso -> dígitos (forma canônica)
    tokens = _normalize_numerals(tokens)
    return tokens


# --------------------------------------------------------------------------- #
# WER (SPEC-005 §4.1)                                                          #
# --------------------------------------------------------------------------- #
def _levenshtein_ops(ref_tokens: list[str], hyp_tokens: list[str]
                     ) -> tuple[int, int, int]:
    """Distância de edição com backtrace -> (substituições, deleções, inserções).

    Custo: match=0, substituição/deleção/inserção=1. Backtrace prefere o
    caminho de menor custo; empates resolvidos de forma determinística
    (substituição/match, depois deleção, depois inserção).
    """
    n = len(ref_tokens)
    m = len(hyp_tokens)
    # matriz de custos (n+1) x (m+1)
    d = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        d[i][0] = i
    for j in range(1, m + 1):
        d[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = 0 if ref_tokens[i - 1] == hyp_tokens[j - 1] else 1
            d[i][j] = min(
                d[i - 1][j - 1] + cost,  # substituição/match
                d[i - 1][j] + 1,         # deleção (ref tem token a mais)
                d[i][j - 1] + 1,         # inserção (hyp tem token a mais)
            )

    # backtrace
    s = dele = ins = 0
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0:
            cost = 0 if ref_tokens[i - 1] == hyp_tokens[j - 1] else 1
            if d[i][j] == d[i - 1][j - 1] + cost:
                if cost == 1:
                    s += 1
                i -= 1
                j -= 1
                continue
        if i > 0 and d[i][j] == d[i - 1][j] + 1:
            dele += 1
            i -= 1
            continue
        # resta inserção
        ins += 1
        j -= 1
    return s, dele, ins


def wer(reference: str, hypothesis: str) -> dict:
    """Word Error Rate por distância de edição sobre tokens normalizados.

    ``WER = (S + D + I) / N``, com ``N`` = nº de palavras da referência.
    Se ``N == 0``: ``wer = 0.0`` quando a hipótese também é vazia, senão ``1.0``.
    """
    ref_tokens = normalize(reference)
    hyp_tokens = normalize(hypothesis)
    n = len(ref_tokens)
    s, dele, ins = _levenshtein_ops(ref_tokens, hyp_tokens)
    if n == 0:
        wer_value = 0.0 if len(hyp_tokens) == 0 else 1.0
    else:
        wer_value = (s + dele + ins) / n
    return {
        "wer": wer_value,
        "substitutions": s,
        "deletions": dele,
        "insertions": ins,
        "ref_words": n,
    }


# --------------------------------------------------------------------------- #
# TER (SPEC-005 §4.2)                                                          #
# --------------------------------------------------------------------------- #
def _count_subseq(haystack: list[str], needle: list[str]) -> int:
    """Conta ocorrências (não sobrepostas) da sublista contígua ``needle`` em
    ``haystack``."""
    if not needle:
        return 0
    count = 0
    i = 0
    ln = len(needle)
    while i <= len(haystack) - ln:
        if haystack[i:i + ln] == needle:
            count += 1
            i += ln
        else:
            i += 1
    return count


def ter(reference: str, hypothesis: str, anchored_terms: list[str]) -> dict:
    """Term Error Rate sobre o vocabulário ancorado (SPEC-005 §4.2).

    ``TER = termos_ancorados_errados / termos_ancorados_totais``, contados por
    ocorrência na referência. Um termo conta como "errado" quando aparece menos
    vezes na hipótese do que na referência (ausente ou substituído), após
    :func:`normalize`. ``terms_total == 0`` -> ``ter = 0.0``.

    Retorna ``{"ter", "terms_total", "terms_wrong", "missing"}``; ``missing``
    lista, uma vez por ocorrência faltante, os termos ancorados não recuperados.
    """
    ref_tokens = normalize(reference)
    hyp_tokens = normalize(hypothesis)

    terms_total = 0
    terms_wrong = 0
    missing: list[str] = []

    for term in anchored_terms or []:
        term_tokens = normalize(term)
        if not term_tokens:
            continue
        ref_count = _count_subseq(ref_tokens, term_tokens)
        if ref_count == 0:
            continue  # só conta termos presentes na referência
        hyp_count = _count_subseq(hyp_tokens, term_tokens)
        terms_total += ref_count
        wrong = ref_count - hyp_count
        if wrong > 0:
            terms_wrong += wrong
            missing.extend([term] * wrong)

    ter_value = 0.0 if terms_total == 0 else terms_wrong / terms_total
    return {
        "ter": ter_value,
        "terms_total": terms_total,
        "terms_wrong": terms_wrong,
        "missing": missing,
    }
