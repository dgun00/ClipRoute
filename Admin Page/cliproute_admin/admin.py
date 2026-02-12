import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(page_title="ClipRoute 관리자", layout="wide")
st.title("📍 여행 코스 데이터 자동 매핑 도구")

# 1. 파일 업로드
uploaded_file = st.file_uploader("팀장님이 정리한 CSV 파일을 올려주세요!", type="csv")

if uploaded_file:
    # CSV 데이터 읽기 (인코딩 문제 방지를 위해 cp949나 utf-8 사용)
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        df = pd.read_csv(uploaded_file, encoding='cp949')

    st.write("### 📄 업로드된 데이터 미리보기")
    st.dataframe(df.head()) # 상위 5개 데이터 확인

    # 2. 데이터 전송 버튼
    if st.button("🚀 Spring Boot 서버로 데이터 전송하기"):
        bulk_data = []
        
        for _, row in df.iterrows():
            # 팀장님이 만든 Java DTO 구조와 똑같이 매핑합니다.
            course_dto = {
                "title": str(row['코스 제목']),
                "duration": str(row['일수 분류']),
                "region": "제주", # 필요시 직접 입력 가능
                "videoUrl": str(row['유튜브 링크']),
                "youtubeVideoId": str(row['썸네일 ID']), # 팀장님이 뽑은 11자리!
                "viewCount": 0, # 기본값
                "places": [
                    {
                        "name": str(row['장소명']),
                        "address": str(row['주소']),
                        "category": str(row['카테고리']),
                        "sequence": int(row['전체 순서'])
                    }
                ]
            }
            bulk_data.append(course_dto)

        # 3. Spring Boot API 호출
        url = "http://localhost:8080/api/admin/courses/bulk"
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(url, data=json.dumps(bulk_data), headers=headers)
            if response.status_code == 200:
                st.success(f"✅ 성공! {len(bulk_data)}개의 데이터가 전달되었습니다.")
                st.balloons() # 축하 효과!
            else:
                st.error(f"❌ 전송 실패: {response.status_code} - {response.text}")
        except Exception as e:
            st.error(f"⚠️ 서버가 꺼져있는 것 같아요: {e}")