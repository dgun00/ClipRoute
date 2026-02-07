from __future__ import annotations

import re
from difflib import SequenceMatcher


def _norm(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"[\s\-_/]+", " ", s)
    s = re.sub(r"[^0-9a-z가-힣 ]+", "", s)
    return re.sub(r"\s+", " ", s).strip()


def similarity(a: str, b: str) -> float:
    na, nb = _norm(a), _norm(b)
    if not na or not nb:
        return 0.0
    return SequenceMatcher(None, na, nb).ratio()


def is_similar_place(a: str, b: str, *, threshold: float = 0.72) -> bool:
    return similarity(a, b) >= threshold
