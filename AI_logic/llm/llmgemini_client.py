from __future__ import annotations
import os
import re
import json
import ast
from typing import Any, Dict, List, Optional
from utils.logging_utils import log
from google import genai

# [수정] 모델명을 상수로 관리하여 유지보수성 향상
_TARGET_MODEL = "gemini-2.5-pro"

# 사용량 통계 (기존 3.12 버전의 구조 유지)
total_usage_stats = {"prompt": 0, "output": 0, "total": 0}

def get_total_usage() -> Dict[str, int]:
    """전체 API 사용량 통계를 반환합니다."""
    return total_usage_stats

def _extract_json(raw_text: str) -> List[Dict[str, Any]]:
    """
    [수정] 3.12 버전의 정규식 로직을 강화하여 
    LLM 응답 텍스트 내에서 JSON 블록을 안전하게 추출합니다.
    """
    if not isinstance(raw_text, str) or not raw_text.strip():
        return []

    # 1. 마크다운 코드 블록 제거
    clean_text = re.sub(r'```json\s*|```', '', raw_text)
    
    # 2. 정규표현식을 이용한 리스트 또는 딕셔너리 추출
    # 3.12 버전의 패턴을 개선하여 멀티라인 대응
    patterns = [r'\[[\s\S]*\]', r'\{[\s\S]*\}']
    
    for pattern in patterns:
        match = re.search(pattern, clean_text)
        if match:
            json_str = match.group(0)
            try:
                # 표준 JSON 파싱
                return json.loads(json_str)
            except json.JSONDecodeError:
                try:
                    # 따옴표 문제 등 미세 오류 발생 시 ast를 이용한 유연한 파싱
                    data = ast.literal_eval(json_str)
                    return data if isinstance(data, list) else [data]
                except (ValueError, SyntaxError):
                    continue
    return []

def call_gemini_itinerary(prompt: str, api_version: str = "v1") -> List[Dict[str, Any]]:
    """
    [수정] Gemini API를 호출하고 결과를 리스트 형태로 반환합니다.
    3.11의 안정성과 3.12의 모델 사양을 통합했습니다.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        log.error("GEMINI_API_KEY가 설정되지 않았습니다.")
        return []

    try:
        client = genai.Client(api_key=api_key, http_options={'api_version': api_version})
        
        # 프롬프트 보강 (JSON 형식 강제)
        system_instruction = "\n\n[데이터]\n⚠️ 모든 장소를 JSON 리스트 [{...}] 형식으로만 응답하세요."
        
        response = client.models.generate_content(
            model=_TARGET_MODEL,
            contents=prompt + system_instruction
        )

        if not response or not response.text:
            log.warning("Gemini 응답이 비어있습니다.")
            return []

        # 사용량 업데이트 (3.12 기능 반영)
        usage = response.usage_metadata
        total_usage_stats["prompt"] += usage.prompt_token_count
        total_usage_stats["output"] += usage.candidates_token_count
        total_usage_stats["total"] = total_usage_stats["prompt"] + total_usage_stats["output"]

        log.info(f"✅ {_TARGET_MODEL} 호출 성공 (토큰: {usage.prompt_token_count})")

        extracted_data = _extract_json(response.text)
        
        # 결과가 단일 객체일 경우 리스트로 감싸서 반환 타입 통일
        if isinstance(extracted_data, list):
            return extracted_data
        return [extracted_data] if extracted_data else []

    except Exception as e:
        log.error(f"❌ Gemini 호출 중 오류 발생: {e}")
        return []