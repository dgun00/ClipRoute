
from __future__ import annotations
# PATCH_APPLIED: allow 2-char Korean proper nouns + heuristic day inference (2026-01-24)

from pathlib import Path
from typing import Dict, List, Any, Optional

import re
import json

import config
from llm.gemini_client import normalize_places_from_text
from utils.logging_utils import log
from utils.io import save_json
from utils.text_cleaner import chunk_text


_DESC_MARKER = "[DESCRIPTION_CHAPTERS]"
_CHAPTER_RE = re.compile(
    r"^\s*(?:[-•*·]\s*)?(?P<ts>(?:\d{1,2}:)?\d{1,2}:\d{2})\s*(?:[-–—:)]\s*)?(?P<title>.+?)\s*$"
)

_DAY_RE = re.compile(r"(?:(?:day)\s*(\d{1,2})|([1-9]\d?)\s*일차)", re.IGNORECASE)

# --- Generic candidate filtering (keep only concrete proper nouns as much as possible) ---
_GENERIC_EXACT = {
    "숙소",
    "카페",
    "식당",
    "맛집",
    "편의점",
    "공항",
    "터미널",
    "주차장",
    "해변",
    "바다",
    "시장",
    "마트",
    "호텔",
    "펜션",
    "게스트하우스",
    "vlog",
    "Vlog",
    "브이로그",
    "인트로",
    "오프닝",
    "엔딩",
    "마무리",
    "구독",
    "좋아요",
    "구독과 좋아요",
    "구독과좋아요",
    "댓글",
    "협찬",
    "광고",
    "문의",
    "인스타",
    "인스타그램",
}


_GENERIC_PATTERN = re.compile(
    r"^(?:도착\s*장소|이전\s*방문\s*장소|방문\s*장소|예약\s*문의\s*장소|실내\s*장소|현장|여기)$"
)


# --- NEW: Drop obvious non-place chapter titles / social / url tokens early ---
_DESC_NON_PLACE_EXACT = {
    "인트로",
    "오프닝",
    "엔딩",
    "마무리",
    "하이라이트",
    "예고",
    "공지",
    "공지사항",
}

_URL_LIKE_RE = re.compile(
    r"(?i)(https?://|www\.|instagram\.com|youtu\.be|youtube\.com|t\.me/|open\.kakao\.com|kakao\.me|bit\.ly|\bemail\b|@\w{2,})"
)


# --- NEW: Canonicalize place names to reduce duplicates (emoji/spacing/brackets) ---
# We keep a human-readable cleaned name, and a stricter key for dedup.
_EMOJI_RE = re.compile(
    "["  # common emoji blocks
    "\U0001F300-\U0001FAFF"  # symbols & pictographs + extended
    "\U00002700-\U000027BF"  # dingbats
    "\U00002600-\U000026FF"  # misc symbols
    "]+",
    flags=re.UNICODE,
)


def _canonicalize_place_name(name: str) -> tuple[str, str]:
    """Return (clean_display_name, canonical_key).

    - Removes emojis / variation selectors
    - Removes bracketed suffixes like (..), [..], {..}
    - Normalizes whitespace
    - canonical_key additionally removes spaces and lowercases (for robust dedup)
    """
    n = (name or "").strip()
    if not n:
        return "", ""

    # Remove emoji + variation selector + ZWJ
    n = n.replace("\ufe0f", "").replace("\u200d", "")
    n = _EMOJI_RE.sub(" ", n)

    # Drop bracket contents (often category / emojis / notes)
    n = re.sub(r"\([^)]*\)", " ", n)
    n = re.sub(r"\[[^\]]*\]", " ", n)
    n = re.sub(r"\{[^}]*\}", " ", n)

    # Keep only generally safe characters for names
    n = re.sub(r"[^0-9A-Za-z가-힣&+\.\-\s]+", " ", n)
    n = re.sub(r"\s+", " ", n).strip()

    key = re.sub(r"\s+", "", n).lower()
    return n, key


