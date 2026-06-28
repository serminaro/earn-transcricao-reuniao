"""DoD-3: montagem do envelope e conformidade contra o schema 1.0.

Cobre R-TRANS-02 e R-SCHEMA-01/05. Determinístico, sem GPU.
"""

from __future__ import annotations

import copy

import pytest

from src import transcrever
from src.transcrever import SchemaValidationError


# --- build_envelope ---------------------------------------------------------

def test_build_envelope_shape(sample_segments):
    env = transcrever.build_envelope(
        sample_segments,
        audio_source="reuniao.m4a",
        model="large-v3",
        compute_type="int8",
        language="pt",
        params={
            "condition_on_previous_text": False,
            "vad": True,
            "initial_prompt_used": True,
        },
        created_at="2026-06-27T14:30:00+00:00",
        pipeline_version="abc1234",
    )
    assert set(env.keys()) == {"schema_version", "metadata", "segments"}
    assert env["schema_version"] == transcrever.SCHEMA_VERSION == "1.0"
    assert env["metadata"]["audio_source"] == "reuniao.m4a"
    assert env["metadata"]["speakers_mapped"] is False  # INV-01-3
    assert env["segments"] == sample_segments


def test_build_envelope_default_created_at(sample_segments):
    env = transcrever.build_envelope(
        sample_segments,
        audio_source="reuniao.m4a",
        model="large-v3",
        compute_type="int8",
        language="pt",
        params={
            "condition_on_previous_text": False,
            "vad": True,
            "initial_prompt_used": False,
        },
    )
    # created_at None gera um ISO 8601 date-time válido para o schema.
    assert isinstance(env["metadata"]["created_at"], str)
    assert "T" in env["metadata"]["created_at"]


def test_build_envelope_output_is_schema_valid(sample_segments):
    env = transcrever.build_envelope(
        sample_segments,
        audio_source="reuniao.m4a",
        model="large-v3",
        compute_type="int8",
        language="pt",
        params={
            "condition_on_previous_text": False,
            "vad": True,
            "initial_prompt_used": True,
        },
        created_at="2026-06-27T14:30:00+00:00",
    )
    # Não levanta: a saída do build_envelope é conforme.
    assert transcrever.validate_envelope(env) is None


# --- load_schema / validate_envelope (caminho feliz) ------------------------

def test_load_schema_returns_dict(schema_path):
    schema = transcrever.load_schema(schema_path)
    assert isinstance(schema, dict)
    assert schema["required"] == ["schema_version", "metadata", "segments"]


def test_validate_accepts_valid_envelope(valid_envelope):
    assert transcrever.validate_envelope(valid_envelope) is None


# --- validate_envelope (rejeições; mensagem cita o caminho do campo) --------

def _missing_required_field(env):
    del env["segments"]
    return env, "segments"


def _additional_prop_root(env):
    env["extra"] = 1
    return env, "extra"


def _additional_prop_segment(env):
    env["segments"][0]["confidence"] = 0.8
    return env, "confidence"


def _additional_prop_word(env):
    env["segments"][0]["words"][0]["lang"] = "pt"
    return env, "lang"


def _wrong_type(env):
    env["segments"][0]["start"] = "zero"  # esperado number
    return env, "start"


def _end_before_start(env):
    env["segments"][0]["start"] = 5.0
    env["segments"][0]["end"] = 1.0  # end < start (INV-2 / R-SCHEMA-05)
    return env, "end"


def _score_out_of_range(env):
    env["segments"][0]["words"][0]["score"] = 1.5  # fora de [0,1]
    return env, "score"


@pytest.mark.parametrize(
    "mutate",
    [
        _missing_required_field,
        _additional_prop_root,
        _additional_prop_segment,
        _additional_prop_word,
        _wrong_type,
        _end_before_start,
        _score_out_of_range,
    ],
    ids=[
        "missing_required",
        "additional_root",
        "additional_segment",
        "additional_word",
        "wrong_type",
        "end_before_start",
        "score_out_of_range",
    ],
)
def test_validate_rejects_and_points_to_field(valid_envelope, mutate):
    broken, field = mutate(copy.deepcopy(valid_envelope))
    with pytest.raises(SchemaValidationError) as exc:
        transcrever.validate_envelope(broken)
    # A mensagem aponta o caminho do campo inválido (SPEC-006 §6, INV-01-2).
    assert field in str(exc.value)


def test_schema_validation_error_is_value_error(valid_envelope):
    broken = copy.deepcopy(valid_envelope)
    del broken["metadata"]
    with pytest.raises(ValueError):
        transcrever.validate_envelope(broken)
