import json
import time
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi
from google import genai 
import config

# 1. 설정
INPUT_JSON = "youtube_step1_candidates.json"
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

# 2. Gemini 클라이언트
client = genai.Client(api_key=config.GEMINI_API_KEY)

def fetch_transcript(video_id):
    """베리님이 성공했던 fetch 방식을 클래스 메서드로 호출"""
    try:
        # 베리님 원본에서 성공했던 명령어는 'fetch'가 포함된 로직입니다.
        # 가장 범용적인 'get_transcript'를 다시 한번 정확한 문법으로 씁니다.
        # 만약 이것도 안되면 라이브러리가 'ytt_api.fetch' 방식을 원하는 것입니다.
        from youtube_transcript_api import YouTubeTranscriptApi as yta
        fetched = yta.get_transcript(video_id, languages=["ko", "en"])
        text = " ".join([t["text"] for t in fetched])
        return {"success": True, "text": text}
    except Exception as e:
        return {"success": False, "reason": str(e)}

def extract_courses_with_gemini(transcript_text):
    """'전복죽', '흑돼지'를 장소에서 절대 제외하는 정밀 프롬프트"""
    prompt = f"""
    너는 여행 장소 분석가야. 자막에서 실제 방문한 '상호명(가게이름)'만 JSON으로 추출해.
    
    [절대 규칙]
    1. '전복죽', '고기국수', '흑돼지', '회국수'는 메뉴 이름이지 장소가 아니다. 절대 place_name에 넣지 마.
    2. '명진전복', '숙성도', '자매국수' 같은 고유한 상호명만 추출해.
    3. 가게 이름이 없으면 리스트에 넣지 마.
    
    [결과 형식]
    [
      {{"day": 1, "order": 1, "place_name": "상호명", "search_query": "제주 상호명", "category": "식당"}}
    ]
    
    자막: {transcript_text[:10000]}
    """
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    
    raw_text = response.text
    start = raw_text.find("[")
    end = raw_text.rfind("]")
    return json.loads(raw_text[start:end+1])

def main():
    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        videos = json.load(f)

    print(f"🚀 [치키 복구 엔진] 분석 시작 (자막 명령어 수정 완료)...")

    for idx, v in enumerate(videos, start=1):
        video_id = v["video_id"]
        print(f"[{idx}/8] {video_id} 분석 중...", end=" ")

        res = fetch_transcript(video_id)
        if not res["success"]:
            # 만약 또 'get_transcript' 에러가 나면 여기서 'fetch'로 자동 전환 시도
            try:
                from youtube_transcript_api import YouTubeTranscriptApi as yta
                # 객체 생성 후 fetch 호출 (베리님 스타일)
                api = yta()
                fetched = api.fetch(video_id, languages=["ko", "en"])
                transcript_data = fetched.to_raw_data()
                text = " ".join([t["text"] for t in transcript_data])
                res = {"success": True, "text": text}
            except:
                print(f"❌ 실패: {res['reason']}")
                continue

        try:
            courses = extract_courses_with_gemini(res["text"])
            out_path = OUTPUT_DIR / f"step2_courses_{video_id}.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump({"video_id": video_id, "courses": courses}, f, ensure_ascii=False, indent=2)
            print(f"✅ 성공! ({len(courses)}개 상호명)")
            time.sleep(1)
        except Exception as e:
            print(f"⚠️ 에러: {e}")

if __name__ == "__main__":
    main()