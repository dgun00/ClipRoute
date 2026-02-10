import gspread
from google.oauth2.service_account import Credentials
from utils.logging_utils import log
import os

def upload_to_google_sheet(sheet_id, all_vids, refined_data, videos_info=None, region="제주"):
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_path = r'C:\Users\송치웅\Desktop\Project\Clip Route\Data\v6\credentials.json'
        creds = Credentials.from_service_account_file(creds_path, scopes=scope)
        client = gspread.authorize(creds)
        doc = client.open_by_key(sheet_id)

        region_map = {"제주": "제주", "부산": "부산", "강릉": "강릉"}
        worksheet_name = region_map.get(region, region)
        sheet = doc.worksheet(worksheet_name)

        all_rows = []
        HEADER = ["코스 제목 (유튜브 명)", "일수 분류", "일차", "전체 순서", "시점", "장소명", "주소", "카테고리", "조회수", "유튜브 링크"]

        safe_videos = videos_info if videos_info else []
        safe_data = refined_data if refined_data else {}

        for v_info in safe_videos:
            vid = v_info.get('video_id')
            itinerary = safe_data.get(vid, [])
            if not itinerary: continue

            # ✅ [개선 1] 동일 영상 내 장소 중복 제거 (장소명+일차 기준)
            seen_places = set()
            unique_itinerary = []
            for item in itinerary:
                place_key = f"{item.get('place_name')}_{item.get('day')}"
                if place_key not in seen_places:
                    unique_itinerary.append(item)
                    seen_places.add(place_key)

            all_rows.append([""] * 10)
            all_rows.append(HEADER)

            last_day = None
            for idx, item in enumerate(unique_itinerary):
                current_day = item.get('day', 1)
                
                # ✅ [개선 2] 구분선 중복 도배 방지 (정확히 날짜 바뀔 때 1번만)
                if last_day is not None and last_day != current_day:
                    all_rows.append([f"--- Day {current_day} 코스 시작 ---"] + [""] * 9)
                last_day = current_day

                ts = str(item.get('timestamp', '0:00'))
                
                # ✅ [개선 3] 시간 환각 보정 (24시간 넘는 시간은 분/초로 강제 변환)
                time_suffix = ""
                try:
                    parts = ts.split(":")
                    if len(parts) == 2:
                        time_suffix = f"&t={int(parts[0])*60 + int(parts[1])}s"
                    elif len(parts) == 3:
                        hh, mm, ss = map(int, parts)
                        if hh >= 24: # 환각 발생 시
                            time_suffix = f"&t={mm*60 + ss}s"
                        else:
                            time_suffix = f"&t={hh*3600 + mm*60 + ss}s"
                except: pass

                row = [
                    v_info.get('title', '') if idx == 0 else "",
                    v_info.get('day_category', '-'),
                    current_day,
                    idx + 1,
                    ts,
                    item.get('place_name', '이름없음'),
                    item.get('address', '주소 미추출'),
                    item.get('category', '미분류'),
                    f"{v_info.get('view_count', 0):,}" if idx == 0 else "",
                    f'=HYPERLINK("{v_info.get("url")}{time_suffix}", "🎥 영상 보기")'
                ]
                all_rows.append(row)

        if all_rows:
            sheet.append_rows(all_rows, value_input_option='USER_ENTERED')
            log("sheets", f"✅ '{worksheet_name}' 데이터 클리닝 및 업로드 완료!")

    except Exception as e:
        log("sheets", f"❌ 시트 업로드 에러: {e}")