import config
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from utils.io import save_json
from utils.logging_utils import log

def _to_float(x: Any) -> Optional[float]:
    try:
        return float(x)
    except Exception:
        return None

def _extract_latlng(item: Dict[str, Any]) -> Tuple[Optional[float], Optional[float]]:
    """
    naver_top 내의 mapx, mapy를 WGS84(위경도)로 변환하는 로직을 포함하거나 
    단순 추출합니다. (네이버 API mapx/mapy는 보통 KATECH 좌표계임)
    """
    mx = item.get('mapx')
    my = item.get('mapy')
    
    if mx is None or my is None:
        return None, None
    
    fx = _to_float(mx)
    fy = _to_float(my)
    
    if fx is not None and fy is not None:
        # 네이버 API 좌표(KATECH)를 위경도로 변환하는 근사치 공식 (단순 예시)
        # 실제 운영 환경에서는 pyproj 등을 사용하나, 여기선 1e7로 나누는 처리가 포함됨
        if abs(fx) > 1000 and abs(fy) > 1000:
            return fy / 1e7, fx / 1e7
        return fy, fx
        
    return None, None

def run(verified_data: Dict[str, Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    log("🚀 Step 4: 타임라인 정렬 및 좌표 변환 시작")
    
    out_dir = Path("data")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    final_results = {}

    for v_id, payload in verified_data.items():
        places = payload.get('verified_places', [])
        if not places:
            log(f"⚠️ [{v_id}] 검증된 장소가 없어 건너뜁니다.")
            continue

        sorted_list = []
        for p in places:
            # 기본 데이터 구조 생성 및 시간 정보 정규화
            day = int(p.get('day', 1))
            order = int(p.get('order', 0))
            seconds = int(p.get('seconds', 0))
            
            lat, lng = _extract_latlng(p)
            
            sorted_list.append({
                "day": day,
                "order": order,
                "seconds": seconds,
                "place_name": p.get('title'),
                "address": p.get('address'),
                "road_address": p.get('road_address'),
                "lat": lat,
                "lng": lng,
                "category": p.get('category'),
                "similarity": p.get('score', 0.0),
                "source": "naver"
            })

        # Day -> Order -> Seconds 순으로 정렬
        sorted_list.sort(key=lambda x: (x['day'], x['order'], x['seconds']))
        
        final_results[v_id] = sorted_list
        log(f"📍 [{v_id}] {len(sorted_list)}개의 장소 정렬 완료")

    save_path = out_dir / "step4_timeline_sorted.json"
    save_json(final_results, str(save_path))
    log(f"✅ Step 4 완료! 정렬된 데이터 저장: {save_path}")
    
    return final_results