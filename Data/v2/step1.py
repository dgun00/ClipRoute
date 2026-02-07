import requests
import isodate
import config
import pandas as pd
import json

YOUTUBE_API_KEY = config.YOUTUBE_API_KEY
SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


# 1. 유튜브 검색
def search_videos(query, max_results=50):
    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": max_results,
        "key": YOUTUBE_API_KEY
    }
    res = requests.get(SEARCH_URL, params=params)
    res.raise_for_status()
    return [item["id"]["videoId"] for item in res.json()["items"]]


# 2. 영상 메타데이터 수집
def fetch_video_metadata(video_ids):
    params = {
        "part": "snippet,contentDetails",
        "id": ",".join(video_ids),
        "key": YOUTUBE_API_KEY
    }
    res = requests.get(VIDEOS_URL, params=params)
    res.raise_for_status()

    videos = []
    for item in res.json()["items"]:
        duration_sec = int(
            isodate.parse_duration(
                item["contentDetails"]["duration"]
            ).total_seconds()
        )

        videos.append({
            "video_id": item["id"],
            "title": item["snippet"]["title"],
            "channel_name": item["snippet"]["channelTitle"],
            "upload_date": item["snippet"]["publishedAt"][:10],  # 날짜만
            "source_url": f"https://www.youtube.com/watch?v={item['id']}",
            "thumbnail_url": item["snippet"]["thumbnails"]["high"]["url"],
            "duration_sec": duration_sec,
            "caption_flag": item["contentDetails"]["caption"],   # true / false
            "live_status": item["snippet"]["liveBroadcastContent"]
        })

    return videos


# 3. 실행부 (Step 1)
def main():
    keyword = input("검색 키워드를 입력하세요: ")

    video_ids = search_videos(keyword)
    print(f"[SEARCH] 검색 결과: {len(video_ids)}개")

    videos = fetch_video_metadata(video_ids)
    print(f"[METADATA] 메타데이터 수집: {len(videos)}개")

    rows = []
    json_candidates = []

    for v in videos:
        filter_reasons = []

        # Step 1 시스템 필터 (기계적 판별만)
        if v["caption_flag"] != "true":
            filter_reasons.append("NO_CAPTION")

        if not (600 <= v["duration_sec"] <= 3600):
            filter_reasons.append("INVALID_DURATION")

        if v["live_status"] != "none":
            filter_reasons.append("LIVE_VIDEO")

        system_pass = len(filter_reasons) == 0

        rows.append({
            **v,
            "system_pass": system_pass,
            "filter_reason": ",".join(filter_reasons)
        })

        # JSON 후보 (Step 2 입력용)
        if system_pass:
            json_candidates.append({
                "video_id": v["video_id"],
                "title": v["title"],
                "channel_name": v["channel_name"],
                "upload_date": v["upload_date"],
                "source_url": v["source_url"],
                "thumbnail_url": v["thumbnail_url"],
                "duration_sec": v["duration_sec"],
                "region_tag": None  # Step 1에서는 비워둠 (사람이 지정)
            })

    # CSV 저장 (전체 결과)
    df = pd.DataFrame(rows)
    df.to_csv("youtube_step1_candidates.csv", index=False)
    print("\n[EXPORT] youtube_step1_candidates.csv 저장 완료")

    # JSON 저장 (Step 1 최종 산출물)
    with open("youtube_step1_candidates.json", "w", encoding="utf-8") as f:
        json.dump(json_candidates, f, ensure_ascii=False, indent=2)

    print("[EXPORT] youtube_step1_candidates.json 저장 완료")

    print("\n=== Step 1 통과 영상 수 ===")
    print("SYSTEM PASS:", len(json_candidates))


if __name__ == "__main__":
    main()
