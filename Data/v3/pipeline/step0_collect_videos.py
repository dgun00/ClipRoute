from pathlib import Path
import requests
import config
from utils.io import save_json
from utils.logging_utils import log

SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


def run(*, keyword: str | None = None, max_results: int = 10, region_tag: str | None = None):
    data_dir = Path(getattr(config, "DATA_DIR", "data"))
    out_dir = data_dir / "step0_videos"
    out_dir.mkdir(parents=True, exist_ok=True)

    if keyword is None:
        keyword = input("YouTube 검색 키워드를 입력하세요: ").strip()

    # 1️⃣ 검색
    r = requests.get(
        SEARCH_URL,
        params={
            "part": "snippet",
            "q": keyword,
            "type": "video",
            "maxResults": max_results,
            "key": config.YOUTUBE_API_KEY,
        },
        timeout=30,
    )
    r.raise_for_status()

    video_ids = [
        it["id"]["videoId"]
        for it in r.json().get("items", [])
        if it.get("id", {}).get("videoId")
    ]

    if not video_ids:
        save_json(out_dir / "videos.json", [])
        log("step0", f"keyword={keyword} saved=EMPTY total=0")
        return

    # 2️⃣ 메타데이터
    r = requests.get(
        VIDEOS_URL,
        params={
            "part": "snippet,contentDetails",
            "id": ",".join(video_ids),
            "key": config.YOUTUBE_API_KEY,
        },
        timeout=30,
    )
    r.raise_for_status()

    videos = []
    for it in r.json().get("items", []):
        sn = it.get("snippet", {})
        videos.append(
            {
                "video_id": it["id"],
                "title": sn.get("title"),
                "channel_name": sn.get("channelTitle"),
                "upload_date": (sn.get("publishedAt") or "")[:10],
                "description": sn.get("description") or "",
                "source_url": f"https://www.youtube.com/watch?v={it['id']}",
                "duration_sec": None,
                "search_keyword": keyword,
                "region_tag": region_tag,
            }
        )

    save_json(out_dir / "videos.json", videos)
    log("step0", f"keyword={keyword} saved=data/step0_videos/videos.json total={len(videos)}")