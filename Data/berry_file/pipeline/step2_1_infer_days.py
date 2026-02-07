from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import json
import os
import re

import config
from utils.io import save_json
from utils.logging_utils import log



_DESC_MARKER = "[DESCRIPTION_CHAPTERS]"

# --- Helper functions for day marker extraction ---
def _ts_to_seconds(ts: str) -> Optional[float]:
    """Parse timestamps like HH:MM:SS or MM:SS into seconds."""
    if not ts:
        return None
    ts = ts.strip()
    m = re.match(r"^(?:(\d{1,2}):)?(\d{1,2}):(\d{2})$", ts)
    if not m:
        return None
    h = m.group(1)
    mm = m.group(2)
    ss = m.group(3)
    try:
        hh = int(h) if h is not None else 0
        mi = int(mm)
        se = int(ss)
    except Exception:
        return None
    return float(hh * 3600 + mi * 60 + se)


def _extract_day_from_text(text: str) -> Optional[int]:
    """Extract explicit day number from text (e.g., '2일차', 'Day 3', '둘째날')."""
    if not text:
        return None
    t = text.strip()

    # 1) N일차
    m = re.search(r"(\d+)\s*일\s*차", t)
    if m:
        try:
            d = int(m.group(1))
            return d if d > 0 else None
        except Exception:
            return None

    # 2) Day N
    m = re.search(r"\bday\s*(\d+)\b", t, flags=re.IGNORECASE)
    if m:
        try:
            d = int(m.group(1))
            return d if d > 0 else None
        except Exception:
            return None

    # 3) 첫째/둘째/셋째/...
    ord_map = {"첫째": 1, "둘째": 2, "셋째": 3, "넷째": 4, "다섯째": 5, "여섯째": 6, "일곱째": 7}
    m = re.search(r"(첫째|둘째|셋째|넷째|다섯째|여섯째|일곱째)\s*(?:날|째\s*날)", t)
    if m:
        return ord_map.get(m.group(1))

    return None


# --- Helper: Only accept explicit travel-day expressions, not episode/part numbers ---
def _is_valid_day_evidence(evidence: str, day: int) -> bool:
    """Return True only when evidence is an explicit *travel day* expression.

    This blocks common false-positives like episode/part/vlog numbers (e.g., "Vlog 6", "EP.02").
    """
    if not evidence or day <= 0:
        return False

    ev = evidence.strip()

    # If it looks like an episode/part label, reject unless it also contains an explicit day expression.
    # Examples to reject: "Vlog 6", "VLOG #066", "EP.02", "Episode 2", "Part 3", "2편".
    episode_like = bool(
        re.search(r"\b(vlog|ep\.?|episode|part)\s*#?\s*\d+\b", ev, flags=re.IGNORECASE)
        or re.search(r"\b\d+\s*(편|화|부)\b", ev)
    )

    extracted = _extract_day_from_text(ev)

    # Must be a day expression that maps to the same day.
    if extracted is None or int(extracted) != int(day):
        return False

    # If it is episode-like but also contains an explicit day expression (e.g., "Day 2"), allow.
    if episode_like:
        explicit_day = bool(
            re.search(r"\d+\s*일\s*차", ev)
            or re.search(r"\bday\s*\d+\b", ev, flags=re.IGNORECASE)
            or re.search(r"(첫째|둘째|셋째|넷째|다섯째|여섯째|일곱째)\s*(?:날|째\s*날)", ev)
        )
        return explicit_day

    return True


def _extract_time_and_day_from_line(line: str) -> Optional[Dict[str, Any]]:
    """Try to parse a description/chapter line into {time_sec, day, evidence}."""
    if not line:
        return None
    l = line.strip()
    # Find the first timestamp token
    tm = re.search(r"\b(\d{1,2}:\d{2}(?::\d{2})?)\b", l)
    if not tm:
        return None
    sec = _ts_to_seconds(tm.group(1))
    if sec is None:
        return None

    day = _extract_day_from_text(l)
    if day is None:
        return None

    # Evidence: extract an explicit day substring from the same line.
    # (Avoid using only timestamps as evidence.)
    ev = None
    day_pat = re.compile(
        r"(\d+\s*일\s*차|\d+\s*일차|\bday\s*\d+\b|\d+\s*일\s*째|\d+\s*일째|"
        r"첫째\s*(?:날|째\s*날)|둘째\s*(?:날|째\s*날)|셋째\s*(?:날|째\s*날)|넷째\s*(?:날|째\s*날)|"
        r"다섯째\s*(?:날|째\s*날)|여섯째\s*(?:날|째\s*날)|일곱째\s*(?:날|째\s*날)|"
        r"첫째날|둘째날|셋째날|넷째날|다섯째날|여섯째날|일곱째날)",
        flags=re.IGNORECASE,
    )
    m = day_pat.search(l)
    if m:
        ev = m.group(0)
    else:
        # Last resort (should be rare): keep timestamp.
        ev = tm.group(1)

    return {"time_sec": float(sec), "day": int(day), "evidence": ev, "line": l[:200]}


