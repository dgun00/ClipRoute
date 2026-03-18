import requests
import re
import html
import random
from pathlib import Path
from typing import Any, Dict, List, Optional
from utils.io import save_json
from utils.logging_utils import log
from utils.similarity import similarity
import config

def _strip_html(text: str) -> str:
    if not text:
        return ""
    # HTML 태그 제거 및 언이스케이프 처리
    clean = re.sub(r'<[^>]*>', '', text)
    return html.unescape(clean).strip()

def _get_naver_headers() -> Dict[str, str]:
    cid = getattr(config, 'NAVER_CLIENT_ID', None)
    secret = getattr(config, 'NAVER_CLIENT_SECRET', None)
    if not cid or not secret:
        raise RuntimeError("config.NAVER_CLIENT_ID 또는 NAVER_CLIENT_SECRET이 설정되지 않았습니다.")
    return {
        "X-Naver-Client-Id": cid,
        "X-Naver-Client-Secret": secret
    }

def _search_local(query: str, display: int = 5) -> List[Dict[str, Any]]:
    url = "https://openapi.naver.com/v1/search/local.json"
    params = {
        "query": query,
        "display": display,
        "sort": "random"
    }
    try:
        res = requests.get(url, headers=_get_naver_headers(), params=params, timeout=10)
        res.raise_for_status()
        items = res.json().get('items', [])
        
        results = []
        for item in items:
            results.append({
                "title": _strip_html(item.get('title', '')),
                "category": item.get('category', ''),
                "description": item.get('description', ''),
                "address": item.get('address', ''),
                "road_address": item.get('roadAddress', ''),
                "mapx": item.get('mapx', ''),
                "mapy": item.get('mapy', ''),
                "link": item.get('link', '')
            })
        return results
    except Exception as e:
        log(f"❌ Naver API 오류: {e}")
        return []

def _pick_best(search_name: str, candidates: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not candidates:
        return None
    
    best_node = None
    best_score = -1.0
    
    threshold = getattr(config, 'NAVER_SIM_THRESHOLD', 0.6)

    for cand in candidates:
        # 제목 기반 유사도 측정
        score = similarity(search_name, cand['title'])
        if score > best_score:
            best_score = score
            best_node = cand
            
    if best_node and best_score >= threshold:
        best_node['score'] = best_score
        return best_node
    return None

def run(normalized_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    log("🚀 Step 3: 네이버 API 기반 장소 검증 및 상세 정보 수집 시작")
    
    if not getattr(config, 'ENABLE_NAVER', True):
        log("⚠️ ENABLE_NAVER=False; 네이버 검증 단계를 건너뜁니다.")
        return {item['video_id']: {"video_id": item['video_id'], "verified_places": []} for item in normalized_data}

    out_dir = Path("data")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    final_results = {}

    for entry in normalized_data:
        v_id = entry.get('video_id')
        keywords = entry.get('normalized_keywords', [])
        verified_list = []

        log(f"🔍 [{v_id}] 장소 검증 중...")
        
        for kw in keywords:
            candidates = _search_local(kw)
            best = _pick_best(kw, candidates)
            
            if best:
                verified_list.append(best)
                log(f"✅ 검증 성공: [{kw}] -> [{best['title']}] (유사도: {best.get('score', 0):.2f})")
            else:
                log(f"❓ 검증 실패 또는 검색 결과 없음: [{kw}]")

        final_results[v_id] = {
            "video_id": v_id,
            "verified_places": verified_list
        }

    save_path = out_dir / "step3_naver_verified.json"
    save_json(final_results, str(save_path))
    log(f"✅ Step 3 완료! 검증된 데이터 저장: {save_path}")
    
    return final_results