from __future__ import annotations

import json
import os
import re
import time
import ast
from typing import Any, Dict, List, Optional

from utils.logging_utils import log

try:
    from google import genai
except Exception:
    genai = None

_DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
total_usage_stats = {"prompt": 0, "output": 0, "total": 0}

def get_total_usage() -> Dict[str, int]:
    return total_usage_stats

def _get_client() -> Any:
    if genai is None:
        raise RuntimeError("google-genai 패키지가 설치되어 있지 않습니다.")
    api_key = os.getenv("GEMINI_API_KEY")
    return genai.Client(api_key=api_key)

def _extract_json(raw_text: str) -> Any:
    """[V5-1 완주용] JSON을 못 찾거나 형식이 깨져도 빈 리스트를 반환해 에러를 방지합니다."""
    if not isinstance(raw_text, str) or not raw_text.strip():
        return []

    # 1. 마크다운 코드 블록 제거
    s = raw_text.strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", s, re.IGNORECASE)
    if m:
        s = m.group(1).strip()

    # 2. JSON 경계 찾기
    l_bracket, r_bracket = s.find("["), s.rfind("]")
    l_brace, r_brace = s.find("{"), s.rfind("}")
    
    start, end = -1, -1
    if l_bracket != -1 and (l_brace == -1 or l_bracket < l_brace):
        start, end = l_bracket, r_bracket
    elif l_brace != -1:
        start, end = l_brace, r_brace

    # JSON 구조가 없으면 에러 대신 빈 리스트 반환 (V5-1 핵심 안정화)
    if start == -1 or end == -1:
        log("llm", "No JSON found in response, skipping this chunk")
        return []

    clean_s = s[start : end + 1]

    try:
        return json.loads(clean_s)
    except json.JSONDecodeError:
        # 3. 느슨한 파이썬 리터럴 파싱 시도
        clean_s = re.sub(r",\s*([\]}])", r"\1", clean_s)
        try:
            return ast.literal_eval(clean_s)
        except Exception:
            return []

def _call_gemini(prompt: str, *, model: str, max_retries: int = 2) -> str:
    client = _get_client()
    for attempt in range(max_retries + 1):
        try:
            resp = client.models.generate_content(model=model, contents=prompt)
            if hasattr(resp, "usage_metadata") and resp.usage_metadata:
                u = resp.usage_metadata
                total_usage_stats["prompt"] += u.prompt_token_count or 0
                total_usage_stats["output"] += u.candidates_token_count or 0
                total_usage_stats["total"] += u.total_token_count or 0
            return getattr(resp, "text", "") or ""
        except Exception as e:
            time.sleep(1.5 * (2 ** attempt))
    return "" # 실패 시 빈 문자열 반환

# ✅ [V5-1] 가성비 Day Scanner (동적 문맥 분석)
def extract_days_v5_1(*, video_id: str, text: str, model: str = _DEFAULT_MODEL) -> List[Dict[str, Any]]:
    anchors = ["다음 날", "Day", "일차", "아침", "자고 일어나", "체크아웃", "굿모닝"]
    found_segments = []
    for anchor in anchors:
        for m in re.finditer(anchor, text, re.IGNORECASE):
            start, end = max(0, m.start() - 150), min(len(text), m.end() + 150)
            found_segments.append(text[start:end])
    
    scanning_context = "\n---\n".join(set(found_segments)) if found_segments else text[:3000]

    prompt = f"다음 여행 자막 문맥에서 날짜 변경 지점을 JSON 배열로 추출하라: {scanning_context}"
    raw = _call_gemini(prompt, model=model)
    data = _extract_json(raw)
    return data if isinstance(data, list) else []

# ✅ [V5-1] 멀티 키워드 장소 추출
def normalize_places_v5_1(*, video_id: str, text: str, region_hint: str = "", model: str = _DEFAULT_MODEL) -> List[Dict[str, Any]]:
    if not text.strip(): return []

    prompt = f"[지역: {region_hint}] 자막에서 방문 장소명과 검색어 후보(search_candidates)를 JSON으로 추출하라: {text}"
    raw = _call_gemini(prompt, model=model)
    data = _extract_json(raw)
    
    if not isinstance(data, list): return []
    
    for x in data: 
        x["video_id"] = video_id
        x["source"] = "gemini-v5-1"
    return data

# ✅ [V5-1] 호환용 키워드 정규화
def normalize_search_keywords(*, video_id: str, phrases: List[str], region_hint: str = "", model: str = _DEFAULT_MODEL) -> List[Dict[str, Any]]:
    if not phrases: return []
    payload = json.dumps(phrases, ensure_ascii=False)
    prompt = f"다음 장소명들을 네이버 검색 최적화 형태로 정규화하여 JSON 배열로 반환하라: {payload}"
    raw = _call_gemini(prompt, model=model)
    data = _extract_json(raw)
    return data if isinstance(data, list) else []