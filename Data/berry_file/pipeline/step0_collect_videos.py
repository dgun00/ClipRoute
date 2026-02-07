from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

import config
from utils.io import save_json
from utils.logging_utils import log

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


def _parse_iso8601_duration(d: str) -> int:
    """Parse YouTube ISO8601 duration (e.g., PT1H2M3S) into seconds."""
    if not d or not d.startswith("PT"):
        return 0
    h = m = s = 0
    cur = ""
    for ch in d[2:]:
        if ch.isdigit():
            cur += ch
            continue
        if not cur:
            continue
        val = int(cur)
        cur = ""
        if ch == "H":
            h = val
        elif ch == "M":
            m = val
        elif ch == "S":
            s = val
    return h * 3600 + m * 60 + s


def _format_duration(seconds: int) -> str:
    """Format seconds to H:MM:SS or M:SS for readability."""
    try:
        sec = int(seconds or 0)
    except Exception:
        sec = 0
    if sec < 0:
        sec = 0
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def _normalize_region_core(region: str) -> str:
    r = (region or "").strip()
    if not r:
        return ""
    r = r.split()[0]

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


def _looks_like_omnibus(title: str) -> bool:
    """대략적인 옴니버스/리스트/랭킹/모음류 감지 (완벽하진 않음)."""
    t = (title or "").lower()
    bad = [
        "best",
        "top",
        "모음",
        "총정리",
        "정리",
        "랭킹",
        "순위",
        "리스트",
        "전국",
        "n곳",
        "곳 추천",
        "맛집 best",
        "맛집 top",
        "모아",
    ]
    return any(b in t for b in bad)


def _parse_published_at(s: str) -> Optional[datetime]:
    if not s:
        return None
    try:
        # e.g. 2026-01-18T12:34:56Z
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s)
    except Exception:
        return None


