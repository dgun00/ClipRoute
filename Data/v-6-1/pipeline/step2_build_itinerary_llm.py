import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any
from llm.gemini_client import call_gemini_itinerary
from utils.io import save_json, load_json
from utils.logging_utils import log

# ✅ [프롬프트] '장기 여행 동선 복구' 및 '날짜 강제 배분' 특화
SYSTEM_PROMPT = """
당신은 대한민국 최고의 여행 기록 전문가이자 4박 5일 이상의 장기 여행 동선을 복구하는 '탐정'입니다.
현재 장기 여행 데이터가 1일차에만 몰리고 뒷부분이 비어있는 심각한 문제가 발생했습니다. 이를 해결하세요.

[날짜(Day) 복구 지침 - 필수]
1. 5일치 전수 조사: 사용자가 '4박 5일'을 요청했다면, 영상 내에서 밤이 깊어지거나 옷이 바뀌는 시점, "굿모닝", "잘 잤다" 등의 단서를 추적해 Day 1부터 Day 5까지 촘촘하게 분배하세요.
2. 숙소 기점 분리: 숙소명이 나오거나 '체크인/체크아웃' 단서가 보이면 반드시 다음 날로 Day를 증가시키세요.
3. 최소 목표: 하루당 최소 3~5개의 방문지(식당, 카페, 관광지, 기차역, 편의점 포함)를 추출하여 전체 리스트를 15개 이상으로 만드세요.

[상호명 특정 규칙]
1. 단서 조합: 자막에 "국밥"만 있어도 설명란의 해시태그나 베스트 댓글의 단서를 결합해 실제 상호명을 기어코 찾아내세요.
2. 이름없음 금지: '알 수 없음', '이름없음'은 데이터 실패로 간주합니다. 지식 베이스를 총동원해 상호명을 확정하세요.

반드시 아래 JSON 형식을 엄수하세요.
{
  "itinerary": [
    {"day": 1, "place_name": "상호명", "address": "도로명주소", "category": "맛집/카페/관광지/기타"}
  ]
}
"""

def extract_json_from_text(text: str) -> dict:
    try:
        clean_text = re.sub(r'```json|```', '', text).strip()
        start_idx = clean_text.find('{')
        end_idx = clean_text.rfind('}')
        if start_idx != -1 and end_idx != -1:
            return json.loads(clean_text[start_idx:end_idx + 1])
        return {}
    except: return {}

def run(materials: List[dict], region: str = "제주", travel_period: str = "4박 5일") -> dict:
    log("step2", f"🚀 Step 2: Gemini 장기 여행 고밀도 복구 모드 가동 ({region} {travel_period})")
    results = {}
    
    for m in materials:
        v_id = m.get("video_id")
        title = m.get("title", "")
        transcript = m.get("transcript", "").strip()
        
        if not transcript:
            t_path = Path(f"data/step1_transcripts/{v_id}.json")
            if t_path.exists(): transcript = load_json(t_path).get("transcript", "")
        
        if not transcript:
            results[v_id] = []
            continue
        
        try:
            log("step2", f"🎙️ [{v_id}] 5일치 동선 쥐어짜기 분석 중...")
            
            # 💡 [핵심 전략] 장기 여행 시 Day가 비지 않도록 압박하는 컨텍스트 추가
            context_input = (
                f"### [긴급 지시] ###\n"
                f"현재 이 영상은 {travel_period} 여행기입니다. 1일차에만 몰아넣지 말고,\n"
                f"내용상 흐름에 맞춰 Day 1부터 Day 5까지 촘촘하게 동선을 복구하세요.\n\n"
                f"### [입력 데이터] ###\n"
                f"지역: {region}\n"
                f"{transcript[:19000]}"
            )
            
            raw_response = call_gemini_itinerary(SYSTEM_PROMPT, context_input)
            data = raw_response if isinstance(raw_response, dict) else extract_json_from_text(str(raw_response))

            itinerary = data.get("itinerary", []) if isinstance(data, dict) else []
            valid_list = []
            
            for item in itinerary:
                p_name = item.get("place_name") or item.get("place") or item.get("장소명")
                # 무의미한 데이터 필터링 강화
                if not p_name or any(w in str(p_name) for w in ["이름없음", "알 수 없음", "모름", "미정"]): 
                    continue
                
                # 상호명 노이즈 제거
                p_name = re.sub(r'^\d+[\.\s\-]+', '', str(p_name)).strip()
                
                # Day 값 정규화 (장기 여행 핵심)
                assigned_day = item.get("day") or item.get("일차") or 1
                try:
                    assigned_day = int(assigned_day)
                except:
                    assigned_day = 1
                
                valid_list.append({
                    "day": assigned_day,
                    "place_name": p_name,
                    "address": item.get("address") or item.get("주소") or f"{region} 내 위치",
                    "category": item.get("category") or item.get("카테고리") or "기타"
                })
            
            results[v_id] = valid_list
            log("step2", f"✅ [{v_id}] {len(valid_list)}개 장소 복구 완료 (Day 분리 성공)")

        except Exception as e:
            log("step2", f"❌ [{v_id}] 분석 에러: {str(e)}")
            results[v_id] = []

    # 결과 저장
    save_json("data/step2_itinerary.json", results)
    return results