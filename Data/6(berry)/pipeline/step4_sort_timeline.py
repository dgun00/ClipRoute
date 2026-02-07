from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import json
import re

import config
from utils.io import save_json
from utils.logging_utils import log


def _norm_phrase(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def _is_obvious_non_place(phrase: str) -> bool:
    p = _norm_phrase(phrase).lower()
    if not p:
        return True

    # very common non-place tokens
    if "vlog" in p or "브이로그" in p:
        return True

    # trip-length / itinerary phrases
    if re.search(r"\d+\s*박\s*\d+\s*일", p):
        return True
    if "당일치기" in p or "코스" in p or "일정" in p:
        # allow if it also looks like a named POI (rare) -> handled by plausibility check later
        return True

    # recommendation / generic category phrases
    if "추천" in p and ("카페" in p or "맛집" in p or "편집샵" in p):
        return True

    # sentences or long fragments
    if len(p) >= 25 and p.count(" ") >= 2:
        return True

    return False


def _is_plausible_place_name(phrase: str) -> bool:
    p = _norm_phrase(phrase)
    if not p:
        return False

    # must contain at least one Korean character or letter
    if not re.search(r"[가-힣A-Za-z]", p):
        return False

    # too long with many spaces -> likely a sentence
    if len(p) >= 30 and p.count(" ") >= 2:
        return False

    # reject obvious non-place
    if _is_obvious_non_place(p):
        return False

    # very short single-syllable Korean words are usually ambiguous (e.g., '오른' can be real; keep)
    # so do not reject by length alone.
    return True


def _to_float(x: Any) -> Optional[float]:
    if x is None:
        return None
    try:
        return float(x)
    except Exception:
        return None


def _parse_timecode_seconds(x: Any) -> Optional[float]:
    """Parse seconds from either numeric or timecode strings.

    Accepts:
    - float/int seconds
    - "HH:MM:SS(.mmm)" or "MM:SS(.mmm)" strings
    """
    if x is None:
        return None

    if isinstance(x, (int, float)):
        return float(x)

    if isinstance(x, str):
        s = x.strip()
        if not s:
            return None

        # pure number string
        try:
            return float(s)
        except Exception:
            pass

        m = re.match(r"^(?:(\d+):)?(\d{1,2}):(\d{2})(?:\.(\d+))?$", s)
        if not m:
            return None

        hh = int(m.group(1) or 0)
        mm = int(m.group(2) or 0)
        ss = int(m.group(3) or 0)
        frac = m.group(4) or ""
        ms = 0.0
        if frac:
            frac = (frac + "000")[:3]
            ms = int(frac) / 1000.0

        return hh * 3600 + mm * 60 + ss + ms

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
        title = (
            (payload or {}).get("title")
            or (payload or {}).get("stats", {}).get("title")
            or title_map.get(vid, "")
        ).strip()
        if title:
            log("step4", "video", video_id=vid, title=title)

        places = (payload or {}).get("verified_places") or []

        final_places: List[dict] = []
        for p in places:
            lat, lng = _extract_latlng(p)

            sec = _parse_timecode_seconds(p.get("seconds"))
            # seed(제목/설명 기반) 후보가 seconds=0으로 들어오면 정렬/일자 추론을 망치므로 None으로 처리
            if p.get("source") == "seed" and (sec is None or sec <= 0):
                sec = None

            final_places.append(
                {
                    "day": int(p.get("day") or 1),
                    "order": int(p.get("order") or 9999),
                    "seconds": sec,
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

        # 정렬 정책:
        # 1) day 오름차순
        # 2) seconds가 있는 항목(실제 타임라인 근거) 먼저
        # 3) seconds 오름차순
        # 4) seconds가 없을 때만 order로 보조 정렬
        final_places.sort(
            key=lambda x: (
                x["day"],
                0 if x["seconds"] is not None else 1,
                x["seconds"] if x["seconds"] is not None else 1_000_000,
                x["order"],
            )
        )

        # ✅ order 재부여(드랍/필터 후에도 보기 좋게 1..N)
        # 요구사항: day마다 order를 다시 1..N으로 리셋하지 않고,
        # 전체 타임라인에서 order는 1..N 연속으로 증가시키되 day만 변경되도록 한다.
        # - order_raw: 원본(order) 보존
        # - day_order: day 내부에서의 순번(디버깅/표시용)
        global_order = 0
        day_counters: Dict[int, int] = {}
        for x in final_places:
            d = int(x.get("day") or 1)
            global_order += 1
            day_counters[d] = day_counters.get(d, 0) + 1

            x["order_raw"] = x.get("order")
            x["day_order"] = day_counters[d]
            x["order"] = global_order

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
