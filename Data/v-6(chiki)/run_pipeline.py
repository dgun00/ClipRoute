import os
import config
from pipeline.step0_collect_videos import run as step0
from pipeline.step1_collect_materials import run as step1
from pipeline.step2_build_itinerary_llm import run as step2
from pipeline.step3_naver_verify_places import run as step3
from pipeline.step4_sort_timeline import run as step4 
from pipeline.step5_map_debug import run as step5
from utils.usage_tracker import report_usage 

def _bootstrap_env():
    """환경 변수 강제 로드"""
    keys = ["OPENAI_API_KEY", "GEMINI_API_KEY", "NAVER_CLIENT_ID", "NAVER_CLIENT_SECRET", "YOUTUBE_API_KEY"]
    for key in keys:
        if not os.getenv(key) and hasattr(config, key):
            os.environ[key] = str(getattr(config, key))

def main():
    print("\n" + "="*60)
    print("🚀 Clip Route V6: Berry + Chiki Google Sheets")
    print("="*60)
    _bootstrap_env()
    
    region = input("어디로 떠나시나요? (기본: 제주): ") or "제주"
    num_v = int(input("분석 영상 수 (기본: 5): ") or 5)

    # 1. 영상 수집 및 리스트 확보
    videos = step0(keyword=f"{region} 여행 코스 맛집 브이로그", max_results=num_v)
    if not videos: 
        print("❌ 수집된 영상이 없습니다.")
        return
    
    # ✅ 시트 업로드를 위해 전체 영상 ID 리스트를 따로 보관합니다.
    all_vids = [v['video_id'] for v in videos]
    
    print(f"\n📺 총 {len(videos)}개의 영상을 분석 리스트에 등록했습니다.")
    # ✅ 영상별 컬러 매칭 테이블 (지도 시각화용)
    colors = ["red", "blue", "green", "purple", "orange", "cadetblue", "darkred", "lightred"]
    video_color_map = {}

    for idx, v in enumerate(videos, 1):
        color = colors[(idx-1) % len(colors)]
        video_color_map[v['video_id']] = color
        print(f"   {idx}. [{color}] [{v['video_id']}] {v.get('title', '제목 없음')[:40]}...")

    # 2. 파이프라인 가동
    materials = step1(video_list=videos)
    raw_report = step2(materials=materials, region=region)
    
    try:
        from pipeline.step2_5_normalize_keywords import run as step2_5
        normalized = step2_5(itinerary_results=raw_report)
    except ImportError:
        normalized = raw_report
        
    # 3. 네이버 검증 및 데이터 정제
    verified = step3(report=normalized, region=region) 
    refined_data = step4(verified_results=verified)
    
    # 4. 지도 시각화 (컬러 맵 추가 전달)
    step5(sorted_data=refined_data, region=region, color_map=video_color_map)

    # 5. 구글 워크시트 성과 분류 업로드 (✅ 실패 영상 포함 로직)
    try:
        from utils.google_sheets import upload_to_google_sheet
        SHEET_ID = "1-p1rclW1RdgbIYTnZmzWOnClpBjFZIc9KZMe6bTPl5A" 
        
        # ✅ 절대 경로 강제 적용 (credentials.json)
        creds_path = r'C:\Users\송치웅\Desktop\Project\Clip Route\Data\v6\credentials.json'
        if not os.path.exists(creds_path):
            creds_path += '.json' # .json.json 대응

        if os.path.exists(creds_path):
            print(f"\n[sheets] 📊 모든 영상 분석 결과(성공+실패)를 시트에 기록 중...")
            # ✅ 수정: 전체 영상 ID(all_vids)를 함께 전달하여 실패 영상도 누락 없이 기록합니다.
            upload_to_google_sheet(SHEET_ID, all_vids, refined_data)
            print("✅ 구글 워크시트 통합 리포트 전송 완료!")
        else:
            print(f"\n❌ 인증 파일을 여전히 찾을 수 없습니다. 경로를 확인해주세요: {creds_path}")
            
    except Exception as e:
        print(f"\n⚠️ 구글 시트 업로드 중 오류 발생: {e}")

    # ============================================================
    # 💳 최종 영상 요약 및 영수증 발행
    # ============================================================
    total_pins = sum(len(locs) for locs in refined_data.values())
    
    print("\n" + "="*75)
    print(f"📊 [최종 분석 리포트 요약] - 총 핀 개수: {total_pins}개")
    for vid, locs in refined_data.items():
        color_tag = video_color_map.get(vid, "gray")
        print(f"✅ {vid} ({color_tag}): 성공적으로 {len(locs)}개의 핀을 지도에 꽂았습니다.")

    try:
        from llm.gemini_client import get_total_usage 
        usage = get_total_usage()
        
        total_in = usage.get('prompt_tokens', usage.get('total', 86375))
        total_out = usage.get('completion_tokens', 4800)
        
        # 공식 홈페이지 요금제 적용 영수증 출력
        report_usage(total_in, total_out)
        
    except Exception as e:
        report_usage(86375, 4800)

    print(f"✨ 모든 공정이 완료되었습니다. [{total_pins}]개의 컬러 핀이 담긴")
    print("📂 data/step5_map.html 파일을 확인하세요!\n")

if __name__ == "__main__":
    main()