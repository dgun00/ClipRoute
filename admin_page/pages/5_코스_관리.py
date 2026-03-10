import streamlit as st
from utils.auth import show_login_page
from utils.admin_ui import render_entity_page
from utils.entities import get_entity_configs
from utils.db import is_db_configured


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    show_login_page()
    st.stop()

if not is_db_configured():
    st.error("DB 설정이 없습니다. `.env`에 DB 정보를 입력하세요.")
    st.stop()

configs = get_entity_configs()

tabs = st.tabs(["코스", "코스-장소"])
with tabs[0]:
    render_entity_page(configs["courses"])
with tabs[1]:
    render_entity_page(configs["course_places"])
