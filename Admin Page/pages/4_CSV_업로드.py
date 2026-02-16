import io
import pandas as pd
import streamlit as st

from utils.auth import show_login_page
from utils.admin_ui import render_csv_upload
from utils.entities import get_entity_configs
from utils.db import is_db_configured, fetch_fk_options
from utils.csv_import import import_preprocessed_csv, PREPROCESSED_COLUMNS, normalize_preprocessed_df


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
    options=["엔티티별 CSV", "전처리 CSV(코스/장소 일괄)"],
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


if mode == "엔티티별 CSV":
    entity_keys = [
        "regions",
        "places",
        "images",
        "members",
        "courses",
        "course_places",
        "image_place",
        "image_course",
    ]

    selected = st.selectbox(
        "대상 엔티티",
        options=entity_keys,
        format_func=lambda k: configs[k].label,
    )

    render_csv_upload(configs[selected])
else:
    st.subheader("전처리 CSV 업로드")
    st.caption("형식: " + ", ".join(PREPROCESSED_COLUMNS))

    region_options = fetch_fk_options("regions", "id", "region_name")
    if not region_options:
        st.error("regions 테이블에 데이터가 없습니다. 먼저 지역을 생성하세요.")
        st.stop()
    region_id = st.selectbox(
        "지역 선택",
        options=[r["id"] for r in region_options],
        format_func=lambda x: f"{x} | {region_options[[r['id'] for r in region_options].index(x)]['label']}",
    )

    member_options = fetch_fk_options("members", "id", "email")
    if not member_options:
        st.error("members 테이블에 데이터가 없습니다. 먼저 멤버를 생성하세요.")
        st.stop()
    author_id = st.selectbox(
        "작성자(멤버) 선택",
        options=[m["id"] for m in member_options],
        format_func=lambda x: f"{x} | {member_options[[m['id'] for m in member_options].index(x)]['label']}",
    )

    source_mode = st.radio(
        "source_video_id 처리",
        options=["유튜브 링크로 매칭", "고정 source_video_id 사용"],
        horizontal=True,
    )

    default_source_video_id = None
    if source_mode == "고정 source_video_id 사용":
        video_options = fetch_fk_options("videos", "id", "title")
        if not video_options:
            st.error("videos 테이블에 데이터가 없습니다. 먼저 비디오를 생성하세요.")
            st.stop()
        default_source_video_id = st.selectbox(
            "source_video_id 선택",
            options=[v["id"] for v in video_options],
            format_func=lambda x: f"{x} | {video_options[[v['id'] for v in video_options].index(x)]['label']}",
        )

    uploaded = st.file_uploader("CSV 파일 업로드", type=["csv"])
    if uploaded:
        df = _read_csv_with_fallback(uploaded)
        df = normalize_preprocessed_df(df)
        df = df.dropna(how="all")

        st.subheader("미리보기")
        st.dataframe(df.head(20), use_container_width=True)

        lat_col = None
        lng_col = None
        default_lat = None
        default_lng = None

        if "위도" in df.columns and "경도" in df.columns:
            lat_col = "위도"
            lng_col = "경도"
        else:
            with st.expander("위도/경도 컬럼 지정", expanded=True):
                lat_col = st.selectbox("위도 컬럼", options=["(없음)"] + list(df.columns))
                lng_col = st.selectbox("경도 컬럼", options=["(없음)"] + list(df.columns))
                if lat_col == "(없음)":
                    lat_col = None
                if lng_col == "(없음)":
                    lng_col = None

        if lat_col is None or lng_col is None:
            with st.expander("기본 위도/경도 입력", expanded=True):
                st.caption("CSV에 위도/경도 컬럼이 없으면 아래 기본 값을 사용합니다.")
                default_lat = st.number_input("기본 위도", value=0.0, format="%.6f")
                default_lng = st.number_input("기본 경도", value=0.0, format="%.6f")

        if st.button("전처리 CSV 업로드"):
            try:
                result = import_preprocessed_csv(
                    df=df,
                    region_id=region_id,
                    author_id=author_id,
                    source_video_mode="default" if source_mode == "고정 source_video_id 사용" else "yt",
                    default_source_video_id=default_source_video_id,
                    lat_col=lat_col,
                    lng_col=lng_col,
                    default_lat=default_lat,
                    default_lng=default_lng,
                )
                st.success(
                    f"완료: courses {result['courses']}건 places {result['places']}건 course_place {result['course_place']}건 skip {result['skipped']}건"
                )
            except Exception as exc:
                st.error(f"업로드 실패: {exc}")