def _load_chapter_markers(data_dir: Path, video_id: str) -> List[Dict[str, Any]]:
    """Load chapter markers saved by step2 (if present)."""
    markers: List[Dict[str, Any]] = []
    # Typical location in this project
    p = data_dir / "step2_places_raw" / f"chapters_{video_id}.json"
    if not p.exists():
        return markers
    try:
        obj = json.loads(p.read_text(encoding="utf-8", errors="ignore"))
    except Exception:
        return markers

    # Accept common shapes:
    # {"chapters": [{"start": 12.3, "title": "2일차 ..."}, ...]}
    chapters = obj.get("chapters") if isinstance(obj, dict) else None
    if not isinstance(chapters, list):
        return markers

    for ch in chapters:
        if not isinstance(ch, dict):
            continue
        title = (ch.get("title") or "").strip()
        day = _extract_day_from_text(title)
        if day is None:
            continue
        st = ch.get("start")
        if isinstance(st, (int, float)):
            markers.append({"day": int(day), "evidence": title[:80] or "chapter", "source": "chapter", "time_sec": float(st)})

    return markers


def _extract_cue_markers(cues: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """Extract explicit day markers directly from cue texts with time_sec."""
    out: List[Dict[str, Any]] = []
    if not cues:
        return out

    # Match explicit day expressions
    pat = re.compile(r"(\d+\s*일\s*차|\bday\s*\d+\b|첫째\s*(?:날|째\s*날)|둘째\s*(?:날|째\s*날)|셋째\s*(?:날|째\s*날)|넷째\s*(?:날|째\s*날)|다섯째\s*(?:날|째\s*날)|여섯째\s*(?:날|째\s*날)|일곱째\s*(?:날|째\s*날))",
                      flags=re.IGNORECASE)

    for c in cues:
        if not isinstance(c, dict):
            continue
        txt = (c.get("text") or "")
        st = c.get("start")
        if not isinstance(st, (int, float)):
            continue
        m = pat.search(txt)
        if not m:
            continue
        ev = m.group(1)
        day = _extract_day_from_text(ev)
        if day is None:
            continue
        out.append({"day": int(day), "evidence": ev.strip(), "source": "cue", "time_sec": float(st)})

    # Dedup by (day, rounded_time)
    seen = set()
    dedup: List[Dict[str, Any]] = []
    for m in sorted(out, key=lambda x: (float(x.get("time_sec") or 0), int(x.get("day") or 0))):
        k = (int(m.get("day") or 0), int(float(m.get("time_sec") or 0) // 5))
        if k in seen:
            continue
        seen.add(k)
        dedup.append(m)
    return dedup


def _merge_markers(*marker_lists: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Merge markers preferring those with time_sec, keep evidence/source when available."""
    merged: List[Dict[str, Any]] = []
    for lst in marker_lists:
        for m in lst or []:
            if not isinstance(m, dict):
                continue
            try:
                day = int(m.get("day") or 0)
            except Exception:
                day = 0
            evidence = (m.get("evidence") or "").strip()
            if day <= 0 or not evidence:
                continue
            mm: Dict[str, Any] = {"day": day, "evidence": evidence}
            src = (m.get("source") or "").strip()
            if src:
                mm["source"] = src
            ts = m.get("time_sec")
            if isinstance(ts, (int, float)):
                mm["time_sec"] = float(ts)
            merged.append(mm)

    # Prefer markers with time_sec, then by time
    merged.sort(key=lambda x: (0 if isinstance(x.get("time_sec"), (int, float)) else 1, float(x.get("time_sec") or 0), int(x.get("day") or 0)))

    seen = set()
    out: List[Dict[str, Any]] = []
    for m in merged:
        d = int(m["day"])
        t = m.get("time_sec")
        bucket = int(float(t) // 5) if isinstance(t, (int, float)) else None
        k = (d, bucket, m["evidence"].lower())
        if k in seen:
            continue
        seen.add(k)
        out.append(m)

    return out


def _fill_seconds_from_cues(place: Dict[str, Any], cues: Optional[List[Dict[str, Any]]]) -> Optional[int]:
    """Try to assign place['seconds'] from cues by matching original_phrase then place_name."""
    if not cues or not isinstance(place, dict):
        return None

    # If already has seconds > 0, keep it
    try:
        cur = int(place.get("seconds") or 0)
    except Exception:
        cur = 0
    if cur > 0:
        return cur

    # Candidate needles
    needles: List[str] = []
    op = (place.get("original_phrase") or "").strip()
    if op:
        needles.append(op)
    pn = (place.get("place_name") or "").strip()
    if pn and pn not in needles:
        needles.append(pn)

    def norm(s: str) -> str:
        s = s.lower()
        s = re.sub(r"<[^>]+>", " ", s)  # strip vtt tags
        s = re.sub(r"[^0-9a-z가-힣]+", " ", s)
        return re.sub(r"\s+", " ", s).strip()

    needles_n = [norm(n) for n in needles if n]
    if not needles_n:
        return None

    best: Optional[float] = None
    for c in cues:
        if not isinstance(c, dict):
            continue
        st = c.get("start")
        if not isinstance(st, (int, float)):
            continue
        txt = norm(c.get("text") or "")
        if not txt:
            continue
        for nn in needles_n:
            # Require a meaningful needle length to avoid matching common words
            if len(nn) < 3:
                continue
            if nn in txt:
                if best is None or float(st) < best:
                    best = float(st)
                break

    if best is None:
        return None

    return int(best)


def _extract_json_obj(s: str) -> Optional[dict]:
    """LLM 출력에서 JSON 객체 1개를 최대한 견고하게 추출."""
    if not s:
        return None
    s = s.strip()

    # 1) 그대로 파싱
    try:
        obj = json.loads(s)
        return obj if isinstance(obj, dict) else None
    except Exception:
        pass

    # 2) 첫 { ... } 블록 파싱
    m = re.search(r"\{[\s\S]*\}", s)
    if not m:
        return None
    try:
        obj = json.loads(m.group(0))
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def _call_gemini(prompt: str, model: str) -> str:
    """google-genai SDK로 Gemini 호출(지연 import)."""
    api_key = (os.getenv("GEMINI_API_KEY") or getattr(config, "GEMINI_API_KEY", "") or "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing")

    # NOTE: Pylance에서 google 패키지 import 경고가 뜰 수 있으나,
    # 실제 실행 환경에 `google-genai`가 설치되어 있으면 정상 동작합니다.
    try:
        from google import genai  # type: ignore
    except Exception as e:
        raise RuntimeError(f"google-genai not installed: {e}. Try: pip install google-genai")

    client = genai.Client(api_key=api_key)
    resp = client.models.generate_content(model=model, contents=prompt)
    return getattr(resp, "text", "") or ""


def infer_day_markers_from_transcript(
    *,
    video_id: str,
    title: str,
    description: str,
    transcript: str,
    transcript_source: str,
    yt_vtt: Optional[str] = None,
    whisper_text: Optional[str] = None,
    cues: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """대본에서 '여행 일차(day) 구분'만 추출.

    반환(JSON):
      {
        "trip_type": "single_day"|"multi_day"|"unknown",
        "start_day": 1,
        "markers": [{"day": 2, "evidence": "2일차", "source": "transcript|description|title|cue", "time_sec": 123.4}, ...],
        "notes": "..."
      }

    - evidence는 transcript에 실제로 존재하는 문자열이어야 함.
    - 장소명/상호/지명은 절대 추출하지 않음.
    """

    model = (
        getattr(config, "GEMINI_DAY_MODEL", None)
        or getattr(config, "GEMINI_MODEL", None)
        or os.getenv("GEMINI_MODEL")
        or "gemini-2.5-flash"
    )
    model = str(model).strip()

    base = (transcript or "").strip()
    desc = (description or "").strip()
    src = (transcript_source or "").strip()

    # transcript 안에 description 챕터가 붙는 구조도 있고 아닐 수도 있음
    desc_chapters = ""
    if _DESC_MARKER in base:
        before, after = base.split(_DESC_MARKER, 1)
        base = (before or "").strip()
        desc_chapters = (after or "").strip()

    # --- 빠른 규칙 기반 시그널 추출(LLM 보조) ---
    # 목표: "여행 일차" 판별 안정성 최우선
    # - 제목/설명에 '당일치기/0박1일'이 명시되면 description chapter에 Day 2/3가 섞여 있어도 'single_day'로 고정
    # - 'N박M일' 패턴이 명시되면 'multi_day'로 고정

    single_kw = [
        "당일치기",
        "당일",
        "당일코스",
        "당일 코스",
        "0박1일",
        "0박 1일",
        "원데이",
        "원데이투어",
        "원데이 투어",
        "당일여행",
        "당일 여행",
        "daytrip",
        "day trip",
        "day-trip",
        "one day",
        "one-day",
    ]

    # 'N박M일' 또는 숙박/여정 표현(멀티데이)
    multi_kw = [
        "숙박",
        "연박",
        "1박",
        "2박",
        "3박",
        "4박",
        "5박",
        "1박2일",
        "1박 2일",
        "2박3일",
        "2박 3일",
        "3박4일",
        "3박 4일",
        "4박5일",
        "4박 5일",
    ]

    # 원문(대소문/표기 유지) 기반 텍스트
    text_all_raw = "\n".join([title or "", desc or "", desc_chapters or "", base or ""]).strip()
    text_all = text_all_raw.lower()

    # 제목에 명시된 신호는 최우선(설명란 day1/day2가 '일상 브이로그 day1~'로 섞이는 케이스 방지)
    title_l = (title or "").lower()
    title_single_hit = any(k.lower() in title_l for k in single_kw)
    title_multi_hit = any(k.lower() in title_l for k in multi_kw)

    single_hit = title_single_hit or any(k.lower() in text_all for k in single_kw)

    # multi_hit은 너무 광범위하면 오탐이 생길 수 있으므로, 정규식으로 'N박M일'을 먼저 보고
    # 그 다음에 보조적으로 키워드를 반영
    nights_days_re = re.search(r"(\d+)\s*박\s*(\d+)\s*일", text_all_raw)

    def _expected_trip_days(txt: str) -> Optional[int]:
        """제목/설명/대본에서 '예상 여행 일수'를 최대한 보수적으로 추정."""
        raw = (txt or "").strip()
        if not raw:
            return None
        low = raw.lower()

        # 1) 당일치기/0박1일 계열
        if re.search(r"당일치기|0\s*박\s*1\s*일|원데이|day\s*trip|day-trip|daytrip|one\s*day|one-day", low):
            return 1

        # 2) N박M일 계열 (M이 일수)
        m = re.search(r"(\d+)\s*박\s*(\d+)\s*일", raw)
        if m:
            try:
                m_days = int(m.group(2))
                return m_days if m_days > 0 else None
            except Exception:
                return None

        # 3) N박만 있는 경우는 (N+1)일로 추정 (보수적)
        m = re.search(r"(\d+)\s*박", raw)
        if m:
            try:
                n = int(m.group(1))
                return (n + 1) if n > 0 else None
            except Exception:
                return None

        return None

    # Strongest trip-length signal should come from title/description only.
    # (Transcript/chapters can contain misleading "Day 2" like EP/Part labels or unrelated captions.)
    expected_days_primary = _expected_trip_days("\n".join([title or "", desc or ""]))
    expected_days_secondary = _expected_trip_days(text_all_raw)

    # Primary wins when available
    expected_days = expected_days_primary if expected_days_primary is not None else expected_days_secondary

    multi_hit = title_multi_hit or (nights_days_re is not None) or any(k.lower() in text_all for k in multi_kw)

    # expected_days가 명확하면, hit 판단보다 우선
    if expected_days == 1:
        single_hit = True
        multi_hit = False
    elif isinstance(expected_days, int) and expected_days >= 2:
        multi_hit = True

    # day 마커 후보(문자열)
    day_marker_patterns = [
        r"(\d+)\s*일\s*차",
        r"(\d+)\s*일차",
        r"(\d+)\s*일\s*째",
        r"(\d+)\s*일째",
        r"day\s*(\d+)",
        r"(첫째|둘째|셋째|넷째|다섯째|여섯째|일곱째)\s*날",
        r"(첫째|둘째|셋째|넷째|다섯째|여섯째|일곱째)\s*째\s*날",
        r"(첫날|둘째날|셋째날|넷째날|다섯째날|여섯째날|일곱째날)",
    ]

    ordinal_map = {"첫째": 1, "둘째": 2, "셋째": 3, "넷째": 4, "다섯째": 5, "여섯째": 6, "일곱째": 7}

    raw_markers: List[Dict[str, Any]] = []
    for pat in day_marker_patterns:
        for m in re.finditer(pat, text_all, flags=re.IGNORECASE):
            g = m.group(1)
            day = 0
            if g is None:
                continue
            if g.isdigit():
                day = int(g)
            else:
                day = int(ordinal_map.get(g, 0))
            if day > 0:
                ev = m.group(0)
                raw_markers.append({"day": day, "evidence": ev})

    # description/chapter timestamp lines (parse for markers)
    ts_items: List[Dict[str, Any]] = []
    for line in (desc + "\n" + desc_chapters).splitlines():
        l = line.strip()
        if not l:
            continue
        item = _extract_time_and_day_from_line(l)
        if item:
            ts_items.append(item)

    # Keep a short list of raw lines for prompt readability
    ts_lines: List[str] = [x.get("line") for x in ts_items if x.get("line")][:20]

    cue_markers = _extract_cue_markers(cues)

    # cue 기반 day 힌트(프롬프트 표시용)
    cue_hits: List[Dict[str, Any]] = []
    for cm in cue_markers[:50]:
        cue_hits.append({"day": cm.get("day"), "evidence": cm.get("evidence"), "time_sec": cm.get("time_sec")})

    # 비용/안정성: 길이 제한(섹션별 제한)
    # NOTE: day 마커는 후반부에 나오는 경우가 있어 너무 짧게 자르면 누락됩니다.
    #       비용을 고려해 "완전 무제한"은 피하되, 기존보다 충분히 여유를 둡니다.
    base = base[:20000]
    desc = desc[:9000]
    desc_chapters = desc_chapters[:9000]

    # Deterministic markers (to merge with LLM markers later)
    deterministic_markers: List[Dict[str, Any]] = []
    # From description/chapter timestamp lines
    for it in ts_items:
        deterministic_markers.append({"day": int(it["day"]), "evidence": str(it["evidence"]), "source": "description", "time_sec": float(it["time_sec"])})
    # From cues
    deterministic_markers.extend(cue_markers)

    prompt = f"""
너는 여행 브이로그의 메타데이터(제목/설명/자막/Whisper)를 종합해서 '여행 일차(day) 구분'만 판단하는 도구다.
반드시 JSON 객체(단일)만 출력한다. 설명/문장 출력 금지.

[목표]
- 영상이 당일치기인지/다일차 여행인지(trip_type)
- 영상이 여행의 몇 일차부터 시작하는지(start_day)
- 대본/설명에서 확인되는 day 마커 목록(markers)

[중요]
- 장소명(상호/지명) 추출 금지.
- evidence는 원문(제목/설명/자막/챕터라인/자막 cue text)에 실제로 존재하는 문자열을 그대로 반환.
- 'EP.2', 'Episode 2', 'Part 3', 'Vlog 6', '2편' 같은 **시리즈/회차 번호는 여행 일차가 아니다**. 이를 day로 판단하지 마라.

[입력 시그널]
- transcript_source: {src}
- single_hit(당일치기 강신호): {single_hit}
- multi_hit(숙박/다일 신호): {multi_hit}
- description/chapter timestamp lines(최대 20개):
{ts_lines[:20]}
- cue 기반 day 힌트(최대 20개):
{cue_hits[:20]}

[추가 지침]
- markers에는 가능하면 time_sec를 채워라. (cue_hits 또는 timestamp lines에서 시간 추정 가능)
- start_day는 영상이 여행의 몇 일차부터 시작하는지(예: 2일차부터 시작하면 2).

[출력 스키마]
{{
  "trip_type": "single_day"|"multi_day"|"unknown",
  "start_day": 1,
  "markers": [
    {{"day": 2, "evidence": "2일차", "source": "transcript|description|title|cue", "time_sec": 123.4}},
    ...
  ],
  "notes": "optional"
}}

[video_id] {video_id}
[title]
{title}

[description]
{desc}

[description_chapters]
{desc_chapters}

[transcript]
{base}
""".strip()

    raw = _call_gemini(prompt, model=model)
    data = _extract_json_obj(raw)

    if not isinstance(data, dict):
        return {"trip_type": "unknown", "start_day": 1, "markers": [], "notes": "invalid_json"}

    trip_type = (data.get("trip_type") or "unknown").strip()

    # --- Hard override: 규칙 기반 신호가 강하면 LLM보다 우선 ---
    # 1) expected_days가 1이면 무조건 single_day (설명란 day1/day2 섞임 방지)
    # 2) expected_days가 2 이상이면 multi_day 우선
    # 3) 그 외에는 single_hit/multi_hit로 보조 판단

    if expected_days == 1:
        trip_type = "single_day"
        data["start_day"] = 1
        # If it's explicitly a day-trip, ignore any day>1 markers from transcript/chapters.
        data["markers"] = []
        data["notes"] = ((data.get("notes") or "").strip() + " | rule_override:expected_days=1(primary_win)").strip(" |")

    elif isinstance(expected_days, int) and expected_days >= 2:
        trip_type = "multi_day"
        data["notes"] = ((data.get("notes") or "").strip() + f" | rule_override:expected_days={expected_days}").strip(" |")

    else:
        # single_hit && !multi_hit  -> single_day 확정
        if single_hit and not multi_hit:
            trip_type = "single_day"
            data["start_day"] = 1
            data["notes"] = ((data.get("notes") or "").strip() + " | rule_override:single").strip(" |")
        elif multi_hit:
            trip_type = "multi_day"
            if single_hit:
                data["notes"] = ((data.get("notes") or "").strip() + " | rule_override:multi_conflict").strip(" |")
            else:
                data["notes"] = ((data.get("notes") or "").strip() + " | rule_override:multi").strip(" |")

    # start_day 보정
    try:
        start_day = int(data.get("start_day") or 1)
    except Exception:
        start_day = 1
    if start_day <= 0:
        start_day = 1

    markers = data.get("markers")
    if not isinstance(markers, list):
        markers = []

    cleaned: List[Dict[str, Any]] = []
    for m in markers:
        if not isinstance(m, dict):
            continue
        try:
            day = int(m.get("day") or 0)
        except Exception:
            day = 0
        evidence = (m.get("evidence") or "").strip()
        if day <= 0 or not evidence:
            continue
        # Guard: accept only explicit travel-day evidence (blocks EP/Vlog numbers)
        if not _is_valid_day_evidence(evidence, day):
            continue
        out_m: Dict[str, Any] = {"day": day, "evidence": evidence}
        src_m = (m.get("source") or "").strip()
        if src_m:
            out_m["source"] = src_m
        ts = m.get("time_sec")
        if isinstance(ts, (int, float)):
            out_m["time_sec"] = float(ts)
        cleaned.append(out_m)

    # Merge deterministic markers (description/cue) with LLM markers
    merged_markers = _merge_markers(cleaned, deterministic_markers)

    # If we have early markers and no day-1 marker, adjust start_day (e.g., edited videos starting on day 2)
    if merged_markers:
        has_day1 = any(int(m.get("day") or 0) == 1 for m in merged_markers)
        if not has_day1:
            earliest = merged_markers[0]
            try:
                sd = int(earliest.get("day") or start_day)
                if sd > start_day:
                    start_day = sd
            except Exception:
                pass

    cleaned = merged_markers

    # Safety: if there are no explicit day markers, do NOT allow start_day>1.
    # This prevents EP/series numbers from becoming start_day.
    if not cleaned and start_day > 1:
        start_day = 1

    if trip_type not in {"single_day", "multi_day", "unknown"}:
        trip_type = "unknown"

    return {
        "trip_type": trip_type,
        "start_day": start_day,
        "markers": cleaned,
        "notes": (data.get("notes") or "").strip(),
    }


def _mention_index(transcript: str, place_name: str) -> int:
    t = transcript or ""
    n = (place_name or "").strip()
    if not t or not n:
        return 10**12
    idx = t.lower().find(n.lower())
    return idx if idx >= 0 else 10**12


def _markers_to_positions(transcript: str, markers: List[dict]) -> List[Dict[str, Any]]:
    t = transcript or ""
    out: List[Dict[str, Any]] = []

    for m in markers or []:
        if not isinstance(m, dict):
            continue
        try:
            day = int(m.get("day") or 0)
        except Exception:
            day = 0
        evidence = (m.get("evidence") or "").strip()
        if day <= 0 or not evidence:
            continue

        idx = t.find(evidence)
        if idx < 0:
            idx = t.lower().find(evidence.lower())
        if idx < 0:
            continue

        out.append({"idx": idx, "day": day, "evidence": evidence})

    out.sort(key=lambda x: x["idx"])

    # 연속 동일 day 마커 제거
    dedup: List[Dict[str, Any]] = []
    last_day: Optional[int] = None
    for x in out:
        if last_day == x["day"]:
            continue
        dedup.append(x)
        last_day = x["day"]

    return dedup


def _infer_day_from_positions(positions: List[Dict[str, Any]], mention_idx: int, start_day: int = 1) -> int:
    if not positions:
        return max(1, int(start_day or 1))

    day = max(1, int(start_day or 1))
    for m in positions:
        if mention_idx >= int(m.get("idx") or 0):
            day = int(m.get("day") or day)
        else:
            break
    return max(1, day)


def run(materials: List[dict], places_raw: Dict[str, List[dict]]) -> Dict[str, List[dict]]:
    """Step2-1: LLM-Day

    - materials: step1 결과(영상별 transcript/title 포함)
    - places_raw: step2 결과(기본 day=1)

    산출:
    - data/step2_1_day_inferred.json
    - data/step2_1_day_inferred/day_inferred_<video_id>.json
    - data/step2_1_day_inferred/_summary.json
    """

    data_dir = Path(getattr(config, "DATA_DIR", "data"))
    out_dir = data_dir / "step2_1_day_inferred"
    out_dir.mkdir(parents=True, exist_ok=True)

    mat_by_id: Dict[str, dict] = {}
    for it in materials or []:
        vid = it.get("video_id")
        if vid:
            mat_by_id[str(vid)] = it

    enable = bool(getattr(config, "ENABLE_GEMINI", True)) and bool(getattr(config, "ENABLE_GEMINI_DAY", True))

    results: Dict[str, List[dict]] = {}
    summary: List[Dict[str, Any]] = []

    for video_id, places in (places_raw or {}).items():
        info = mat_by_id.get(video_id, {})
        title = (info.get("title") or "").strip()
        transcript = info.get("transcript") or ""

        description = info.get("description") or ""
        transcript_source = info.get("transcript_source") or ""
        yt_vtt = info.get("yt_dlp_transcript_vtt")
        whisper_text = info.get("whisper_transcript")

        # step2에서 vtt cues를 저장하는 경우를 대비해 로드(있으면 활용)
        cues = None
        try:
            cues_path = data_dir / "step1_vtt_cues" / f"cues_{video_id}.json"
            if cues_path.exists():
                cues = json.loads(cues_path.read_text(encoding="utf-8", errors="ignore")).get("cues")
        except Exception:
            cues = None

        # step2가 저장한 chapters 파일이 있으면 로드하여 day 마커(time_sec)로 활용
        chapter_markers = _load_chapter_markers(data_dir, video_id)

        if not places:
            payload = {
                "meta": {
                    "video_id": video_id,
                    "title": title,
                    "trip_type": "unknown",
                    "marker_count": 0,
                    "reassigned": 0,
                    "note": "no_places",
                },
                "places": [],
            }
            save_json(out_dir / f"day_inferred_{video_id}.json", payload)
            results[video_id] = []
            summary.append({**payload["meta"], "count": 0})
            continue

        if not enable:
            payload = {
                "meta": {
                    "video_id": video_id,
                    "title": title,
                    "trip_type": "unknown",
                    "marker_count": 0,
                    "reassigned": 0,
                    "note": "llm_disabled",
                },
                "places": places,
            }
            save_json(out_dir / f"day_inferred_{video_id}.json", payload)
            results[video_id] = places
            summary.append({**payload["meta"], "count": len(places)})
            continue

        # If transcript is empty, avoid calling LLM; use title/description heuristics + deterministic markers.
        if not transcript.strip():
            td = (title + "\n" + (description or "")).lower()
            if re.search(r"당일치기|0\s*박\s*1\s*일|원데이|day\s*trip|day-trip|daytrip|one\s*day|one-day", td):
                trip_type = "single_day"
                start_day = 1
            elif re.search(r"\d+\s*박\s*\d+\s*일|\d+\s*박|숙박|연박", title + "\n" + (description or "")):
                trip_type = "multi_day"
                start_day = 1
            else:
                trip_type = "unknown"
                start_day = 1

            cue_markers_no_tx = _extract_cue_markers(cues)
            markers = _merge_markers(cue_markers_no_tx, chapter_markers)
            if markers:
                has_day1 = any(int(m.get("day") or 0) == 1 for m in markers)
                if not has_day1:
                    try:
                        sd = int(markers[0].get("day") or 1)
                        if sd > 1:
                            start_day = sd
                    except Exception:
                        pass

            positions = []

            time_markers: List[Dict[str, Any]] = []
            for m in markers:
                if isinstance(m, dict) and isinstance(m.get("time_sec"), (int, float)) and int(m.get("day") or 0) > 0:
                    time_markers.append({"time_sec": float(m["time_sec"]), "day": int(m["day"])})
            time_markers.sort(key=lambda x: x["time_sec"])

            def _infer_day_by_time(sec: int) -> int:
                d = max(1, start_day)
                for tm in time_markers:
                    if sec >= int(tm["time_sec"]):
                        d = int(tm["day"]) or d
                    else:
                        break
                return max(1, d)

            reassigned = 0
            updated: List[dict] = []

            if trip_type == "single_day":
                for p in places:
                    cur = dict(p)
                    filled_sec = _fill_seconds_from_cues(cur, cues)
                    if filled_sec is not None and int(cur.get("seconds") or 0) <= 0:
                        cur["seconds"] = int(filled_sec)
                        cur.setdefault("seconds_source", "cues")
                    if int(cur.get("day") or 1) != 1:
                        reassigned += 1
                    cur["day"] = 1
                    cur.setdefault("day_source", "heuristic")
                    cur.setdefault("day_reason", "single_day")
                    updated.append(cur)
            else:
                for p in places:
                    cur = dict(p)
                    filled_sec = _fill_seconds_from_cues(cur, cues)
                    if filled_sec is not None and int(cur.get("seconds") or 0) <= 0:
                        cur["seconds"] = int(filled_sec)
                        cur.setdefault("seconds_source", "cues")
                    sec = int(cur.get("seconds") or 0)
                    if time_markers and sec > 0:
                        new_day = _infer_day_by_time(sec)
                        cur.setdefault("day_reason", "time_markers")
                    else:
                        new_day = start_day
                        cur.setdefault("day_reason", "start_day")
                    old_day = int(cur.get("day") or 1)
                    if new_day != old_day:
                        reassigned += 1
                    cur["day"] = new_day
                    cur.setdefault("day_source", "heuristic")
                    updated.append(cur)

            by_day: Dict[int, List[dict]] = {}
            for p in updated:
                d = int(p.get("day") or 1)
                by_day.setdefault(d, []).append(p)

            final: List[dict] = []
            for d in sorted(by_day.keys()):
                items = by_day[d]
                items.sort(
                    key=lambda x: (
                        int(x.get("seconds") or 0) == 0,
                        int(x.get("seconds") or 0),
                        int(x.get("order") or 10**9),
                    )
                )
                for i, it in enumerate(items, start=1):
                    it["order"] = i
                    final.append(it)

            results[video_id] = final

            payload = {
                "meta": {
                    "video_id": video_id,
                    "title": title,
                    "trip_type": trip_type,
                    "start_day": start_day,
                    "marker_count": len(time_markers),
                    "reassigned": reassigned,
                    "markers": markers[:20],
                    "notes": "no_transcript:heuristic+deterministic",
                },
                "places": final,
            }
            save_json(out_dir / f"day_inferred_{video_id}.json", payload)
            summary.append({**payload["meta"], "count": len(final)})

            log(
                "step2.1",
                "day_inferred",
                video_id=video_id,
                title=title,
                trip_type=trip_type,
                markers=0,
                reassigned=reassigned,
            )
            continue

        log("step2.1", "video", video_id=video_id, title=title)

        try:
            llm_obj = infer_day_markers_from_transcript(
                video_id=video_id,
                title=title,
                description=description,
                transcript=transcript,
                transcript_source=transcript_source,
                yt_vtt=yt_vtt,
                whisper_text=whisper_text,
                cues=cues,
            )
        except Exception as e:
            llm_obj = {"trip_type": "unknown", "start_day": 1, "markers": [], "notes": f"llm_error:{str(e)[:200]}"}

        trip_type = (llm_obj.get("trip_type") or "unknown").strip()
        start_day = int(llm_obj.get("start_day") or 1)
        # Final safety override: title/description explicitly says day-trip => force single_day.
        td = (title + "\n" + (description or "")).lower()
        if re.search(r"당일치기|0\s*박\s*1\s*일|원데이|day\s*trip|day-trip|daytrip|one\s*day|one-day", td):
            trip_type = "single_day"
            start_day = 1
        if start_day <= 0:
            start_day = 1
        markers = _merge_markers(llm_obj.get("markers") or [], chapter_markers)
        # If there are no explicit day markers at all, we must not trust start_day>1.
        # (Typical false positive: EP.02 / Vlog 6)
        if not markers and start_day > 1:
            start_day = 1

        positions = _markers_to_positions(transcript, markers)

        # time 기반 마커(가능하면 seconds로 day 배정)
        time_markers: List[Dict[str, Any]] = []
        for m in markers:
            if isinstance(m, dict) and isinstance(m.get("time_sec"), (int, float)) and int(m.get("day") or 0) > 0:
                time_markers.append({"time_sec": float(m["time_sec"]), "day": int(m["day"])})
        time_markers.sort(key=lambda x: x["time_sec"])

        def _infer_day_by_time(sec: int) -> int:
            d = max(1, start_day)
            for tm in time_markers:
                if sec >= int(tm["time_sec"]):
                    d = int(tm["day"]) or d
                else:
                    break
            return max(1, d)

        reassigned = 0
        updated: List[dict] = []

        if trip_type == "single_day":
            for p in places:
                cur = dict(p)

                # Fill seconds first (so later sorting is meaningful)
                filled_sec = _fill_seconds_from_cues(cur, cues)
                if filled_sec is not None and int(cur.get("seconds") or 0) <= 0:
                    cur["seconds"] = int(filled_sec)
                    cur.setdefault("seconds_source", "cues")

                if int(cur.get("day") or 1) != 1:
                    reassigned += 1
                cur["day"] = 1
                cur.setdefault("day_source", "llm_day")
                cur.setdefault("day_reason", "single_day")
                updated.append(cur)
        else:
            if not positions and start_day > 1:
                # 영상이 2일차부터 시작하는 편집본 같은 케이스
                for p in places:
                    cur = dict(p)

                    # Fill seconds first (even if day is forced to start_day)
                    filled_sec = _fill_seconds_from_cues(cur, cues)
                    if filled_sec is not None and int(cur.get("seconds") or 0) <= 0:
                        cur["seconds"] = int(filled_sec)
                        cur.setdefault("seconds_source", "cues")

                    old_day = int(cur.get("day") or 1)
                    if start_day != old_day:
                        reassigned += 1
                    cur["day"] = start_day
                    cur.setdefault("day_source", "llm_day")
                    cur.setdefault("day_reason", "start_day")
                    updated.append(cur)
            else:
                for p in places:
                    cur = dict(p)

                    # 1) Fill seconds first from cues (so time-based day inference can use it)
                    filled_sec = _fill_seconds_from_cues(cur, cues)
                    if filled_sec is not None and int(cur.get("seconds") or 0) <= 0:
                        cur["seconds"] = int(filled_sec)
                        cur.setdefault("seconds_source", "cues")

                    pn = (cur.get("place_name") or "").strip()
                    mi = _mention_index(transcript, pn)

                    # 2) Infer day: time-based first (if we have time markers and seconds), else text-position-based
                    sec = int(cur.get("seconds") or 0)
                    if time_markers and sec > 0:
                        new_day = _infer_day_by_time(sec)
                        cur.setdefault("day_reason", "time_markers")
                    else:
                        new_day = _infer_day_from_positions(positions, mi, start_day=start_day)
                        cur.setdefault("day_reason", "markers")

                    old_day = int(cur.get("day") or 1)
                    if new_day != old_day:
                        reassigned += 1

                    cur["day"] = new_day
                    cur.setdefault("day_source", "llm_day")
                    updated.append(cur)

        # day별 seconds/order 기준 정렬 후 order 재부여
        by_day: Dict[int, List[dict]] = {}
        for p in updated:
            d = int(p.get("day") or 1)
            by_day.setdefault(d, []).append(p)

        final: List[dict] = []
        for d in sorted(by_day.keys()):
            items = by_day[d]
            items.sort(
                key=lambda x: (
                    int(x.get("seconds") or 0) == 0,
                    int(x.get("seconds") or 0),
                    int(x.get("order") or 10**9),
                )
            )
            for i, it in enumerate(items, start=1):
                it["order"] = i
                final.append(it)

        results[video_id] = final

        payload = {
            "meta": {
                "video_id": video_id,
                "title": title,
                "trip_type": trip_type,
                "start_day": start_day,
                "marker_count": len(positions) if positions else len(time_markers),
                "reassigned": reassigned,
                "markers": positions[:20],
                "notes": llm_obj.get("notes") or "",
            },
            "places": final,
        }
        save_json(out_dir / f"day_inferred_{video_id}.json", payload)
        summary.append({**payload["meta"], "count": len(final)})

        log(
            "step2.1",
            "day_inferred",
            video_id=video_id,
            title=title,
            trip_type=trip_type,
            markers=len(positions),
            reassigned=reassigned,
        )

    save_json(out_dir / "_summary.json", summary)
    save_json(data_dir / "step2_1_day_inferred.json", results)
    log("step2.1", "saved", path=str(out_dir), videos=len(results))
    return results