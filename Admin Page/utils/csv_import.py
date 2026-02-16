import re
from datetime import datetime
from typing import Dict, Optional, Tuple

import pandas as pd

from utils.db import fetch_one, insert_rows


PREPROCESSED_COLUMNS = [
    "코스 제목 (유튜브 명)",
    "일수 분류",
    "일차",
    "전체 순서",
    "장소명",
    "주소",
    "카테고리",
    "조회수",
    "유튜브 링크",
]


def normalize_preprocessed_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    cols = [str(c) for c in df.columns]
    unnamed_only = all(c.startswith("Unnamed") for c in cols)
    if unnamed_only:
        max_rows = min(5, len(df))
        for i in range(max_rows):
            row_vals = [str(v).strip() for v in df.iloc[i].tolist()]
            if "코스 제목 (유튜브 명)" in row_vals and "장소명" in row_vals:
                df = df.iloc[i + 1 :].copy()
                df.columns = row_vals
                df = df.dropna(how="all")
                break

    return df


def _extract_youtube_id(value: Optional[str]) -> Optional[str]:
    if not value or not isinstance(value, str):
        return None
    value = value.strip()
    if "v=" in value:
        match = re.search(r"v=([A-Za-z0-9_-]+)", value)
        return match.group(1) if match else None
    if "youtu.be/" in value:
        match = re.search(r"youtu\.be/([A-Za-z0-9_-]+)", value)
        return match.group(1) if match else None
    if re.fullmatch(r"[A-Za-z0-9_-]{6,}", value):
        return value
    return None


def _parse_travel_days(value: Optional[str]) -> Optional[int]:
    if not value or not isinstance(value, str):
        return None
    v = value.strip()
    if "당일" in v:
        return 1
    nums = re.findall(r"\d+", v)
    if nums:
        try:
            return int(nums[-1])
        except Exception:
            return None
    return None


def _normalize_category(value: Optional[str]) -> str:
    if not value or not isinstance(value, str):
        return "기타"
    v = value.strip()
    if v in ("맛집", "카페", "숙소", "관광지", "기타"):
        return v
    return "기타"


def _get_existing_place_id(region_id: int, name: str, address: Optional[str]) -> Optional[int]:
    row = fetch_one(
        "SELECT id FROM places WHERE region_id = %s AND place_name = %s AND (address = %s OR (address IS NULL AND %s IS NULL)) LIMIT 1",
        [region_id, name, address, address],
    )
    return row["id"] if row else None


def _get_existing_course_id(region_id: int, author_id: int, title: str) -> Optional[int]:
    row = fetch_one(
        "SELECT id FROM courses WHERE region_id = %s AND author_id = %s AND title = %s LIMIT 1",
        [region_id, author_id, title],
    )
    return row["id"] if row else None


def _get_video_id_from_yt(yt_id: str) -> Optional[int]:
    row = fetch_one("SELECT id FROM videos WHERE yt_video_id = %s LIMIT 1", [yt_id])
    return row["id"] if row else None


