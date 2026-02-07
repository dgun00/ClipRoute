from __future__ import annotations

import os
import re

import config
from pipeline.step0_collect_videos import run as step0
from pipeline.step1_collect_materials import run as step1
from pipeline.step2_build_itinerary_llm import run as step2
from pipeline.step2_1_infer_days import run as step2_1
from pipeline.step2_5_normalize_keywords import run as step2_5
from pipeline.step3_naver_verify_places import run as step3
from pipeline.step4_sort_timeline import run as step4
from pipeline.step5_map_debug import run as step5
from utils.logging_utils import log


def _bootstrap_env():
    if not os.getenv("GEMINI_API_KEY") and getattr(config, "GEMINI_API_KEY", None):
        os.environ["GEMINI_API_KEY"] = str(getattr(config, "GEMINI_API_KEY"))
    if not os.getenv("GEMINI_MODEL") and getattr(config, "GEMINI_MODEL", None):
        os.environ["GEMINI_MODEL"] = str(getattr(config, "GEMINI_MODEL"))


def _normalize_region_input(region: str) -> str:
    r = (region or "").strip()
    if not r:
        return ""
    r = r.split()[0]

    suffixes = [
        "특별자치도", "특별자치시", "자치도", "특별시", "광역시",
        "특별자치구", "시", "도", "군", "구",
    ]

    core = r
    changed = True
    while changed:
        changed = False
        for suf in suffixes:
            if core.endswith(suf) and len(core) > len(suf):
                core = core[:-len(suf)]
                changed = True
                break
    return core


def _infer_region_from_keyword(keyword: str) -> str:
    k = (keyword or "").strip()
    if not k:
        return ""
    first = k.split()[0]
    if not re.search(r"[가-힣]", first):
        return ""
    return _normalize_region_input(first)


def main():
    _bootstrap_env()
    log("pipeline", "start")

    if hasattr(config, "validate_required_keys"):
        config.validate_required_keys()

    keyword = input("YouTube 검색 키워드를 입력하세요: ").strip()
    keyword = " ".join(keyword.split())
    if not keyword:
        log("pipeline", "empty keyword, abort")
        return

    region = input("지역(region)을 입력하세요 (예: 제주, 부산) [엔터=자동]: ").strip()
    region = _normalize_region_input(region) if region else _infer_region_from_keyword(keyword)

    if region and region not in keyword:
        keyword_for_search = f"{region} {keyword}".strip()
    else:
        keyword_for_search = keyword

    print(f"[pipeline] region={region or 'N/A'}")

    limit_raw = input("가져올 영상 수 (기본 5): ").strip()
    limit = int(limit_raw) if limit_raw.isdigit() else 5

    videos = step0(keyword=keyword_for_search, max_results=limit, region_tag=region)

    # ✅ 분석 대상 영상 리스트 출력(디버깅/검증용)
    print("\n" + "=" * 70)
    print(f"📺 분석 대상 영상 리스트 (총 {len(videos)}개)")
    print("=" * 70)
    for i, v in enumerate(videos, 1):
        vid = v.get("video_id")
        title = (v.get("title") or "").strip()
        # step0에서 duration_sec / has_caption 을 넣는 경우를 고려
        dur = v.get("duration_sec")
        dur_txt = f"{int(dur)//60:02d}:{int(dur)%60:02d}" if isinstance(dur, (int, float)) else "N/A"
        cap = v.get("has_caption")
        cap_txt = "Y" if cap is True else ("N" if cap is False else "N/A")

        # 제목이 길면 잘라서 출력
        short = title if len(title) <= 60 else title[:60] + "…"
        print(f" {i:2d}/{len(videos):2d} | {dur_txt} | cap={cap_txt} | {vid} | {short}")
    print("=" * 70 + "\n")
    materials = step1(videos)
    places_raw = step2(materials)
    places_day = step2_1(materials, places_raw)
    places_norm = step2_5(places_day)
    verified = step3(places_norm, region=region)
    timeline = step4(verified)
    final_all = step5(timeline)

    log("pipeline", "end", total_videos=final_all.get("total_videos"))


if __name__ == "__main__":
    main()
