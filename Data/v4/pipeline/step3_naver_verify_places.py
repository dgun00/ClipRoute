from __future__ import annotations

import html
import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

import config
from utils.io import save_json
from utils.logging_utils import log
from utils.similarity import similarity



_URL = "https://openapi.naver.com/v1/search/local.json"

_REGION_SUFFIXES = [
    "특별자치도",
    "특별자치시",
    "자치도",
    "특별시",
    "광역시",
    "특별자치구",
    "시",
    "도",
    "군",
    "구",
]

def _normalize_region(region: Optional[str]) -> Dict[str, str]:
    """Normalize region input without maintaining city-specific lists.

    - Uses the first whitespace token.
    - Strips common administrative suffixes.
    """
    raw = (region or "").strip()
    if not raw:
        return {"raw": "", "core": ""}

    # keep the first token to avoid inputs like "제주 제주도"
    raw = raw.split()[0]

    core = raw
    # strip common suffixes repeatedly
    changed = True
    while changed:
        changed = False
        for suf in _REGION_SUFFIXES:
            if core.endswith(suf) and len(core) > len(suf):
                core = core[: -len(suf)]
                changed = True
                break

    return {"raw": raw, "core": core}


def _candidate_in_region(candidate: Dict[str, Any], region_raw: str, region_core: str) -> bool:
    """Return True if candidate address looks like it belongs to the region.

    Uses substring match against both region_raw and region_core.
    """
    addr = (candidate.get("road_address") or "") + " " + (candidate.get("address") or "")
    addr = addr.strip()
    if not addr:
        return False

    # Prefer core (e.g., "제주" matches "제주특별자치도")
    if region_core and region_core in addr:
        return True

    # Fallback to raw (e.g., "서울" matches "서울특별시")
    if region_raw and region_raw in addr:
        return True

    return False


def _strip_html(s: str) -> str:
    if not s:
        return ""
    s = html.unescape(s)
    s = re.sub(r"<[^>]+>", "", s)
    return s.strip()


def _naver_headers() -> Dict[str, str]:
    cid = getattr(config, "NAVER_CLIENT_ID", None)
    secret = getattr(config, "NAVER_CLIENT_SECRET", None)
    if not cid or not secret:
        raise RuntimeError("config.NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 가 필요합니다.")
    return {
        "X-Naver-Client-Id": cid,
        "X-Naver-Client-Secret": secret,
    }


def _search_local(query: str, *, display: int = 5, sort: str = "comment") -> List[Dict[str, Any]]:
    r = requests.get(
        _URL,
        headers=_naver_headers(),
        params={"query": query, "display": display, "start": 1, "sort": sort},
        timeout=15,
    )
    r.raise_for_status()
    items = r.json().get("items", [])
    out: List[Dict[str, Any]] = []
    for it in items:
        title = _strip_html(it.get("title", ""))
        out.append(
            {
                "title": title,
                "category": it.get("category"),
                "description": it.get("description"),
                "address": it.get("address"),
                "road_address": it.get("roadAddress"),
                "mapx": it.get("mapx"),
                "mapy": it.get("mapy"),
                "link": it.get("link"),
            }
        )
    return out


def _pick_best(search_name: str, candidates: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    best = None
    best_score = -1.0
    for c in candidates:
        score = similarity(search_name, c.get("title") or "")
        if score > best_score:
            best_score = score
            best = dict(c)
            best["similarity"] = score
    return best


def run(norm: Dict[str, List[dict]], *, region: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """Step3: 네이버 지역검색으로 존재 검증 + 주소/좌표 확보.

    입력: {video_id: [ ... place dict ... ]}
    출력: {video_id: {video_id, verified_places:[...]}}
    """
    data_dir = Path(getattr(config, "DATA_DIR", "data"))
    out_dir = data_dir / "step3_naver_verified"
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

    if norm is None:
        raise ValueError("step3_naver_verify_places.run: norm is required")

    # region filtering (no city-specific hardcoding)
    region_info = _normalize_region(region or getattr(config, "TARGET_REGION", None))
    region_raw = region_info["raw"]
    region_core = region_info["core"]
    enforce_region = bool(getattr(config, "ENFORCE_REGION_MATCH", True)) and bool(region_core or region_raw)

    naver_limit = int(getattr(config, "NAVER_SEARCH_LIMIT", 5))
    naver_sort = str(getattr(config, "NAVER_SORT", "comment"))
    rate_sleep = float(getattr(config, "NAVER_RATE_SLEEP_SEC", 0.0))
    sim_threshold = float(getattr(config, "NAVER_SIM_THRESHOLD", 0.55))

    enable = bool(getattr(config, "ENABLE_NAVER", True))
    if not enable:
        log("step3", "ENABLE_NAVER=False; skipping")
        # 그대로 감싸서 다음 스텝이 깨지지 않게
        wrapped: Dict[str, Dict[str, Any]] = {
            vid: {"video_id": vid, "verified_places": places}
            for vid, places in norm.items()
        }
        for vid, payload in wrapped.items():
            save_json(out_dir / f"naver_verified_{vid}.json", payload)
        return wrapped

    results: Dict[str, Dict[str, Any]] = {}

    for video_id, places in norm.items():
        title = title_map.get(video_id, "")
        if title:
            log("step3", "video", video_id=video_id, title=title)

        verified: List[dict] = []
        stats = {
            "video_id": video_id,
            "title": title,
            "region_raw": region_raw,
            "region_core": region_core,
            "enforce_region": enforce_region,
            "api_error": 0,
            "no_candidates": 0,
            "region_filtered_out": 0,
            "sim_low": 0,
            "kept": 0,
            "region_filtered_out_examples": [],
        }

        for p in places:
            search_name = (p.get("search_name") or "").strip()
            if not search_name:
                continue

            # region-aware query
            query = f"{region_core or region_raw} {search_name}".strip() if (region_core or region_raw) else search_name

            try:
                candidates = _search_local(query, display=naver_limit, sort=naver_sort)
            except Exception as e:
                log("step3", "naver api error", video_id=video_id, title=title, query=query, err=str(e)[:200])
                stats["api_error"] += 1
                continue
            finally:
                if rate_sleep > 0:
                    time.sleep(rate_sleep)

            if not candidates:
                stats["no_candidates"] += 1
                continue

            if enforce_region:
                before = len(candidates)
                candidates = [c for c in candidates if _candidate_in_region(c, region_raw, region_core)]
                if not candidates:
                    stats["region_filtered_out"] += 1
                    # keep a small trace for debugging
                    stats["region_filtered_out_examples"].append({"title": title, "search_name": search_name, "query": query, "before": before})
                    continue

            top = _pick_best(search_name, candidates)

            # 보수적으로: 유사도가 너무 낮으면 drop
            top_sim = (top or {}).get("similarity") if top else None
            if top is None or (top_sim is not None and top_sim < sim_threshold):
                stats["sim_low"] += 1
                continue

            verified.append(
                {
                    **p,
                    "naver_candidates": candidates,
                    "naver_top": top,
                    "similarity": top_sim,
                    "address": (top or {}).get("address"),
                    "road_address": (top or {}).get("road_address"),
                    "mapx": (top or {}).get("mapx"),
                    "mapy": (top or {}).get("mapy"),
                }
            )
            stats["kept"] += 1

        payload = {
            "video_id": video_id,
            "title": title,
            "verified_places": verified,
            "stats": stats,
        }
        results[video_id] = payload

        save_json(out_dir / f"naver_verified_{video_id}.json", payload)
        log("step3", "verified", video_id=video_id, title=title, count=len(verified), region=region_core or region_raw, enforce_region=enforce_region)

    return results
