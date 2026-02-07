from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import json
import config
from utils.io import save_json
from utils.logging_utils import log


def _to_float(x: Any) -> Optional[float]:
    if x is None:
        return None
    try:
        return float(x)
    except Exception:
        return None


def _extract_latlng(p: dict) -> Tuple[Optional[float], Optional[float]]:
    """mapx/mapy -> (lat, lng)

    - 2023-08-25 이후 Naver 지역검색은 WGS84*1e7 좌표로 변경된 공지가 있음.
      (mapx=longitude*1e7, mapy=latitude*1e7) 기준으로 변환.
    - 혹시 구좌표계(작은 값)면 변환 불가로 None 처리.
    """
    mapx = p.get("mapx")
    mapy = p.get("mapy")
    if (not mapx or not mapy) and isinstance(p.get("naver_top"), dict):
        mapx = p["naver_top"].get("mapx")
        mapy = p["naver_top"].get("mapy")

    fx = _to_float(mapx)
    fy = _to_float(mapy)
    if fx is None or fy is None:
        return None, None

    # WGS84*1e7이면 보통 1e8 ~ 1e9 규모
    if abs(fx) >= 1e8 and abs(fy) >= 1e8:
        lng = fx / 1e7
        lat = fy / 1e7
        return lat, lng

    return None, None


def run(verified: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Step4: day/order/seconds 기준으로 정렬된 최종 타임라인 생성."""
    data_dir = Path(getattr(config, "DATA_DIR", "data"))
    out_dir = data_dir / "step4_timeline_sorted"
    out_dir.mkdir(parents=True, exist_ok=True)

    # step1 결과에서 video_id -> title 매핑을 만들어 로그/디버그 가독성을 높임
    title_map: Dict[str, str] = {}
    try:
        step1_path = data_dir / "step1_materials.json"
        if step1_path.exists():
            with step1_path.open("r", encoding="utf-8") as f:
                step1_items = json.load(f)
            if isinstance(step1_items, list):
                for it in step1_items:
                    vid = (it or {}).get("video_id")
                    ttl = ((it or {}).get("title") or "").strip()
                    if vid and ttl:
                        title_map[vid] = ttl
    except Exception:
        title_map = title_map

    if verified is None:
        raise ValueError("step4_sort_timeline.run: verified is required")

    results: Dict[str, Dict[str, Any]] = {}

    for vid, payload in verified.items():
        # title 우선순위: step3 payload(title) -> step1 title_map
        title = ((payload or {}).get("title") or (payload or {}).get("stats", {}).get("title") or title_map.get(vid, "")).strip()
        if title:
            log("step4", "video", video_id=vid, title=title)

        places = (payload or {}).get("verified_places") or []

        final_places: List[dict] = []
        for p in places:
            lat, lng = _extract_latlng(p)
            final_places.append(
                {
                    "day": int(p.get("day") or 1),
                    "order": int(p.get("order") or 9999),
                    "seconds": p.get("seconds"),
                    "original_phrase": p.get("original_phrase"),
                    "place_name": p.get("place_name"),
                    "search_name": p.get("search_name"),
                    "lat": lat,
                    "lng": lng,
                    "address": p.get("address") or (p.get("naver_top") or {}).get("address"),
                    "road_address": p.get("road_address") or (p.get("naver_top") or {}).get("road_address"),
                    "visit_confidence": p.get("visit_confidence"),
                    "visit_reason": p.get("visit_reason"),
                    "similarity": p.get("similarity"),
                    "source": p.get("source"),
                    "naver_top": p.get("naver_top"),
                }
            )

        final_places.sort(
            key=lambda x: (
                x["day"],
                x["order"],
                x["seconds"] if x["seconds"] is not None else 1_000_000,
            )
        )

        result = {
            "video_id": vid,
            "title": title,
            "final_places": final_places,
            "count": len(final_places),
        }
        results[vid] = result

        save_json(out_dir / f"final_places_{vid}.json", result)
        log("step4", "saved", video_id=vid, title=title, count=len(final_places))

    log("step4", "done", videos=len(results))
    return results
