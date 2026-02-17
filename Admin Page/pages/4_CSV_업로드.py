import io
import pandas as pd
import streamlit as st

from utils.auth import show_login_page
from utils.admin_ui import render_csv_upload
from utils.entities import get_entity_configs
from utils.db import is_db_configured, fetch_fk_options, fetch_all
from utils.csv_import import (
    import_preprocessed_csv,
    PREPROCESSED_COLUMNS,
    normalize_preprocessed_df,
    import_cliproute_csv,
    CLIPROUTE_COLUMNS,
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

configs = get_entity_configs()

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

    role_filter = st.selectbox("멤버 역할", options=["ADMIN", "USER"], index=0)
    member_options = fetch_all(
        "SELECT id, email AS label FROM members WHERE role = %s ORDER BY id DESC LIMIT 5000",
        [role_filter],
    )
    if not member_options:
        st.error("members 테이블에 해당 역할 멤버가 없습니다.")
        st.stop()
    author_id = st.selectbox(
        "작성자(멤버) 선택",
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

        if st.button("전처리 CSV 업로드"):
            try:
                result = import_preprocessed_csv(
                    df=df,
                    region_id=region_id,
                    author_id=author_id,
                    source_video_mode="yt",
                    default_source_video_id=None,
                    lat_col=lat_col,
                    lng_col=lng_col,
                    default_lat=None,
                    default_lng=None,
                )
                st.success(
                    f"완료: courses {result['courses']}건 places {result['places']}건 course_place {result['course_place']}건 skip {result['skipped']}건"
                )
            except Exception as exc:
                st.error(f"업로드 실패: {exc}")
