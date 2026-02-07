import os
import re
import requests
from pathlib import Path
from typing import List, Dict, Any
import config
from utils.io import save_json
from utils.logging_utils import log

def _has_timeline(desc: str) -> bool:
    """설명란에 시간 정보가 있는지 확인"""
    return bool(re.search(r'\d{1,2}:\d{2}', desc))

def _detect_day_context(desc: str) -> bool:
    """설명란에 날짜 관련 키워드가 있는지 확인"""
    pattern = r'(?:Day\s*\d|\d일차|첫째\s*날|둘째\s*날|셋째\s*날|마지막\s*날)'
    return bool(re.search(pattern, desc, re.IGNORECASE))

def run(keyword: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """유튜브 API를 통해 영상을 수집합니다. (인자 구조 수정 완료)"""
    log("step0", f"🚀 유튜브 영상 수집 가동: {keyword}")
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        log("step0", "❌ YOUTUBE_API_KEY가 없습니다. 환경변수나 config를 확인하세요.")
        return []
        
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": keyword,
        "type": "video",
        "maxResults": 50,
        "key": api_key,
        "regionCode": "KR",
        "relevanceLanguage": "ko"
    }
    
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        items = r.json().get("items", [])
    except Exception as e:
        log("step0", f"❌ API 호출 실패: {e}")
        return []
    
    out = []
    for it in items:
        vid = it.get("id", {}).get("videoId")
        if not vid: continue
        
        sn = it.get("snippet", {})
        title = sn.get("title", "")
        desc = sn.get("description", "")
        
        # 옴니버스 필터링 (팀장님 기준 준수)
        if any(bad in title.lower() for bad in ["best", "top", "모음", "순위", "정리", "랭킹"]):
            continue
            
        out.append({
            "video_id": vid,
            "title": title,
            "description": desc,
            "has_timeline": _has_timeline(desc),
            "has_day_context": _detect_day_context(desc)
        })
        if len(out) >= max_results:
            break
            
    # 데이터 폴더 생성 및 저장
    Path("data").mkdir(exist_ok=True)
    save_json("data/step0_videos.json", out)
    return out