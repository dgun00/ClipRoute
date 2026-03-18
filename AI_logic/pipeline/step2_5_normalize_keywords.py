import os
import re
import json
from utils.io import load_json, save_json
from utils.logging_utils import log
from llm.gemini_client import ask_gemini

def run(itinerary_results):
    log("🚀 Step 2.5: 장소명 정규화 및 검색 키워드 최적화 시작")
    
    # 1. 오타 및 잘못된 명칭 교정 맵 (바이트코드 내부 매핑 기반)
    correction_map = {
        "후쿠오카": "후쿠오카 공항",
        "도쿄타워": "도쿄 타워",
        "스카이트리": "도쿄 스카이트리",
        "오사카성": "오사카 성",
        "해리포터": "유니버셜 스튜디오 재팬 해리포터",
        "라라포트": "라라포트 후쿠오카",
        "오호리": "오호리 공원",
        "텐진": "텐진역"
    }

    normalized_data = []
    
    # itinerary_results가 리스트인지 확인 후 반복
    items = itinerary_results if isinstance(itinerary_results, list) else [itinerary_results]

    for vid_data in items:
        v_id = vid_data.get('video_id', 'unknown')
        locations = vid_data.get('locations', [])
        
        if not locations:
            log(f"⚠️ {v_id}: 추출된 장소가 없어 건너뜁니다.")
            continue

        corrected_list = []
        for loc in locations:
            original_name = loc.strip()
            # 기본 매핑 교정
            processed_name = correction_map.get(original_name, original_name)
            
            # 2. Gemini를 통한 지명 정밀 교정 프롬프트
            prompt = f"""
            다음은 여행 영상에서 추출된 장소명 리스트입니다. 
            이 명칭이 오타이거나 검색하기에 부정확하다면 정확한 구글 지도 검색 명칭으로 바꿔주세요.
            대상: {processed_name}
            형식: 장소명만 답변하세요.
            """
            
            try:
                # LLM 호출을 통해 정제된 명칭 획득
                refined_name = ask_gemini(prompt).strip()
                # 불필요한 따옴표나 마침표 제거
                refined_name = re.sub(r'["\'\.]', '', refined_name)
                
                if refined_name:
                    corrected_list.append({
                        "original": original_name,
                        "normalized": refined_name
                    })
                    log(f"📍 정규화: [{original_name}] -> [{refined_name}]")
            except Exception as e:
                log(f"❌ Gemini 정규화 중 오류: {e}")
                corrected_list.append({"original": original_name, "normalized": processed_name})

        # 최종 결과 저장 구조 생성
        result_entry = {
            "video_id": v_id,
            "normalized_keywords": [item["normalized"] for item in corrected_list],
            "details": corrected_list
        }
        normalized_data.append(result_entry)

    # 결과 파일 저장
    save_path = "data/step2_5_normalized.json"
    save_json(normalized_data, save_path)
    
    log(f"✅ Step 2.5 완료! 정규화된 키워드가 {save_path}에 저장되었습니다.")
    log(f"🔗 다음 단계(Step 3): 이 키워드를 기반으로 이미지를 생성하거나 정보를 검색합니다.")
    
    return normalized_data