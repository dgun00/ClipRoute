import os
import re
from datetime import datetime
from typing import Dict, Optional, Tuple

import pandas as pd
import requests
import boto3
from botocore.exceptions import ClientError

from utils.db import fetch_one, insert_rows


PREPROCESSED_COLUMNS = [
    "video_title",
    "channel_name",
    "course_title",
    "travel_day",
    "visit_day",
    "visit_order",
    "place_name",
    "address",
    "place_category",
    "yt_video_id",
    "original_name",
]


S3_BUCKET = os.getenv("S3_BUCKET") or os.getenv("AWS_S3_BUCKET")
S3_REGION = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "ap-northeast-2"


def _get_s3_client():
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    if not (access_key and secret_key and S3_BUCKET):
        raise RuntimeError("S3 설정이 필요합니다. (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET)")
    return boto3.client(
        "s3",
        region_name=S3_REGION,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )


def _s3_url_for_key(key: str) -> str:
    return f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{key}"


def _s3_object_exists(s3, key: str) -> bool:
    try:
        s3.head_object(Bucket=S3_BUCKET, Key=key)
        return True
    except ClientError as exc:
        code = exc.response.get("Error", {}).get("Code")
        if code in ("404", "NoSuchKey", "NotFound"):
            return False
        raise


def _upload_youtube_thumbnail_to_s3(yt_id: str) -> Tuple[str, bool]:
    if not yt_id:
        raise ValueError("이미지 업로드 실패: yt_video_id 없음")
    key = f"images/courses/{yt_id}.jpg"

    s3 = _get_s3_client()
    if _s3_object_exists(s3, key):
        return _s3_url_for_key(key), False

    candidates = [
        "maxresdefault.jpg",
        "sddefault.jpg",
        "hqdefault.jpg",
    ]
    resp = None
    for name in candidates:
        url = f"https://img.youtube.com/vi/{yt_id}/{name}"
        resp = requests.get(url, stream=True, timeout=15)
        if resp.status_code == 200:
            break
    if resp is None or resp.status_code != 200:
        status = resp.status_code if resp is not None else "no-response"
        raise ValueError(f"이미지 업로드 실패: {yt_id} (HTTP {status})")

    s3.upload_fileobj(
        resp.raw,
        S3_BUCKET,
        key,
        ExtraArgs={"ContentType": "image/jpeg"},
    )
    return _s3_url_for_key(key), True


