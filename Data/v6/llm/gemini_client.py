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
    if not isinstance(raw_text, str) or not raw_text.strip():
        return []
    s = raw_text.strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", s, re.IGNORECASE)
    if m: s = m.group(1).strip()
    l_bracket, r_bracket = s.find("["), s.rfind("]")
    l_brace, r_brace = s.find("{"), s.rfind("}")
    start, end = -1, -1
    if l_bracket != -1 and (l_brace == -1 or l_bracket < l_brace):
        start, end = l_bracket, r_bracket
    elif l_brace != -1:
        start, end = l_brace, r_brace
    if start == -1 or end == -1:
        return []
    clean_s = s[start : end + 1]
    try:
        return json.loads(clean_s)
    except json.JSONDecodeError:
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
    return ""

# ✅ V6 전용: 추출용 함수
def call_gemini_itinerary(prompt: str, content: str, model: str = _DEFAULT_MODEL) -> Dict[str, Any]:
    full_prompt = f"{prompt}\n\n[데이터]\n{content}"
    raw = _call_gemini(full_prompt, model=model)
    data = _extract_json(raw)
    return {"itinerary": data} if isinstance(data, list) else data

# ✅ V6 전용: 정규화용 함수
def call_gemini_normalization(prompt: str, content: str, model: str = _DEFAULT_MODEL) -> Dict[str, Any]:
    full_prompt = f"{prompt}\n\n[정규화 대상]\n{content}"
    raw = _call_gemini(full_prompt, model=model)
    data = _extract_json(raw)
    return {"itinerary": data} if isinstance(data, list) else data