# --- Title/Description seed extraction (must-keep candidates) ---
_SEED_SPLIT_RE = re.compile(r"[,\n]|[|]|[•·]|[/]|[→▶]|[–—-]")
_SEED_CLEAN_RE = re.compile(r"[\[\]{}<>\"'“”‘’]|#+")
_SEED_TRIM_RE = re.compile(r"^\s*[-•*·]+\s*|\s+$")

# Seed filtering: drop obvious non-place tokens/sentences even if they appear in title/description
_SEED_TOO_SENTENCE_RE = re.compile(
    r"(추천|다녀오|다녀왔|다녀오기|브이로그|vlog|영상|편집|여행\s*브이로그|여행\s*기록)",
    re.IGNORECASE,
)

# Drop common travel-duration / itinerary phrases that are not a place name
_SEED_DURATION_RE = re.compile(r"\b\d+\s*(?:박|일)\b|\b(?:당일치기|1박2일|2박3일|3박4일|4박5일|5박6일)\b")


def _extract_place_seeds_from_text(text: str, region_tag: str) -> List[str]:
    """Extract visit-place-like tokens from title/description with minimal hardcoding."""
    t = (text or "").strip()
    if not t:
        return []

    # Keep bracket contents by just loosening separators
    t = t.replace("(", " ").replace(")", " ")
    t = t.replace("【", " ").replace("】", " ")
    t = _SEED_CLEAN_RE.sub(" ", t)
    t = re.sub(r"\s+", " ", t).strip()

    parts: List[str] = []
    for seg in _SEED_SPLIT_RE.split(t):
        s = _SEED_TRIM_RE.sub("", seg).strip()
        if not s:
            continue

        # Drop URL/social handles/mentions
        if _URL_LIKE_RE.search(s):
            continue

        # Drop region-only tokens
        if region_tag and (s == region_tag or s == f"{region_tag}도"):
            continue

        # Very long segments are likely sentences
        if len(s) > 40:
            continue

        # Sentence-like / non-place phrases should not become seeds
        if _SEED_TOO_SENTENCE_RE.search(s):
            continue

        # Travel-duration / itinerary phrases are not places
        if _SEED_DURATION_RE.search(s):
            continue

        # Too many whitespace tokens usually indicates a sentence, not a place
        if len(s.split()) >= 6:
            continue

        # Drop generic tokens here (seed should be concrete)
        if _is_generic_place_name(s):
            continue

        parts.append(s)

    # De-dup while preserving order
    seen = set()
    out: List[str] = []
    for p in parts:
        if p in seen:
            continue
        seen.add(p)
        out.append(p)
    return out


def _build_seed_candidates(video_id: str, title: str, description: str, region_tag: str) -> List[dict]:
    """Build must-keep candidates from title/description."""
    seeds: List[str] = []
    seeds += _extract_place_seeds_from_text(title, region_tag)
    seeds += _extract_place_seeds_from_text(description, region_tag)

    # De-dup while preserving order
    seen = set()
    uniq: List[str] = []
    for s in seeds:
        if s in seen:
            continue
        seen.add(s)
        uniq.append(s)

    out: List[dict] = []
    order = 0
    for s in uniq:
        order += 1
        out.append(
            {
                "video_id": video_id,
                "day": 1,
                "order": order,
                "seconds": 0,
                "place_name": s,
                "original_phrase": s,
                "category": "",
                "visit_confidence": "high",
                "visit_reason": "title/description seed",
                "source": "seed",
                "region_tag": region_tag,
                "video_title": title,
                "source_weight": 5,
                "must_keep": True,
                "candidate_strength": "seed",
                "seconds_source": "none",
            }
        )
    return out


