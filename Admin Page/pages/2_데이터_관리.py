import streamlit as st
from datetime import datetime
from utils.auth import check_login, show_login_page
from utils.api import fetch_all_data, create_data, update_data, delete_data

# 세션 상태 초기화
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# 로그인 확인
if not st.session_state.authenticated:
    show_login_page()
    st.stop()

# 페이지 설정
st.title("✏️ 데이터 관리")
st.markdown("데이터를 생성, 수정, 삭제할 수 있습니다.")
st.markdown("---")

# 탭 생성
tab1, tab2, tab3 = st.tabs(["➕ 새 데이터 추가", "✏️ 데이터 수정", "🗑️ 데이터 삭제"])

# 탭 1: 새 데이터 추가
with tab1:
    st.subheader("새로운 데이터 추가")
    
    with st.form("create_form"):
        name = st.text_input("이름*", placeholder="데이터 이름 입력")
        category = st.selectbox("카테고리*", ["카테고리 A", "카테고리 B", "카테고리 C"])
        status = st.selectbox("상태*", ["활성", "비활성", "대기"])
        
        col1, col2 = st.columns([1, 3])
        with col1:
            submitted = st.form_submit_button("✅ 추가", use_container_width=True)
        with col2:
            if submitted:
                if not name:
                    st.error("❌ 이름은 필수 입력 항목입니다.")
                else:
                    new_data = {
                        "name": name,
                        "category": category,
                        "status": status,
                        "created_at": datetime.now().strftime("%Y-%m-%d")
                    }
                    if create_data(new_data):
                        st.success(f"✅ '{name}' 데이터가 추가되었습니다!")
                        st.balloons()
                    else:
                        st.error("❌ 데이터 추가에 실패했습니다.")

# 탭 2: 데이터 수정
with tab2:
    st.subheader("기존 데이터 수정")
    
    # 데이터 목록 가져오기
    data_list = fetch_all_data()
    
    if data_list:
        # 수정할 데이터 선택
        selected_item = st.selectbox(
            "수정할 데이터 선택",
            options=data_list,
            format_func=lambda x: f"ID {x['id']} - {x['name']}"
        )
        
        if selected_item:
            with st.form("update_form"):
                st.write(f"**선택된 항목**: {selected_item['name']}")
                
                new_name = st.text_input("이름*", value=selected_item['name'])
                new_category = st.selectbox(
                    "카테고리*",
                    ["카테고리 A", "카테고리 B", "카테고리 C"],
                    index=["카테고리 A", "카테고리 B", "카테고리 C"].index(selected_item['category'])
                )
                new_status = st.selectbox(
                    "상태*",
                    ["활성", "비활성", "대기"],
                    index=["활성", "비활성", "대기"].index(selected_item['status'])
                )
                
                col1, col2 = st.columns([1, 3])
                with col1:
                    update_submitted = st.form_submit_button("💾 수정", use_container_width=True)
                with col2:
                    if update_submitted:
                        if not new_name:
                            st.error("❌ 이름은 필수 입력 항목입니다.")
                        else:
                            updated_data = {
                                "name": new_name,
                                "category": new_category,
                                "status": new_status
                            }
                            if update_data(selected_item['id'], updated_data):
                                st.success(f"✅ 데이터가 수정되었습니다!")
                                st.rerun()
                            else:
                                st.error("❌ 데이터 수정에 실패했습니다.")
    else:
        st.info("수정할 데이터가 없습니다.")

# 탭 3: 데이터 삭제
with tab3:
    st.subheader("데이터 삭제")
    st.warning("⚠️ 삭제된 데이터는 복구할 수 없습니다.")
    
    # 데이터 목록 가져오기
    data_list = fetch_all_data()
    
    if data_list:
        # 삭제할 데이터 선택
        delete_item = st.selectbox(
            "삭제할 데이터 선택",
            options=data_list,
            format_func=lambda x: f"ID {x['id']} - {x['name']} ({x['category']})"
        )
        
        if delete_item:
            col1, col2, col3 = st.columns([2, 1, 2])
            
            with col2:
                if st.button("🗑️ 삭제", type="primary", use_container_width=True):
                    if delete_data(delete_item['id']):
                        st.success(f"✅ '{delete_item['name']}' 데이터가 삭제되었습니다.")
                        st.rerun()
                    else:
                        st.error("❌ 데이터 삭제에 실패했습니다.")
    else:
        st.info("삭제할 데이터가 없습니다.")

st.markdown("---")

# 현재 데이터 개수 표시
st.info(f"📊 현재 총 **{len(data_list)}개**의 데이터가 있습니다.")
