import json
import time
import requests
from pathlib import Path
from difflib import SequenceMatcher
import config

# =========================
# 기본 설정
# =========================
INPUT_DIR = Path("outputs")          # Step2 결과 폴더
OUTPUT_DIR = Path("outputs")         # Step3 결과도 동일 폴더
SLEEP_SEC = 0.8                      # 네이버 API rate limit 완화

OUTPUT_DIR.mkdir(exist_ok=True)

NAVER_CLIENT_ID = config.NAVER_CLIENT_ID
NAVER_CLIENT_SECRET = config.NAVER_CLIENT_SECRET

SEARCH_URL = "https://openapi.naver.com/v1/search/local.json"
HEADERS = {
    "X-Naver-Client-Id": NAVER_CLIENT_ID,
    "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
}

# =========================
# 유틸 함수
# =========================
def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def clean_html(text):
    return text.replace("<b>", "").replace("</b>", "").strip()

# =========================
# 핵심: 장소 검증 (Step3의 본체)
# =========================
def verify_place(place, region_hint=None):
    query = place["search_query"]

    params = {
        "query": query,
        "display": 5,
        "sort": "random"
    }

    res = requests.get(SEARCH_URL, headers=HEADERS, params=params)
    res.raise_for_status()

    items = res.json().get("items", [])
    if not items:
        return {**place, "verified": False}

    best = None
    best_score = 0

    for item in items:
        name = clean_html(item["title"])
        address = item["address"]
        category = item["category"]

        score = 0
        score += similarity(place["place_name"], name) * 0.5

        if place["category"] in category:
            score += 0.3

        if region_hint and region_hint in address:
            score += 0.2

        if score > best_score:
            best_score = score
            best = item

    if best_score < 0.4 or not best:
        return {**place, "verified": False}

    return {
        "day": place["day"],
        "order": place["order"],
        "name": clean_html(best["title"]),
        "category": place["category"],
        "sub_category": best["category"],
        "address": best["address"],
        "road_address": best["roadAddress"],
        "lat": float(best["mapy"]) / 1e7,
        "lng": float(best["mapx"]) / 1e7,
        "naver_link": best["link"],
        "verified": True
    }

# =========================
# Step3 실행 로직
# =========================
def run_step3(step2_json_path: Path):
    with open(step2_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if data.get("step2_status") != "SUCCESS":
        print(f"⏭️  SKIP (Step2 실패): {step2_json_path.name}")
        return

    verified_places = []

    region_hint = data.get("region_tag")

    for place in data["courses"]:
        try:
            result = verify_place(place, region_hint=region_hint)
            verified_places.append(result)
            time.sleep(SLEEP_SEC)

        except Exception as e:
            verified_places.append({
                **place,
                "verified": False,
                "error": str(e)
            })

    output = {
        "video_id": data["video_id"],
        "title": data["title"],
        "verified_places": verified_places
    }

    out_path = OUTPUT_DIR / f"step3_verified_{data['video_id']}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✅ STEP3 저장 완료 → {out_path.name}")

# =========================
# 메인
# =========================
def main():
    step2_files = sorted(INPUT_DIR.glob("step2_courses_*.json"))

    print(f"📦 Step2 파일 수: {len(step2_files)}")

    for file in step2_files:
        print(f"🔍 검증 중: {file.name}")
        run_step3(file)

if __name__ == "__main__":
    main()
