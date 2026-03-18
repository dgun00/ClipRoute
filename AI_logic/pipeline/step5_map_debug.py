from __future__ import annotations
import config
from pathlib import Path
from typing import Any, Dict
from utils.io import save_json
from utils.logging_utils import log

def run(timeline: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    log("🚀 Step 5: 타임라인 데이터 통합 및 최종 리포트 생성 (지도 디버그용)")
    
    # 1. 출력 디렉토리 설정
    out_dir = Path(getattr(config, "DATA_DIR", "data"))
    out_dir.mkdir(parents=True, exist_ok=True)
    
    if not timeline:
        raise ValueError("step5_map_debug.run: timeline is required")

    all_results = []
    combined_data = {}

    # 2. 개별 비디오 데이터 처리 및 저장
    for vid, payload in timeline.items():
        # payload 내의 verified_places 또는 timeline 리스트 추출
        places = payload.get('verified_places', [])
        count = len(places)
        
        # 개별 결과 구조화
        result = {
            "video_id": vid,
            "count": count,
            "final_places": places
        }
        
        # 개별 파일 저장 (예: data/step5_VID123_final.json)
        vid_save_path = out_dir / f"step5_{vid}_final.json"
        save_json(result, str(vid_save_path))
        log(f"💾 saved video: {vid_save_path}")
        
        # 통합 리스트에 추가
        all_results.append(result)
        combined_data[vid] = result

    # 3. 전체 통합 파일 저장
    final_all_path = out_dir / "step5_final_all.json"
    final_report = {
        "total_videos": len(all_results),
        "videos": combined_data
    }
    save_json(final_report, str(final_all_path))
    log(f"✅ saved final_all: {final_all_path}")
    
    return final_report