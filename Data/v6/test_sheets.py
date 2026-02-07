import os
import gspread
from google.oauth2.service_account import Credentials

def test_connection():
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    
    # ✅ 후보 1: 팀장님이 지은 이름 / 후보 2: 윈도우가 멋대로 붙인 이름
    path1 = r'C:\Users\송치웅\Desktop\Project\Clip Route\Data\v6\credentials.json'
    path2 = r'C:\Users\송치웅\Desktop\Project\Clip Route\Data\v6\credentials.json.json'
    
    # 둘 중 존재하는 파일을 자동으로 선택
    final_path = path1 if os.path.exists(path1) else path2
    
    if not os.path.exists(final_path):
        print(f"❌ 여전히 파일을 찾을 수 없습니다. 폴더에 있는 파일의 실제 이름을 다시 확인해주세요.")
        return

    try:
        print(f"📂 사용 중인 파일: {os.path.basename(final_path)}")
        creds = Credentials.from_service_account_file(final_path, scopes=scope)
        client = gspread.authorize(creds)
        
        SHEET_ID = "1-p1rclW1RdgbIYTnZmzWOnClpBjFZIc9KZMe6bTPl5A"
        doc = client.open_by_key(SHEET_ID)
        sheet = doc.get_worksheet(0)
        
        print("🔗 시트 연결 시도 중...")
        sheet.update_acell('A1', '🚀 치웅 팀장님, 드디어 연결 성공입니다!')
        print("✅ 성공! 구글 시트 A1 셀을 확인하세요.")
        
    except Exception as e:
        print(f"❌ 연결 실패: {e}")

if __name__ == "__main__":
    test_connection()