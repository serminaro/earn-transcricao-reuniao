"""01_transcrever — áudio → JSON fonte de verdade (SPEC-009).

Duas fatias num só módulo:

* **Determinística** (DoD-3, testável sem GPU): `build_envelope`, `load_schema`,
  `validate_envelope`, `write_outputs`, `derive_txt`, `derive_srt`,
  `format_timestamp_srt`. Embrulho (DEC-004), validação contra
  `data/schema/transcricao.schema.json` e derivação de TXT/SRT a partir do JSON.
* **GPU** (DoD-2, eval; não exercitada por teste determinístico): `transcribe`,
  `run` e as etapas privadas `_load_audio`/`_run_asr`/`_align_words`/`_diarize`.
  Orquestra WhisperX (DEC-007) + pyannote (DEC-008).

O módulo importa SEM GPU / whisperx / torch / pyannote / yaml: todo import pesado
vive DENTRO da função que o usa, nunca no topo. Comportamento: SPEC-009. Forma do
JSON: SPEC-006 + schema 1.0 (JSON Schema Draft 2020-12).
"""

from __future__ import annotations

import functools
import json
import os
from pathlib import Path
from typing import Any, Optional

# --- Constantes de módulo ---------------------------------------------------

SCHEMA_VERSION: str = "1.0"
SCHEMA_PATH: Path = (
    Path(__file__).resolve().parent.parent / "data" / "schema" / "transcricao.schema.json"
)

# Parâmetros de stack fixados em DEC-007 (gravados em metadata.params).
_MODEL: str = "large-v3"
_COMPUTE_TYPE: str = "int8"
_BATCH_SIZE: int = 16


# --- Hierarquia de exceções (SPEC-009 §6) -----------------------------------

class TranscribeError(Exception):
    """Base de todos os modos de falha do 01."""


class SchemaValidationError(TranscribeError, ValueError):
    """JSON montado não-conforme; a mensagem inclui o caminho do campo inválido."""


class GpuUnavailableError(TranscribeError):
    """CUDA indisponível e cpu=False; cita a flag --cpu."""


class HfTokenError(TranscribeError):
    """HF_TOKEN ausente ou sem acesso ao modelo gated de diarização (DEC-008)."""


class AudioInputError(TranscribeError):
    """Áudio ausente, ilegível ou em formato não suportado."""


# --- Fatia determinística (testável sem GPU; DoD-3) -------------------------

def build_envelope(
    segments: list[dict],
    *,
    audio_source: str,
    model: str,
    compute_type: str,
    language: str,
    params: dict,
    created_at: Optional[str] = None,
    pipeline_version: Optional[str] = None,
    speakers_mapped: bool = False,
) -> dict:
    """Monta o objeto raiz conforme DEC-004 / SPEC-006 §4.1.

    Função pura: NÃO valida (chamar `validate_envelope` em seguida). `created_at=None`
    gera `datetime.now(timezone.utc).isoformat()`. `speakers_mapped` é sempre False na
    saída do 01 (INV-01-3).
    """
    if created_at is None:
        from datetime import datetime, timezone

        created_at = datetime.now(timezone.utc).isoformat()

    metadata: dict[str, Any] = {
        "audio_source": audio_source,
        "created_at": created_at,
        "model": model,
        "compute_type": compute_type,
        "language": language,
        "pipeline_version": pipeline_version,
        "speakers_mapped": bool(speakers_mapped),
        "params": params,
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "metadata": metadata,
        "segments": segments,
    }


@functools.lru_cache(maxsize=None)
def _load_schema_cached(schema_path_str: str) -> dict:
    with open(schema_path_str, encoding="utf-8") as fh:
        return json.load(fh)


def load_schema(schema_path: os.PathLike | str = SCHEMA_PATH) -> dict:
    """Lê e retorna o JSON Schema como dict (cacheável por caminho)."""
    return _load_schema_cached(os.fspath(schema_path))