def import_preprocessed_csv(
    df: pd.DataFrame,
    region_id: int,
    author_id: int,
    source_video_mode: str,
    default_source_video_id: Optional[int],
    lat_col: Optional[str],
    lng_col: Optional[str],
    default_lat: Optional[float] = None,
    default_lng: Optional[float] = None,
) -> Dict[str, int]:
    result = {"courses": 0, "places": 0, "course_place": 0, "skipped": 0}

    df = normalize_preprocessed_df(df.copy())

    for col in PREPROCESSED_COLUMNS:
        if col not in df.columns:
            raise ValueError(f"필수 컬럼 누락: {col}")

    df = df.dropna(how="all")
    df["코스 제목 (유튜브 명)"] = df["코스 제목 (유튜브 명)"].ffill()
    df["유튜브 링크"] = df["유튜브 링크"].ffill()
    df["일수 분류"] = df["일수 분류"].ffill()

    if lat_col and lat_col in df.columns:
        df[lat_col] = pd.to_numeric(df[lat_col], errors="coerce")
    if lng_col and lng_col in df.columns:
        df[lng_col] = pd.to_numeric(df[lng_col], errors="coerce")

    place_rows = []
    place_key_to_id: Dict[Tuple[str, Optional[str]], int] = {}

    for _, row in df.iterrows():
        place_name = str(row.get("장소명") or "").strip()
        if not place_name:
            result["skipped"] += 1
            continue
        address = str(row.get("주소") or "").strip() or None
        key = (place_name, address)
        if key in place_key_to_id:
            continue

        existing_id = _get_existing_place_id(region_id, place_name, address)
        if existing_id:
            place_key_to_id[key] = existing_id
            continue

        if lat_col and lng_col:
            lat = row.get(lat_col)
            lng = row.get(lng_col)
        else:
            lat = default_lat
            lng = default_lng

        if lat is None or lng is None or pd.isna(lat) or pd.isna(lng):
            raise ValueError(f"위도/경도 누락: {place_name}")

        place_rows.append(
            {
                "region_id": region_id,
                "place_name": place_name,
                "place_category": _normalize_category(row.get("카테고리")),
                "ai_tag": row.get("카테고리"),
                "address": address,
                "lat": float(lat),
                "lng": float(lng),
                "external_id": None,
                "external_link": None,
                "deleted_at": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        )

    if place_rows:
        insert_rows("places", list(place_rows[0].keys()), place_rows)
        for r in place_rows:
            existing_id = _get_existing_place_id(region_id, r["place_name"], r["address"])
            if existing_id:
                place_key_to_id[(r["place_name"], r["address"])] = existing_id
        result["places"] += len(place_rows)

    course_title_to_id: Dict[str, int] = {}
    course_rows = []

    for _, row in df.iterrows():
        title = str(row.get("코스 제목 (유튜브 명)") or "").strip()
        if not title:
            result["skipped"] += 1
            continue
        if title in course_title_to_id:
            continue

        existing_id = _get_existing_course_id(region_id, author_id, title)
        if existing_id:
            course_title_to_id[title] = existing_id
            continue

        travel_days = _parse_travel_days(str(row.get("일수 분류") or ""))
        if not travel_days:
            travel_days = 1

        if source_video_mode == "default":
            source_video_id = default_source_video_id
        else:
            yt_id = _extract_youtube_id(str(row.get("유튜브 링크") or ""))
            source_video_id = _get_video_id_from_yt(yt_id) if yt_id else None

        if not source_video_id:
            result["skipped"] += 1
            continue

        course_rows.append(
            {
                "source_video_id": source_video_id,
                "region_id": region_id,
                "author_id": author_id,
                "original_course_id": None,
                "title": title,
                "description": None,
                "travel_days": travel_days,
                "is_customized": False,
                "is_rep": False,
                "deleted_at": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        )

    if course_rows:
        insert_rows("courses", list(course_rows[0].keys()), course_rows)
        for r in course_rows:
            existing_id = _get_existing_course_id(region_id, author_id, r["title"])
            if existing_id:
                course_title_to_id[r["title"]] = existing_id
        result["courses"] += len(course_rows)

    course_place_rows = []
    for _, row in df.iterrows():
        title = str(row.get("코스 제목 (유튜브 명)") or "").strip()
        place_name = str(row.get("장소명") or "").strip()
        if not title or not place_name:
            result["skipped"] += 1
            continue
        course_id = course_title_to_id.get(title)
        if not course_id:
            result["skipped"] += 1
            continue
        address = str(row.get("주소") or "").strip() or None
        place_id = place_key_to_id.get((place_name, address))
        if not place_id:
            result["skipped"] += 1
            continue

        visit_day = row.get("일차")
        visit_order = row.get("전체 순서")

        course_place_rows.append(
            {
                "course_id": course_id,
                "place_id": place_id,
                "visit_day": int(visit_day) if pd.notna(visit_day) else None,
                "visit_order": int(visit_order) if pd.notna(visit_order) else None,
                "deleted_at": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        )

    if course_place_rows:
        insert_rows("course_place", list(course_place_rows[0].keys()), course_place_rows)
        result["course_place"] += len(course_place_rows)

    return result