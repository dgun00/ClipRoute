from __future__ import annotations
import os
import config
from pipeline.step0_collect_videos import run as step0
from pipeline.step1_collect_materials import run as step1
from pipeline.step2_build_itinerary_llm import run as step2
from pipeline.step3_naver_verify_places import run as step3
from pipeline.step4_sort_timeline import run as step4
from pipeline.step5_map_debug import run as step5

def _bootstrap_env():
    keys = ["OPENAI_API_KEY", "GEMINI_API_KEY", "NAVER_CLIENT_ID", "NAVER_CLIENT_SECRET"]
    for key in keys:
        if not os.getenv(key) and getattr(config, key, None):
            os.environ[key] = str(getattr(config, key))

def main():
    print("\n" + "="*50 + "\n🚀 Clip Route V5-6: Gemini 2.5 Flash Full Stack\n" + "="*50)
    _bootstrap_env()
    
    region = input("어디로 떠나시나요?: ")
    num_videos_raw = input("분석 영상 수: ")
    num_videos = int(num_videos_raw) if num_videos_raw.isdigit() else 10

    # Step 0: 수집
    videos = step0(keyword=f"{region} 여행 코스 맛집 브이로그")
    if not videos: return print("❌ 수집된 영상이 없습니다.")

    # 분석 대상 영상 리스트 출력
    print("\n" + "="*65 + f"\n📺 분석 대상 영상 리스트 (총 {len(videos)}개)\n" + "="*65)
    for i, v in enumerate(videos, 1):
        print(f"  {i:2d}. [{v.get('video_id')}] {v.get('title')[:40]}...")
    print("="*65 + "\n")

    # Step 1: Whisper STT
    materials = step1(videos)
    
    # Step 2: Gemini 2.5 Flash 병렬 분석
    report = step2(materials)
    
    # Step 3: 검증
    print(f"\n[Step 3] 지도 API 검증 중...")
    verified = step3(report, region=region) 
    
    # Step 4: 이중 정렬 (Day + Order)
    print(f"\n[Step 4] 일차별/순서별 타임라인 정렬 중...")
    sorted_data = step4(verified)
    
    # Step 5: 지도 시각화
    print(f"[Step 5] 최종 지도 생성 중...")
    try:
        step5(sorted_data, region)
    except:
        step5(sorted_data)

    # 💰 정산
    usage = report.get("usage", {})
    t_total = usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0)
    print("\n" + "="*70 + f"\n💰 [TOTAL BILL] Gemini 2.5 Flash Usage: {t_total:,} tokens\n" + "="*70)
    print("data/step5_map.html 확인")

if __name__ == "__main__":
    main()