def _is_generic_place_name(name: str) -> bool:
    n = (name or "").strip()
    if not n:
        return True

    # vlog/브이로그 같은 일반 단어는 장소가 아님(케이스/대소문자 무관)
    if n.lower() in {"vlog", "travel vlog"}:
        return True
    if n in {"브이로그"}:
        return True

    # 구분선/데코 문자만 있는 경우(예: "〰️〰️", "---", "====")는 장소가 아님
    compact = re.sub(r"\s+", "", n)
    if compact:
        # remove common separator symbols and emoji-like wave characters
        stripped = re.sub(r"[\-_=~—–·•*|/\\]+", "", compact)
        stripped = stripped.replace("〰", "")
        stripped = stripped.replace("️", "")  # variation selector
        # if nothing meaningful remains, treat as generic
        if not stripped:
            return True

    # 괄호/기호만으로 구성된 경우
    if re.fullmatch(r"[\W_]+", n):
        return True

    # 너무 짧은 토큰은 고유명사로 보기 어려움
    # - 한글 2글자 고유명사(예: 우무)는 유효할 수 있으므로 보수적으로 1글자만 탈락
    # - 영문/숫자만 2글자 이하인 경우는 보통 노이즈가 많아 탈락
    has_korean = any('가' <= ch <= '힣' for ch in n)
    if has_korean:
        if len(n) <= 1:
            return True
    else:
        if len(n) <= 2:
            return True

    # 정확히 카테고리/일반명인 경우
    if n in _GENERIC_EXACT:
        return True

    # "도착 장소" 같은 템플릿성 라벨
    if _GENERIC_PATTERN.match(n):
        return True

    # Day 구분 헤더 자체가 장소로 들어오는 경우 제거
    if re.fullmatch(r"(?i)day\s*\d{1,2}", n):
        return True
    if re.fullmatch(r"[1-9]\d?\s*일차", n):
        return True

    # "식당/카페" 같이 슬래시로 뭉개진 라벨
    if "/" in n and len(n) <= 20:
        # 예: "식당/카페", "식당/카페 (실내)"
        if any(tok in n for tok in ["식당", "카페", "숙소", "장소", "실내"]):
            return True

    return False


def _ts_to_seconds(ts: str) -> int:
    ts = (ts or "").strip()
    if not ts:
        return 0
    parts = ts.split(":")
    try:
        if len(parts) == 2:
            mm, ss = parts
            return int(mm) * 60 + int(ss)
        if len(parts) == 3:
            hh, mm, ss = parts
            return int(hh) * 3600 + int(mm) * 60 + int(ss)
    except Exception:
        return 0
    return 0


def _extract_description_chapter_lines(transcript: str) -> List[str]:
    if not transcript or _DESC_MARKER not in transcript:
        return []
    after = transcript.split(_DESC_MARKER, 1)[1]
    lines = [ln.strip() for ln in after.splitlines() if ln.strip()]
    # keep only timestamp-like lines
    out: List[str] = []
    for ln in lines:
        if _CHAPTER_RE.match(ln):
            out.append(ln)
    return out


def _strip_day_token(text: str) -> tuple[str, int]:
    """Return (cleaned_text, day_hint) where day_hint=0 if none."""
    t = (text or "").strip()
    if not t:
        return "", 0
    m = _DAY_RE.search(t)
    if not m:
        return t, 0
    day = 0
    try:
        if m.group(1):
            day = int(m.group(1))
        elif m.group(2):
            day = int(m.group(2))
    except Exception:
        day = 0
    # remove the matched token to avoid polluting place name
    cleaned = (t[: m.start()] + t[m.end() :]).strip()
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    return cleaned, day


def _guess_place_name_from_chapter_title(title_text: str) -> str:
    """Heuristic: take the first segment before common delimiters."""
    t = (title_text or "").strip()
    if not t:
        return ""
    # normalize separators
    for sep in [" | ", " - ", " — ", " – ", " : ", " · ", " / "]:
        if sep in t:
            t = t.split(sep, 1)[0].strip()
    # trim trailing bracket parts
    for b in ["(", "[", "{"]:
        if b in t:
            t = t.split(b, 1)[0].strip()
    # remove leading bullets
    t = t.lstrip("-•*· ").strip()
    return t


