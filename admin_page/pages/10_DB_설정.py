import os
import streamlit as st
from utils.auth import show_login_page
from utils.db import get_db_config, is_db_configured


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    show_login_page()
    st.stop()

st.title("⚙️ DB 설정")
st.markdown("---")

st.subheader("📌 시스템 정보")
col1, col2 = st.columns(2)

with col1:
    st.info("애플리케이션")
    st.write("Clirpoute Admin (Streamlit)")

with col2:
    st.info("환경")
    st.write("개발 (Development)")

st.markdown("---")

st.subheader("🔌 DB 설정")
db_cfg = get_db_config()

if is_db_configured():
    st.success("DB 설정이 감지되었습니다.")
    st.write(
        {
            "host": db_cfg["host"],
            "port": db_cfg["port"],
            "db": db_cfg["db"],
            "user": db_cfg["user"],
        }
    )
else:
    st.error("DB 설정이 없습니다. `.env`에 DB 정보를 입력하세요.")

st.markdown("---")

st.subheader("🔐 관리자 계정")
st.write(
    {
        "ADMIN_USERNAME": os.getenv("ADMIN_USERNAME", "admin"),
        "ADMIN_PASSWORD": "********",
    }
)
