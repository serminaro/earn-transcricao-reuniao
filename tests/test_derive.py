"""DoD-3: derivação de TXT e SRT a partir de um JSON fixo (R-TRANS-04).

TXT/SRT são funções puras do envelope; não tocam ASR. Determinístico, sem GPU.
"""

from __future__ import annotations

import pytest

from src import transcrever


# --- derive_txt -------------------------------------------------------------

def test_derive_txt_lines_and_labels(valid_envelope):
    txt = transcrever.derive_txt(valid_envelope)
    lines = txt.splitlines()
    assert lines == [
        "SPEAKER_00: Bom dia a todos.",
        "SPEAKER_01: Vamos começar a reunião.",
        "DESCONHECIDO: Texto sem dono.",
    ]


def test_derive_txt_prefers_speaker_when_present(valid_envelope):
    # No 01 speaker é null; se um dia preenchido, label = speaker.
    valid_envelope["segments"][0]["speaker"] = "Ana"
    txt = transcrever.derive_txt(valid_envelope)
    assert txt.splitlines()[0] == "Ana: Bom dia a todos."


# --- format_timestamp_srt ---------------------------------------------------

@pytest.mark.parametrize(
    "seconds,expected",
    [
        (0.0, "00:00:00,000"),
        (2.5, "00:00:02,500"),
        (3661.5, "01:01:01,500"),
        (59.999, "00:00:59,999"),
    ],
)
def test_format_timestamp_srt(seconds, expected):
    assert transcrever.format_timestamp_srt(seconds) == expected


# --- derive_srt -------------------------------------------------------------

def test_derive_srt_blocks(valid_envelope):
    srt = transcrever.derive_srt(valid_envelope)
    assert "1\n00:00:00,000 --> 00:00:02,500\nSPEAKER_00: Bom dia a todos." in srt
    assert "2\n00:00:02,500 --> 00:00:05,000\nSPEAKER_01: Vamos começar a reunião." in srt
    assert "3\n00:00:05,000 --> 00:00:06,000\nDESCONHECIDO: Texto sem dono." in srt


def test_derive_srt_indices_are_1_based_and_sequential(valid_envelope):
    srt = transcrever.derive_srt(valid_envelope)
    # Há exatamente 3 segmentos → índices 1, 2, 3 presentes como blocos.
    blocks = [b for b in srt.strip().split("\n\n") if b.strip()]
    assert len(blocks) == 3
    assert blocks[0].splitlines()[0] == "1"
    assert blocks[2].splitlines()[0] == "3"
