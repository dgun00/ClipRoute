import pandas as pd
import re

def run_cleaner(file_path):
    # 1. 시트 불러오기 (엑셀 파일명 입력)
    df = pd.read_excel(file_path)
    print(f"🔄 클리닝 시작: {len(df)}개 데이터 분석 중...")

    # 2. 기간 불일치 제거 (당일치기인데 제목에 2박3일 있는 경우 등)
    def is_mismatch(row):
        title = str(row['코스 제목 (유튜브 명)'])
        period = str(row['일수 분류'])
        if period == "당일치기" and any(x in title for x in ["1박", "2박", "3박", "1박2일", "2박3일"]):
            return True
        return False
    
    df = df[~df.apply(is_mismatch, axis=1)]

    # 3. 중복 데이터 제거 (영상 제목 + 장소명이 겹치면 삭제)
    df = df.drop_duplicates(subset=['코스 제목 (유튜브 명)', '장소명'], keep='first')

    # 4. 카테고리 및 상호명 보정
    df['장소명'] = df['장소명'].str.replace(r'^[0-9]+[\.\s\-]+', '', regex=True).str.strip()
    df.loc[df['장소명'].str.contains('호텔|스테이|펜션|리조트', na=False), '카테고리'] = '숙소'

    # 5. 결과 저장
    output_path = file_path.replace(".xlsx", "_cleaned.xlsx")
    df.to_excel(output_path, index=False)
    print(f"✅ 클리닝 완료! 저장됨: {output_path} (남은 데이터: {len(df)}개)")

# 실행 (파일명만 팀장님 파일명으로 바꾸세요)
run_cleaner("제주_여행_리스트.xlsx")