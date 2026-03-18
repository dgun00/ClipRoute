import os
import json
import re
from pathlib import Path
from typing import List, Dict, Any
from llm.gemini_client import call_gemini_itinerary
from utils.io import save_json, load_json
from utils.logging_utils import log

SYSTEM_PROMPT = """당신은 대한민국의 최고 전문가이자 4박 5일 이상의 장기 여행 동선을 복구하는 '최종 전문가'입니다.
현재 장기 여행 데이터가 1일차에만 몰려 있고 뒷부분이 누락되어 있는 심각한 문제가 발생했습니다. 이를 해결하세요.

[필수 지침]
1. 5일치 전수 조사: 사용자가 '4박 5일'을 요청했다면, 영상 내에서 밤이 깊어지거나 옷이 바뀌는 시점, "다음 날", "잘 잤다" 등의 단어를 추적해 Day 1부터 Day 5까지 촘촘하게 분배하세요.
2. 숙소 기점 분리: 숙소명이 나오거나 '체크인/체크아웃' 단어가 보이면 반드시 다음 날로 Day를 증가시키세요.
3. 최소 목표: 하루당 최소 3~5개의 방문지(식당, 카페, 관광지, 기차역, 터미널 등)를 추출하여 전체 리스트를 15개 이상으로 만드세요.

[상호명 확정 규칙]
1. 단어 조합: 자막에 "태국 국밥"만 있어도 설명란의 해시태그나 베스트 댓글의 단어를 결합해 실제 상호명을 기어코 찾아내세요.
2. 이름 없음 금지: '알 수 없음', '이름없음'은 데이터 실격입니다. 지식 베이스를 총동원해 상호명을 확정하세요.

반드시 아래 JSON 형식을 엄수하세요.
{
    "itinerary": [
        {"day": 1, "place_name": "상호명", "address": "도로명주소", "category": "맛집/카페/관광지/기타"}
    ]
}"""

def extract_json_from_text(text: str) -> str:
    text = text.strip()
    # 마크다운 제거나 불필요한 텍스트 정제
    if '```json' in text:
        text = text.split('```json')[1].split('```')[0]
    elif '```' in text:
        text = text.split('```')[1].split('```')[0]
    
    start_idx = text.find('[')
    end_idx = text.rfind(']') + 1
    if start_idx == -1:
        start_idx = text.find('{')
        end_idx = text.rfind('}') + 1
    
    return text[start_idx:end_idx]

def run(materials: List[Dict], region: str, travel_period: str):
    log(f"🚀 Step 2: Gemini 인지 기반 여행 일정 복구 모드 가동 ({region})")
    
    results = []
    for m in materials:
        v_id = m.get('video_id')
        title = m.get('title')
        transcript = m.get('transcript')
        
        # 스텝 1에서 저장된 자막 파일 경로 확인
        t_path = Path(f"data/step1_transcripts/{v_id}.json")
        if t_path.exists():
            context_input = load_json(t_path)
            raw_response = context_input.get('transcript', transcript)
        else:
            raw_response = transcript

        log(f"🎙️ [{v_id}] 5일치 일정 추출 및 인지 분석 중...")
        
        user_prompt = f"""### [원본 지식] ###
현재 이 영상은 {region} 여행기입니다. 1일차에만 몰려 있지 않도록 하고, 
영상 내용에 맞춰 Day 1부터 Day {travel_period}까지 촘촘하게 일정을 복구하세요.

### [영상 데이터] ###
영상 제목: {title}
자막: {raw_response[:8000]} # 토큰 제한 고려"""

        try:
            # Gemini API 호출부 (llm/gemini_client.py 내 정의된 함수 사용)
            response_text = call_gemini_itinerary(SYSTEM_PROMPT, user_prompt)
            data = json.loads(extract_json_from_text(response_text))
            
            valid_list = data.get('itinerary', [])
            for item in valid_list:
                item['video_id'] = v_id
                # 3.12 바이트코드에서 확인된 assigned_day 보정 로직
                assigned_day = item.get('day', 1)
                item['day'] = int(assigned_day)
                results.append(item)
                
            log(f"✅ [{v_id}] 일정 복구 완료 (Day 분리 성공)")
            
        except Exception as e:
            log(f"❌ [{v_id}] 복구 실패: {str(e)}")
            continue

    save_path = "data/step2_itinerary.json"
    save_json(results, save_path)
    log(f"🏁 Step 2 완료: {len(results)}개의 일정 저장됨 -> {save_path}")
    return results