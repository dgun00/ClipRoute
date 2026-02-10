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

_TARGET_MODEL = "gemini-2.5-pro"
total_usage_stats = {"prompt": 0, "output": 0, "total": 0}

def get_total_usage() -> Dict[str, int]:
    return total_usage_stats

def _extract_json(raw_text: str) -> Any:
    """Gemini 2.5 Pro의 방대한 응답에서 JSON 배열만 정밀 추출"""
    if not isinstance(raw_text, str) or not raw_text.strip(): return []
    
    # 1. 불필요한 마크다운 태그 제거
    clean_text = re.sub(r"```json|```", "", raw_text, flags=re.IGNORECASE).strip()
    
    # 2. 대괄호 [ ] 사이의 내용만 추출 (가장 바깥쪽 기준)
    match = re.search(r"(\[[\s\S]*\])", clean_text)
    if not match:
        # 리스트가 아니면 중괄호 { } 라도 찾음
        match = re.search(r"(\{[\s\S]*\})", clean_text)
        
    if match:
        json_str = match.group(1)
        try:
            return json.loads(json_str)
        except:
            try:
                # JSON 형식이 약간 틀렸을 경우 보정 (따옴표 등)
                return ast.literal_eval(json_str)
            except:
                log("llm", "❌ JSON 파싱 최종 실패")
                return []
    return []

def call_gemini_itinerary(prompt: str, content: str) -> Dict[str, Any]:
    """Gemini 2.5 Pro 호출 엔진"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: return {"itinerary": []}

    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1'})

    try:
        # ✅ 모델에게 형식을 더 엄격하게 지시하여 '1개만 추출'되는 현상 방지
        response = client.models.generate_content(
            model=_TARGET_MODEL,
            contents=f"{prompt}\n\n[데이터]\n{content}\n\n⚠️ 모든 장소를 빠짐없이 JSON 리스트 [{{...}}, {{...}}] 형식으로만 응답하세요."
        )
        
        if response.usage_metadata:
            u = response.usage_metadata
            total_usage_stats["prompt"] += u.prompt_token_count or 0
            total_usage_stats["output"] += u.candidates_token_count or 0

        extracted_data = _extract_json(response.text)
        # 리스트가 아니면 리스트로 감싸서 반환
        itinerary = extracted_data if isinstance(extracted_data, list) else [extracted_data]
        
        log("llm", f"✅ 2.5 Pro가 {len(itinerary)}개의 장소 후보를 찾아냈습니다.")
        return {"itinerary": itinerary}

    except Exception as e:
        log("llm", f"❌ 2.5 Pro 엔진 오류: {e}")
        return {"itinerary": []}