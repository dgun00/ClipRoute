from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Union

PathLike = Union[str, Path]


def ensure_parent(path: PathLike) -> Path:
    p = Path(path)
    if p.parent and str(p.parent) not in (".", ""):
        p.parent.mkdir(parents=True, exist_ok=True)
    return p


def save_json(path: PathLike, data: Any, *, ensure_ascii: bool = False) -> Path:
    """JSON 저장. (path가 첫 번째 인자)"""
    p = ensure_parent(path)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=ensure_ascii, indent=2)
    return p


def load_json(path: PathLike, *, default: Any | None = None) -> Any:
    p = Path(path)
    if not p.exists():
        if default is not None:
            return default
        raise FileNotFoundError(f"missing json: {p}")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)
