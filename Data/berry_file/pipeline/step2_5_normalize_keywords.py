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
    region_map: Dict[str, str] = {}
    try:
        step1_path = data_dir / "step1_materials.json"
        if step1_path.exists():
            with step1_path.open("r", encoding="utf-8") as f:
                step1_items = json.load(f)
            if isinstance(step1_items, list):
                for it in step1_items:
                    vid = (it or {}).get("video_id")
                    ttl = ((it or {}).get("title") or "").strip()
                    rgn = ((it or {}).get("region_tag") or "").strip()
                    if vid and ttl:
                        title_map[vid] = ttl
                    if vid and rgn:
                        region_map[vid] = rgn
    except Exception:
        # 실패해도 파이프라인은 계속 진행
        pass

    if raw is None:
        raise ValueError("step2_5_normalize_keywords.run: raw is required")

    enable = bool(getattr(config, "ENABLE_GEMINI", True))
    if not enable:
        log("step2.5", "ENABLE_GEMINI=False; skipping")
        save_json(out_path, raw)
        save_json(out_dir / "_summary.json", summary)
        return raw

    def _is_must_keep(p: dict) -> bool:
        """Step2에서 seed/제목/설명 기반으로 강하게 남겨둔 후보는 Step2.5에서도 최대한 보존."""
        if not isinstance(p, dict):
            return False
        if bool(p.get("must_keep")):
            return True
        src = (p.get("source") or "").strip().lower()
        if src in {"seed", "title_seed", "desc_seed", "title", "description"}:
            return True
        try:
            return float(p.get("source_weight") or 0) >= 4
        except Exception:
            return False

    results: Dict[str, List[dict]] = {}

    total_videos = len(raw)
    for idx, (video_id, places) in enumerate(raw.items(), 1):
        title = title_map.get(video_id, "")
        region_hint = region_map.get(video_id, "")
        log(
            "step2.5",
            "video",
            video_id=video_id,
            title=title or None,
            idx=f"{idx}/{total_videos}",
            region=region_hint or None,
        )

        if not places:
            save_json(
                out_dir / f"keywords_{video_id}.json",
                {"video_id": video_id, "title": title, "idx": idx, "total": total_videos, "region": region_hint, "kept": [], "dropped": []},
            )
            summary.append({"video_id": video_id, "title": title, "raw": 0, "kept": 0, "dropped": 0, "note": "empty_places"})
            results[video_id] = []
            # 영상별 파일도 남기면 디버깅이 편함
            continue

        phrases_raw = [(p.get("place_name") or "").strip() for p in places if (p.get("place_name") or "").strip()]
        # LLM 토큰 절약: 중복 phrase 제거(등장 순서 유지)
        phrases = list(dict.fromkeys(phrases_raw))
        if not phrases:
            save_json(
                out_dir / f"keywords_{video_id}.json",
                {"video_id": video_id, "title": title, "idx": idx, "total": total_videos, "region": region_hint, "kept": [], "dropped": []},
            )
            summary.append({"video_id": video_id, "title": title, "raw": len(places), "kept": 0, "dropped": 0, "note": "empty_phrases"})
            results[video_id] = []
            continue

        log(
            "llm",
            "step2.5 normalize",
            video_id=video_id,
            title=title or None,
            idx=f"{idx}/{total_videos}",
            region=region_hint or None,
            phrases=len(phrases),
        )

        try:
            normalized = normalize_search_keywords(
                video_id=video_id,
                phrases=phrases,
                region_hint=region_hint,
            )
        except Exception as e:
            log("step2.5", "normalize error", video_id=video_id, err=str(e)[:200])
            save_json(
                out_dir / f"keywords_{video_id}.json",
                {
                    "video_id": video_id,
                    "title": title,
                    "idx": idx,
                    "total": total_videos,
                    "region": region_hint,
                    "kept": [],
                    "dropped": [{"reason": "llm_error", "err": str(e)[:200]}],
                },
            )
            summary.append({"video_id": video_id, "title": title, "raw": len(places), "kept": 0, "dropped": len(places), "note": "llm_error"})
            results[video_id] = []
            continue

        # LLM 원본 출력도 영상별로 저장(디버깅 최강)
        save_json(
            out_dir / f"llm_normalized_{video_id}.json",
            {"video_id": video_id, "title": title, "idx": idx, "total": total_videos, "region": region_hint, "phrases": phrases, "normalized": normalized},
        )

        mapping = {
            (str(n.get("original_phrase")) if n.get("original_phrase") is not None else "").strip(): n
            for n in (normalized or [])
            if isinstance(n, dict) and (str(n.get("original_phrase")) if n.get("original_phrase") is not None else "").strip()
        }

        merged: List[dict] = []
        dropped: List[Dict[str, Any]] = []

        for p in places:
            phrase = (p.get("place_name") or "").strip()
            if not phrase:
                continue

            must_keep = _is_must_keep(p)

            n = mapping.get(phrase)
            if not n:
                if must_keep:
                    merged.append(
                        {
                            **p,
                            "search_name": phrase,
                            "keyword_confidence": 0.0,
                            "keyword_reason": "must_keep_fallback_missing_mapping",
                            "search_name_source": "fallback",
                        }
                    )
                    dropped.append({"place_name": phrase, "reason": "missing_mapping", "kept_override": True})
                else:
                    dropped.append({"place_name": phrase, "reason": "missing_mapping"})
                continue

            if n.get("candidate_drop"):
                if must_keep:
                    fallback_name = (n.get("search_name") or "").strip() or phrase
                    merged.append(
                        {
                            **p,
                            "search_name": fallback_name,
                            "keyword_confidence": n.get("confidence"),
                            "keyword_reason": "must_keep_override_candidate_drop",
                            "search_name_source": "fallback" if fallback_name == phrase else "llm",
                        }
                    )
                    dropped.append({"place_name": phrase, "reason": "candidate_drop", "detail": n, "kept_override": True})
                else:
                    dropped.append({"place_name": phrase, "reason": "candidate_drop", "detail": n})
                continue

            search_name = (n.get("search_name") or "").strip()
            if not search_name:
                if must_keep:
                    merged.append(
                        {
                            **p,
                            "search_name": phrase,
                            "keyword_confidence": n.get("confidence"),
                            "keyword_reason": "must_keep_fallback_empty_search_name",
                            "search_name_source": "fallback",
                        }
                    )
                    dropped.append({"place_name": phrase, "reason": "empty_search_name", "detail": n, "kept_override": True})
                else:
                    dropped.append({"place_name": phrase, "reason": "empty_search_name", "detail": n})
                continue

            merged.append(
                {
                    **p,
                    "search_name": search_name,
                    "keyword_confidence": n.get("confidence"),
                    "keyword_reason": n.get("reason"),
                    "search_name_source": "llm",
                }
            )

        results[video_id] = merged
        log(
            "step2.5",
            "normalized",
            video_id=video_id,
            title=title or None,
            idx=f"{idx}/{total_videos}",
            region=region_hint or None,
            count=len(merged),
        )

        # kept/dropped를 영상별로 저장
        save_json(
            out_dir / f"keywords_{video_id}.json",
            {"video_id": video_id, "title": title, "idx": idx, "total": total_videos, "region": region_hint, "kept": merged, "dropped": dropped},
        )
        summary.append({"video_id": video_id, "title": title, "raw": len(places), "kept": len(merged), "dropped": len(dropped)})

    save_json(out_path, results)
    save_json(out_dir / "_summary.json", summary)
    log("step2.5", "saved", path=str(out_path), videos=len(results))
    return results