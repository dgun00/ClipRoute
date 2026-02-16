import streamlit as st
from utils.auth import check_login, show_login_page
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="Clirpoute 관리자",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 세션 상태 초기화
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# 로그인 확인
if not st.session_state.authenticated:
    show_login_page()
else:
    # 사이드바
    with st.sidebar:
        st.title("🔧 Clirpoute 관리자")
        st.divider()
        st.info("관리자 페이지에 오신 것을 환영합니다!")
        
        if st.button("🚪 로그아웃", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
    
    # 메인 페이지
    st.title("📊 대시보드")
    st.markdown("---")
    
    # 통계 카드
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="총 데이터", value="150", delta="12")
    
    with col2:
        st.metric(label="오늘 추가", value="5", delta="2")
    
    with col3:
        st.metric(label="활성 사용자", value="42", delta="-3")
    
    with col4:
        st.metric(label="처리 대기", value="8", delta="1")
    
    st.markdown("---")
    
    # 안내 메시지
    st.info("👈 왼쪽 사이드바에서 원하는 페이지를 선택하세요.")
    
    # 빠른 액션
    st.subheader("🚀 빠른 작업")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 CSV 업로드", use_container_width=True):
            st.switch_page("pages/4_CSV_업로드.py")
    
    with col2:
        if st.button("🗺️ 지역 관리", use_container_width=True):
            st.switch_page("pages/7_지역_관리.py")
    
    with col3:
        if st.button("👤 멤버 관리", use_container_width=True):
            st.switch_page("pages/6_멤버_관리.py")
    
    # 최근 활동
    st.markdown("---")
    st.subheader("📌 최근 활동")
    
    with st.container():
        st.markdown("""
        - 🟢 2024-02-11 15:30 - 새로운 데이터 추가됨 (ID: 151)
        - 🟡 2024-02-11 14:15 - 데이터 수정됨 (ID: 98)
        - 🔴 2024-02-11 13:05 - 데이터 삭제됨 (ID: 45)
        - 🟢 2024-02-11 12:00 - 새로운 데이터 추가됨 (ID: 150)
        """)
