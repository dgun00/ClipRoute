import io
import pandas as pd
import streamlit as st

from utils.auth import show_login_page
from utils.db import is_db_configured, fetch_all
from utils.csv_import import (
    import_preprocessed_csv,
    PREPROCESSED_COLUMNS,
    normalize_preprocessed_df,
)


if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    show_login_page()
    st.stop()

st.title("CSV 업로드")
st.markdown("---")

if not is_db_configured():
    st.error("DB 설정이 없습니다. `.env`에 DB 정보를 입력하세요.")
    st.stop()

mode = st.radio(
    "업로드 방식",
    options=["전처리 CSV(코스/장소 일괄)"],
    horizontal=True,
)


def _read_csv_with_fallback(uploaded_file):
    raw = uploaded_file.getvalue()
    for enc in ["utf-8-sig", "cp949", "euc-kr"]:
        try:
            return pd.read_csv(io.BytesIO(raw), encoding=enc)
        except Exception:
            continue
    return pd.read_csv(io.BytesIO(raw))


if mode == "전처리 CSV(코스/장소 일괄)":
    st.subheader("전처리 CSV 업로드")
    st.caption("형식: " + ", ".join(PREPROCESSED_COLUMNS))

    member_options = fetch_all(
        "SELECT id, email AS label FROM members WHERE role = %s ORDER BY id DESC LIMIT 5000",
        ["ADMIN"],
    )
    if not member_options:
        st.error("members 테이블에 해당 역할 멤버가 없습니다.")
        st.stop()
    author_id = st.selectbox(
        "작성자(ADMIN) 선택",
        options=[m["id"] for m in member_options],
        format_func=lambda x: f"{x} | {member_options[[m['id'] for m in member_options].index(x)]['label']}",
    )

    uploaded = st.file_uploader("CSV 파일 업로드", type=["csv"])
    if uploaded:
        df = _read_csv_with_fallback(uploaded)
        df = normalize_preprocessed_df(df)
        df = df.dropna(how="all")

        # region_id must exist in CSV
        if "region_id" not in df.columns:
            st.error("region_id 컬럼을 CSV에 포함해주세요.")
            st.stop()

        # latitude/longitude columns: accept either "??/??" or "lat/lng"
        if "위도" in df.columns and "경도" in df.columns:
            lat_col = "위도"
            lng_col = "경도"
        elif "lat" in df.columns and "lng" in df.columns:
            lat_col = "lat"
            lng_col = "lng"
        else:
            st.error("CSV에 위도/경도(또는 lat/lng) 컬럼을 포함해주세요.")
            st.stop()

        region_id = df["region_id"].dropna().astype(int).iloc[0] if not df["region_id"].dropna().empty else None
        if region_id is None:
            st.error("region_id 값이 비어 있습니다.")
            st.stop()

        st.subheader("미리보기")
        st.dataframe(df.head(20), use_container_width=True)

        is_running = st.session_state.get("csv_upload_running", False)

        if is_running:
            st.info("업로드 중... 잠시만 기다려주세요.")
            st.button("업로드 중...", disabled=True)
        else:
            if st.button("전처리 CSV 업로드"):
                st.session_state["csv_upload_done"] = False
                st.session_state["csv_upload_message"] = ""
                st.session_state["csv_upload_status"] = ""
                st.session_state["csv_upload_show_dialog"] = False
                st.session_state["csv_upload_running"] = True
                st.session_state["csv_upload_payload"] = {
                    "df": df,
                    "region_id": region_id,
                    "author_id": author_id,
                    "lat_col": lat_col,
                    "lng_col": lng_col,
                }
                st.rerun()

        if is_running and st.session_state.get("csv_upload_payload"):
            payload = st.session_state.get("csv_upload_payload", {})
            try:
                result = import_preprocessed_csv(
                    df=payload["df"],
                    region_id=payload["region_id"],
                    author_id=payload["author_id"],
                    source_video_mode="yt",
                    default_source_video_id=None,
                    lat_col=payload["lat_col"],
                    lng_col=payload["lng_col"],
                    default_lat=None,
                    default_lng=None,
                )
                message = (
                    f"완료: videos {result['videos']}건 images {result['images']}건 courses {result['courses']}건 "
                    f"places {result['places']}건 course_place {result['course_place']}건 "
                    f"이미지업로드 {result.get('image_uploads', 0)}건"
                )
                st.success(message)
                st.session_state["csv_upload_done"] = True
                st.session_state["csv_upload_message"] = message
                st.session_state["csv_upload_status"] = "success"
                st.session_state["csv_upload_show_dialog"] = True
            except Exception as exc:
                message = f"업로드 실패: {exc}"
                st.error(message)
                st.session_state["csv_upload_done"] = True
                st.session_state["csv_upload_message"] = message
                st.session_state["csv_upload_status"] = "error"
                st.session_state["csv_upload_show_dialog"] = True
            finally:
                st.session_state["csv_upload_running"] = False
                st.session_state["csv_upload_payload"] = None
                st.rerun()

    if st.session_state.get("csv_upload_done"):
        status = st.session_state.get("csv_upload_status", "success")
        msg = st.session_state.get("csv_upload_message", "")
        if status == "error":
            st.error(msg or "CSV 업로드가 실패했습니다.")
        else:
            st.success(msg or "CSV 업로드가 완료되었습니다.")

    if st.session_state.get("csv_upload_show_dialog") and hasattr(st, "dialog"):
        @st.dialog("업로드 완료")
        def _done_dialog():
            status = st.session_state.get("csv_upload_status", "success")
            if status == "error":
                st.error("CSV 업로드가 실패했습니다.")
            else:
                st.warning("CSV 업로드가 완료되었습니다.")
            st.write(st.session_state.get("csv_upload_message", ""))
            if st.button("닫기", type="primary"):
                st.session_state["csv_upload_show_dialog"] = False

        _done_dialog()
