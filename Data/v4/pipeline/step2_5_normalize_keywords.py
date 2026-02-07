from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Any

import json
import config
from llm.gemini_client import normalize_search_keywords
from utils.logging_utils import log
from utils.io import save_json


def run(raw: Dict[str, List[dict]]) -> Dict[str, List[dict]]:
    """Step2.5: place_name -> search_name 정규화 (네이버 검색용)"""
    data_dir = Path(getattr(config, "DATA_DIR", "data"))
    out_path = data_dir / "step2_5_keywords_normalized.json"

    # 추가: 영상별 저장 디렉터리 + 요약
    out_dir = data_dir / "step2_5_keywords_normalized"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary: List[Dict[str, Any]] = []

    # step1에서 저장된 title을 불러와 video_id -> title 매핑 생성 (디버그 편의용)
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
        # 실패해도 파이프라인은 계속 진행
        title_map = title_map

    if raw is None:
        raise ValueError("step2_5_normalize_keywords.run: raw is required")

    enable = bool(getattr(config, "ENABLE_GEMINI", True))
    if not enable:
        log("step2.5", "ENABLE_GEMINI=False; skipping")
        save_json(out_path, raw)
        save_json(out_dir / "_summary.json", summary)
        return raw

    results: Dict[str, List[dict]] = {}

    for video_id, places in raw.items():
        title = title_map.get(video_id, "")
        if title:
            log("step2.5", "video", video_id=video_id, title=title)

        if not places:
            save_json(out_dir / f"keywords_{video_id}.json", {"video_id": video_id, "title": title, "kept": [], "dropped": []})
            summary.append({"video_id": video_id, "title": title, "raw": 0, "kept": 0, "dropped": 0, "note": "empty_places"})
            results[video_id] = []
            # 영상별 파일도 남기면 디버깅이 편함
            continue

        phrases = [p.get("place_name") for p in places if (p.get("place_name") or "").strip()]
        if not phrases:
            save_json(out_dir / f"keywords_{video_id}.json", {"video_id": video_id, "title": title, "kept": [], "dropped": []})
            summary.append({"video_id": video_id, "title": title, "raw": len(places), "kept": 0, "dropped": 0, "note": "empty_phrases"})
            results[video_id] = []
            continue

        log("llm", "step2.5 normalize", video_id=video_id, title=title, phrases=len(phrases))

        try:
            normalized = normalize_search_keywords(
                video_id=video_id,
                phrases=phrases,
                region_hint="",  # region은 Step3에서 강제(prefix+주소필터) 적용하므로 여기서는 비워도 됨
            )
        except Exception as e:
            log("step2.5", "normalize error", video_id=video_id, err=str(e)[:200])
            save_json(out_dir / f"keywords_{video_id}.json", {"video_id": video_id, "title": title, "kept": [], "dropped": [{"reason": "llm_error", "err": str(e)[:200]}]})
            summary.append({"video_id": video_id, "title": title, "raw": len(places), "kept": 0, "dropped": len(places), "note": "llm_error"})
            results[video_id] = []
            continue

        # LLM 원본 출력도 영상별로 저장(디버깅 최강)
        save_json(
            out_dir / f"llm_normalized_{video_id}.json",
            {"video_id": video_id, "title": title, "phrases": phrases, "normalized": normalized},
        )

        mapping = {
            n["original_phrase"]: n
            for n in (normalized or [])
            if isinstance(n, dict) and n.get("original_phrase")
        }

        merged: List[dict] = []
        dropped: List[Dict[str, Any]] = []

        for p in places:
            phrase = p.get("place_name")
            if not phrase:
                continue

            n = mapping.get(phrase)
            if not n:
                dropped.append({"place_name": phrase, "reason": "missing_mapping"})
                continue

            if n.get("candidate_drop"):
                dropped.append({"place_name": phrase, "reason": "candidate_drop", "detail": n})
                continue

            search_name = (n.get("search_name") or "").strip()
            if not search_name:
                dropped.append({"place_name": phrase, "reason": "empty_search_name", "detail": n})
                continue

            merged.append(
                {
                    **p,
                    "search_name": search_name,
                    "keyword_confidence": n.get("confidence"),
                    "keyword_reason": n.get("reason"),
                }
            )

        results[video_id] = merged
        log("step2.5", "normalized", video_id=video_id, count=len(merged))

        # kept/dropped를 영상별로 저장
        save_json(
            out_dir / f"keywords_{video_id}.json",
            {"video_id": video_id, "title": title, "kept": merged, "dropped": dropped},
        )
        summary.append({"video_id": video_id, "title": title, "raw": len(places), "kept": len(merged), "dropped": len(dropped)})

    save_json(out_path, results)
    save_json(out_dir / "_summary.json", summary)
    log("step2.5", "saved", path=str(out_path), videos=len(results))
    return results