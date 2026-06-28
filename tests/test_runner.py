"""Teste leve do FORMATO do registro de metricas do runner (SPEC-005 secao 6).

Deterministico, sem GPU. Substitui (monkeypatch) os seams de importacao
preguicosa do runner (`_transcribe`, `_derive_txt`, `_grade_wer`, `_grade_ter`),
de modo que este teste NAO depende de `src.transcrever` nem de `eval.grader`
estarem implementados. Verifica:

- a forma do registro (chaves obrigatorias da secao 6);
- o veredito vs. thresholds (verde sse wer<=WER_THRESHOLD e ter<=TER_THRESHOLD);
- DER reportado como `n/d`;
- o flag with_prompt e o config (prompt omitido quando with_prompt=False);
- a fronteira de privacidade de record_summary (sumario sem `detail`; detalhe
  em diretorio separado).
"""

import json

import pytest

from eval import runner


REQUIRED_KEYS = {
    "sample_id", "pipeline_version", "params", "with_prompt",
    "wer", "ter", "der", "verdict", "date", "detail",
}


def _make_sample(tmp_path, *, language="pt", terms=("Acme", "EBITDA")):
    sample = tmp_path / "amostra_x"
    sample.mkdir()
    (sample / "audio.wav").write_bytes(b"\x00")  # placeholder; transcribe e stub
    (sample / "ref.txt").write_text("SPEAKER_00: a Acme bateu o EBITDA\n", encoding="utf-8")
    lines = [f"language: {language}", "anchored_terms:"]
    lines += [f"  - {t}" for t in terms]
    (sample / "meta.yml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return sample


def _stub_envelope():
    return {
        "schema_version": "1.0",
        "metadata": {
            "audio_source": "audio.wav",
            "params": {
                "condition_on_previous_text": False,
                "vad": True,
                "initial_prompt_used": True,
                "model": "large-v3",
                "compute_type": "int8",
            },
            "pipeline_version": "abc1234",
            "speakers_mapped": False,
        },
        "segments": [],
    }


@pytest.fixture
def patched(monkeypatch):
    """Substitui os seams do runner por stubs deterministicos.
    `captured` registra os argumentos passados ao ASR (audio_path, config)."""
    captured = {}

    def fake_transcribe(audio_path, config, *, cpu=False):
        captured["audio_path"] = audio_path
        captured["config"] = dict(config)
        captured["cpu"] = cpu
        return _stub_envelope()

    monkeypatch.setattr(runner, "_transcribe", fake_transcribe)
    monkeypatch.setattr(runner, "_derive_txt", lambda env: "SPEAKER_00: a Acme bateu o EBITDA")
    return captured


def _wer_stub(value):
    return lambda ref, hyp: {
        "wer": value, "substitutions": 0, "deletions": 0,
        "insertions": 0, "ref_words": 6,
    }


def _ter_stub(value):
    return lambda ref, hyp, terms: {
        "ter": value, "terms_total": len(terms),
        "terms_wrong": 0, "missing": [],
    }


def test_registro_tem_forma_da_secao_6(tmp_path, monkeypatch, patched):
    monkeypatch.setattr(runner, "_grade_wer", _wer_stub(0.05))
    monkeypatch.setattr(runner, "_grade_ter", _ter_stub(0.0))
    sample = _make_sample(tmp_path)

    reg = runner.run_sample(sample)

    assert set(reg) == REQUIRED_KEYS
    assert reg["sample_id"] == "amostra_x"
    assert reg["pipeline_version"] == "abc1234"
    assert reg["params"]["model"] == "large-v3"
    assert reg["with_prompt"] is True
    assert reg["der"] == "n/d"
    assert isinstance(reg["wer"], float) and isinstance(reg["ter"], float)
    # config montado: language + initial_prompt derivado dos termos ancorados.
    assert patched["config"]["language"] == "pt"
    assert patched["config"].get("initial_prompt")


def test_veredito_verde_e_vermelho(tmp_path, monkeypatch, patched):
    sample = _make_sample(tmp_path)

    monkeypatch.setattr(runner, "_grade_wer", _wer_stub(runner.WER_THRESHOLD))
    monkeypatch.setattr(runner, "_grade_ter", _ter_stub(runner.TER_THRESHOLD))
    assert runner.run_sample(sample)["verdict"] == "verde"  # <= ambos os limiares

    monkeypatch.setattr(runner, "_grade_wer", _wer_stub(runner.WER_THRESHOLD + 0.01))
    assert runner.run_sample(sample)["verdict"] == "vermelho"  # wer estourou

    monkeypatch.setattr(runner, "_grade_wer", _wer_stub(0.0))
    monkeypatch.setattr(runner, "_grade_ter", _ter_stub(runner.TER_THRESHOLD + 0.01))
    assert runner.run_sample(sample)["verdict"] == "vermelho"  # ter estourou


def test_with_prompt_false_omite_prompt(tmp_path, monkeypatch, patched):
    monkeypatch.setattr(runner, "_grade_wer", _wer_stub(0.0))
    monkeypatch.setattr(runner, "_grade_ter", _ter_stub(0.0))
    sample = _make_sample(tmp_path)

    reg = runner.run_sample(sample, with_prompt=False)

    assert reg["with_prompt"] is False
    assert "initial_prompt" not in patched["config"]


def test_pipeline_version_explicito_sobrepoe(tmp_path, monkeypatch, patched):
    monkeypatch.setattr(runner, "_grade_wer", _wer_stub(0.0))
    monkeypatch.setattr(runner, "_grade_ter", _ter_stub(0.0))
    sample = _make_sample(tmp_path)

    reg = runner.run_sample(sample, pipeline_version="cli-override")
    assert reg["pipeline_version"] == "cli-override"


def test_record_summary_fronteira_de_privacidade(tmp_path, monkeypatch, patched):
    monkeypatch.setattr(runner, "_grade_wer", _wer_stub(0.0))
    monkeypatch.setattr(runner, "_grade_ter", _ter_stub(0.0))
    sample = _make_sample(tmp_path)
    reg = runner.run_sample(sample)

    summary_dir = tmp_path / "logs"
    detail_dir = tmp_path / "outputs_eval"
    paths = runner.record_summary(reg, summary_dir, detail_dir)

    assert paths["summary"].parent == summary_dir
    assert paths["detail"].parent == detail_dir

    summary = json.loads(paths["summary"].read_text(encoding="utf-8"))
    assert "detail" not in summary  # sumario versionavel NAO carrega teor
    assert summary["verdict"] == "verde"
    assert summary["wer"] == 0.0

    detail = json.loads(paths["detail"].read_text(encoding="utf-8"))
    assert detail["sample_id"] == "amostra_x"
    assert "detail" in detail


def test_experimento_c09_calcula_ter_delta(tmp_path, monkeypatch):
    # ASR retorna prompt_used conforme config; TER cai quando ha prompt.
    def fake_transcribe(audio_path, config, *, cpu=False):
        env = _stub_envelope()
        env["metadata"]["params"]["initial_prompt_used"] = "initial_prompt" in config
        return env

    monkeypatch.setattr(runner, "_transcribe", fake_transcribe)
    monkeypatch.setattr(runner, "_derive_txt", lambda env: "hyp")
    monkeypatch.setattr(runner, "_grade_wer", _wer_stub(0.0))

    def ter_by_prompt(ref, hyp, terms):
        # Sem acesso ao config aqui; simula via contador de chamadas.
        ter_by_prompt.calls += 1
        value = 0.02 if ter_by_prompt.calls == 1 else 0.10
        return {"ter": value, "terms_total": len(terms), "terms_wrong": 0, "missing": []}

    ter_by_prompt.calls = 0
    monkeypatch.setattr(runner, "_grade_ter", ter_by_prompt)

    sample = _make_sample(tmp_path)
    out = runner.run_experiment_c09(sample)

    assert set(out) == {"with_prompt", "without_prompt", "ter_delta"}
    assert out["with_prompt"]["with_prompt"] is True
    assert out["without_prompt"]["with_prompt"] is False
    # ter_delta = ter(sem) - ter(com) = 0.10 - 0.02 > 0
    assert out["ter_delta"] == pytest.approx(0.08)
