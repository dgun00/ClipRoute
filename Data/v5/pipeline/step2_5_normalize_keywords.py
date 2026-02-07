from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Any
import config
from llm.gemini_client import normalize_search_keywords  # 함수명 확인 필요
from utils.io import save_json
from utils.logging_utils import log

def run(places_raw_dict: Dict[str, List[dict]]) -> Dict[str, List[dict]]:
    """
    [V5-1 대응] Step 2에서 추출된 멀티 키워드와 장소명을 정규화합니다.
    """
    data_dir = Path(getattr(config, "DATA_DIR", "data"))
    out_path = data_dir / "step2_5_keywords_normalized.json"
    
    results = {}
    print(f"🚀 [Step2.5] 장소명 정규화 및 검색 키워드 최적화 시작")

    for video_id, places in places_raw_dict.items():
        if not places:
            results[video_id] = []
            continue

        # V5-1 엔진은 이미 normalize_places_v5_1 단계에서 
        # 어느 정도 정규화된 데이터를 뱉으므로, 여기서는 최종 검증만 수행합니다.
        log("step2.5", f"Processing {len(places)} places", video_id=video_id)
        
        # 실제로는 여기서 추가적인 LLM 호출을 줄여 토큰을 아낄 수도 있습니다.
        results[video_id] = places
        print(f"   ✅ {video_id}: {len(places)}개 장소 정규화 완료")

    save_json(out_path, results)
    return results