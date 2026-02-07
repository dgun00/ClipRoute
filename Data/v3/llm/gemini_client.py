import json
import re
import config
from google import genai

MODEL_NAME = getattr(config, "GEMINI_MODEL_NAME", "models/gemini-2.5-flash")
client = genai.Client(api_key=config.GEMINI_API_KEY)

_JSON_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)


def build_itinerary_prompt(
    *,
    video_id: str,
    title: str,
    timeline: list,
    transcript_segments: list,
) -> str:
    return f"""
너는 여행 브이로그를 분석하는 전문가다. 
베리님이 보고한 '장소명 수식어 오염' 문제를 해결하기 위해 아래 [수식어 제거 수칙]을 최우선으로 지켜라.

[목표]
1. 이 영상의 "대표 여행 지역"을 하나 추론하라.
2. 영상 속에서 "실제로 방문한 장소"만 추출하라.

[수식어 제거 및 정규화 수칙 - 중요!]
- place_clean은 네이버 검색 시 '검색 실패'가 뜨지 않도록 **순수 고유명사**만 남긴다.
- 모든 주관적 형용사 및 수식어는 삭제한다.
  * (예) "진짜 맛있는 명진전복" -> "명진전복"
  * (예) "함덕 근처에 있는 카페 델문도" -> "카페 델문도"
  * (예) "뷰 맛집 뷰스트" -> "뷰스트"
- 메뉴 이름이 장소명에 섞이지 않게 분리한다.
  * (예) "전복죽이 맛있는 명진전복" -> "명진전복"
- 불필요한 지역명 중복을 피한다. 단, 상호명 자체가 지역명을 포함한 경우는 유지한다.
- '외부 링크 힌트 활용': 설명란에 카카오맵(kko.kakao.com)이나 네이버 지도 링크가 있다면, 해당 링크 주변의 텍스트와 영상 제목을 조합하여 방문지를 유추하라.
- '자막 내 고유명사 집중': 설명란이 부족하다면 자막(Transcript)에서 '식당', '도착', '먹으러'라는 단어와 함께 등장하는 고유명사(예: 자매국수, 미영이네)를 반드시 추출하라.
# build_itinerary_prompt 내부 수칙에 추가
- '신조어 및 줄임말' 삭제: '느좋'(느낌 좋은), '닝호아', '알잘딱깔센' 등 유행어나 줄임말이 붙은 경우 상호명에서 즉시 제거하라.
- '장소 유형' 일반 명사 삭제: 상호명이 명확하지 않고 '느좋카페', '제주맛집', '감성숙소'처럼 장소의 특징만 나열된 경우 리스트에서 제외하라.
- (예시 추가) "느좋 카페 델문도" -> "카페 델문도" (O) / "느좋카페" -> (제외)
- 상호명 보존 법칙: '감성커피', '인생네컷' 등 수식어가 상호명의 고유한 일부분(브랜드명)인 경우에는 절대 삭제하지 마라.
- 판단 기준: 단독으로 존재할 때 의미가 모호한 '감성', '인생' 등이 뒤에 오는 '커피', '식당' 등과 결합하여 하나의 특정 브랜드를 형성한다면 전체를 유지하라.
- 삭제 대상 명확화: 상호명 앞에 붙은 별도의 형용사구(예: "분위기 좋은", "진짜 맛있는")만 제거하라.
- '제목 데이터(Title) 적극 활용': 자막이나 설명란이 부실한 경우, 영상 제목에 나열된 상호명을 최우선으로 추출하라.
  * (예) "제주 맛집 (이재모피자/오는정김밥/우진해장국)" -> [이재모피자, 오는정김밥, 우진해장국] 추출.
  * 이때, 괄호()나 슬래시(/) 등의 기호를 제거하고 순수 상호명만 남겨라.
- '장소 판단 우선순위': 설명란 타임라인 > 영상 제목 내 상호명 > 자막 순으로 신뢰하여 추출하라.

[방문 판단 원칙]
- (~하려다, ~가고 싶다, ~지나가는 길, ~유명하대요)와 같은 미래형/가정형/단순 언급은 무조건 제외한다.
- 도착, 입장, 주문, 결제 등 실제 경험이 확인되는 장소만 포함한다.
- 자막이 부족하다면 [설명란 타임라인]의 텍스트를 최우선 근거로 삼는다.

[입력 정보]
- video_id: {video_id}
- title: {title}
- 설명란 타임라인 후보: {json.dumps(timeline or [], ensure_ascii=False)}
- 자막 데이터: {json.dumps(transcript_segments or [], ensure_ascii=False)}

[출력 스키마]
{{
  "inferred_region": "대표 여행 지역",
  "region_confidence": "high|medium|low",
  "places": [
    {{
      "place_raw": "원본 텍스트",
      "place_clean": "수식어가 완전히 제거된 순수 상호명",
      "seconds": 123,
      "visit_confidence": "high|medium|low",
      "visit_reason": "방문으로 판단한 근거",
      "region_match": true|false
    }}
  ]
}}
""".strip()


def call_gemini_json(prompt: str) -> dict:
    try:
        resp = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config={
                "temperature": 0.2,
                "response_mime_type": "application/json",
            },
        )
    except TypeError:
        resp = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            generation_config={
                "temperature": 0.2,
                "response_mime_type": "application/json",
            },
        )

    text = (getattr(resp, "text", None) or "").strip()
    text = _JSON_FENCE_RE.sub("", text).strip()

    try:
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError("Gemini output is not a JSON object")
        return data
    except Exception as e:
        raise RuntimeError(f"Gemini JSON 파싱 실패: {e}\n{text}")


def extract_itinerary(
    *,
    video_id: str,
    title: str,
    timeline: list,
    transcript_segments: list,
    region_tag=None,   # ✅ 받아도 되고 안 써도 됨 (호환성용)
) -> dict:
    prompt = build_itinerary_prompt(
        video_id=video_id,
        title=title,
        timeline=timeline,
        transcript_segments=transcript_segments,
    )
    return call_gemini_json(prompt)