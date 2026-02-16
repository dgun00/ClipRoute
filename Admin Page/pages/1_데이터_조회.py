import streamlit as st
import pandas as pd
from utils.auth import check_login, show_login_page
from utils.api import fetch_all_data

# 세션 상태 초기화
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# 로그인 확인
if not st.session_state.authenticated:
    show_login_page()
    st.stop()

# 페이지 설정
st.title("📄 데이터 조회")
st.markdown("모든 데이터를 조회하고 필터링할 수 있습니다.")
st.markdown("---")

# 데이터 로드
@st.cache_data
def load_data():
    return fetch_all_data()

data = load_data()
df = pd.DataFrame(data)

# 필터 섹션
with st.expander("🔍 필터 옵션", expanded=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        category_filter = st.multiselect(
            "카테고리",
            options=df['category'].unique(),
            default=df['category'].unique()
        )
    
    with col2:
        status_filter = st.multiselect(
            "상태",
            options=df['status'].unique(),
            default=df['status'].unique()
        )
    
    with col3:
        search_term = st.text_input("🔎 이름 검색", placeholder="검색어 입력")

# 필터 적용
filtered_df = df[
    (df['category'].isin(category_filter)) &
    (df['status'].isin(status_filter))
]

if search_term:
    filtered_df = filtered_df[filtered_df['name'].str.contains(search_term, case=False, na=False)]

# 통계 표시
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("전체 데이터", len(df))
with col2:
    st.metric("필터된 데이터", len(filtered_df))
with col3:
    st.metric("활성 상태", len(df[df['status'] == '활성']))

st.markdown("---")

# 데이터 테이블 표시
st.subheader("📊 데이터 목록")

if len(filtered_df) > 0:
    # 데이터프레임 표시
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "id": st.column_config.NumberColumn("ID", width="small"),
            "name": st.column_config.TextColumn("이름", width="medium"),
            "category": st.column_config.TextColumn("카테고리", width="medium"),
            "status": st.column_config.TextColumn("상태", width="small"),
            "created_at": st.column_config.DateColumn("생성일", width="medium"),
        }
    )
    
    # CSV 다운로드 버튼
    csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 CSV로 다운로드",
        data=csv,
        file_name="clirpoute_data.csv",
        mime="text/csv",
    )
else:
    st.warning("⚠️ 필터 조건에 맞는 데이터가 없습니다.")

# 새로고침 버튼
if st.button("🔄 데이터 새로고침", use_container_width=True):
    st.cache_data.clear()
    st.rerun()
