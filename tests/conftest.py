"""Fixtures determinísticas para os testes do 01 (DoD-3). Sem GPU/whisperx/torch.

Garante que `import src.transcrever` funcione independentemente do diretório de
invocação do pytest, inserindo a raiz do repo em sys.path.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def schema_path() -> Path:
    return REPO_ROOT / "data" / "schema" / "transcricao.schema.json"


@pytest.fixture
def valid_envelope() -> dict:
    """Envelope conforme SPEC-006 / schema 1.0, recarregado a cada teste (mutável)."""
    return json.loads((FIXTURES_DIR / "envelope_valid.json").read_text(encoding="utf-8"))


@pytest.fixture
def sample_segments(valid_envelope) -> list[dict]:
    """Segmentos já na forma da SPEC-006 §4.3, prontos para `build_envelope`."""
    return copy.deepcopy(valid_envelope["segments"])
