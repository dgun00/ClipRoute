import streamlit as st
import os
from utils.auth import check_login, show_login_page

# 세션 상태 초기화
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# 로그인 확인
if not st.session_state.authenticated:
    show_login_page()
    st.stop()

# 페이지 설정
st.title("⚙️ 설정")
st.markdown("시스템 설정 및 정보를 확인할 수 있습니다.")
st.markdown("---")

# 시스템 정보
st.subheader("📌 시스템 정보")

col1, col2 = st.columns(2)

with col1:
    st.info("**애플리케이션 버전**")
    st.write("v1.0.0")
    
    st.info("**프레임워크**")
    st.write("Streamlit")

with col2:
    st.info("**환경**")
    st.write("개발 (Development)")
    
    st.info("**API 상태**")
    st.write("🔴 연결되지 않음 (Mock 데이터 사용 중)")

st.markdown("---")

# API 설정
st.subheader("🔌 API 설정")

with st.form("api_settings"):
    api_base_url = st.text_input(
        "API Base URL",
        value=os.getenv('API_BASE_URL', 'http://localhost:8000'),
        placeholder="http://localhost:8000"
    )
    
    api_key = st.text_input(
        "API Key",
        value="",
        type="password",
        placeholder="API 키를 입력하세요"
    )
    
    col1, col2 = st.columns([1, 3])
    with col1:
        save_api = st.form_submit_button("💾 저장", use_container_width=True)
    with col2:
        if save_api:
            st.info("ℹ️ API 설정은 .env 파일에서 직접 수정하세요.")

st.markdown("---")

# 계정 설정
st.subheader("👤 계정 설정")

with st.expander("비밀번호 변경"):
    with st.form("change_password"):
        current_password = st.text_input("현재 비밀번호", type="password")
        new_password = st.text_input("새 비밀번호", type="password")
        confirm_password = st.text_input("새 비밀번호 확인", type="password")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            change_pw = st.form_submit_button("🔑 변경", use_container_width=True)
        with col2:
            if change_pw:
                if not all([current_password, new_password, confirm_password]):
                    st.error("❌ 모든 필드를 입력해주세요.")
                elif new_password != confirm_password:
                    st.error("❌ 새 비밀번호가 일치하지 않습니다.")
                else:
                    st.info("ℹ️ 비밀번호 변경은 .env 파일에서 직접 수정하세요.")

st.markdown("---")

# 데이터 관리
st.subheader("🗂️ 데이터 관리")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📤 데이터 내보내기", use_container_width=True):
        st.info("데이터 내보내기 기능은 개발 중입니다.")

with col2:
    if st.button("📥 데이터 가져오기", use_container_width=True):
        st.info("데이터 가져오기 기능은 개발 중입니다.")

with col3:
    if st.button("🔄 캐시 초기화", use_container_width=True):
        st.cache_data.clear()
        st.success("✅ 캐시가 초기화되었습니다.")
        st.rerun()

st.markdown("---")

# 위험 영역
st.subheader("⚠️ 위험 영역")

with st.expander("🔴 모든 데이터 삭제", expanded=False):
    st.error("**경고**: 이 작업은 되돌릴 수 없습니다!")
    
    confirm_delete = st.checkbox("정말로 모든 데이터를 삭제하시겠습니까?")
    
    if confirm_delete:
        if st.button("🗑️ 모든 데이터 삭제", type="primary"):
            st.warning("이 기능은 아직 구현되지 않았습니다.")

st.markdown("---")

# 도움말
st.subheader("❓ 도움말")

with st.expander("자주 묻는 질문 (FAQ)"):
    st.markdown("""
    **Q: API를 어떻게 연동하나요?**  
    A: `.env` 파일에서 `API_BASE_URL`과 `API_KEY`를 설정한 후, `utils/api.py`의 함수들을 실제 API 호출로 교체하세요.
    
    **Q: 관리자 계정은 어떻게 변경하나요?**  
    A: `.env` 파일에서 `ADMIN_USERNAME`과 `ADMIN_PASSWORD`를 수정하세요.
    
    **Q: 데이터가 저장되지 않아요.**  
    A: 현재는 Mock 데이터를 사용하고 있어 앱을 재시작하면 초기화됩니다. 실제 API 연동 후 영구 저장이 가능합니다.
    """)

with st.expander("연락처"):
    st.info("문의사항이 있으시면 시스템 관리자에게 연락하세요.")
