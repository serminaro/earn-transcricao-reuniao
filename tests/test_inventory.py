"""Testes determinísticos do contrato de inventário (SPEC-008, DoD-3).

Cobrem a validação contra `reuniao.schema.json` (R-INV-01), a derivação de
`initial_prompt` a partir de `vocabulario` (DEC-007, SPEC-008 §3) e a resolução
de áudio por nome em `data/audios/` (SPEC-008 §4/§6), sem GPU/whisperx. A leitura
de YAML é exercitada quando PyYAML está disponível (senão o teste é pulado).
"""

from __future__ import annotations

import pytest

from src import transcrever
from src.transcrever import AudioInputError, InventoryError


# ── _validate_inventory: conformidade ao schema (R-INV-01) ──────────────────

def test_valid_inventory_passes(tmp_path):
    transcrever._validate_inventory({"audio": "reuniao.m4a"}, tmp_path / "inv.yml")


def test_inventory_missing_audio_fails(tmp_path):
    with pytest.raises(InventoryError) as exc:
        transcrever._validate_inventory({"language": "pt"}, tmp_path / "inv.yml")
    assert "audio" in str(exc.value)


def test_inventory_bad_language_pattern_fails(tmp_path):
    with pytest.raises(InventoryError):
        transcrever._validate_inventory(
            {"audio": "a.m4a", "language": "portugues"}, tmp_path / "inv.yml"
        )


def test_inventory_audio_with_path_fails(tmp_path):
    # 'audio' é só o nome; barra é divergência (R-INV-02 / pattern do schema).
    with pytest.raises(InventoryError):
        transcrever._validate_inventory(
            {"audio": "data/audios/a.m4a"}, tmp_path / "inv.yml"
        )


def test_inventory_speaker_mapping_bad_key_fails(tmp_path):
    # Chaves devem casar ^SPEAKER_[0-9]+$ (additionalProperties: false no objeto).
    with pytest.raises(InventoryError):
        transcrever._validate_inventory(
            {"audio": "a.m4a", "speaker_mapping": {"Bruno": "x"}}, tmp_path / "inv.yml"
        )


def test_inventory_speaker_mapping_good_key_passes(tmp_path):
    transcrever._validate_inventory(
        {"audio": "a.m4a", "speaker_mapping": {"SPEAKER_00": "Bruno"}},
        tmp_path / "inv.yml",
    )


def test_inventory_allows_extra_fields(tmp_path):
    # additionalProperties: true — 02/03 crescem sem quebrar (SPEC-008 §7).
    transcrever._validate_inventory(
        {"audio": "a.m4a", "campo_futuro_02": 1}, tmp_path / "inv.yml"
    )


# ── _effective_initial_prompt: explícito vence, senão deriva (DEC-007) ──────

def test_explicit_prompt_wins_over_vocabulario():
    cfg = {"initial_prompt": "Reunião X", "vocabulario": ["A", "B"]}
    assert transcrever._effective_initial_prompt(cfg) == "Reunião X"


def test_prompt_derived_from_vocabulario():
    cfg = {"vocabulario": ["Gabriel Dorte", "Azul", "CCO"]}
    assert transcrever._effective_initial_prompt(cfg) == "Gabriel Dorte, Azul, CCO"


def test_no_prompt_no_vocabulario_is_none():
    assert transcrever._effective_initial_prompt({"audio": "a.m4a"}) is None


def test_blank_and_none_vocabulario_entries_dropped():
    cfg = {"vocabulario": [" ", "Azul", None, ""]}
    assert transcrever._effective_initial_prompt(cfg) == "Azul"


# ── _resolve_audio: por nome em data/audios/ (SPEC-008 §4/§6) ───────────────

def test_resolve_audio_found(tmp_path, monkeypatch):
    audio = tmp_path / "reuniao.m4a"
    audio.write_bytes(b"\x00")
    monkeypatch.setattr(transcrever, "AUDIOS_DIR", tmp_path)
    assert transcrever._resolve_audio("reuniao.m4a") == audio


def test_resolve_audio_missing_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(transcrever, "AUDIOS_DIR", tmp_path)
    with pytest.raises(AudioInputError) as exc:
        transcrever._resolve_audio("nao_existe.m4a")
    assert "nao_existe.m4a" in str(exc.value)


# ── _load_inventory: round-trip e modos de falha (requer PyYAML) ────────────

def test_load_inventory_roundtrip(tmp_path):
    yaml = pytest.importorskip("yaml")
    inv = tmp_path / "inv.yml"
    inv.write_text(
        yaml.safe_dump({"audio": "a.m4a", "language": "pt"}), encoding="utf-8"
    )
    assert transcrever._load_inventory(inv)["audio"] == "a.m4a"


def test_load_inventory_missing_file_fails(tmp_path):
    pytest.importorskip("yaml")
    with pytest.raises(InventoryError):
        transcrever._load_inventory(tmp_path / "nao_existe.yml")


def test_load_inventory_non_mapping_fails(tmp_path):
    pytest.importorskip("yaml")
    inv = tmp_path / "inv.yml"
    inv.write_text("- a\n- b\n", encoding="utf-8")
    with pytest.raises(InventoryError):
        transcrever._load_inventory(inv)


def test_load_inventory_invalid_against_schema_fails(tmp_path):
    yaml = pytest.importorskip("yaml")
    inv = tmp_path / "inv.yml"
    inv.write_text(yaml.safe_dump({"language": "pt"}), encoding="utf-8")  # sem audio
    with pytest.raises(InventoryError):
        transcrever._load_inventory(inv)
