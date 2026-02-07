import sys
from pathlib import Path

# ✅ import 전에 root 경로 보정
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import config
from utils.io import load_json, save_json
from utils.logging_utils import log
from utils.text_cleaner import resolve_map_links  # ✅ 링크 해석 함수 추가
from llm.gemini_client import extract_itinerary


def _norm_place_name(text: str) -> str:
    return (text or "").strip()


def _dedup_keep_order(items, key_fn):
    seen = set()
    out = []
    for x in items:
        k = key_fn(x)
        if not k or k in seen:
            continue
        seen.add(k)
        out.append(x)
    return out


def run(*, skip_llm: bool = False):
    data_dir = Path(getattr(config, "DATA_DIR", "data"))
    materials = load_json(data_dir / "step1_materials.json") or []

    out_dir = data_dir / "step2_itinerary"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"🚀 [치키 정밀 엔진] 분석 시작 (총 {len(materials)}개 영상)")

    for item in materials:
        vid = item["video_id"]
        title = item.get("title", "")
        description = item.get("description", "") # 설명란 확보

        # ✅ [안정성 강화 핵심] 설명란에 지도 링크(카카오/네이버)가 있으면 제목을 긁어와 힌트로 추가
        print(f"🔍 {vid} 링크 분석 중...")
        map_hints = resolve_map_links(description)
        
        # 설명란 데이터 보강: 링크에서 긁어온 상호명을 텍스트로 추가하여 Gemini에게 전달
        enriched_content = description
        if map_hints:
            enriched_content = f"{description}\n\n[지도 링크 상호명 힌트]: {map_hints}"
            print(f"🔗 {vid} 지도 링크에서 힌트 발견: {map_hints}")

        timeline_candidates = item.get("timeline_candidates") or []
        transcript_segments = item.get("transcript_segments") or []

        # ✅ (A) 설명란/전처리 후보는 "무조건" 포함
        base_itinerary = []
        for i, t in enumerate(timeline_candidates, start=1):
            raw = t.get("raw_place", "")
            place = _norm_place_name(raw)
            if not place:
                continue
            base_itinerary.append(
                {
                    "day": int(t.get("day", 1)),
                    "order": int(t.get("order", i)),
                    "place_name": place,
                    "search_queries": [place],
                    "seconds": t.get("seconds"),
                    "visit_confidence": 0.9,
                    "visit_reason": "description_timeline",
                    "source": t.get("source", "description"),
                }
            )

        llm_status = "SKIPPED" if skip_llm else "NOT_RUN"
        llm_fail_reason = None
        inferred_region = None
        region_confidence = None
        llm_places = []

        # ✅ (B) LLM 호출 보완: 자막이 없으면 '보강된 설명란'을 대신 전송
        if not skip_llm:
            try:
                # 💡 핵심 수정: 자막이 없으면 링크 힌트가 포함된 enriched_content를 보냄
                final_segments = transcript_segments if transcript_segments else enriched_content 
                
                llm_resp = extract_itinerary(
                    video_id=vid,
                    title=title,
                    timeline=timeline_candidates,
                    transcript_segments=final_segments, # 보정된 데이터 전송
                    region_tag=item.get("region_tag"),
                )

                inferred_region = llm_resp.get("inferred_region")
                region_confidence = llm_resp.get("region_confidence")
                places = llm_resp.get("places") or []

                for p in places:
                    place = _norm_place_name(p.get("place_clean") or p.get("place_raw"))
                    if not place:
                        continue

                    sq = [place]
                    if inferred_region:
                        sq.append(f"{inferred_region} {place}")

                    llm_places.append(
                        {
                            "day": int(p.get("day", 1)),
                            "order": int(p.get("order", 9999)),
                            "place_name": place,
                            "search_queries": sq,
                            "seconds": p.get("seconds"),
                            "visit_confidence": p.get("visit_confidence"),
                            "visit_reason": p.get("visit_reason"),
                            "source": "llm",
                            "region_match": p.get("region_match"),
                            "region_reason": p.get("region_reason"),
                        }
                    )

                llm_status = "SUCCESS"
            except Exception as e:
                llm_status = "LLM_ERROR"
                llm_fail_reason = str(e)
                log("step2", f"{vid} LLM error: {llm_fail_reason}")

        # ✅ (C) 합치기: 설명란(base) + LLM(llm_places)
        merged = base_itinerary + llm_places
        merged = _dedup_keep_order(merged, key_fn=lambda x: x.get("place_name"))
        merged.sort(key=lambda x: (int(x.get("day", 1)), int(x.get("order", 9999))))

        for idx, x in enumerate(merged, start=1):
            x["order"] = idx

        result = {
            "video_id": vid,
            "title": title,
            "region_tag": item.get("region_tag"),
            "step2_status": llm_status,
            "llm_fail_reason": llm_fail_reason,
            "inferred_region": inferred_region,
            "region_confidence": region_confidence,
            "itinerary": merged,
        }

        save_json(out_dir / f"itinerary_{vid}.json", result)
        log("step2", f"{vid} places={len(merged)} status={llm_status}")
        print(f"✅ {vid} 분석 완료: 장소 {len(merged)}개 발견 (상태: {llm_status})")

    log("step2", "done")
    print("🏁 모든 작업이 완료되었습니다.")


if __name__ == "__main__":
    run()