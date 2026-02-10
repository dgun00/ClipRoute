import os
from utils.logging_utils import log
from utils.io import save_json

def run(verified_results: dict):
    log("step4", "🧹 Step 4 (v6-1): Day 보정 및 정렬")
    refined_data = {}

    for vid, places in verified_results.items():
        if not places:
            refined_data[vid] = []
            continue

        # ✅ 팀장님의 Day 0 보정 로직 적용
        has_day_zero = any((p.get('day') if p.get('day') is not None else 1) == 0 for p in places)
        
        corrected_places = []
        for p in places:
            raw_day = p.get('day', 1) or 1
            current_day = int(raw_day)
            
            if has_day_zero:
                p['day'] = current_day + 1
            elif current_day <= 0:
                p['day'] = 1
            else:
                p['day'] = current_day
                
            corrected_places.append(p)

        # 시간 및 방문 순서에 따른 최종 정렬
        corrected_places.sort(key=lambda x: (x.get('day', 1), x.get('seconds', 0), x.get('visit_order', 999)))
        
        for i, p in enumerate(corrected_places, 1):
            p['visit_order'] = i

        refined_data[vid] = corrected_places
        log("step4", f"✅ [{vid}] 정제 완료 ({len(corrected_places)}개)")

    return refined_data