def _build_candidates_from_description(video_id: str, lines: List[str]) -> List[dict]:
    """Build strong candidates from description chapters.

    NOTE:
    - Day inference is handled in Step2-1 (LLM-day).
    - Step2 should not assign day from chapter titles. Here we keep only seconds + stable order,
      and set day=1 for all candidates.
    """
    candidates: List[dict] = []
    order = 0

    for ln in lines:
        m = _CHAPTER_RE.match(ln)
        if not m:
            continue
        ts = m.group("ts")
        title_part = m.group("title")

        # Extract day hint from chapter titles (e.g., "2일차", "Day 2") but do NOT assign day here.
        clean_title, day_hint = _strip_day_token(title_part)
        sec = _ts_to_seconds(ts)

        place_name = _guess_place_name_from_chapter_title(clean_title)
        if not place_name:
            continue

        # Drop obvious non-place chapter titles
        if place_name in _DESC_NON_PLACE_EXACT:
            continue
        if _URL_LIKE_RE.search(place_name):
            continue

        order += 1
        candidates.append(
            {
                "video_id": video_id,
                "day": 1,
                "order": order,
                "seconds": sec,
                "place_name": place_name,
                "original_phrase": ln,
                "category": "",  # Step3/네이버에서 보강
                "visit_confidence": "high",
                "visit_reason": "description chapters",
                "source": "description",
                "region_tag": "",
                "video_title": "",
                "source_weight": 3,
                "candidate_strength": "description",
                "seconds_source": "description",
                "seconds_evidence": {
                    "chapter_ts": ts,
                    "chapter_seconds": sec,
                    "chapter_line": ln,
                    "chapter_title_raw": title_part,
                    "chapter_title_clean": clean_title,
                    "day_hint": day_hint,
                },
            }
        )

    return candidates


#
# === VTT cues helpers ===
def _load_vtt_cues(path_str: str) -> List[Dict[str, Any]]:
    """Load cues JSON saved by Step1.

    Expected format: {"video_id":..., "title":..., "cues": [{"start":..., "end":..., "text":...}, ...]}
    """
    p = (path_str or "").strip()
    if not p:
        return []
    try:
        with open(p, "r", encoding="utf-8") as f:
            obj = json.load(f)
        cues = (obj or {}).get("cues") or []
        if isinstance(cues, list):
            # keep only well-formed entries
            out: List[Dict[str, Any]] = []
            for c in cues:
                if not isinstance(c, dict):
                    continue
                if "start" not in c or "text" not in c:
                    continue
                out.append(c)
            return out
    except Exception:
        return []
    return []




def _norm_for_cue_match(s: str) -> str:
    s = (s or "").lower()
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"[^0-9a-z가-힣]+", "", s)
    return s.strip()


