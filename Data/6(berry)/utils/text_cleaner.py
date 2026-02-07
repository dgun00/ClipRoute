from __future__ import annotations

import re
from typing import List


_VTT_TS = re.compile(r"^\d{2}:\d{2}:\d{2}\.\d{3} \-\-\> \d{2}:\d{2}:\d{2}\.\d{3}")
_TAG = re.compile(r"<[^>]+>")


def vtt_to_text(vtt: str) -> str:
    """VTT 자막을 plain text로 변환합니다."""
    out: List[str] = []
    for raw in vtt.splitlines():
        s = raw.strip("\ufeff ")
        if not s:
            continue
        if s == "WEBVTT":
            continue
        if _VTT_TS.match(s):
            continue
        if s.isdigit():
            continue
        if s.startswith(("NOTE", "STYLE", "REGION")):
            continue

        s = _TAG.sub("", s)
        s = re.sub(r"\s+", " ", s).strip()
        if s:
            out.append(s)

    text = " ".join(out)
    return re.sub(r"\s+", " ", text).strip()


def merge_transcripts(yt_dlp_vtt: str | None, whisper_text: str | None) -> str:
    """yt-dlp(VTT) + Whisper 결과를 합쳐 단일 transcript로 만듭니다."""
    a = vtt_to_text(yt_dlp_vtt) if yt_dlp_vtt else ""
    b = (whisper_text or "").strip()
    if a and b:
        return a + "\n" + b
    return a or b


def chunk_text(text: str, *, max_chars: int = 2500, overlap: int = 100) -> List[str]:
    """LLM 호출용 텍스트 chunking.

    - max_chars 기준으로 자르되, 가능하면 문장 구분자 근처에서 분리
    - overlap 만큼 겹쳐서 맥락 손실 줄임
    """
    t = re.sub(r"\s+", " ", (text or "")).strip()
    if not t:
        return []
    if len(t) <= max_chars:
        return [t]

    chunks: List[str] = []
    start = 0
    min_cut = int(max_chars * 0.6)
    seps = [". ", "! ", "? ", "。", "…", "\n"]

    while start < len(t):
        end = min(len(t), start + max_chars)
        piece = t[start:end]

        cut = len(piece)
        if end < len(t):
            best = -1
            for sep in seps:
                idx = piece.rfind(sep)
                if idx > best:
                    best = idx
            if best >= min_cut:
                cut = best + 1  # sep 포함

        chunk = t[start:start + cut].strip()
        if chunk:
            chunks.append(chunk)

        # 다음 시작점 (overlap 적용)
        next_start = start + cut - overlap
        if next_start <= start:
            next_start = start + cut
        start = next_start

    return chunks
