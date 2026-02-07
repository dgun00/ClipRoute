from __future__ import annotations

import json
import os
import re
import time
from typing import Any, Dict, List, Optional

from utils.logging_utils import log


try:
    # Google Gen AI SDK (python-genai)
    from google import genai
except Exception as e:  # pragma: no cover
    genai = None  # type: ignore
    _import_error = e
else:
    _import_error = None


_DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def _get_client() -> Any:
    if genai is None:
        raise RuntimeError(
            "google-genai(python-genai) 패키지가 없습니다. "
            "pip install google-genai 로 설치하세요."
        ) from _import_error

    api_key = os.getenv("GEMINI_API_KEY")
    # config.py가 있는 프로젝트에서는 config.GEMINI_API_KEY를 두는 편이라서,
    # 여기서는 환경변수를 우선하고, 없으면 호출자 쪽에서 예외 처리하도록 둡니다.
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY 가 설정되지 않았습니다. "
            "(환경변수 또는 config.py에서 로딩하도록 run_pipeline에서 처리)"
        )
    return genai.Client(api_key=api_key)


_FENCE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)


def _extract_json(raw_text: str) -> Any:
    """LLM 응답에서 JSON만 안전하게 뽑아서 파싱합니다.

    - ```json ...``` 코드펜스 대응
    - 앞/뒤 설명 텍스트 섞여도 대응
    """
    if not isinstance(raw_text, str) or not raw_text.strip():
        raise ValueError("empty LLM response")

    m = _FENCE.search(raw_text)
    if m:
        raw_text = m.group(1)

    s = raw_text.strip()

    # 1) 배열 우선
    l = s.find("[")
    r = s.rfind("]")
    if 0 <= l < r:
        return json.loads(s[l : r + 1])

    # 2) 객체
    l = s.find("{")
    r = s.rfind("}")
    if 0 <= l < r:
        return json.loads(s[l : r + 1])

    raise ValueError("no JSON found in LLM response")


def _call_gemini(prompt: str, *, model: str, max_retries: int = 2) -> str:
    client = _get_client()
    last_err: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            resp = client.models.generate_content(model=model, contents=prompt)
            text = getattr(resp, "text", None) or ""
            return text
        except Exception as e:
            last_err = e
            wait = 1.5 * (2 ** attempt)
            log("llm", f"gemini error, retrying", attempt=attempt + 1, wait_sec=wait, err=str(e)[:200])
            time.sleep(wait)

    raise RuntimeError(f"Gemini API failed after retries: {last_err}")


def normalize_places_from_text(
    *,
    video_id: str,
    text: str,
    region_hint: str = "",
    model: str = _DEFAULT_MODEL,
) -> List[Dict[str, Any]]:
    """Step2: 자막에서 '실제로 방문한 장소' 후보를 JSON 배열로 추출."""

    region_hint = (region_hint or "").strip()
    hint = region_hint if region_hint else "없음"

    prompt = f"""
너는 여행 영상 자막에서 '실제로 방문한 장소'만 뽑는 엔진이다.
반드시 JSON 배열만 출력한다. 설명/문장 출력 금지.

[규칙]
1) 방문(행동) 근거가 있는 경우만 포함:
   - 도착, 들어가, 입장, 주문, 결제, 먹어, 마셔, 웨이팅, 예약, 체크인 등
2) 단순 언급/희망/추천/스쳐지나감은 제외:
   - 가고 싶다, 유명하대, 지나가다가, 보이네요, 다음에 등
3) 메뉴명/음식명은 장소가 아니다:
   - 흑돼지, 전복죽, 갈치조림 같은 건 제외
4) 결과는 중복 최소화(같은 장소 반복 언급은 1번으로)

[출력 형식]
[
  {{
    "day": 1,
    "order": 1,
    "seconds": 0,
    "place_name": "장소 원문(가능하면 상호명/관광지명)",
    "original_phrase": "자막에서 나온 원문 구절(짧게)",
    "category": "식당/카페/관광지/숙소/기타",
    "confidence": "high/medium/low",
    "reason": "방문 판단 근거(짧게)"
  }}
]

[지역 힌트] {hint}
[video_id] {video_id}

[자막]
{text}
""".strip()

    log("llm", f"[normalize] video_id={video_id}")

    raw = _call_gemini(prompt, model=model)
    data = _extract_json(raw)

    if not isinstance(data, list):
        raise ValueError("LLM output is not a JSON array")

    cleaned: List[Dict[str, Any]] = []
    for x in data:
        if not isinstance(x, dict):
            continue
        place_name = (x.get("place_name") or "").strip()
        if not place_name:
            continue

        cleaned.append(
            {
                "video_id": video_id,
                "day": int(x.get("day") or 1),
                "order": int(x.get("order") or 9999),
                "seconds": x.get("seconds"),
                "place_name": place_name,
                "original_phrase": (x.get("original_phrase") or "").strip() or None,
                "category": (x.get("category") or "기타").strip(),
                "visit_confidence": (x.get("confidence") or "unknown").strip(),
                "visit_reason": (x.get("reason") or "").strip() or None,
                "source": "gemini",
            }
        )

    return cleaned


