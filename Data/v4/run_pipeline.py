from __future__ import annotations

import os

import re

import config
from pipeline.step0_collect_videos import run as step0
from pipeline.step1_collect_materials import run as step1
from pipeline.step2_build_itinerary_llm import run as step2
from pipeline.step2_5_normalize_keywords import run as step2_5
from pipeline.step3_naver_verify_places import run as step3
from pipeline.step4_sort_timeline import run as step4
from pipeline.step5_map_debug import run as step5
from utils.logging_utils import log


def _bootstrap_env():
    # gemini_client는 환경변수를 우선 사용 (공식 SDK도 env를 지원)
    # config에 키를 둔 경우에도 자동 세팅해서 충돌을 줄임
    if not os.getenv("GEMINI_API_KEY") and getattr(config, "GEMINI_API_KEY", None):
        os.environ["GEMINI_API_KEY"] = str(getattr(config, "GEMINI_API_KEY"))
    if not os.getenv("GEMINI_MODEL") and getattr(config, "GEMINI_MODEL", None):
        os.environ["GEMINI_MODEL"] = str(getattr(config, "GEMINI_MODEL"))


def _normalize_region_input(region: str) -> str:
    """Normalize user region input without per-city hardcoding.

    - keeps only the first whitespace token (e.g., "제주 제주도" -> "제주")
    - strips common administrative suffixes (e.g., "제주도" -> "제주")
    """
    r = (region or "").strip()
    if not r:
        return ""

    r = r.split()[0]

    # strip common suffixes repeatedly
    suffixes = [
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

    core = r
    changed = True
    while changed:
        changed = False
        for suf in suffixes:
            if core.endswith(suf) and len(core) > len(suf):
                core = core[: -len(suf)]
                changed = True
                break

    return core


def _infer_region_from_keyword(keyword: str) -> str:
    """Best-effort region inference from the keyword when the user leaves region blank.

    This does NOT maintain a city list; it only tries to extract the first token that looks like a region.
    """
    k = (keyword or "").strip()
    if not k:
        return ""

    # take the first token (e.g., "제주도 vlog" -> "제주도")
    first = k.split()[0]
    # If first token is too short or looks like noise (e.g., "ㅈ제"), ignore it.
    if not re.search(r"[가-힣]", first):
        return ""

    return _normalize_region_input(first)


def main():
    _bootstrap_env()
    log("pipeline", "start")
    # Fail fast if required env vars are missing
    if hasattr(config, "validate_required_keys"):
        config.validate_required_keys()

    keyword = input("YouTube 검색 키워드를 입력하세요: ").strip()
    # collapse multiple spaces and remove accidental whitespace
    keyword = " ".join(keyword.split())
    if not keyword:
        log("pipeline", "empty keyword, abort")
        return

    region = input("지역(region)을 입력하세요 (예: 제주, 부산) [엔터=자동]: ").strip()
    region = _normalize_region_input(region) if region else _infer_region_from_keyword(keyword)

    # Make Step0 search region-aware without changing Step0 signature.
    # If keyword already contains the region, don't duplicate.
    if region and region not in keyword:
        keyword_for_search = f"{region} {keyword}".strip()
    else:
        keyword_for_search = keyword

    print(f"[pipeline] region={region or 'N/A'}")

    limit_raw = input("가져올 영상 수 (기본 5): ").strip()
    limit = int(limit_raw) if limit_raw.isdigit() else 5

    videos = step0(keyword=keyword_for_search, max_results=limit, region_tag=region)
    materials = step1(videos)
    places_raw = step2(materials)
    places_norm = step2_5(places_raw)
    verified = step3(places_norm, region=region)
    timeline = step4(verified)
    final_all = step5(timeline)

    log("pipeline", "end", total_videos=final_all.get("total_videos"))


if __name__ == "__main__":
    main()