def _find_seconds_from_cues(place_name: str, cues: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Find earliest cue where cue text contains place_name (case-insensitive, normalized).

    Returns a dict:
      {"seconds": int, "cue_index": int, "cue_start": float, "cue_end": float}
    If not found, returns {"seconds": 0}.
    """
    name = (place_name or "").strip()
    if not name or not cues:
        return {"seconds": 0}

    # Normalize for robust matching (handles spacing/punctuation/emoji-stripped names)
    n0 = _norm_for_cue_match(name)
    # Avoid too-short matches (reduce false positives)
    if len(n0) < 3:
        return {"seconds": 0}

    for idx, c in enumerate(cues):
        try:
            txt = str(c.get("text") or "")
            if not txt:
                continue
            t0 = _norm_for_cue_match(txt)
            if not t0:
                continue
            if n0 in t0:
                start = c.get("start")
                end = c.get("end")
                try:
                    sec_int = int(float(start))
                except Exception:
                    sec_int = 0
                if sec_int <= 0:
                    continue
                return {
                    "seconds": sec_int,
                    "cue_index": idx,
                    "cue_start": float(start) if start is not None else 0.0,
                    "cue_end": float(end) if end is not None else 0.0,
                }
        except Exception:
            continue

    return {"seconds": 0}


def _mention_index(transcript: str, place_name: str) -> int:
    """Find first occurrence index of place_name inside transcript (case-insensitive).

    Returns a large number if not found.
    """
    t = (transcript or "")
    n = (place_name or "").strip()
    if not t or not n:
        return 10**12
    idx = t.lower().find(n.lower())
    return idx if idx >= 0 else 10**12


# === Day inference helpers (LLM1-1 replacement / heuristic) ===
_DAY_WORDS = {
    "첫째": 1,
    "둘째": 2,
    "셋째": 3,
    "넷째": 4,
    "다섯째": 5,
    "여섯째": 6,
    "일곱째": 7,
    "여덟째": 8,
    "아홉째": 9,
    "열째": 10,
}

_DAY_MARKER_RE = re.compile(
    r"(?:(?P<num>[1-9]\d?)\s*일\s*차|day\s*(?P<day>[1-9]\d?)|(?P<word>첫째|둘째|셋째|넷째|다섯째|여섯째|일곱째|여덟째|아홉째|열째)\s*날)",
    re.IGNORECASE,
)


def _extract_day_markers(transcript: str) -> List[Dict[str, Any]]:
    """Return ordered list of day markers: [{"idx": int, "day": int, "match": str}]"""
    t = transcript or ""
    if not t:
        return []

    markers: List[Dict[str, Any]] = []
    for m in _DAY_MARKER_RE.finditer(t):
        day = 0
        try:
            if m.group("num"):
                day = int(m.group("num"))
            elif m.group("day"):
                day = int(m.group("day"))
            elif m.group("word"):
                day = int(_DAY_WORDS.get(m.group("word"), 0))
        except Exception:
            day = 0
        if day <= 0:
            continue
        markers.append({"idx": m.start(), "day": day, "match": m.group(0)})

    # de-dup consecutive same-day markers
    dedup: List[Dict[str, Any]] = []
    last_day = None
    for x in sorted(markers, key=lambda d: d["idx"]):
        if last_day == x["day"]:
            continue
        dedup.append(x)
        last_day = x["day"]

    return dedup


def _infer_day_from_markers(markers: List[Dict[str, Any]], mention_idx: int) -> int:
    """Pick the latest marker before mention_idx."""
    if not markers:
        return 0
    day = 0
    for m in markers:
        if mention_idx >= int(m.get("idx") or 0):
            day = int(m.get("day") or 0)
        else:
            break
    return day


def run(materials: List[dict]) -> Dict[str, List[dict]]:
    """Step2: transcript -> (방문 장소 후보)"""
    data_dir = Path(getattr(config, "DATA_DIR", "data"))
    out_path = data_dir / "step2_places_raw.json"

    # 추가: 영상별 저장 디렉터리 + 요약
    out_dir = data_dir / "step2_places_raw"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary: List[Dict[str, Any]] = []

    if materials is None:
        raise ValueError("step2_build_itinerary_llm.run: materials is required")

    results: Dict[str, List[dict]] = {}

    enable = bool(getattr(config, "ENABLE_GEMINI", True))
    if not enable:
        log("step2", "ENABLE_GEMINI=False; skipping")
        save_json(out_path, results)
        save_json(out_dir / "_summary.json", summary)
        return results

    total_videos = len(materials)

    for video_idx, item in enumerate(materials, 1):
        video_id = item.get("video_id")
        title = (item.get("title") or "").strip()
        transcript = item.get("transcript") or ""
        description = (item.get("description") or "").strip()
        if not video_id:
            continue

        # 영상 처리 시작 로그(타이틀 포함, idx/total/region 추가)
        region_tag = (item.get("region_tag") or "").strip()
        log(
            "step2",
            "video",
            video_id=video_id,
            title=title or None,
            idx=f"{video_idx}/{total_videos}",
            region=region_tag or None,
        )

        transcript_len = len(transcript)

        # Step1에서 저장된 VTT cues(자막 타임스탬프) 로드: 있으면 seconds 보강에 사용
        vtt_cues_path = (item.get("vtt_cues_path") or "").strip()
        vtt_cues = _load_vtt_cues(vtt_cues_path)

        # transcript가 비면: 결과 0개로 기록 + 영상별 파일도 남김(디버깅용)
        if not transcript.strip():
            empty_payload = {
                "meta": {
                    "video_id": video_id,
                    "title": title,
                    "idx": video_idx,
                    "total": total_videos,
                    "transcript_len": transcript_len,
                    "chunks": 0,
                    "region_tag": region_tag,
                    "note": "empty_transcript",
                },
                "places": [],
            }
            save_json(out_dir / f"places_raw_{video_id}.json", empty_payload)
            summary.append(
                {
                    "video_id": video_id,
                    "title": title,
                    "transcript_len": transcript_len,
                    "chunks": 0,
                    "region_tag": region_tag,
                    "count": 0,
                    "note": "empty_transcript",
                }
            )
            results[video_id] = []
            continue

        # (A) description chapters -> strong candidates (seconds/day/order)
        marker_present = _DESC_MARKER in transcript
        chapter_lines = _extract_description_chapter_lines(transcript)
        chapter_candidates = _build_candidates_from_description(video_id, chapter_lines) if chapter_lines else []

        # Build LLM header context so title/description/chapters are visible to the model
        ctx_parts: List[str] = []
        if title:
            ctx_parts.append("[TITLE]\n" + title)
        if description:
            ctx_parts.append("[DESCRIPTION]\n" + description[:2000])
        if chapter_lines:
            ctx_parts.append("[DESCRIPTION_CHAPTERS]\n" + "\n".join(chapter_lines[:80]))
        llm_header = "\n\n".join(ctx_parts).strip()

        # 챕터 디버그 파일(항상 저장): 챕터가 없거나 파싱 실패해도 원인 확인 가능
        save_json(
            out_dir / f"chapters_{video_id}.json",
            {
                "meta": {
                    "video_id": video_id,
                    "title": title,
                    "region_tag": region_tag,
                    "marker_present": marker_present,
                    "desc_chapter_lines": len(chapter_lines),
                    "desc_chapter_candidates": len(chapter_candidates),
                },
                "chapter_lines": chapter_lines,
                "chapter_candidates": chapter_candidates,
            },
        )

        if chapter_candidates:
            log(
                "step2",
                "desc_chapters",
                video_id=video_id,
                title=title or None,
                idx=f"{video_idx}/{total_videos}",
                region=region_tag or None,
                count=len(chapter_candidates),
            )

        # LLM에는 챕터 섹션을 제외한 본문을 우선 전달(중복/노이즈 감소)
        transcript_for_llm = transcript
        if _DESC_MARKER in transcript:
            base = transcript.split(_DESC_MARKER, 1)[0].strip()
            if base:
                transcript_for_llm = base

        transcript_for_order = transcript_for_llm
        chunks = chunk_text(transcript_for_llm, max_chars=2500, overlap=120)

        collected: List[dict] = []
        if chapter_candidates:
            collected.extend(chapter_candidates)
            # Fill meta for description candidates
            for _p in chapter_candidates:
                _p["region_tag"] = region_tag
                _p["video_title"] = title

        # ✅ title/description seed candidates (must_keep)
        seed_candidates = _build_seed_candidates(video_id, title, description, region_tag)
        if seed_candidates:
            collected.extend(seed_candidates)

        for i, chunk in enumerate(chunks):
            log(
                "llm",
                "normalize chunk",
                video_id=video_id,
                title=title or None,
                idx=f"{video_idx}/{total_videos}",
                chunk=f"{i+1}/{len(chunks)}",
            )
            try:
                places = normalize_places_from_text(
                    video_id=video_id,
                    text=(llm_header + "\n\n[TRANSCRIPT_CHUNK]\n" + chunk) if llm_header else chunk,
                    region_hint=region_tag,
                )
                if isinstance(places, list):
                    # Attach meta for downstream steps
                    for _p in places:
                        if isinstance(_p, dict):
                            _p.setdefault("region_tag", region_tag)
                            _p.setdefault("video_title", title)
                    collected.extend(places)
            except Exception as e:
                log("step2", "chunk error", video_id=video_id, err=str(e)[:200])

        # 기본 가중치 부여: description 후보(3) > 기타(1)
        for p in collected:
            if "source_weight" not in p:
                p["source_weight"] = 3 if (p.get("source") == "description") else 1
            p.setdefault("candidate_strength", p.get("source") or "llm")

        # (B0) Canonicalize place names early to reduce duplicates and improve VTT cue matching.
        # Store raw name for traceability.
        for p in collected:
            try:
                raw = (p.get("place_name") or "").strip()
                if raw and "place_name_raw" not in p:
                    p["place_name_raw"] = raw
                clean_name, key = _canonicalize_place_name(raw)
                if clean_name:
                    p["place_name"] = clean_name
                if key:
                    p["_place_key"] = key
            except Exception:
                continue

        # (B) yt-dlp 자막 cues가 있으면 seconds=0 후보를 시간으로 보강
        seconds_filled_from_vtt = 0
        if vtt_cues:
            sec_cache: Dict[str, Any] = {}
            for p in collected:
                try:
                    cur_sec = int(p.get("seconds") or 0)
                except Exception:
                    cur_sec = 0
                if cur_sec != 0:
                    continue
                name = (p.get("place_name") or "").strip()
                if not name:
                    continue
                if name not in sec_cache:
                    sec_cache[name] = _find_seconds_from_cues(name, vtt_cues)
                ev = sec_cache[name]
                sec = int(ev.get("seconds") or 0)
                if sec > 0:
                    p["seconds"] = sec
                    p["seconds_evidence"] = {
                        "cue_index": int(ev.get("cue_index") or 0),
                        "cue_start": float(ev.get("cue_start") or 0.0),
                        "cue_end": float(ev.get("cue_end") or 0.0),
                    }
                    # 디버깅/추적용
                    p["seconds_source"] = "vtt"
                    vr = (p.get("visit_reason") or "").strip()
                    p["visit_reason"] = (vr + "; vtt_cue_match").strip("; ")
                    seconds_filled_from_vtt += 1

            log(
                "step2",
                "vtt_cues",
                video_id=video_id,
                title=title or None,
                idx=f"{video_idx}/{total_videos}",
                region=region_tag or None,
                cues=len(vtt_cues),
                filled=seconds_filled_from_vtt,
            )

        # (C) Whisper/텍스트 기반 영상용: seconds가 없는 후보는 언급 순서(mention index)로 정렬 보조
        for p in collected:
            try:
                cur_sec = int(p.get("seconds") or 0)
            except Exception:
                cur_sec = 0
            if cur_sec == 0:
                p["_mention_idx"] = _mention_index(transcript_for_order, p.get("place_name") or "")
            else:
                p["_mention_idx"] = 0


        # (D) 구체 상호/지명이 아닌 일반어 후보 제거 (특히 yt-dlp/whisper 텍스트가 빈약한 영상에서 0개 방지용)
        dropped_generic = 0
        filtered_collected: List[dict] = []
        for p in collected:
            pn = (p.get("place_name") or "").strip()

            # ✅ must_keep candidates: keep only if they still look like a place.
            #    (Seeds from title/description should NOT force-keep obvious non-places like "vlog" or sentences.)
            if p.get("must_keep"):
                if _is_generic_place_name(pn):
                    # Drop generic must_keep seeds; keep non-seed must_keep if any exist in future.
                    if p.get("candidate_strength") == "seed":
                        dropped_generic += 1
                        continue
                    p["is_generic"] = True
                filtered_collected.append(p)
                continue

            if _is_generic_place_name(pn):
                # Do NOT drop description-derived candidates; keep them but mark as generic.
                if p.get("source") == "description":
                    p["is_generic"] = True
                    filtered_collected.append(p)
                    continue

                dropped_generic += 1
                continue

            filtered_collected.append(p)
        if dropped_generic:
            log(
                "step2",
                "drop_generic",
                video_id=video_id,
                title=title or None,
                idx=f"{video_idx}/{total_videos}",
                region=region_tag or None,
                dropped=dropped_generic,
                kept=len(filtered_collected),
            )
        collected = filtered_collected

        # 중복 제거 + day/order 재정렬
        seen = set()
        merged: List[dict] = []
        for p in collected:
            place_name = (p.get("place_name") or "").strip()
            if not place_name:
                continue
            day = 1
            sec = int(p.get("seconds") or 0)
            # 같은 day/place라도 서로 다른 seconds면 유지
            place_key = (p.get("_place_key") or place_name).strip()
            key = (day, place_key, sec)
            if key in seen:
                continue
            seen.add(key)
            p["day"] = day
            p["seconds"] = sec
            merged.append(p)

        # day별로 seconds 우선 정렬하고 order를 1..N으로 재부여
        by_day: Dict[int, List[dict]] = {}
        for p in merged:
            by_day.setdefault(int(p.get("day") or 1), []).append(p)

        uniq: List[dict] = []
        for day in sorted(by_day.keys()):
            items = by_day[day]
            # seconds가 0인 것은 뒤로; mention_idx 반영, 설명란 후보 우선
            items.sort(
                key=lambda x: (
                    int(x.get("seconds") or 0) == 0,
                    int(x.get("seconds") or 0),
                    -int(x.get("source_weight") or 1),
                    int(x.get("_mention_idx") or 10**12),
                    int(x.get("order") or 10**9),
                )
            )
            # 동일 place_name 중복 압축
            compact: List[dict] = []
            for cand in items:
                pn = (cand.get("place_name") or "").strip()
                if not pn:
                    continue

                sec = int(cand.get("seconds") or 0)
                sw = int(cand.get("source_weight") or 1)

                # 이미 같은 place가 있으면 비교
                replaced = False
                for j, kept in enumerate(compact):
                    kept_key = (kept.get("_place_key") or (kept.get("place_name") or "")).strip()
                    cand_key = (cand.get("_place_key") or pn).strip()
                    if kept_key != cand_key:
                        continue

                    kept_sec = int(kept.get("seconds") or 0)
                    kept_sw = int(kept.get("source_weight") or 1)

                    # seconds 있는 게 우선
                    if kept_sec == 0 and sec > 0:
                        compact[j] = cand
                        replaced = True
                        break
                    if kept_sec > 0 and sec == 0:
                        replaced = True
                        break

                    # 둘 다 seconds>0 이면, 아주 근접(<=20s)하면 더 강한 후보만 유지
                    if kept_sec > 0 and sec > 0 and abs(kept_sec - sec) <= 20:
                        if sw > kept_sw:
                            compact[j] = cand
                        replaced = True
                        break

                if not replaced:
                    compact.append(cand)

            items = compact
            for order_idx, p in enumerate(items, start=1):
                p["order"] = order_idx
                if "_mention_idx" in p:
                    p.pop("_mention_idx", None)
                if "_place_key" in p:
                    p.pop("_place_key", None)
                uniq.append(p)

        results[video_id] = uniq
        log(
            "step2",
            "places_raw",
            video_id=video_id,
            title=title or None,
            idx=f"{video_idx}/{total_videos}",
            region=region_tag or None,
            count=len(uniq),
        )

        # 영상별 저장 + summary 누적
        meta = {
            "video_id": video_id,
            "title": title,
            "idx": video_idx,
            "total": total_videos,
            "transcript_len": transcript_len,
            "chunks": len(chunks),
            "region_tag": region_tag,
            "marker_present": marker_present,
            "desc_chapter_lines": len(chapter_lines),
            "desc_chapter_candidates": len(chapter_candidates),
            "vtt_cues_path": vtt_cues_path,
            "vtt_cues_count": len(vtt_cues),
            "seconds_filled_from_vtt": seconds_filled_from_vtt,
            "dropped_generic": dropped_generic,
        }
        save_json(out_dir / f"places_raw_{video_id}.json", {"meta": meta, "places": uniq})
        summary.append({**meta, "count": len(uniq)})

    save_json(out_path, results)
    save_json(out_dir / "_summary.json", summary)
    log("step2", "saved", path=str(out_path), videos=len(results))
    return results