"""Configuration loader. Single source of truth: config.json in this directory."""

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

_ROOT = Path(__file__).parent
_CONFIG_FILE = _ROOT / "config.json"


def _to_namespace(obj: Any) -> Any:
    if isinstance(obj, dict):
        return SimpleNamespace(**{k: _to_namespace(v) for k, v in obj.items()})
    if isinstance(obj, list):
        return [_to_namespace(v) for v in obj]
    return obj


def _resolve_path(rel: str) -> str:
    return str(_ROOT / rel)


with open(_CONFIG_FILE) as _f:
    _raw = json.load(_f)


class Config:
    def __init__(self, cfg: dict) -> None:
        self.server = _to_namespace(cfg["server"])
        self.llm = _to_namespace(cfg["llm"])
        self.report_analysis_agent = _to_namespace(cfg["report_analysis_agent"])

        self.paths = SimpleNamespace(
            secrets_file=_resolve_path(cfg["paths"]["secrets_file"]),
        )


config = Config(_raw)