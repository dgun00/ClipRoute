import os
import re
from utils.io import load_json, save_json
from utils.logging_utils import log
from llm.gemini_client import ask_gemini

def run(itinerary_results: dict):
    """
    Step 2.5: 자막 오타(삼덕->함덕)를 교정하고 상호명을 네이버 검색에 최적화합니다.
    """
    log("step2_5", "💎 Step 2.5: 고정밀 장소명 정규화 가동")
    
    normalized_data = {}
    
    # 지능형 교정 맵 (영상 자막 특유의 오타를 사전 차단)
    correction_map = {
        "삼덕 해수욕장": "함덕 해수욕장",
        "삼덕 해수육장": "함덕 해수욕장",
        "저팔개": "저팔계",
        "깡촌 흑돼지": "깡촌흑돼지",
        "경성초상": "경성수산",
        "손고래": "섬고래",
        "저지장탕": "저지해장국",
        "또간집 1등 밀면": "산방식당" # 영상 맥락 기반 교정
    }

    for vid, data in itinerary_results.items():
        # 데이터 구조 유연성 확보 (리스트/딕셔너리 대응)
        locations = data if isinstance(data, list) else data.get("itinerary", [])
        if not locations: continue
        
        corrected_list = []
        log("step2_5", f"🔄 [{vid}] {len(locations)}개 장소 정밀 검수 중...")

        for loc in locations:
            original_name = loc.get("place_name", "")
            
            # 1. 수동 교정 맵 적용
            processed_name = original_name
            for wrong, right in correction_map.items():
                if wrong in original_name:
                    processed_name = processed_name.replace(wrong, right)
            
            # 2. 불필요한 수식어 제거 (예: "뷰 좋은", "저렴한")
            processed_name = re.sub(r'(뷰 좋은|저렴한|찐로컬|맛집|포장|체크인|예정인|식당)', '', processed_name).strip()
            
            # 3. 데이터 업데이트
            loc["place_name"] = processed_name
            
            # 4. 검색 후보군(search_candidates) 생성 로직 보강
            if "search_candidates" not in loc:
                loc["search_candidates"] = [f"제주 {processed_name}", processed_name]
            
            corrected_list.append(loc)
            
            if original_name != processed_name:
                log("step2_5", f"   ✨ 교정 완료: [{original_name}] -> [{processed_name}]")

        normalized_data[vid] = {"itinerary": corrected_list}

    save_json("data/step2_5_normalized.json", normalized_data)
    log("step2_5", "✨ 장소명 정규화 완료! 이제 네이버 검증(Step 3)으로 이동하세요.")
    return normalized_data