def _search(query: str, max_results: int, api_key: str) -> List[Dict[str, Any]]:
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "order": str(getattr(config, "YT_SEARCH_ORDER", "date")),
        "key": api_key,
    }
    r = requests.get(SEARCH_URL, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("items", [])


def _fetch_videos(video_ids: List[str], api_key: str) -> List[Dict[str, Any]]:
    if not video_ids:
        return []
    r = requests.get(
        VIDEOS_URL,
        params={
            "part": "snippet,contentDetails",
            "id": ",".join(video_ids),
            "key": api_key,
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json().get("items", [])


def run(*, keyword: str, max_results: int = 10, region_tag: str | None = None) -> List[Dict[str, Any]]:
    """Step0: YouTube 후보 영상 수집 + 1차 필터링

    사용자 기준 반영 필터:
    - 캡션 필수(선택): REQUIRE_CAPTIONS=true 인 경우만 contentDetails.caption == 'true' 필수
    - 캡션 우선(기본): PREFER_CAPTIONS=true면 caption=true 영상이 앞에 오도록 정렬
    - 길이: 10분~60분 (MIN_VIDEO_DURATION~MAX_VIDEO_DURATION)
    - 포맷: 일반 영상 (라이브/예정 제외)
    - (선택) region_tag가 주어지면 title/description에 region_core 포함 필터
    - (선택) 옴니버스/리스트류 title 패턴 제외
    - (선택) 최신성: MAX_VIDEO_AGE_DAYS

    저장:
    - data/step0_videos/videos.json
    - data/step0_videos/_summary.json (드랍 사유 통계)
    """

    if not keyword or not keyword.strip():
        raise ValueError("step0_collect_videos.run: keyword must be a non-empty string")

    api_key = getattr(config, "YOUTUBE_API_KEY", None)
    if not api_key:
        raise RuntimeError("config.YOUTUBE_API_KEY 가 필요합니다.")

    data_dir = Path(getattr(config, "DATA_DIR", "data"))
    out_dir = data_dir / "step0_videos"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 필터 옵션
    min_dur = int(getattr(config, "MIN_VIDEO_DURATION", 600))
    max_dur = int(getattr(config, "MAX_VIDEO_DURATION", 3600))
    require_captions = bool(getattr(config, "REQUIRE_CAPTIONS", False))
    prefer_captions = bool(getattr(config, "PREFER_CAPTIONS", True))
    # Step0에서는 region을 기본적으로 '필수 드랍 조건'으로 쓰지 않음(테스트 효율/누락 방지)
    # region 강제는 Step3(네이버 검증)에서 enforce_region=True로 처리
    enforce_region_in_metadata = bool(getattr(config, "ENFORCE_REGION_IN_METADATA", False))
    prefer_region_in_metadata = bool(getattr(config, "PREFER_REGION_IN_METADATA", True))
    exclude_omnibus = bool(getattr(config, "EXCLUDE_OMNIBUS", True))
    max_age_days = int(getattr(config, "MAX_VIDEO_AGE_DAYS", 0) or 0)

    region_tag = (region_tag or "").strip()
    region_core = _normalize_region_core(region_tag)

    # 1) 검색
    search_items = _search(keyword, max_results=max_results, api_key=api_key)

    # search 단계에서 라이브 힌트를 확보 (snippet.liveBroadcastContent)
    live_map: Dict[str, str] = {}
    ids: List[str] = []
    for it in search_items:
        vid = (it.get("id") or {}).get("videoId")
        if not vid:
            continue
        ids.append(vid)
        sn = it.get("snippet") or {}
        live_map[vid] = (sn.get("liveBroadcastContent") or "none").lower()

    if not ids:
        save_json(out_dir / "videos.json", [])
        save_json(out_dir / "_summary.json", {"query": keyword, "total_fetched": 0, "kept": 0})
        log("step0", "saved=EMPTY", keyword=keyword, total=0)
        return []

    # 2) 메타데이터
    items = _fetch_videos(ids, api_key=api_key)

    stats: Dict[str, Any] = {
        "query": keyword,
        "region_tag": region_tag,
        "region_core": region_core,
        "total_fetched": len(items),
        "kept": 0,
        "dropped_duration": 0,
        "dropped_live": 0,
        "dropped_no_caption": 0,
        "dropped_omnibus": 0,
        "dropped_region_mismatch": 0,
        "dropped_old": 0,
        "kept_caption_true": 0,
        "kept_caption_false": 0,
        "kept_region_match": 0,
        "kept_region_mismatch": 0,
    }

    out: List[Dict[str, Any]] = []
    now = datetime.now(timezone.utc)

    for it in items:
        sn = it.get("snippet", {})
        cd = it.get("contentDetails", {})

        vid = it.get("id")
        title = (sn.get("title") or "").strip()
        description = sn.get("description") or ""
        channel_name = (sn.get("channelTitle") or "").strip()
        published_at = sn.get("publishedAt") or ""

        thumbs = sn.get("thumbnails") or {}
        thumbnail_url = ""
        for k in ("high", "standard", "medium", "default"):
            u = ((thumbs.get(k) or {}).get("url") or "").strip()
            if u:
                thumbnail_url = u
                break

        duration_sec = _parse_iso8601_duration(cd.get("duration") or "")
        caption_flag = str(cd.get("caption") or "").lower()  # 'true'/'false'

        # 라이브/예정 제외 (search 힌트 기반)
        live_status = (live_map.get(vid) or "none").lower()
        if live_status != "none":
            stats["dropped_live"] += 1
            continue

        # 길이 필터
        if duration_sec <= 0 or duration_sec < min_dur or duration_sec > max_dur:
            stats["dropped_duration"] += 1
            continue

        # 자막 필터 (가능 여부) - 필수일 때만 드랍
        if require_captions and caption_flag != "true":
            stats["dropped_no_caption"] += 1
            continue

        # 옴니버스 제외
        if exclude_omnibus and _looks_like_omnibus(title):
            stats["dropped_omnibus"] += 1
            continue

        # 최신성 필터(선택)
        if max_age_days > 0:
            dt = _parse_published_at(published_at)
            if dt is not None:
                age_days = (now - dt).days
                if age_days > max_age_days:
                    stats["dropped_old"] += 1
                    continue

        # region 메타 필터(선택)
        # Step0에서는 기본적으로 드랍하지 않으며(ENFORCE_REGION_IN_METADATA 기본 False),
        # region을 쓰더라도 "선호/정렬" 용도로만 쓰는 것을 권장.
        region_match = None
        if region_core:
            text = f"{title} {description}"
            region_match = (region_core in text)

        if region_core and enforce_region_in_metadata:
            if not region_match:
                stats["dropped_region_mismatch"] += 1
                continue

        if region_match is True:
            stats["kept_region_match"] += 1
        elif region_match is False:
            stats["kept_region_mismatch"] += 1

        if caption_flag == "true":
            stats["kept_caption_true"] += 1
        else:
            stats["kept_caption_false"] += 1

        out.append(
            {
                "video_id": vid,
                "title": title,
                "thumbnail_url": thumbnail_url,
                "channel_name": channel_name,
                "upload_date": (published_at or "")[:10],
                "description": description,
                "source_url": f"https://www.youtube.com/watch?v={vid}",
                "duration_sec": duration_sec,
                "duration_str": _format_duration(duration_sec),
                "caption": caption_flag,
                "live_status": live_status,
                "search_keyword": keyword,
                "region_tag": region_core or region_tag,
                "region_match": bool(region_match) if region_match is not None else None,
            }
        )

    # 우선순위 정렬(드랍은 하지 않음)
    # 1) 캡션 true 우선 (PREFER_CAPTIONS)
    # 2) region 메타 매칭(true) 우선 (PREFER_REGION_IN_METADATA)
    if prefer_captions or (region_core and prefer_region_in_metadata):
        out.sort(
            key=lambda x: (
                (x.get("caption") != "true") if prefer_captions else False,
                (x.get("region_match") is not True) if (region_core and prefer_region_in_metadata) else False,
                x.get("upload_date") or "",
            )
        )

    # 결과 가독성: 각 항목에 순번/총개수 부여
    total_kept = len(out)
    for idx, item in enumerate(out, start=1):
        item["rank"] = idx
        item["rank_total"] = total_kept

    stats["kept"] = len(out)

    save_json(out_dir / "videos.json", out)
    save_json(out_dir / "_summary.json", stats)

    log("step0", "saved", path=str(out_dir / "videos.json"), total=len(out), keyword=keyword)
    log("step0", "filter_stats", **stats)

    return out
