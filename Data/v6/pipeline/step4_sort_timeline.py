import os
from utils.logging_utils import log

def run(verified_results: dict):
    """
    Step 4: 방문 순서 누적은 유지하되, Day 0만 1로 강제 교정합니다. (중략 없음)
    """
    log("step4", "🧹 Step 4 가동: 타임라인 데이터 정규화 (Day None/0 교정)")
    
    refined_data = {}

    for vid, places in verified_results.items():
        if not isinstance(places, list) or not places:
            log("step4", f"⚠️ [{vid}] 데이터가 비어있어 건너뜁니다.")
            continue

        corrected_places = []
        
        # ✅ 방어 로직: p.get('day')가 None일 경우를 대비해 1로 간주하고 체크
        # (TypeError: '<=' not supported between NoneType and int 에러 방지)
        has_day_zero = any((p.get('day') if p.get('day') is not None else 1) == 0 for p in places)

        for p in places:
            # ✅ 보정: day가 None이면 기본값 1 부여
            raw_day = p.get('day')
            if raw_day is None:
                current_day = 1
            else:
                try:
                    current_day = int(raw_day)
                except (ValueError, TypeError):
                    current_day = 1
            
            # 1. Day 0이 포함된 영상이라면 전체적으로 +1일 (0->1, 1->2 ...)
            # 2. 단순히 0만 있는 경우에도 1로 상향 조정
            if has_day_zero:
                p['day'] = current_day + 1
            elif current_day <= 0:
                p['day'] = 1
            else:
                p['day'] = current_day # 정상적인 경우 유지
                
            corrected_places.append(p)
            
        refined_data[vid] = corrected_places
        log("step4", f"✅ [{vid}] 정제 완료: {len(corrected_places)}개 장소 (Day 교정 완료)")

    return refined_data