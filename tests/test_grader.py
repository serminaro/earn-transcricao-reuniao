"""Testes determinísticos do grader (SPEC-005 §4): normalize, wer, ter.

Todos os valores esperados são calculados à mão a partir de pares ref/hyp
sintéticos. Sem GPU, sem jiwer — apenas Python puro.
"""

from __future__ import annotations

import pytest

from eval.grader import normalize, wer, ter


# --------------------------------------------------------------------------- #
# normalize (SPEC-005 §4.4)                                                    #
# --------------------------------------------------------------------------- #
class TestNormalize:
    def test_minusculas_e_pontuacao(self):
        assert normalize("Olá, Mundo!") == ["olá", "mundo"]

    def test_preserva_acentuacao(self):
        # acento é distintivo em PT-BR: NÃO pode ser removido
        assert normalize("Ação São João é ótimo") == [
            "ação", "são", "joão", "é", "ótimo"
        ]

    def test_colapsa_espacos(self):
        assert normalize("  a   b\tc\nd  ") == ["a", "b", "c", "d"]

    def test_string_vazia(self):
        assert normalize("") == []
        assert normalize("   ") == []

    def test_none_retorna_lista_vazia(self):
        assert normalize(None) == []

    def test_numeral_por_extenso_simples(self):
        assert normalize("vinte e três") == ["23"]

    def test_numeral_digito_inalterado(self):
        assert normalize("23") == ["23"]

    def test_numeral_extenso_e_digito_colapsam_igual(self):
        # o ponto da normalização de numeral: ambas as formas batem
        assert normalize("vinte e três") == normalize("23")

    def test_numeral_centena_composta(self):
        assert normalize("cento e cinquenta") == ["150"]

    def test_numeral_milhar(self):
        assert normalize("dois mil") == ["2000"]
        assert normalize("mil e quinhentos") == ["1500"]

    def test_e_conjuncao_fora_de_numeral_e_preservado(self):
        # "e" só some quando liga dois numerais; aqui é conjunção comum
        assert normalize("pão e queijo") == ["pão", "e", "queijo"]

    def test_fronteira_digito_letra(self):
        assert normalize("reunião às 23h") == ["reunião", "às", "23", "h"]


# --------------------------------------------------------------------------- #
# wer (SPEC-005 §4.1)                                                          #
# --------------------------------------------------------------------------- #
class TestWer:
    def test_identico_wer_zero(self):
        r = wer("o gato preto", "o gato preto")
        assert r == {
            "wer": 0.0,
            "substitutions": 0,
            "deletions": 0,
            "insertions": 0,
            "ref_words": 3,
        }

    def test_uma_substituicao(self):
        # [o,gato,preto] vs [o,cachorro,preto] -> S=1
        r = wer("o gato preto", "o cachorro preto")
        assert r["substitutions"] == 1
        assert r["deletions"] == 0
        assert r["insertions"] == 0
        assert r["ref_words"] == 3
        assert r["wer"] == pytest.approx(1 / 3)

    def test_uma_delecao(self):
        # ref [a,casa,azul,grande] vs hyp [a,casa,grande] -> D=1
        r = wer("a casa azul grande", "a casa grande")
        assert r["deletions"] == 1
        assert r["substitutions"] == 0
        assert r["insertions"] == 0
        assert r["ref_words"] == 4
        assert r["wer"] == pytest.approx(1 / 4)

    def test_uma_insercao(self):
        # ref [bom,dia] vs hyp [bom,dia,pessoal] -> I=1
        r = wer("bom dia", "bom dia pessoal")
        assert r["insertions"] == 1
        assert r["substitutions"] == 0
        assert r["deletions"] == 0
        assert r["ref_words"] == 2
        assert r["wer"] == pytest.approx(1 / 2)

    def test_mistura_sub_e_insercao(self):
        # ref [o,rato,roeu,a,roupa] (N=5)
        # hyp [o,gato,comeu,a,roupa,do,rei]
        # rato->gato (S), roeu->comeu (S), + do,rei (I) => S=2,I=2,D=0
        r = wer("o rato roeu a roupa", "o gato comeu a roupa do rei")
        assert r["substitutions"] == 2
        assert r["insertions"] == 2
        assert r["deletions"] == 0
        assert r["ref_words"] == 5
        assert r["wer"] == pytest.approx(4 / 5)

    def test_ref_vazia_hyp_vazia(self):
        r = wer("", "")
        assert r["wer"] == 0.0
        assert r["ref_words"] == 0

    def test_ref_vazia_hyp_nao_vazia(self):
        r = wer("", "apareceu texto do nada")
        assert r["wer"] == 1.0
        assert r["ref_words"] == 0
        assert r["insertions"] == 4

    def test_numeral_nao_punido(self):
        # "23" vs "vinte e três" normalizam igual -> WER 0
        r = wer("o prazo é 23 dias", "o prazo é vinte e três dias")
        assert r["wer"] == 0.0


