from pathlib import Path
import config
from utils.io import load_json, save_json
from utils.logging_utils import log


def _extract_latlng(p: dict):
    """
    mapx/mapy 또는 naver_top.mapx/mapy 에서 좌표 추출
    """
    mapx = p.get("mapx")
    mapy = p.get("mapy")

    if (not mapx or not mapy) and isinstance(p.get("naver_top"), dict):
        mapx = p["naver_top"].get("mapx")
        mapy = p["naver_top"].get("mapy")

    if not mapx or not mapy:
        return None, None

    try:
        return float(mapy) / 1e7, float(mapx) / 1e7
    except Exception:
        return None, None


def run():
    data_dir = Path(getattr(config, "DATA_DIR", "data"))
    in_dir = data_dir / "step3_naver_verified"
    out_dir = data_dir / "step4_timeline_sorted"
    out_dir.mkdir(parents=True, exist_ok=True)

    for fp in sorted(in_dir.glob("naver_verified_*.json")):
        data = load_json(fp)
        vid = data.get("video_id")

        verified_places = data.get("verified_places") or []

        final_places = []

        for p in verified_places:
            lat, lng = _extract_latlng(p)

            final_places.append(
                {
                    "day": int(p.get("day", 1)),
                    "order": int(p.get("order", 9999)),
                    "seconds": p.get("seconds"),
                    "place_name": p.get("place_name"),
                    "lat": lat,
                    "lng": lng,
                    "address": p.get("address")
                    or (p.get("naver_top") or {}).get("address"),
                    "road_address": p.get("road_address")
                    or (p.get("naver_top") or {}).get("road_address"),
                    "visit_confidence": p.get("visit_confidence"),
                    "visit_reason": p.get("visit_reason"),
                    "similarity": p.get("similarity"),
                    "source": p.get("source"),
                }
            )

        # ✅ Step4의 핵심 역할: 정렬만
        final_places.sort(
            key=lambda x: (
                x["day"],
                x["order"],
                x["seconds"] if x["seconds"] is not None else 1_000_000,
            )
        )

        result = {
            "video_id": vid,
            "title": data.get("title"),
            "inferred_region": data.get("inferred_region"),
            "region_confidence": data.get("region_confidence"),
            "final_places": final_places,
        }

        save_json(out_dir / f"final_places_{vid}.json", result)
        log("step4", f"{vid} final_places={len(final_places)}")

    log("step4", "done")