def validate_envelope(
    envelope: dict, schema_path: os.PathLike | str = SCHEMA_PATH
) -> None:
    """Valida `envelope` contra o schema (Draft 2020-12, `format` date-time checado).

    Sucesso → None. Falha → `SchemaValidationError` cuja mensagem inclui o caminho do
    campo inválido (json-pointer + mensagem do validador), conforme SPEC-006 §6 e
    INV-01-2. O invariante `end >= start` (SPEC-006 §5) não é expressável em JSON Schema
    e é checado à mão aqui. Não escreve nada.
    """
    from jsonschema import Draft202012Validator

    schema = load_schema(schema_path)
    validator = Draft202012Validator(
        schema, format_checker=Draft202012Validator.FORMAT_CHECKER
    )
    errors = sorted(
        validator.iter_errors(envelope), key=lambda e: list(e.absolute_path)
    )
    if errors:
        err = errors[0]
        pointer = (
            "/" + "/".join(str(p) for p in err.absolute_path)
            if err.absolute_path
            else "<root>"
        )
        raise SchemaValidationError(f"{pointer}: {err.message}")

    # Invariante de SPEC-006 §5: end >= start (não codificável no JSON Schema).
    for i, seg in enumerate(envelope.get("segments", [])):
        start, end = seg.get("start"), seg.get("end")
        if (
            isinstance(start, (int, float))
            and isinstance(end, (int, float))
            and end < start
        ):
            raise SchemaValidationError(
                f"/segments/{i}/end: end ({end}) < start ({start}) viola o "
                "invariante de ordem temporal (SPEC-006 §5)."
            )
    return None


def _segment_label(item: dict) -> str:
    """`label = speaker or speaker_raw or "DESCONHECIDO"` (SPEC-009 §3.2)."""
    return item.get("speaker") or item.get("speaker_raw") or "DESCONHECIDO"


def derive_txt(envelope: dict) -> str:
    """Função pura do JSON (R-TRANS-04). Uma linha por segmento: `f"{label}: {text}"`."""
    lines = [
        f"{_segment_label(seg)}: {seg.get('text', '')}"
        for seg in envelope.get("segments", [])
    ]
    return "\n".join(lines)


def derive_srt(envelope: dict) -> str:
    """Função pura do JSON. SRT padrão: índice 1-based, linha de tempo
    `HH:MM:SS,mmm --> HH:MM:SS,mmm` de `start`/`end`, texto prefixado pelo mesmo
    `label` de `derive_txt`. Sem re-invocar ASR.
    """
    blocks = []
    for i, seg in enumerate(envelope.get("segments", []), start=1):
        start = format_timestamp_srt(seg.get("start", 0.0))
        end = format_timestamp_srt(seg.get("end", 0.0))
        label = _segment_label(seg)
        blocks.append(f"{i}\n{start} --> {end}\n{label}: {seg.get('text', '')}")
    return "\n\n".join(blocks) + "\n"