def normalize_search_keywords(
    *,
    video_id: str,
    phrases: List[str],
    region_hint: str = "",
    model: str = _DEFAULT_MODEL,
) -> List[Dict[str, Any]]:
    """Step2.5: 원문 phrase -> 네이버 검색용 search_name 정규화."""

    region_hint = (region_hint or "").strip()
    hint = region_hint if region_hint else "없음"

    # 입력 개수와 동일 길이로 매핑을 강제하기 위해, 중복 제거는 하지 않음.
    payload = json.dumps(phrases, ensure_ascii=False)

    prompt = f"""
너는 '장소명 정규화' 엔진이다.
입력 phrase는 자막 원문이 섞여 있을 수 있다.
반드시 JSON 배열만 출력하고, 설명은 절대 출력하지 마라.

[목표]
- 네이버 지역검색에 넣기 좋은 '검색어(search_name)'로 정리한다.

[규칙]
1) 수식어/감탄/형용 제거:
   - 맛있는, 유명한, 진짜, 너무, 완전, 대박, 최고, 찐, 핫한 등 제거
2) 조사/어미/불필요한 문장부호 제거:
   - ~에, ~에서, ~가는길, ~왔어요 같은 꼬리 제거
3) 메뉴/음식명으로 의심되면 제외(candidate_drop=true):
   - 전복죽, 흑돼지, 갈치조림 등
4) 브랜드+지점명은 유지:
   - '스타벅스 제주...점', '홍콩반점0410 연동점' 등은 유지
5) 너무 일반적인 단어는 제외(candidate_drop=true):
   - 카페, 식당, 맛집, 해변, 관광지 같은 단독 일반명사
6) 결과는 입력 개수와 동일한 길이로 만든다(매핑 깨지면 안됨).

[출력 형식]
[
  {{
    "original_phrase": "...",
    "search_name": "...",
    "candidate_drop": false,
    "confidence": "high/medium/low",
    "reason": "짧게"
  }}
]

[지역 힌트] {hint}
[video_id] {video_id}

[입력 phrases]
{payload}
""".strip()

    log("llm", f"[normalize-keywords] video_id={video_id} phrases={len(phrases)}")

    raw = _call_gemini(prompt, model=model)
    data = _extract_json(raw)

    if not isinstance(data, list):
        raise ValueError("LLM output is not a JSON array")

    # 길이 맞추기(안 맞으면 전부 drop 처리로 보수적으로)
    if len(data) != len(phrases):
        log("step2.5", "LLM length mismatch; fallback to drop-all", got=len(data), expected=len(phrases))
        return [
            {
                "original_phrase": p,
                "search_name": "",
                "candidate_drop": True,
                "confidence": "low",
                "reason": "length mismatch",
            }
            for p in phrases
        ]

    out: List[Dict[str, Any]] = []
    for original, x in zip(phrases, data):
        if not isinstance(x, dict):
            out.append(
                {
                    "original_phrase": original,
                    "search_name": "",
                    "candidate_drop": True,
                    "confidence": "low",
                    "reason": "invalid item",
                }
            )
            continue

        out.append(
            {
                "original_phrase": original,
                "search_name": (x.get("search_name") or "").strip(),
                "candidate_drop": bool(x.get("candidate_drop")),
                "confidence": (x.get("confidence") or "unknown").strip(),
                "reason": (x.get("reason") or "").strip() or None,
            }
        )

    return out
