from typing import Dict, List, Any
from utils.io import save_json

def run(verified_dict: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """날짜별로 묶고, 그 안에서 방문 순서(1, 2, 3...)대로 정렬합니다."""
    sorted_itinerary = {}

    for video_id, places in verified_dict.items():
        # 1. Day 라벨별 그룹화
        day_groups = {}
        for p in places:
            label = p.get("day_label", "1일차")
            if label not in day_groups:
                day_groups[label] = []
            day_groups[label].append(p)
        
        # 2. 날짜 정렬 후 내부 방문 순서 정렬
        video_timeline = []
        for label in sorted(day_groups.keys()):
            # 내부 장소들을 visit_order 기준으로 오름차순 정렬
            day_places = sorted(day_groups[label], key=lambda x: x.get("visit_order", 99))
            
            video_timeline.append({
                "day": f"{label} : ", # 치키님이 요청하신 '1일차 : ' 포맷
                "locations": day_places
            })
        
        sorted_itinerary[video_id] = video_timeline

    save_json("data/step4_sorted_timeline.json", sorted_itinerary)
    return sorted_itinerary