def format_timestamp_srt(seconds: float) -> str:
    """Formata segundos como `HH:MM:SS,mmm` (helper público, testável)."""
    total_ms = int(round(max(0.0, float(seconds)) * 1000.0))
    hours, rem = divmod(total_ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    secs, millis = divmod(rem, 1_000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def write_outputs(
    envelope: dict, out_dir: os.PathLike | str, stem: str
) -> dict[str, Path]:
    """Valida ANTES de gravar; inválido levanta e não grava nada (INV-01-2).

    Grava `{stem}.json` (UTF-8, ensure_ascii=False, indent 2), `{stem}.txt`,
    `{stem}.srt` em `out_dir`. Retorna {"json": Path, "txt": Path, "srt": Path}.
    """
    validate_envelope(envelope)  # falha cedo: nada é gravado se inválido.

    out = Path(os.fspath(out_dir))
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": out / f"{stem}.json",
        "txt": out / f"{stem}.txt",
        "srt": out / f"{stem}.srt",
    }
    paths["json"].write_text(
        json.dumps(envelope, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    paths["txt"].write_text(derive_txt(envelope) + "\n", encoding="utf-8")
    paths["srt"].write_text(derive_srt(envelope), encoding="utf-8")
    return paths


# --- Fatia GPU (imports preguiçosos; eval DoD-2, não teste determinístico) --

def transcribe(audio_path: os.PathLike | str, config: dict, cpu: bool = False) -> dict:
    """Orquestra WhisperX (DEC-007) + pyannote (DEC-008) e retorna o envelope VÁLIDO.

    Todos os imports de whisperx/torch/pyannote.audio ocorrem DENTRO desta função (e
    das etapas privadas). Falha cedo: áudio ilegível → AudioInputError; sem CUDA e
    cpu=False → GpuUnavailableError citando --cpu; HF_TOKEN ausente → HfTokenError.
    Mapeia o resultado para a forma da SPEC-006 e chama `build_envelope` +
    `validate_envelope`. `speakers_mapped=False`, `speaker=None` em todo nível.
    """
    # Import pesado PREGUIÇOSO — nunca no topo do módulo.
    try:
        import torch
    except ImportError as exc:  # ambiente sem a stack de GPU
        raise TranscribeError(
            "torch indisponível: instale a stack de transcrição (ver environment.yml)."
        ) from exc

    audio = Path(os.fspath(audio_path))
    if not audio.is_file():
        raise AudioInputError(f"Áudio ausente ou ilegível: {audio}")

    # GPU: por padrão exige CUDA; sem ela, falha citando --cpu (SPEC-009 §6).
    if cpu:
        device = "cpu"
    else:
        if not torch.cuda.is_available():
            raise GpuUnavailableError(
                "CUDA indisponível: o 01 exige GPU NVIDIA. Rode com a flag --cpu para "
                "forçar execução em CPU (large-v3 em CPU é ordens de grandeza mais lento)."
            )
        device = "cuda"

    # Diarização gated (DEC-008): HF_TOKEN tem de existir no ambiente.
    hf_token = os.environ.get("HF_TOKEN")
    if not hf_token:
        raise HfTokenError(
            "HF_TOKEN ausente no ambiente: necessário para baixar o modelo gated de "
            "diarização (pyannote.audio, DEC-008)."
        )

    language = config.get("language", "pt")
    initial_prompt = config.get("initial_prompt") or None

    # Etapas em ordem sobre uma só carga do áudio (SPEC-009 §4).
    waveform = _load_audio(audio)
    asr_result = _run_asr(waveform, config, device)
    aligned = _align_words(asr_result, waveform, device)
    diarized = _diarize(waveform, aligned, device, hf_token)
    segments = _map_segments(diarized)

    params = {
        "condition_on_previous_text": False,
        "vad": True,
        "initial_prompt_used": bool(initial_prompt),
        "batch_size": _BATCH_SIZE,
    }
    envelope = build_envelope(
        segments,
        audio_source=audio.name,  # basename, sem caminho absoluto (SPEC-006 §4.2)
        model=_MODEL,
        compute_type=_COMPUTE_TYPE,
        language=language,
        params=params,
        pipeline_version=config.get("pipeline_version"),
        speakers_mapped=False,  # INV-01-3
    )
    validate_envelope(envelope)
    return envelope


def run(
    audio_path: os.PathLike | str,
    config_path: os.PathLike | str,
    out_dir: os.PathLike | str,
    *,
    cpu: bool = False,
) -> dict[str, Path]:
    """Entrypoint de orquestração: lê o YAML, chama `transcribe`, `write_outputs`."""
    config = _load_config(config_path)
    envelope = transcribe(audio_path, config, cpu=cpu)
    stem = Path(os.fspath(audio_path)).stem
    return write_outputs(envelope, out_dir, stem)


# --- Etapas privadas da fatia GPU (imports preguiçosos) ---------------------

def _load_config(config_path: os.PathLike | str) -> dict:
    """Lê o YAML da reunião. Import de PyYAML preguiçoso (não exigido pela fatia
    determinística). O 01 lê só `language` e `initial_prompt`; o resto é ignorado."""
    import yaml  # lazy: stack de execução, não usada pelos testes determinísticos

    with open(os.fspath(config_path), encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise TranscribeError(f"Config YAML inválido (esperado mapa): {config_path}")
    return data


def _load_audio(audio_path: os.PathLike | str):
    """Carrega a forma de onda via WhisperX (SPEC-009 §4 passo 1)."""
    import whisperx

    try:
        return whisperx.load_audio(os.fspath(audio_path))
    except Exception as exc:  # arquivo corrompido/formato não suportado
        raise AudioInputError(f"Falha ao ler o áudio: {audio_path} ({exc})") from exc


def _run_asr(audio, config: dict, device: str):
    """Transcreve com large-v3/int8, VAD ativo, condition_on_previous_text=False
    (DEC-007), aplicando o initial_prompt do YAML quando houver."""
    import whisperx

    initial_prompt = config.get("initial_prompt") or None
    asr_options = {
        "condition_on_previous_text": False,
        "initial_prompt": initial_prompt,
    }
    model = whisperx.load_model(
        _MODEL,
        device,
        compute_type=_COMPUTE_TYPE,
        language=config.get("language", "pt"),
        asr_options=asr_options,
    )
    return model.transcribe(audio, batch_size=_BATCH_SIZE)


def _align_words(asr_result, audio, device: str):
    """Alinhamento word-level (SPEC-009 §4 passo 3). Palavras não posicionadas ficam
    com timestamps/score nulos — válido, não erro (SPEC-006 §6)."""
    import whisperx

    align_model, metadata = whisperx.load_align_model(
        language_code=asr_result.get("language", "pt"), device=device
    )
    aligned = whisperx.align(
        asr_result["segments"],
        align_model,
        metadata,
        audio,
        device,
        return_char_alignments=False,
    )
    # Preserva o idioma para mapeamento/coerência a jusante.
    aligned.setdefault("language", asr_result.get("language", "pt"))
    return aligned


def _diarize(audio, aligned, device: str, hf_token: str):
    """Diariza com pyannote integrado ao WhisperX e costura os labels nos segmentos
    e palavras (DEC-008). Trecho sem atribuição → speaker None (SPEC-009 §4.1)."""
    import whisperx

    diarize_pipeline = whisperx.DiarizationPipeline(
        use_auth_token=hf_token, device=device
    )
    diarize_segments = diarize_pipeline(audio)
    return whisperx.assign_word_speakers(diarize_segments, aligned)


def _map_segments(whisperx_result: dict) -> list[dict]:
    """Mapeia o resultado do WhisperX para a forma de segmento/palavra da SPEC-006:
    o label cru do pyannote vira `speaker_raw`; `speaker` (nome real) fica None até o
    passo 02 (INV-01-3, INV-01-4)."""
    segments: list[dict] = []
    for seg in whisperx_result.get("segments", []):
        words = []
        for w in seg.get("words", []):
            words.append(
                {
                    "word": w.get("word", ""),
                    "start": w.get("start"),
                    "end": w.get("end"),
                    "score": w.get("score"),
                    "speaker_raw": w.get("speaker"),
                    "speaker": None,
                }
            )
        segments.append(
            {
                "start": float(seg.get("start", 0.0)),
                "end": float(seg.get("end", 0.0)),
                "text": (seg.get("text") or "").strip(),
                "speaker_raw": seg.get("speaker"),
                "speaker": None,
                "words": words,
            }
        )
    return segments


def _build_arg_parser():
    import argparse

    parser = argparse.ArgumentParser(
        prog="01_transcrever",
        description="Transcreve um áudio de reunião no JSON fonte de verdade (SPEC-009).",
    )
    parser.add_argument("audio", help="caminho do áudio local da reunião")
    parser.add_argument("config", help="YAML de configuração da reunião")
    parser.add_argument("out_dir", help="diretório de saída (JSON/TXT/SRT)")
    parser.add_argument(
        "--cpu",
        action="store_true",
        help="força execução consciente em CPU (large-v3 é muito mais lento)",
    )
    return parser


if __name__ == "__main__":  # pragma: no cover
    args = _build_arg_parser().parse_args()
    written = run(args.audio, args.config, args.out_dir, cpu=args.cpu)
    for kind, path in written.items():
        print(f"{kind}: {path}")
