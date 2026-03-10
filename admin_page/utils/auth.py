import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

def check_login(username: str, password: str) -> bool:
    """관리자 계정 확인"""
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    return username == admin_username and password == admin_password

def show_login_page():
    """로그인 페이지 표시"""
    st.title("🔐 Clirpoute 관리자 로그인")
    
    # 로그인 폼
    with st.form("login_form"):
        st.markdown("관리자 계정으로 로그인하세요")
        username = st.text_input("아이디", placeholder="admin")
        password = st.text_input("비밀번호", type="password", placeholder="비밀번호 입력")
        
        submitted = st.form_submit_button("로그인", use_container_width=True)
        
        if submitted:
            if check_login(username, password):
                st.session_state.authenticated = True
                st.success("✅ 로그인 성공!")
                st.rerun()
            else:
                st.error("❌ 아이디 또는 비밀번호가 올바르지 않습니다.")
    
    # 안내 메시지
    st.info("💡 기본 계정: admin / admin123 (.env 파일에서 변경 가능)")
