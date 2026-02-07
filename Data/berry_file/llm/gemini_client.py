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


_TS_RE = re.compile(r"<?(\d{1,2}:\d{2}:\d{2}(?:\.\d{1,3})?)>?" )


def _ts_to_seconds(ts: str) -> Optional[float]:
    """Convert `HH:MM:SS(.mmm)` to seconds."""
    ts = (ts or "").strip()
    if not ts:
        return None
    m = _TS_RE.search(ts)
    if m:
        ts = m.group(1)

    parts = ts.split(":")
    if len(parts) != 3:
        return None

    try:
        h = int(parts[0])
        mm = int(parts[1])
        ss = float(parts[2])
        return h * 3600 + mm * 60 + ss
    except Exception:
        return None


def _normalize_seconds(value: Any) -> Optional[float]:
    """Accept numbers or timestamp-like strings and normalize to seconds(float)."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        v = value.strip()
        if not v:
            return None
        # numeric string
        try:
            return float(v)
        except Exception:
            pass
        # timestamp string
        return _ts_to_seconds(v)
    return None


def _fallback_keyword(phrase: str) -> Dict[str, Any]:
    """Very conservative local fallback when LLM output is malformed.

    Goal: avoid dropping real place names. Only drop when it is clearly generic.
    """
    p = (phrase or "").strip()
    if not p:
        return {
            "original_phrase": phrase,
            "search_name": "",
            "candidate_drop": True,
            "confidence": "low",
            "reason": "empty",
        }

    generic_exact = {
        "카페",
        "식당",
        "맛집",
        "숙소",
        "호텔",
        "펜션",
        "게스트하우스",
        "해변",
        "바다",
        "시장",
        "마트",
        "공항",
        "터미널",
        "주차장",
        "여기",
        "현장",
    }

    if p in generic_exact:
        return {
            "original_phrase": phrase,
            "search_name": "",
            "candidate_drop": True,
            "confidence": "low",
            "reason": "generic_label",
        }

    # keep by default (even short 2~4 chars could be a real brand/store)
    return {
        "original_phrase": phrase,
        "search_name": p,
        "candidate_drop": False,
        "confidence": "low",
        "reason": "fallback_keep",
    }


def _call_gemini(prompt: str, *, model: str, max_retries: int = 2) -> str:
    client = _get_client()
    last_err: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            resp = client.models.generate_content(model=model, contents=prompt)
            # usage metadata (if available) for cost/debug visibility
            usage = getattr(resp, "usage_metadata", None) or getattr(resp, "usageMetadata", None)
            if usage is not None:
                # try common field names used by SDKs
                pt = getattr(usage, "prompt_token_count", None) or getattr(usage, "promptTokenCount", None)
                ct = getattr(usage, "candidates_token_count", None) or getattr(usage, "candidatesTokenCount", None)
                tt = getattr(usage, "total_token_count", None) or getattr(usage, "totalTokenCount", None)
                log(
                    "llm",
                    "usage",
                    model=model,
                    prompt_tokens=pt,
                    output_tokens=ct,
                    total_tokens=tt,
                )

            text = getattr(resp, "text", None) or ""
            return text
        except Exception as e:
            last_err = e
            wait = 1.5 * (2 ** attempt)
            log(
                "llm",
                "gemini error, retrying",
                model=model,
                attempt=attempt + 1,
                wait_sec=wait,
                err=str(e)[:200],
            )
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
너는 여행 영상의 텍스트(제목/설명/챕터/자막)에서 '장소 후보'를 뽑는 엔진이다.
반드시 JSON 배열만 출력한다. 설명/문장 출력 금지.

[입력 구성]
- 아래 [TEXT] 영역에는 실제 자막뿐 아니라, [TITLE]/[DESCRIPTION]/[DESCRIPTION_CHAPTERS] 같은 메타 정보가 함께 섞여 있을 수 있다.
- 메타에만 등장하고 자막(대사)에 방문 행동이 부족한 경우도 있다.

[규칙]
1) 가능한 한 '실제로 방문한 장소'를 우선한다:
   - 도착, 들어가, 입장, 주문, 결제, 먹어, 마셔, 웨이팅, 예약, 체크인 등 행동 근거가 있으면 confidence를 높게 준다.
2) 행동 근거가 약하더라도, TITLE/DESCRIPTION/CHAPTERS에 등장하는 '구체 상호/지명'은 **절대 누락하지 말고** 후보로 포함한다:
   - 이 경우 confidence는 low로 두고 reason에 `title/description/chapters mention` 같은 근거를 적는다.
3) 단순 언급/희망/추천/스쳐지나감만 있는 경우는 제외:
   - 가고 싶다, 유명하대, 지나가다가, 보이네요, 다음에 등
4) 메뉴명/음식명은 장소가 아니다:
   - 흑돼지, 전복죽, 갈치조림 같은 건 제외
5) 결과는 중복 최소화(같은 장소 반복 언급은 1번으로)

[중요: 고유명사(구체 상호/지명)만]
- place_name은 반드시 특정 장소를 식별 가능한 '고유명사'여야 한다.
- 금지(절대 출력 X, 고유명사가 아니면 아예 제외):
  "숙소", "카페", "식당", "맛집", "편의점", "해변", "바다", "시장", "마트", "공항", "터미널", "주차장", "여기", "현장" 등 일반명사/추상 라벨
  "restaurant", "cafe", "hotel", "guesthouse" 같은 단독 일반명사(이름 없이 업종/시설만 있는 경우)
- 허용(예시):
  "천지연폭포", "정방폭포", "새연교", "우무", "자매국수", "글로시말차" 처럼 고유한 지명/상호/시설명
  "OO게스트하우스", "OO호텔", "OO카페"처럼 고유명사+업종 결합

[타임스탬프/seconds 규칙]
- [TEXT] 안에 `00:00:23.400` 또는 `<00:00:23.400>` 같은 시간 표기가 있으면, 해당 근거 문장과 가까운 장소의 seconds를 초(정수 또는 소수)로 채운다.
- 변환 규칙: HH:MM:SS.mmm -> HH*3600 + MM*60 + SS.mmm
- 변환 불가하면 seconds는 null

[출력 형식]
반드시 아래 키를 갖는 객체들의 JSON 배열만 출력한다.
- day: 정수(없으면 1)
- order: 정수(없으면 9999)
- seconds: 숫자(초) 또는 null
- place_name: 문자열(고유명사)
- original_phrase: 근거가 되는 원문 일부(짧게)
- category: 문자열(식당/카페/관광지/숙소/기타 중 하나 권장)
- confidence: high/medium/low
- reason: 한 줄 근거

[지역 힌트] {hint}
[video_id] {video_id}

[TEXT]
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
                "seconds": _normalize_seconds(x.get("seconds")),
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
5) 너무 일반적인 단어/추상 라벨/템플릿 문구는 제외(candidate_drop=true):
   - 단독 일반명사: "카페", "식당", "맛집", "숙소", "호텔", "펜션", "게스트하우스", "해변", "바다", "시장", "마트", "공항", "터미널", "주차장" 등
   - 템플릿/라벨: "도착 장소", "이전 방문 장소", "방문 장소", "예약 문의 장소", "실내 장소", "여기", "현장" 등
   - 영어 단독 일반명사: "restaurant", "cafe", "hotel", "guesthouse", "bridge", "waterfall" 등(이름 없이 업종/시설만 있는 경우)
   - 이런 경우에는 search_name을 빈 문자열로 두고 candidate_drop=true로 처리한다.
5-1) 2~4글자 한글 단어라도 실제 상호/지명일 수 있다:
   - 예: "우무", "점점"처럼 짧아도 상호일 가능성이 있으면 candidate_drop=false로 두고 search_name을 원문에 가깝게 유지한다.
   - 단, 정말로 대명사/부사/감탄사처럼 장소일 가능성이 매우 낮으면 drop 처리한다.
6) 고유명사+업종 결합은 유지:
   - 예: "우무 카페", "OO게스트하우스", "스타벅스 연동점" 등은 candidate_drop=false
7) 결과는 입력 개수와 동일한 길이로 만든다(매핑 깨지면 안됨).

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
        # Be conservative: try to recover by mapping on `original_phrase`.
        # If still impossible, keep phrases instead of dropping everything.
        log(
            "step2.5",
            "LLM length mismatch; fallback to mapping/fallback_keep",
            got=len(data),
            expected=len(phrases),
        )

        mapping: Dict[str, Dict[str, Any]] = {}
        for item in data:
            if isinstance(item, dict) and item.get("original_phrase"):
                mapping[str(item["original_phrase"]).strip()] = item

        recovered: List[Dict[str, Any]] = []
        for p in phrases:
            key = (p or "").strip()
            item = mapping.get(key)
            if not isinstance(item, dict):
                recovered.append(_fallback_keyword(p))
                continue

            recovered.append(
                {
                    "original_phrase": p,
                    "search_name": (item.get("search_name") or "").strip(),
                    "candidate_drop": bool(item.get("candidate_drop")),
                    "confidence": (item.get("confidence") or "unknown").strip(),
                    "reason": (item.get("reason") or "").strip() or None,
                }
            )

        return recovered

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

        search_name = (x.get("search_name") or "").strip()
        candidate_drop = bool(x.get("candidate_drop"))

        # If model forgot to fill search_name but didn't drop, keep original to avoid losing real places.
        if not search_name and not candidate_drop:
            search_name = (original or "").strip()

        out.append(
            {
                "original_phrase": original,
                "search_name": search_name,
                "candidate_drop": candidate_drop,
                "confidence": (x.get("confidence") or "unknown").strip(),
                "reason": (x.get("reason") or "").strip() or None,
            }
        )

    return out
