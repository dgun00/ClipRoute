import os
import json
from pathlib import Path
from typing import List, Dict, Any
from llm.gemini_client import call_gemini_itinerary
from utils.io import save_json, load_json
from utils.logging_utils import log

SYSTEM_PROMPT = """
당신은 여행 타임라인 추출 전문가입니다. 자막에서 장소와 날짜 정보를 추출하세요.
1. 'day': 날짜 변화 감지 시 1씩 증가.
2. 'visit_order': 방문 순서대로 번호 부여.
3. 'place_name': 상호명을 구체적으로 추출.
4. 'visit_reason': 방문 목적이나 메뉴 기록.
결과는 반드시 {"itinerary": [...]} 구조의 JSON이어야 합니다.
"""

def clean_ellipsis(obj):
    """데이터 내부에 숨은 모든 Ellipsis(...) 객체를 찾아 빈 값으로 바꿉니다."""
    if isinstance(obj, dict):
        return {k: clean_ellipsis(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_ellipsis(v) for v in obj]
    elif obj is Ellipsis or obj is ...:
        return None # 또는 [] 로 변경 가능
    return obj

def run(materials: List[dict], region: str = "제주") -> dict:
    log("step2", "🚀 Step 2: Gemini 타임라인 추출 가동 (딥-클리닝 엔진)")
    results = {}
    
    for m in materials:
        v_id = m.get("video_id")
        transcript = m.get("transcript", "").strip()
        
        if not transcript:
            t_path = Path(f"data/step1_transcripts/{v_id}.json")
            if t_path.exists():
                transcript = load_json(t_path).get("transcript", "")
        
        if not transcript: 
            results[v_id] = []
            continue
        
        try:
            log("step2", f"🎙️ [{v_id}] Gemini 분석 중...")
            data = call_gemini_itinerary(SYSTEM_PROMPT, transcript[:15000])
            
            # 1차 방어: 데이터가 통째로 Ellipsis인 경우
            if data is None or data is ...:
                itinerary = []
            else:
                itinerary = data.get("itinerary", [])
            
            results[v_id] = itinerary
            if itinerary:
                log("step2", f"✅ [{v_id}] {len(itinerary)}개 장소 추출 성공")
            else:
                log("step2", f"⚠️ [{v_id}] 추출된 장소가 없습니다.")

        except Exception as e:
            log("step2", f"❌ [{v_id}] 분석 실패: {e}")
            results[v_id] = []

    # ✅ [핵심 수정] 딥-클리닝 실행
    # 딕셔너리, 리스트 내부의 중첩된 구조까지 모두 뒤져서 ... 을 제거합니다.
    final_clean_results = clean_ellipsis(results)

    # 최종 저장 (인코딩 에러 방지를 위해 cls 옵션 추가 고려 가능하나 우선 일반 저장)
    try:
        save_json("data/step2_itinerary.json", final_clean_results)
    except TypeError:
        # 최후의 수단: 강제 문자열 변환 저장
        log("step2", "⚠️ 일반 저장 실패, 강제 직렬화 시도")
        with open("data/step2_itinerary.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(final_clean_results, indent=2, ensure_ascii=False, default=lambda x: None))

    return final_clean_results