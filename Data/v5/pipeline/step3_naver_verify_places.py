import os
import time
import requests
import re
from typing import Dict, List, Any, Optional
from utils.io import save_json
from utils.logging_utils import log

def search_naver_place(query: str) -> Optional[Dict[str, Any]]:
    client_id = os.getenv("NAVER_CLIENT_ID")
    client_secret = os.getenv("NAVER_CLIENT_SECRET")
    if not client_id or not client_secret: return None

    url = "https://openapi.naver.com/v1/search/local.json"
    headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
    try:
        resp = requests.get(url, headers=headers, params={"query": query, "display": 1}, timeout=5)
        if resp.status_code == 200:
            items = resp.json().get("items", [])
            if items:
                item = items[0]
                return {
                    "title": re.sub(r'<[^>]*>', '', item.get("title", "")),
                    "address": item.get("address"),
                    "mapx": item.get("mapx"),
                    "mapy": item.get("mapy")
                }
    except: return None
    return None

def run(places_dict: Dict[str, Any], region: str = "제주") -> Dict[str, List[dict]]:
    verified_results = {}
    total_found = 0
    actual_data = places_dict.get("itinerary", places_dict)

    for video_id, content in actual_data.items():
        if isinstance(content, dict):
            places = content.get("places", content.get("itinerary", []))
        else:
            places = content if isinstance(content, list) else []

        valid_places = []
        for p in (places or []):
            if isinstance(p, str): # AttributeError 방어
                p = {"place_name": p, "search_candidates": [p], "day": 1}
            
            candidates = p.get("search_candidates", [])
            p_name = p.get("place_name", "")
            if p_name and p_name not in candidates: candidates.append(p_name)

            for query in candidates:
                res = search_naver_place(f"{region} {query}")
                if res:
                    p.update({"verified_name": res["title"], "address": res["address"], "map_x": res["mapx"], "map_y": res["mapy"], "is_verified": True})
                    valid_places.append(p); total_found += 1
                    break
                time.sleep(0.06)
        verified_results[video_id] = valid_places
    save_json("data/step3_verified_places.json", verified_results)
    return verified_results