"""Runner do eval (SPEC-005 secoes 3 e 6).

Andaime DETERMINISTICO em volta do ASR nao-deterministico: dado um diretorio de
amostra do golden set, roda o pipeline (script 01 / `src.transcrever.transcribe`),
deriva a hipotese de texto, chama o grader (WER/TER) e emite um REGISTRO DE
METRICAS conforme SPEC-005 secao 6 (id, versao/commit, parametros, WER, TER,
DER=n/d, veredito, data).

Pontos de extensao (seams):
    A chamada de GPU (`transcribe`), a derivacao de texto (`derive_txt`) e as
    metricas (`grader.wer` / `grader.ter`) sao acessadas via funcoes-modulo de
    importacao PREGUICOSA (`_transcribe`, `_derive_txt`, `_grade_wer`,
    `_grade_ter`). Importar este modulo NAO importa `src.transcrever`,
    `eval.grader`, nem qualquer lib de GPU. Os testes deterministicos
    substituem (monkeypatch) esses seams; a execucao real com GPU esta FORA DE
    ESCOPO deste esqueleto.

Fronteira de privacidade (SPEC-005 secao 6, R-EVAL-04): o registro carrega
`detail` (trechos/palavras erradas, teor sensivel). `record_summary` separa o
sumario agregado (numeros + veredito, versionavel) do detalhe (gitignored,
`outputs/eval/`).
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# ── Limiares provisorios (SPEC-005 secao 5). Calibrar apos a 1a execucao real. ──
WER_THRESHOLD: float = 0.15
TER_THRESHOLD: float = 0.10

# Extensoes de audio aceitas ao localizar `audio.<ext>` na pasta da amostra.
_AUDIO_EXTS: tuple[str, ...] = (
    ".m4a", ".mp3", ".wav", ".flac", ".aac", ".ogg", ".opus", ".mp4",
)

DER_NA: str = "n/d"  # DER fica fora de escopo enquanto a referencia for so texto.


# ──────────────────────────────────────────────────────────────────────────────
# Seams de importacao preguicosa (substituiveis por monkeypatch nos testes).
# Nenhuma lib pesada e importada no topo do modulo.
# ──────────────────────────────────────────────────────────────────────────────

def _transcribe(audio_path: Any, config: dict, *, cpu: bool = False) -> dict:
    """Ponto de extensao da chamada GPU. Importa `src.transcrever.transcribe`
    SOMENTE quando efetivamente invocado (execucao real, fora de escopo deste
    esqueleto). Nos testes este seam e substituido por um stub."""
    from src.transcrever import transcribe  # import preguicoso, intencional

    return transcribe(audio_path, config, cpu=cpu)


def _derive_txt(envelope: dict) -> str:
    """Deriva o TXT humano do envelope (com rotulo de falante; saida do 01)."""
    from src.transcrever import derive_txt  # import preguicoso

    return derive_txt(envelope)


def _plain_text(envelope: dict) -> str:
    """Hipotese para o WER/TER: texto corrido dos segmentos, SEM rotulo de falante.
    O WER mede palavras (nao falante; isso e a DER). Usar o derive_txt aqui injetaria
    os tokens 'speaker'/'NN' do prefixo SPEAKER_XX e inflaria o WER."""
    return " ".join(
        (seg.get("text") or "").strip() for seg in envelope.get("segments", [])
    ).strip()


def _grade_wer(reference: str, hypothesis: str) -> dict:
    from eval.grader import wer  # import preguicoso

    return wer(reference, hypothesis)


def _grade_ter(reference: str, hypothesis: str, anchored_terms: list[str]) -> dict:
    from eval.grader import ter  # import preguicoso

    return ter(reference, hypothesis, anchored_terms)


# ──────────────────────────────────────────────────────────────────────────────
# Leitura da amostra (meta.yml, ref.txt, audio).
# ──────────────────────────────────────────────────────────────────────────────

def _read_meta(meta_path: Path) -> dict:
    """Le `meta.yml`. Usa PyYAML se disponivel; caso contrario, um parser
    minimo de stdlib suficiente para o subconjunto plano de meta.yml
    (chave: valor e listas com `- item`). meta.yml ausente -> {}."""
    if not meta_path.exists():
        return {}
    text = meta_path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
        return data if isinstance(data, dict) else {}
    except ImportError:
        return _mini_yaml(text)


def _mini_yaml(text: str) -> dict:
    """Parser YAML minimo e tolerante: chaves escalares e listas simples.

    Cobre o necessario para meta.yml (language, initial_prompt, listas de
    termos ancorados e falantes). Nao e um parser YAML completo."""
    result: dict[str, Any] = {}
    current_key: Optional[str] = None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        stripped = line.lstrip()
        indented = len(line) - len(stripped)
        if stripped.startswith("- "):
            item = _scalar(stripped[2:].strip())
            if current_key is not None and isinstance(result.get(current_key), list):
                result[current_key].append(item)
            continue
        if ":" in stripped:
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()
            if value == "":
                # Pode abrir uma lista nas linhas seguintes.
                result[key] = []
                current_key = key
            else:
                result[key] = _scalar(value)
                current_key = None
        _ = indented  # estrutura plana; indentacao ignorada de proposito.
    # Remove listas que ficaram vazias por serem, na verdade, escalares nulos.
    return result


def _scalar(token: str) -> Any:
    token = token.strip()
    if len(token) >= 2 and token[0] == token[-1] and token[0] in "\"'":
        return token[1:-1]
    low = token.lower()
    if low in ("true", "false"):
        return low == "true"
    if low in ("null", "~", ""):
        return None
    try:
        return int(token)
    except ValueError:
        pass
    try:
        return float(token)
    except ValueError:
        return token


def _anchored_terms(meta: dict) -> list[str]:
    """Extrai o vocabulario ancorado de meta.yml (SPEC-005 secao 4.2).
    Aceita varios nomes de chave por tolerancia."""
    for key in (
        "anchored_terms", "vocabulario_ancorado", "termos_ancorados",
        "vocabulary", "vocab",
    ):
        value = meta.get(key)
        if isinstance(value, list):
            return [str(v) for v in value if v is not None]
        if isinstance(value, str) and value.strip():
            return [t.strip() for t in value.split(",") if t.strip()]
    return []


def _initial_prompt(meta: dict, anchored: list[str]) -> Optional[str]:
    """initial_prompt explicito em meta.yml; senao, derivado dos termos
    ancorados (nomes/jargao a ancorar, SPEC-005 secao 4.2 / C-09)."""
    explicit = meta.get("initial_prompt")
    if isinstance(explicit, str) and explicit.strip():
        return explicit
    if anchored:
        return ", ".join(anchored)
    return None


def _find_audio(sample_dir: Path) -> Optional[Path]:
    for ext in _AUDIO_EXTS:
        candidate = sample_dir / f"audio{ext}"
        if candidate.exists():
            return candidate
    # Fallback: qualquer arquivo cujo nome comece por "audio.".
    for child in sorted(sample_dir.glob("audio.*")):
        if child.is_file():
            return child
    return None


# ──────────────────────────────────────────────────────────────────────────────
# Runner principal.
# ──────────────────────────────────────────────────────────────────────────────

def run_sample(
    sample_dir,
    *,
    with_prompt: bool = True,
    cpu: bool = False,
    pipeline_version: Optional[str] = None,
) -> dict:
    """Roda o pipeline sobre uma amostra do golden set e devolve o REGISTRO DE
    METRICAS (SPEC-005 secao 6).

    sample_dir: pasta `data/golden/<id>/` com `audio.<ext>`, `ref.txt`,
        opcional `ref.json`, `meta.yml`.

    A chamada de ASR e feita pelo seam `_transcribe` (import preguicoso de
    `src.transcrever.transcribe`); a execucao real com GPU esta fora de escopo
    deste esqueleto e e substituida por stub nos testes.
    """
    sample_dir = Path(os.fspath(sample_dir))
    sample_id = sample_dir.name

    meta = _read_meta(sample_dir / "meta.yml")
    anchored = _anchored_terms(meta)

    ref_path = sample_dir / "ref.txt"
    reference = ref_path.read_text(encoding="utf-8") if ref_path.exists() else ""
    has_ref_json = (sample_dir / "ref.json").exists()

    # config lido pelo 01 (SPEC-009 secao 3.1): language + initial_prompt.
    # Para o experimento C-09 (secao 7.2), with_prompt=False omite o prompt.
    config: dict[str, Any] = {"language": str(meta.get("language", "pt"))}
    if with_prompt:
        prompt = _initial_prompt(meta, anchored)
        if prompt:
            config["initial_prompt"] = prompt

    audio_path = _find_audio(sample_dir)

    # ── Pipeline real (seam) ──
    envelope = _transcribe(audio_path, config, cpu=cpu)

    metadata = envelope.get("metadata") or {}
    params = metadata.get("params", {})
    if pipeline_version is None:
        pipeline_version = metadata.get("pipeline_version")

    hypothesis = _plain_text(envelope)

    # ── Metricas (grader, Python puro) ──
    wer_res = _grade_wer(reference, hypothesis)
    ter_res = _grade_ter(reference, hypothesis, anchored)
    wer_value = float(wer_res.get("wer", 0.0))
    ter_value = float(ter_res.get("ter", 0.0))

    # DER fica `n/d` enquanto nao houver ref.json + implementacao (secao 4.3).
    der: Any = DER_NA  # noqa: F841  (computo de DER fora de escopo)

    verdict = (
        "verde"
        if (wer_value <= WER_THRESHOLD and ter_value <= TER_THRESHOLD)
        else "vermelho"
    )

    return {
        "sample_id": sample_id,
        "pipeline_version": pipeline_version,
        "params": params,
        "with_prompt": with_prompt,
        "wer": wer_value,
        "ter": ter_value,
        "der": der,
        "verdict": verdict,
        "date": datetime.now(timezone.utc).isoformat(),
        # detail: teor potencialmente sensivel -> destino gitignored (record_summary).
        "detail": {
            "wer": wer_res,
            "ter": ter_res,
            "has_ref_json": has_ref_json,
        },
    }


def record_summary(registro: dict, summary_dir, detail_dir) -> dict[str, Path]:
    """Fronteira de privacidade (SPEC-005 secao 6, R-EVAL-04).

    Grava o SUMARIO agregado (so numeros + veredito, SEM teor de reuniao) em
    `summary_dir` (versionavel, ex.: `docs/logs/`) e o DETALHE (trechos/palavras
    erradas) em `detail_dir` (gitignored, ex.: `outputs/eval/`).

    Retorna {"summary": Path, "detail": Path}.
    """
    summary_dir = Path(os.fspath(summary_dir))
    detail_dir = Path(os.fspath(detail_dir))
    summary_dir.mkdir(parents=True, exist_ok=True)
    detail_dir.mkdir(parents=True, exist_ok=True)

    sample_id = registro.get("sample_id", "amostra")
    date = registro.get("date", datetime.now(timezone.utc).isoformat())
    stamp = str(date).replace(":", "").replace("-", "")[:15]
    stem = f"{sample_id}_{stamp}"

    # Sumario: somente numeros e veredito; o campo `detail` e EXCLUIDO.
    summary = {k: v for k, v in registro.items() if k != "detail"}

    summary_path = summary_dir / f"{stem}.summary.json"
    detail_path = detail_dir / f"{stem}.detail.json"

    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    detail_payload = {
        "sample_id": sample_id,
        "date": date,
        "detail": registro.get("detail", {}),
    }
    detail_path.write_text(
        json.dumps(detail_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    return {"summary": summary_path, "detail": detail_path}


def run_experiment_c09(sample_dir, *, cpu: bool = False) -> dict:
    """Experimento C-09 (SPEC-005 secao 7.2): roda a mesma amostra com e sem
    `initial_prompt` e compara a TER. `ter_delta` > 0 indica que o prompt
    reduziu a TER (hipotese confirmada)."""
    with_prompt = run_sample(sample_dir, with_prompt=True, cpu=cpu)
    without_prompt = run_sample(sample_dir, with_prompt=False, cpu=cpu)
    ter_delta = float(without_prompt["ter"]) - float(with_prompt["ter"])
    return {
        "with_prompt": with_prompt,
        "without_prompt": without_prompt,
        "ter_delta": ter_delta,
    }