def normalize_preprocessed_df(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    cols = [str(c) for c in df.columns]
    unnamed_only = all(c.startswith("Unnamed") for c in cols)
    if unnamed_only:
        max_rows = min(5, len(df))
        for i in range(max_rows):
            row_vals = [str(v).strip() for v in df.iloc[i].tolist()]
            if "course_title" in row_vals and "place_name" in row_vals:
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
    if value is None:
        return None
    if isinstance(value, (int, float)):
        try:
            return int(value)
        except Exception:
            return None
    if not isinstance(value, str):
        return None
    v = value.strip()
    if "당일" in v:
        return 1
    match = re.search(r"\d+(?:\.\d+)?", v)
    if match:
        try:
            return int(float(match.group(0)))
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


def _get_existing_course_id(title: str) -> Optional[int]:
    row = fetch_one(
        "SELECT id FROM courses WHERE title = %s LIMIT 1",
        [title],
    )
    return row["id"] if row else None


def _get_existing_course_id_by_source_video(source_video_id: int, region_id: int) -> Optional[int]:
    row = fetch_one(
        "SELECT id FROM courses WHERE source_video_id = %s AND region_id = %s LIMIT 1",
        [source_video_id, region_id],
    )
    return row["id"] if row else None


def _get_video_id_from_yt(yt_id: str) -> Optional[int]:
    row = fetch_one("SELECT id FROM videos WHERE yt_video_id = %s LIMIT 1", [yt_id])
    return row["id"] if row else None


def _exists_course_place(
    course_id: int,
    place_id: int,
    visit_day: Optional[int],
    visit_order: Optional[int],
) -> bool:
    row = fetch_one(
        "SELECT id FROM course_place "
        "WHERE course_id = %s AND place_id = %s "
        "AND (visit_day = %s OR (visit_day IS NULL AND %s IS NULL)) "
        "AND (visit_order = %s OR (visit_order IS NULL AND %s IS NULL)) "
        "LIMIT 1",
        [course_id, place_id, visit_day, visit_day, visit_order, visit_order],
    )
    return row is not None


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
    result = {
        "videos": 0,
        "images": 0,
        "courses": 0,
        "places": 0,
        "course_place": 0,
        "skipped": 0,
        "image_uploads": 0,
    }

    df = normalize_preprocessed_df(df.copy())

    for col in PREPROCESSED_COLUMNS:
        if col not in df.columns:
            raise ValueError(f"필수 컬럼 누락: {col}")

    df = df.dropna(how="all")
    df["course_title"] = df["course_title"].ffill()
    df["yt_video_id"] = df["yt_video_id"].ffill()
    df["travel_day"] = df["travel_day"].ffill()

    df["travel_day_num"] = pd.to_numeric(df.get("travel_day"), errors="coerce")
    df["visit_day_num"] = pd.to_numeric(df.get("visit_day"), errors="coerce")
    travel_days_by_course = df.groupby("course_title")["travel_day_num"].max()
    visit_days_by_course = df.groupby("course_title")["visit_day_num"].max()

    # videos
    video_rows = []
    seen_yt = set()
    for _, row in df.iterrows():
        yt_id = str(row.get("yt_video_id") or "").strip()
        if not yt_id or yt_id in seen_yt:
            continue
        seen_yt.add(yt_id)
        existing_id = _get_video_id_from_yt(yt_id)
        if existing_id:
            continue
        video_rows.append(
            {
                "region_id": region_id,
                "yt_video_id": yt_id,
                "title": str(row.get("video_title") or "").strip() or None,
                "channel_name": str(row.get("channel_name") or "").strip() or None,
                "thumbnail_url": _s3_url_for_key(f"images/courses/{yt_id}.jpg"),
                "upload_date": None,
                "duration": None,
                "video_format": None,
                "has_caption": None,
                "deleted_at": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        )

    if video_rows:
        inserted = insert_rows("videos", list(video_rows[0].keys()), video_rows)
        result["videos"] += inserted

    # images
    image_rows = []
    seen_image_key = set()
    seen_yt_upload = set()
    for _, row in df.iterrows():
        yt_id = str(row.get("yt_video_id") or "").strip()
        if not yt_id:
            continue
        if yt_id in seen_image_key:
            continue
        seen_image_key.add(yt_id)
        if yt_id not in seen_yt_upload:
            _, uploaded = _upload_youtube_thumbnail_to_s3(yt_id)
            seen_yt_upload.add(yt_id)
            if uploaded:
                result["image_uploads"] += 1
        image_url = _s3_url_for_key(f"images/courses/{yt_id}.jpg")
        existing_id = _get_existing_image_id_by_url(image_url)
        if existing_id:
            continue
        image_rows.append(
            {
                "image_url": image_url,
                "original_name": str(row.get("original_name") or "").strip() or None,
                "deleted_at": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        )

    if image_rows:
        inserted = insert_rows("images", list(image_rows[0].keys()), image_rows)
        result["images"] += inserted

    if lat_col and lat_col in df.columns:
        df[lat_col] = pd.to_numeric(df[lat_col], errors="coerce")
    if lng_col and lng_col in df.columns:
        df[lng_col] = pd.to_numeric(df[lng_col], errors="coerce")

    place_rows = []
    place_key_to_id: Dict[Tuple[str, Optional[str]], int] = {}

    for _, row in df.iterrows():
        place_name = str(row.get("place_name") or "").strip()
        if not place_name:
            result["skipped"] += 1
            continue
        address = str(row.get("address") or "").strip() or None
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
                "place_category": _normalize_category(row.get("place_category")),
                "ai_tag": row.get("place_category"),
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
        # mark as queued to avoid duplicates before insert
        place_key_to_id[key] = -1

    if place_rows:
        inserted = insert_rows("places", list(place_rows[0].keys()), place_rows)
        for r in place_rows:
            existing_id = _get_existing_place_id(region_id, r["place_name"], r["address"])
            if existing_id:
                place_key_to_id[(r["place_name"], r["address"])] = existing_id
        result["places"] += inserted

    source_video_to_course_id: Dict[int, int] = {}
    course_rows = []

    for _, row in df.iterrows():
        if source_video_mode == "default":
            source_video_id = default_source_video_id
        else:
            yt_id = _extract_youtube_id(str(row.get("yt_video_id") or ""))
            source_video_id = _get_video_id_from_yt(yt_id) if yt_id else None

        if not source_video_id:
            result["skipped"] += 1
            continue
        if source_video_id in source_video_to_course_id:
            continue

        existing_id = _get_existing_course_id_by_source_video(source_video_id, region_id)
        if existing_id:
            source_video_to_course_id[source_video_id] = existing_id
            continue

        title = str(row.get("course_title") or "").strip()
        if not title:
            title = str(row.get("video_title") or "").strip()
        if not title:
            title = f"course-{source_video_id}"

        travel_days = None
        td = travel_days_by_course.get(title)
        if pd.notna(td):
            travel_days = int(td)
        else:
            td = _parse_travel_days(str(row.get("travel_day") or ""))
            if td:
                travel_days = td
        if not travel_days:
            vd = visit_days_by_course.get(title)
            if pd.notna(vd):
                travel_days = int(vd)
        if not travel_days:
            travel_days = 1
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
        # mark as queued to avoid duplicates before insert
        source_video_to_course_id[source_video_id] = -1

    if course_rows:
        inserted = insert_rows("courses", list(course_rows[0].keys()), course_rows)
        for r in course_rows:
            existing_id = _get_existing_course_id_by_source_video(r["source_video_id"], r["region_id"])
            if existing_id:
                source_video_to_course_id[r["source_video_id"]] = existing_id
        result["courses"] += inserted

    course_place_rows = []
    for _, row in df.iterrows():
        place_name = str(row.get("place_name") or "").strip()
        if not place_name:
            result["skipped"] += 1
            continue

        if source_video_mode == "default":
            source_video_id = default_source_video_id
        else:
            yt_id = _extract_youtube_id(str(row.get("yt_video_id") or ""))
            source_video_id = _get_video_id_from_yt(yt_id) if yt_id else None
        if not source_video_id:
            result["skipped"] += 1
            continue

        course_id = source_video_to_course_id.get(source_video_id)
        if not course_id:
            result["skipped"] += 1
            continue
        address = str(row.get("address") or "").strip() or None
        place_id = place_key_to_id.get((place_name, address))
        if not place_id:
            result["skipped"] += 1
            continue

        visit_day = row.get("visit_day")
        visit_order = row.get("visit_order")

        visit_day_val = int(visit_day) if pd.notna(visit_day) else None
        visit_order_val = int(visit_order) if pd.notna(visit_order) else None
        if _exists_course_place(course_id, place_id, visit_day_val, visit_order_val):
            result["skipped"] += 1
            continue

        course_place_rows.append(
            {
                "course_id": course_id,
                "place_id": place_id,
                "visit_day": visit_day_val,
                "visit_order": visit_order_val,
                "deleted_at": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        )

    if course_place_rows:
        inserted = insert_rows("course_place", list(course_place_rows[0].keys()), course_place_rows)
        result["course_place"] += inserted

    return result


CLIPROUTE_COLUMNS = [
    "video_title",
    "channel_name",
    "yt_video_id",
    "original_name",
    "course_title",
    "travel_day",
    "visit_day",
    "visit_order",
    "place_name",
    "address",
    "place_category",
    "region_id",
    "lat",
    "lng",
]


def _normalize_category_kr(value: Optional[str]) -> str:
    if not value or not isinstance(value, str):
        return "기타"
    v = value.strip()
    if v in ("관광지", "기타", "맛집", "숙소", "카페"):
        return v
    return "기타"


def _get_existing_image_id_by_url(image_url: str) -> Optional[int]:
    row = fetch_one("SELECT id FROM images WHERE image_url = %s LIMIT 1", [image_url])
    return row["id"] if row else None


def import_cliproute_csv(
    df: pd.DataFrame,
    author_id: int = 0,
) -> Dict[str, int]:
    result = {
        "videos": 0,
        "images": 0,
        "places": 0,
        "courses": 0,
        "course_place": 0,
        "skipped": 0,
        "image_uploads": 0,
    }

    for col in CLIPROUTE_COLUMNS:
        if col not in df.columns:
            raise ValueError(f"필수 컬럼 누락: {col}")

    df = df.dropna(how="all")
    for num_col in ["region_id", "lat", "lng", "travel_day", "visit_day", "visit_order"]:
        if num_col in df.columns:
            df[num_col] = pd.to_numeric(df[num_col], errors="coerce")

    def _clean_nan(row: Dict[str, object]) -> Dict[str, object]:
        return {k: (None if pd.isna(v) else v) for k, v in row.items()}

    # videos
    video_rows = []
    seen_yt = set()
    for _, row in df.iterrows():
        yt_id = str(row.get("yt_video_id") or "").strip()
        if not yt_id or yt_id in seen_yt:
            continue
        seen_yt.add(yt_id)
        existing_id = _get_video_id_from_yt(yt_id)
        if existing_id:
            continue
        region_id = row.get("region_id")
        if pd.isna(region_id):
            result["skipped"] += 1
            continue
        video_rows.append(
            {
                "region_id": int(region_id),
                "yt_video_id": yt_id,
                "title": str(row.get("video_title") or "").strip() or None,
                "channel_name": str(row.get("channel_name") or "").strip() or None,
                "thumbnail_url": _s3_url_for_key(f"images/courses/{yt_id}.jpg"),
                "upload_date": None,
                "duration": None,
                "video_format": None,
                "has_caption": None,
                "deleted_at": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        )

    if video_rows:
        video_rows = [_clean_nan(r) for r in video_rows]
        inserted = insert_rows("videos", list(video_rows[0].keys()), video_rows)
        result["videos"] += inserted

    # images
    image_rows = []
    seen_image_key = set()
    seen_yt_upload = set()
    for _, row in df.iterrows():
        yt_id = str(row.get("yt_video_id") or "").strip()
        if not yt_id:
            continue
        if yt_id in seen_image_key:
            continue
        seen_image_key.add(yt_id)
        if yt_id not in seen_yt_upload:
            _, uploaded = _upload_youtube_thumbnail_to_s3(yt_id)
            seen_yt_upload.add(yt_id)
            if uploaded:
                result["image_uploads"] += 1
        image_url = _s3_url_for_key(f"images/courses/{yt_id}.jpg")
        existing_id = _get_existing_image_id_by_url(image_url)
        if existing_id:
            continue
        image_rows.append(
            {
                "image_url": image_url,
                "original_name": str(row.get("original_name") or "").strip() or None,
                "deleted_at": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        )

    if image_rows:
        image_rows = [_clean_nan(r) for r in image_rows]
        inserted = insert_rows("images", list(image_rows[0].keys()), image_rows)
        result["images"] += inserted

    # places
    place_rows = []
    place_key_to_id: Dict[Tuple[int, str, Optional[str]], int] = {}
    for _, row in df.iterrows():
        place_name = str(row.get("place_name") or "").strip()
        if not place_name:
            result["skipped"] += 1
            continue
        address = str(row.get("address") or "").strip() or None
        region_id = row.get("region_id")
        lat = row.get("lat")
        lng = row.get("lng")
        if pd.isna(region_id) or pd.isna(lat) or pd.isna(lng):
            result["skipped"] += 1
            continue
        region_id_int = int(region_id)
        key = (region_id_int, place_name, address)
        if key in place_key_to_id:
            continue
        existing_id = _get_existing_place_id(region_id_int, place_name, address)
        if existing_id:
            place_key_to_id[key] = existing_id
            continue
        place_rows.append(
            {
                "region_id": region_id_int,
                "place_name": place_name,
                "place_category": _normalize_category_kr(row.get("place_category")),
                "ai_tag": row.get("place_category"),
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
        # mark as queued to avoid duplicates before insert
        place_key_to_id[key] = -1

    if place_rows:
        place_rows = [_clean_nan(r) for r in place_rows]
        inserted = insert_rows("places", list(place_rows[0].keys()), place_rows)
        for r in place_rows:
            existing_id = _get_existing_place_id(r["region_id"], r["place_name"], r["address"])
            if existing_id:
                place_key_to_id[(r["region_id"], r["place_name"], r["address"])] = existing_id
        result["places"] += inserted

    # courses
    course_title_to_id: Dict[str, int] = {}
    course_rows = []
    for _, row in df.iterrows():
        title = str(row.get("course_title") or "").strip()
        if not title:
            result["skipped"] += 1
            continue
        if title in course_title_to_id:
            continue
        region_id = row.get("region_id")
        if pd.isna(region_id):
            result["skipped"] += 1
            continue
        existing_id = _get_existing_course_id(title)
        if existing_id:
            course_title_to_id[title] = existing_id
            continue

        yt_id = str(row.get("yt_video_id") or "").strip()
        source_video_id = _get_video_id_from_yt(yt_id) if yt_id else None
        if not source_video_id:
            result["skipped"] += 1
            continue

        travel_days = None
        travel_day_val = row.get("travel_day")
        if pd.notna(travel_day_val):
            try:
                travel_days = int(travel_day_val)
            except Exception:
                travel_days = None
        if not travel_days:
            travel_days = 1

        course_rows.append(
            {
                "source_video_id": source_video_id,
                "region_id": int(region_id),
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
        course_rows = [_clean_nan(r) for r in course_rows]
        inserted = insert_rows("courses", list(course_rows[0].keys()), course_rows)
        for r in course_rows:
            existing_id = _get_existing_course_id(r["title"])
            if existing_id:
                course_title_to_id[r["title"]] = existing_id
        result["courses"] += inserted

    # course_place
    course_place_rows = []
    for _, row in df.iterrows():
        title = str(row.get("course_title") or "").strip()
        place_name = str(row.get("place_name") or "").strip()
        if not title or not place_name:
            result["skipped"] += 1
            continue
        course_id = course_title_to_id.get(title)
        if not course_id:
            result["skipped"] += 1
            continue
        address = str(row.get("address") or "").strip() or None
        place_id = place_key_to_id.get((place_name, address))
        if not place_id:
            result["skipped"] += 1
            continue

        visit_day = row.get("visit_day")
        visit_order = row.get("visit_order")

        visit_day_val = int(visit_day) if pd.notna(visit_day) else None
        visit_order_val = int(visit_order) if pd.notna(visit_order) else None
        if _exists_course_place(course_id, place_id, visit_day_val, visit_order_val):
            result["skipped"] += 1
            continue

        course_place_rows.append(
            {
                "course_id": course_id,
                "place_id": place_id,
                "visit_day": visit_day_val,
                "visit_order": visit_order_val,
                "deleted_at": None,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
        )
    if course_place_rows:
        course_place_rows = [_clean_nan(r) for r in course_place_rows]
        inserted = insert_rows("course_place", list(course_place_rows[0].keys()), course_place_rows)
        result["course_place"] += inserted

    return result