# --------------------------------------------------------------------------- #
# ter (SPEC-005 §4.2)                                                          #
# --------------------------------------------------------------------------- #
class TestTer:
    def test_todos_termos_corretos(self):
        r = ter("time alpha entregou", "time alpha entregou", ["alpha"])
        assert r == {
            "ter": 0.0,
            "terms_total": 1,
            "terms_wrong": 0,
            "missing": [],
        }

    def test_termos_errados(self):
        # ref: joão apresentou o roadmap do kubernetes
        # hyp: joão apresentou o road map do cubernetes
        # João ok; roadmap -> "road map" (ausente); kubernetes -> cubernetes (ausente)
        r = ter(
            "João apresentou o roadmap do Kubernetes",
            "João apresentou o road map do cubernetes",
            ["João", "Kubernetes", "roadmap"],
        )
        assert r["terms_total"] == 3
        assert r["terms_wrong"] == 2
        assert r["ter"] == pytest.approx(2 / 3)
        assert r["missing"] == ["Kubernetes", "roadmap"]

    def test_termo_ausente_na_referencia_nao_conta(self):
        # "beta" não está na referência -> não entra no total
        r = ter("alpha venceu", "alpha venceu", ["beta"])
        assert r["terms_total"] == 0
        assert r["ter"] == 0.0
        assert r["missing"] == []

    def test_termo_multipalavra_correto(self):
        r = ter(
            "reunião em São Paulo amanhã",
            "reunião em são paulo amanhã",
            ["São Paulo"],
        )
        assert r["terms_total"] == 1
        assert r["terms_wrong"] == 0
        assert r["ter"] == 0.0

    def test_termo_multipalavra_errado(self):
        r = ter(
            "reunião em São Paulo amanhã",
            "reunião em são pedro amanhã",
            ["São Paulo"],
        )
        assert r["terms_total"] == 1
        assert r["terms_wrong"] == 1
        assert r["ter"] == 1.0
        assert r["missing"] == ["São Paulo"]

    def test_contagem_por_ocorrencia(self):
        # "Ana" ocorre 2x na referência, 1x na hipótese -> 1 errado de 2
        r = ter("Ana e Ana falaram", "Ana falou", ["Ana"])
        assert r["terms_total"] == 2
        assert r["terms_wrong"] == 1
        assert r["ter"] == pytest.approx(0.5)
        assert r["missing"] == ["Ana"]

    def test_lista_vazia_de_termos(self):
        r = ter("qualquer coisa", "qualquer coisa", [])
        assert r["terms_total"] == 0
        assert r["ter"] == 0.0

    def test_termo_so_pontuacao_e_ignorado(self):
        # termo que normaliza para vazio (só pontuação) é descartado sem erro
        r = ter("qualquer coisa", "qualquer coisa", ["---", "coisa"])
        assert r["terms_total"] == 1
        assert r["ter"] == 0.0
