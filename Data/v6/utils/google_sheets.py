import gspread
from google.oauth2.service_account import Credentials
import os
from utils.logging_utils import log

def upload_to_google_sheet(sheet_id: str, all_video_ids: list, refined_data: dict):
    """
    모든 영상 리스트를 바탕으로 분석 성공/실패 여부를 시트에 업로드합니다.
    """
    log("sheets", "📊 구글 워크시트 전체 성과 기록 시작...")
    
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds_path = r'C:\Users\송치웅\Desktop\Project\Clip Route\Data\v6\credentials.json'

    try:
        if not os.path.exists(creds_path):
            creds_path += '.json'
            if not os.path.exists(creds_path):
                raise FileNotFoundError(f"인증 파일을 찾을 수 없습니다: {creds_path}")

        creds = Credentials.from_service_account_file(creds_path, scopes=scope)
        client = gspread.authorize(creds)
        doc = client.open_by_key(sheet_id)
        sheet = doc.get_worksheet(0)

        sheet.clear()
        # 헤더 구성
        header = ["상태", "영상 ID", "유튜브 링크", "추출된 핀 개수", "비고"]
        rows = [header]

        # 모든 영상 ID를 순회하며 데이터 구성
        for vid in all_video_ids:
            link = f"https://www.youtube.com/watch?v={vid}"
            
            if vid in refined_data and len(refined_data[vid]) > 0:
                # 분석 성공
                pin_count = len(refined_data[vid])
                rows.append(["⭐ 분석 성공", vid, link, pin_count, "장소 식별 완료"])
            else:
                # 분석 실패 (핀 0개)
                rows.append(["❌ 분석 실패", vid, link, 0, "장소 정보 없음 또는 자막 부재"])

        # 시트에 일괄 업데이트
        sheet.update('A1', rows)
        log("sheets", f"✅ 시트 업데이트 완료: 총 {len(all_video_ids)}개 영상 기록됨")

    except Exception as e:
        log("sheets", f"❌ 시트 업로드 실패: {e}")
        raise e