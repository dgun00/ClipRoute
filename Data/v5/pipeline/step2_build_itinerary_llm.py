import os
import json
import re
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
import openai 
from utils.io import save_json
from utils.logging_utils import log

def process_video(m: dict) -> tuple:
    video_id = m["video_id"]
    transcript = m.get("transcript", "")
    if not transcript:
        return video_id, {"itinerary": []}, {"prompt_tokens": 0, "completion_tokens": 0}

    client = openai.OpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    
    # 🚩 Gemini 2.5 Flash에게 '1일차 : ' 와 'visit_order'를 명시적으로 요구
    prompt = f"""
    자막을 분석하여 아래 JSON 포맷으로 응답하세요. 
    자막 내용: {transcript[:15000]} 

    미션:
    1. 날짜 구분 시 'day_label' 필드에 반드시 '1일차 : ', '2일차 : ' 형식으로 작성하세요.
    2. 각 날짜 내 방문 순서를 'visit_order' 필드에 1, 2, 3... 숫자로 기록하세요.
    3. 'place_name'은 네이버 지도 검색이 가능한 실제 상호명이어야 합니다.
    4. 언급된 장소를 하나도 놓치지 말고 추출하세요.

    JSON 응답 형식 (이 구조를 엄격히 지킬 것):
    {{
      "places": [
        {{ 
          "day_label": "1일차 : ", 
          "visit_order": 1,
          "place_name": "상호명", 
          "visit_reason": "방문 이유", 
          "search_candidates": ["지역 상호명"] 
        }}
      ]
    }}
    """
    try:
        response = client.chat.completions.create(
            model="gemini-2.5-flash", 
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={ "type": "json_object" }
        )
        usage = {"prompt_tokens": response.usage.prompt_tokens, "completion_tokens": response.usage.completion_tokens}
        content = response.choices[0].message.content
        data = json.loads(content)
        return video_id, {"itinerary": data.get("places", [])}, usage
    except Exception as e:
        log("step2", f"Gemini API Error: {e}")
        return video_id, {"itinerary": []}, {"prompt_tokens": 0, "completion_tokens": 0}

def run(materials: List[dict]) -> dict:
    log("step2", "🚀 Gemini 2.5 Flash 병렬 분석 (Day 라벨 및 방문 순서 지정)")
    results = {}
    total_usage = {"prompt_tokens": 0, "completion_tokens": 0}
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_video, m): m["video_id"] for m in materials}
        for future in futures:
            v_id, data, usage = future.result()
            results[v_id] = data
            total_usage["prompt_tokens"] += usage["prompt_tokens"]
            total_usage["completion_tokens"] += usage["completion_tokens"]
    save_json("data/step2_itinerary.json", results)
    return {"itinerary": results, "usage": total_usage}