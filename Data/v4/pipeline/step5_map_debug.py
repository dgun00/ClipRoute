from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import json
import config
from utils.io import save_json
from utils.logging_utils import log


def run(timeline: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Step5: 최종 결과를 한 파일로 집계 (지도 디버그/후처리용)."""
    data_dir = Path(getattr(config, "DATA_DIR", "data"))
    out_dir = data_dir / "step5_final"
    out_dir.mkdir(parents=True, exist_ok=True)

    # step1 결과에서 video_id -> title 매핑을 만들어 로그/디버그 가독성을 높임
    title_map: Dict[str, str] = {}
    try:
        step1_path = data_dir / "step1_materials.json"
        if step1_path.exists():
            with step1_path.open("r", encoding="utf-8") as f:
                step1_items = json.load(f)
            if isinstance(step1_items, list):
                for it in step1_items:
                    vid = (it or {}).get("video_id")
                    ttl = ((it or {}).get("title") or "").strip()
                    if vid and ttl:
                        title_map[vid] = ttl
    except Exception:
        title_map = title_map

    if timeline is None:
        raise ValueError("step5_map_debug.run: timeline is required")

    all_results = []
    for vid, payload in timeline.items():
        # title 우선순위: step4 payload(title) -> step1 title_map
        title = ((payload or {}).get("title") or title_map.get(vid, "")).strip()

        final_places = (payload or {}).get("final_places") or []
        result = {
            "video_id": vid,
            "title": title,
            "final_places": final_places,
            "count": len(final_places),
        }
        save_json(out_dir / f"final_{vid}.json", result)
        all_results.append(result)
        log("step5", "saved video", video_id=vid, title=title, count=len(final_places))

    combined = {
        "total_videos": len(all_results),
        "videos": all_results,
    }
    save_json(out_dir / "final_all.json", combined)
    log("step5", "saved final_all", videos=len(all_results))
    return combined
