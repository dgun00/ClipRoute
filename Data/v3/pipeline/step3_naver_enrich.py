import sys
from pathlib import Path
import re
import difflib
import requests

# ✅ import 전에 root 경로 보정
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config
from utils.io import load_json, save_json
from utils.logging_utils import log

NAVER_LOCAL_URL = "https://openapi.naver.com/v1/search/local.json"
_TAG_RE = re.compile(r"<[^>]+>")

# ❌ 장소가 아닌 단어 필터
_INVALID_PLACE_KEYWORDS = {
    "인트로", "오프닝", "엔딩", "시작", "마무리", "브이로그", "vlog"
}


def _strip_html(s: str) -> str:
    return _TAG_RE.sub("", s or "").strip()


def _sim(a: str, b: str) -> float:
    a = (a or "").strip().lower()
    b = (b or "").strip().lower()
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def _naver_local_search(query: str, display: int = 5):
    headers = {
        "X-Naver-Client-Id": config.NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": config.NAVER_CLIENT_SECRET,
    }
    r = requests.get(
        NAVER_LOCAL_URL,
        headers=headers,
        params={"query": query, "display": display},
        timeout=10,
    )
    r.raise_for_status()
    return r.json().get("items", []) or []


def run():
    data_dir = Path(getattr(config, "DATA_DIR", "data"))
    in_dir = data_dir / "step2_itinerary"
    out_dir = data_dir / "step3_naver_verified"
    out_dir.mkdir(parents=True, exist_ok=True)

    for fp in sorted(in_dir.glob("itinerary_*.json")):
        data = load_json(fp)
        vid = data.get("video_id") or fp.stem.replace("itinerary_", "")

        itinerary = data.get("itinerary") or []
        inferred_region = (data.get("inferred_region") or "").strip()

        verified_places = []

        for it in itinerary:
            place_name = (it.get("place_name") or "").strip()
            if not place_name:
                continue

            # ❌ 장소 아닌 단어 제거
            if place_name.lower() in _INVALID_PLACE_KEYWORDS:
                continue

            # ❌ 지역 추론 실패 시 skip
            if not inferred_region:
                continue

            # ✅ 무조건 지역명 prefix
            query = f"{inferred_region} {place_name}"

            try:
                items = _naver_local_search(query, display=5)
            except Exception:
                continue

            best = None
            best_score = -1.0

            for cand in items:
                cand_title = _strip_html(cand.get("title"))
                cand_addr = (cand.get("address") or "") + (cand.get("roadAddress") or "")

                # ❌ 주소에 지역명이 없으면 탈락
                if inferred_region not in cand_addr:
                    continue

                score = _sim(place_name, cand_title)
                if score > best_score:
                    best_score = score
                    best = cand

            if best is None:
                continue

            verified_places.append(
                {
                    "place_name": place_name,
                    "seconds": it.get("seconds"),
                    "order": it.get("order"),
                    "day": it.get("day", 1),
                    "query_used": query,
                    "similarity": best_score,
                    "mapx": best.get("mapx"),
                    "mapy": best.get("mapy"),
                    "address": best.get("address"),
                    "road_address": best.get("roadAddress"),
                    "category": best.get("category"),
                    "source": it.get("source"),
                }
            )

        result = {
            "video_id": vid,
            "title": data.get("title"),
            "inferred_region": inferred_region,
            "region_confidence": data.get("region_confidence"),
            "verified_places": verified_places,
        }

        save_json(out_dir / f"naver_verified_{vid}.json", result)
        log("step3", f"{vid} verified={len(verified_places)}")

    log("step3", "done")