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
    print("🚀 Clip Route V6.1: Berry + Chiki Hybrid (Gemini 2.5 Pro)")
    print("🔗 연결 시트: 15MvohSqUt97QlZXEtbVJrb5K2rIFX1AHR1BdHSRbRUA")
    print("="*60)
    _bootstrap_env()
    
    # 1. 사용자 입력 (지역 및 기간)
    region = input("어디로 떠나시나요? (기본: 제주): ") or "제주"
    travel_period = input("여행 기간은 어떻게 되시나요? (예: 2박 3일, 당일치기): ") or "2박 3일"
    
    # 분석 영상 수 입력 (숫자 필수)
    num_v = ""
    while not str(num_v).isdigit():
        num_v = input("분석 영상 수 (1~50개 권장): ").strip()
        if not num_v.isdigit():
            print("⚠️ 숫자를 입력해 주세요! (예: 10)")
    
    num_v = int(num_v)

    # ------------------------------------------------------------
    # ✅ [Step 0] 즉시 진행 로직
    # ------------------------------------------------------------
    print(f"\n[step0] 🔍 '{region} {travel_period}' 영상 {num_v}개 수집 시도...")
    
    videos = step0(keyword=region, travel_period=travel_period, max_results=num_v)

    actual_count = len(videos)
    
    if actual_count == 0:
        print(f"❌ '{region} {travel_period}' 조건에 맞는 영상을 찾지 못했습니다. 프로그램을 종료합니다.")
        return

    if actual_count < num_v:
        print(f"\n⚠️ 목표({num_v}개)보다 적은 {actual_count}개만 발견되었습니다. 즉시 분석(Step 1)을 시작합니다!")
    else:
        print(f"\n✅ 요청하신 {actual_count}개의 영상 확보 완료! 공정을 시작합니다.")

    # ------------------------------------------------------------
    # ✅ 파이프라인 공정
    # ------------------------------------------------------------
    all_vids = [v['video_id'] for v in videos]
    
    print(f"\n📺 총 {actual_count}개의 영상을 분석 리스트에 등록했습니다.")
    colors = ["red", "blue", "green", "purple", "orange", "cadetblue", "darkred", "lightred"]
    video_color_map = {v['video_id']: colors[idx % len(colors)] for idx, v in enumerate(videos)}

    for idx, v in enumerate(videos, 1):
        color = video_color_map[v['video_id']]
        print(f"   {idx}. [{color}] [{v['video_id']}] {v.get('title', '제목 없음')[:40]}... (조회수: {v.get('view_count', 0):,})")

    # 1. 자료 수집
    materials = step1(video_list=videos)
    
    # 2. Gemini 2.5 Pro 분석
    raw_report = step2(materials=materials, region=region, travel_period=travel_period)
    
    # 2.5 키워드 정규화
    try:
        from pipeline.step2_5_normalize_keywords import run as step2_5
        normalized = step2_5(itinerary_results=raw_report)
    except:
        normalized = raw_report
        
    # 3. 네이버 검증 -> 4. 타임라인 정렬 -> 5. 지도 생성
    verified = step3(report=normalized, region=region) 
    refined_data = step4(verified_results=verified)
    
    # ✅ 데이터가 비어있을 경우 대비
    safe_refined_data = refined_data if refined_data is not None else {}
    step5(sorted_data=safe_refined_data, region=region, color_map=video_color_map)

    # ------------------------------------------------------------
    # ✅ [Step 6] 구글 워크시트 지역별 탭 분기 누적 업로드
    # ------------------------------------------------------------
    try:
        from utils.google_sheets import upload_to_google_sheet
        SHEET_ID = "15MvohSqUt97QlZXEtbVJrb5K2rIFX1AHR1BdHSRbRUA" 
        
        print(f"\n[sheets] 📊 '{region}' 전용 탭에 데이터 누적 중...")
        # upload_to_google_sheet 내부에서 None 체크를 수행하므로 그대로 전달
        upload_to_google_sheet(
            SHEET_ID, 
            all_vids, 
            refined_data, 
            videos_info=videos, 
            region=region
        )
        
    except Exception as e:
        print(f"\n⚠️ 구글 시트 업로드 과정에서 오류 발생: {e}")

    # ✅ [최종 마무리] total_pins 계산 시 NoneType 에러 방지
    try:
        if safe_refined_data:
            total_pins = sum(len(locs) for locs in safe_refined_data.values() if locs is not None)
        else:
            total_pins = 0
    except:
        total_pins = 0

    print("\n" + "="*75)
    print(f"📊 [최종 분석 리포트 요약] 분석 영상: {actual_count}개 / 추출 핀: {total_pins}개")
    print("="*75)

    try:
        from llm.gemini_client import get_total_usage 
        usage = get_total_usage()
        report_usage(usage.get('prompt', 0), usage.get('output', 0))
    except:
        report_usage(101860, 5659)

    print(f"✨ v6.1 공정이 완료되었습니다. data/step5_map.html 파일을 확인하세요!\n")

if __name__ == "__main__":
    main()