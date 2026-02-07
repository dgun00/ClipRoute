from __future__ import annotations

from datetime import datetime
from typing import Any


def log(tag: str, message: str, /, **kv: Any) -> None:
    """간단한 표준 로그 함수."""
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    extra = ""
    if kv:
        extra = " " + " ".join(f"{k}={v}" for k, v in kv.items())
    print(f"[{ts}] [{tag}] {message}{extra}")
