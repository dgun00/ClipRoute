from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Union

PathLike = Union[str, Path]


def ensure_parent(path: PathLike) -> Path:
    p = Path(path)
    if p.parent and str(p.parent) not in (".", ""):
        p.parent.mkdir(parents=True, exist_ok=True)
    return p


def save_json(path: PathLike, data: Any, *, ensure_ascii: bool = False) -> Path:
    """
    JSON 저장 및 누적 업데이트 + 히스토리 백업.
    - 기존 파일이 있으면 읽어와서 새로운 데이터와 병합(update)합니다.
    - 데이터 유실 방지를 위해 history 폴더에 타임스탬프 백업본을 생성합니다.
    """
    p = ensure_parent(path)
    
    # 1. 기존 데이터 로드 및 병합 (누적 저장 로직)
    final_data = data
    if p.exists() and p.stat().st_size > 0:
        try:
            with open(p, "r", encoding="utf-8") as f:
                old_data = json.load(f)
                if isinstance(old_data, dict) and isinstance(data, dict):
                    # 기존 데이터에 새로운 영상 데이터를 업데이트 (중복은 최신본으로)
                    old_data.update(data)
                    final_data = old_data
        except Exception:
            # 파일이 깨졌거나 형식이 다를 경우 현재 데이터로 진행
            pass

    # 2. 마스터 파일 저장 (최신 누적본)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(final_data, f, ensure_ascii=ensure_ascii, indent=2)

    # 3. 히스토리 백업본 생성 (절대 유실 방지)
    try:
        history_dir = p.parent / "history"
        history_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = history_dir / f"{p.stem}_{timestamp}{p.suffix}"
        
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(final_data, f, ensure_ascii=ensure_ascii, indent=2)
    except Exception:
        pass

    return p


def load_json(path: PathLike, *, default: Any | None = None) -> Any:
    p = Path(path)
    if not p.exists():
        if default is not None:
            return default
        raise FileNotFoundError(f"missing json: {p}")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)