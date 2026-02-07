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
    """Return True if candidate looks like it belongs to the region.

    Primary signal: address/road_address contains the region token.
    Fallback signal (only when address fields are empty): title/category contains the region token.

    Note: we intentionally avoid maintaining any city list (no hardcoding).
    """
    addr = f"{candidate.get('road_address') or ''} {candidate.get('address') or ''}".strip()
    if addr:
        if region_core and region_core in addr:
            return True
        if region_raw and region_raw in addr:
            return True
        return False

    title = (candidate.get("title") or "").strip()
    cat = (candidate.get("category") or "").strip()
    hay = f"{title} {cat}".strip()
    if region_core and region_core in hay:
        return True
    if region_raw and region_raw in hay:
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

def _soft_match(search_name: str, title: str) -> bool:
    """Looser match to avoid false negatives for short brand names.

    - strip spaces/punct
    - allow substring match (e.g., '점점' vs '점점서점')
    """
    a = (search_name or "").strip()
    b = (title or "").strip()
    if not a or not b:
        return False

    # normalize: remove whitespace and common punctuation
    a_n = re.sub(r"[\s\-_.·,()\[\]{}<>/\\]+", "", a)
    b_n = re.sub(r"[\s\-_.·,()\[\]{}<>/\\]+", "", b)

    if not a_n or not b_n:
        return False

    # exact / substring
    if a_n == b_n:
        return True
    if a_n in b_n or b_n in a_n:
        return True

    return False


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
    debug_refetch_for_examples = bool(getattr(config, "NAVER_DEBUG_REFETCH_FOR_EXAMPLES", False))
    # Default lowered a bit to reduce false negatives for short brand names
    sim_threshold = float(getattr(config, "NAVER_SIM_THRESHOLD", 0.50))

    # When region filtering cannot be decided from address fields, require stronger name similarity
    region_strict_sim = float(getattr(config, "NAVER_REGION_STRICT_SIM", 0.75))

    # If a region-prefixed query returns nothing, retry once without region (still later filtered by region logic)
    fallback_no_region_on_empty = bool(getattr(config, "NAVER_FALLBACK_NO_REGION_ON_EMPTY", True))

    query_has_region = bool(region_core or region_raw)

    # Soft-rescue tuning (avoid hardcoding)
    soft_rescue_enabled = bool(getattr(config, "NAVER_SOFT_RESCUE_ENABLED", True))
    soft_len_min = int(getattr(config, "NAVER_SOFT_RESCUE_LEN_MIN", 2))
    soft_len_max = int(getattr(config, "NAVER_SOFT_RESCUE_LEN_MAX", 4))
    soft_sim_floor = float(getattr(config, "NAVER_SOFT_RESCUE_SIM_FLOOR", 0.35))
    soft_sim_delta = float(getattr(config, "NAVER_SOFT_RESCUE_SIM_DELTA", 0.15))
    soft_keep_max = int(getattr(config, "NAVER_SOFT_RESCUE_KEEP_MAX", 3))

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
        dropped: List[dict] = []  # keep dropped items for debugging / later review
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
            "forced_kept": 0,
            "region_filtered_out_examples": [],
            "no_candidates_examples": [],
            "sim_low_examples": [],
            "dropped_saved": 0,
            "dropped_reasons": {
                "no_candidates": 0,
                "region_filtered_out": 0,
                "sim_low": 0,
                "api_error": 0,
                "forced_keep": 0,
            },
        }

        for p in places:
            search_name = (p.get("search_name") or "").strip()
            if not search_name:
                continue

            # Strong hints should not be dropped easily (title/description/chapter seeded, or explicit must_keep)
            must_keep = bool(
                p.get("must_keep")
                or (str(p.get("source") or "").lower() in {"title", "description", "desc", "chapters"})
                or (float(p.get("source_weight") or 0) >= 2.0)
            )

            sim_threshold_eff = sim_threshold
            region_relaxed = False

            # Multi-query strategy:
            # 1) region-prefixed query (core/raw)
            # 2) plain search_name
            # 3) space-stripped search_name (helps cases like "아베베 베이커리" vs "아베베베이커리")
            queries: List[str] = []
            if region_core or region_raw:
                prefix = (region_core or region_raw).strip()
                if prefix:
                    queries.append(f"{prefix} {search_name}".strip())
            queries.append(search_name)
            compact = re.sub(r"\s+", "", search_name)
            if compact and compact != search_name:
                queries.append(compact)

            candidates: List[Dict[str, Any]] = []
            used_queries: List[str] = []

            for q in queries:
                if not q:
                    continue
                try:
                    got = _search_local(q, display=naver_limit, sort=naver_sort)
                    used_queries.append(q)
                    if got:
                        candidates.extend(got)
                except Exception as e:
                    # keep dropped item (api error) but continue to try other queries
                    if len(dropped) < 50:
                        try:
                            dropped.append({
                                **p,
                                "_drop_reason": "api_error",
                                "_query": q,
                                "_error": str(e)[:200],
                            })
                            stats["dropped_saved"] += 1
                            stats["dropped_reasons"]["api_error"] += 1
                        except Exception:
                            pass

                    log("step3", "naver api error", video_id=video_id, title=title, query=q, err=str(e)[:200])
                    stats["api_error"] += 1
                finally:
                    if rate_sleep > 0:
                        time.sleep(rate_sleep)

            # de-duplicate candidates by (title, address, road_address)
            if candidates:
                seen = set()
                uniq: List[Dict[str, Any]] = []
                for c in candidates:
                    key = (
                        (c.get("title") or "").strip(),
                        (c.get("address") or "").strip(),
                        (c.get("road_address") or "").strip(),
                    )
                    if key in seen:
                        continue
                    seen.add(key)
                    uniq.append(c)
                candidates = uniq

            # for debugging, remember what we tried
            query = used_queries[0] if used_queries else (queries[0] if queries else search_name)

            if not candidates:
                # Retry once without region prefix if the region-prefixed query returned nothing.
                if fallback_no_region_on_empty and query_has_region and query != search_name:
                    try:
                        candidates = _search_local(search_name, display=naver_limit, sort=naver_sort)
                    except Exception:
                        candidates = []
                    finally:
                        if rate_sleep > 0:
                            time.sleep(rate_sleep)

                # Still no candidates
                if not candidates:
                    # Strong hints should survive even if Naver returns nothing
                    if must_keep:
                        verified.append(
                            {
                                **p,
                                "naver_candidates": [],
                                "naver_top": None,
                                "similarity": None,
                                "_similarity_rescued": False,
                                "_region_relaxed": False,
                                "_sim_threshold_eff": sim_threshold_eff,
                                "_force_keep": True,
                                "_queries_tried": used_queries,
                                "address": None,
                                "road_address": None,
                                "mapx": None,
                                "mapy": None,
                            }
                        )
                        stats["kept"] += 1
                        stats["forced_kept"] += 1
                        stats["dropped_reasons"]["forced_keep"] += 1
                        continue

                    try:
                        if len(dropped) < 50:
                            dropped.append(
                                {
                                    **p,
                                    "_drop_reason": "no_candidates",
                                    "_query": query,
                                    "_fallback_query": (
                                        search_name
                                        if (
                                            fallback_no_region_on_empty
                                            and query_has_region
                                            and query != search_name
                                        )
                                        else None
                                    ),
                                    "naver_candidates": [],
                                    "naver_top": None,
                                }
                            )
                            stats["dropped_saved"] += 1
                            stats["dropped_reasons"]["no_candidates"] += 1
                    except Exception:
                        pass

                    stats["no_candidates"] += 1
                    if len(stats.get("no_candidates_examples", [])) < 20:
                        stats["no_candidates_examples"].append(
                            {
                                "search_name": search_name,
                                "query": query,
                            }
                        )
                    continue


            if enforce_region:
                before = len(candidates)
                in_region = [c for c in candidates if _candidate_in_region(c, region_raw, region_core)]

                if in_region:
                    candidates = in_region
                else:
                    # Some API responses provide shortened addresses that may not include the region token.
                    # If we searched with a region-prefixed query, do not drop everything; instead,
                    # keep candidates but require stronger name similarity to avoid cross-region false matches.
                    if query_has_region:
                        region_relaxed = True
                        sim_threshold_eff = max(sim_threshold, region_strict_sim) if not must_keep else sim_threshold
                    else:
                        try:
                            if len(dropped) < 50:
                                dropped.append({
                                    **p,
                                    "_drop_reason": "region_filtered_out",
                                    "_query": query,
                                    "naver_candidates": [],
                                    "naver_top": None,
                                    "_before": before,
                                })
                                stats["dropped_saved"] += 1
                                stats["dropped_reasons"]["region_filtered_out"] += 1
                        except Exception:
                            pass

                        stats["region_filtered_out"] += 1
                        continue

            top = _pick_best(search_name, candidates)

            # 보수적으로: 유사도가 너무 낮으면 drop
            top_sim = (top or {}).get("similarity") if top else None

            # soft rescue for short brands / substring match
            rescue = False
            if soft_rescue_enabled and top is not None and top_sim is not None and top_sim < sim_threshold_eff:
                title_top = (top or {}).get("title") or ""
                if _soft_match(search_name, title_top):
                    name_len = len(search_name)
                    # 1) 짧은 상호(설정 범위)면 구제
                    if soft_len_min <= name_len <= soft_len_max:
                        rescue = True
                    # 2) 임계치보다 약간 낮은 경우(설정 델타)면 구제, 단 최소 바닥값도 적용
                    if top_sim >= max(soft_sim_floor, sim_threshold_eff - soft_sim_delta):
                        rescue = True

            if top is None or (top_sim is not None and top_sim < sim_threshold_eff and not rescue and not must_keep):
                try:
                    if len(dropped) < 50:
                        dropped.append({
                            **p,
                            "_drop_reason": "sim_low",
                            "_query": query,
                            "naver_candidates": candidates,
                            "naver_top": top,
                            "similarity": top_sim,
                        })
                        stats["dropped_saved"] += 1
                        stats["dropped_reasons"]["sim_low"] += 1
                except Exception:
                    pass

                stats["sim_low"] += 1
                if len(stats.get("sim_low_examples", [])) < 20:
                    stats["sim_low_examples"].append({
                        "search_name": search_name,
                        "query": query,
                        "top_title": (top or {}).get("title") if top else "",
                        "top_similarity": top_sim,
                        "region_raw": region_raw,
                        "region_core": region_core,
                    })
                continue

            # Force-keep for strong hints: accept the best candidate even if similarity is below threshold
            # (still guarded by a minimum floor to reduce obvious false matches)
            if must_keep and top is not None and top_sim is not None and top_sim < sim_threshold_eff:
                # require at least a loose signal: soft match OR minimum similarity floor
                if _soft_match(search_name, (top.get("title") or "")) or top_sim >= soft_sim_floor:
                    rescue = True
                else:
                    # if it is a strong hint but nothing matches, keep without attaching a wrong candidate
                    verified.append(
                        {
                            **p,
                            "naver_candidates": candidates,
                            "naver_top": top,
                            "similarity": top_sim,
                            "_similarity_rescued": False,
                            "_region_relaxed": bool(region_relaxed),
                            "_sim_threshold_eff": sim_threshold_eff,
                            "_force_keep": True,
                            "_queries_tried": used_queries,
                            "address": None,
                            "road_address": None,
                            "mapx": None,
                            "mapy": None,
                        }
                    )
                    stats["kept"] += 1
                    stats["forced_kept"] += 1
                    continue

                # rescued with candidate
                verified.append(
                    {
                        **p,
                        "naver_candidates": candidates,
                        "naver_top": top,
                        "similarity": top_sim,
                        "_similarity_rescued": True,
                        "_region_relaxed": bool(region_relaxed),
                        "_sim_threshold_eff": sim_threshold_eff,
                        "_force_keep": True,
                        "_queries_tried": used_queries,
                        "address": (top or {}).get("address"),
                        "road_address": (top or {}).get("road_address"),
                        "mapx": (top or {}).get("mapx"),
                        "mapy": (top or {}).get("mapy"),
                    }
                )
                stats["kept"] += 1
                stats["forced_kept"] += 1
                continue

            verified.append(
                {
                    **p,
                    "naver_candidates": candidates,
                    "naver_top": top,
                    "similarity": top_sim,
                    "_similarity_rescued": bool(rescue),
                    "_region_relaxed": bool(region_relaxed),
                    "_sim_threshold_eff": sim_threshold_eff,
                    "_queries_tried": used_queries,
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
            "dropped_places": dropped,
            "stats": {
                **stats,
                "soft_rescue": {
                    "enabled": soft_rescue_enabled,
                    "len_min": soft_len_min,
                    "len_max": soft_len_max,
                    "sim_floor": soft_sim_floor,
                    "sim_delta": soft_sim_delta,
                    "keep_max": soft_keep_max,
                },
            },
        }
        results[video_id] = payload

        save_json(out_dir / f"naver_verified_{video_id}.json", payload)
        log("step3", "verified", video_id=video_id, title=title, count=len(verified), region=region_core or region_raw, enforce_region=enforce_region)

    return results
