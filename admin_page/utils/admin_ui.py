from datetime import datetime
from typing import Any, Dict, List, Optional

import os
import pandas as pd
import streamlit as st
import requests
import boto3
from botocore.exceptions import ClientError

from utils.db import (
    count_rows,
    delete_row,
    fetch_fk_options,
    fetch_table_rows,
    get_table_schema,
    insert_rows,
    update_row,
    fetch_one,
)
from utils.entities import EntityConfig


READ_ONLY_DEFAULTS = {"id", "created_at", "updated_at"}

S3_BUCKET = os.getenv("S3_BUCKET") or os.getenv("AWS_S3_BUCKET")
S3_REGION = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "ap-northeast-2"


def _get_s3_client():
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    if not (access_key and secret_key and S3_BUCKET):
        raise RuntimeError("S3 설정이 필요합니다. (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET)")
    return boto3.client(
        "s3",
        region_name=S3_REGION,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )


def _s3_url_for_key(key: str) -> str:
    return f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{key}"


def _normalize_github_url(url: str) -> str:
    u = (url or "").strip()
    if not u:
        return ""
    if "raw.githubusercontent.com" in u:
        return u
    if "github.com/" in u and "/blob/" in u:
        return u.replace("github.com/", "raw.githubusercontent.com/").replace("/blob/", "/")
    return u


def _get_extension_from_url(url: str) -> str:
    clean = (url or "").split("?")[0].split("#")[0]
    _, ext = os.path.splitext(clean)
    if ext:
        return ext.lower()
    return ""


def _upload_image_from_url_to_s3(image_url: str, key: str) -> str:
    if not image_url:
        raise ValueError("이미지 URL이 비어 있습니다.")
    s3 = _get_s3_client()
    resp = requests.get(image_url, stream=True, timeout=20)
    if resp.status_code != 200:
        raise ValueError(f"이미지 다운로드 실패 (HTTP {resp.status_code})")
    content_type = resp.headers.get("Content-Type") or "image/jpeg"
    s3.upload_fileobj(resp.raw, S3_BUCKET, key, ExtraArgs={"ContentType": content_type})
    return _s3_url_for_key(key)


def _confirm_delete(action_key: str, button_label: str, message: str) -> bool:
    if hasattr(st, "dialog"):
        if st.button(button_label, type="primary", key=f"{action_key}_open"):
            st.session_state[f"{action_key}_open"] = True
        if st.session_state.get(f"{action_key}_open"):
            confirmed_key = f"{action_key}_confirmed"

            @st.dialog("삭제 확인")
            def _dialog():
                st.write(message)
                if st.button("삭제", type="primary", key=confirmed_key):
                    st.session_state[confirmed_key] = True

            _dialog()
            if st.session_state.get(confirmed_key):
                st.session_state[f"{action_key}_open"] = False
                st.session_state[confirmed_key] = False
                return True
        return False

    # Fallback when dialog is unavailable
    st.warning(message)
    confirm = st.checkbox("확인했습니다", key=f"{action_key}_check")
    return st.button(button_label, type="primary", key=f"{action_key}_confirm") and confirm


def _is_missing(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def _normalize_type(type_str: str) -> str:
    t = (type_str or "").lower()
    if t.startswith("varchar") or "text" in t:
        return "text"
    if t.startswith("int") or t.startswith("bigint") or t.startswith("smallint"):
        return "int"
    if t.startswith("double") or t.startswith("float") or t.startswith("decimal"):
        return "float"
    if t.startswith("tinyint(1)") or t == "boolean":
        return "bool"
    if t.startswith("datetime") or t.startswith("timestamp"):
        return "datetime"
    if t.startswith("date"):
        return "date"
    return "text"


def _coerce_value(value: Any, col_type: str):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    norm = _normalize_type(col_type)
    if norm == "int":
        try:
            return int(value)
        except Exception:
            return None
    if norm == "float":
        try:
            return float(value)
        except Exception:
            return None
    if norm == "bool":
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return bool(int(value))
        if isinstance(value, str):
            return value.strip().lower() in ("1", "true", "y", "yes", "t")
        return None
    if norm in ("datetime", "date"):
        if isinstance(value, (datetime, pd.Timestamp)):
            return value.to_pydatetime()
        if isinstance(value, str) and value.strip():
            return value.strip()
        return None
    return str(value) if value is not None else None


def _get_schema_map(schema_rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {row["Field"]: row for row in schema_rows}


def _apply_filters(
    df: pd.DataFrame,
    config: EntityConfig,
    schema_map: Dict[str, Dict[str, Any]],
) -> pd.DataFrame:
    if df.empty:
        return df
    if config.key == "regions":
        return df

    st.subheader("검색")
    with st.expander("필터 설정", expanded=False):
        # Course-specific dropdown filters (AND semantics)
        if config.key == "courses":
            def _to_bool_int(v):
                if v is None:
                    return None
                if isinstance(v, (bytes, bytearray)):
                    return 1 if v in (b"\x01", b"1", b"true", b"True") else 0
                if isinstance(v, bool):
                    return 1 if v else 0
                if isinstance(v, (int, float)):
                    return 1 if int(v) == 1 else 0
                if isinstance(v, str):
                    s = v.strip().lower()
                    if s in ("1", "true", "t", "y", "yes"):
                        return 1
                    if s in ("0", "false", "f", "n", "no"):
                        return 0
                return None

            filter_cols = [
                ("source_video_id", "원본 영상 ID"),
                ("original_course_id", "원본 코스 ID"),
                ("region_id", "지역 ID"),
                ("author_id", "작성자 ID"),
                ("is_customized", "커스텀 코스 여부"),
                ("is_rep", "대표 코스 여부"),
            ]
            for col, label in filter_cols:
                if col not in df.columns:
                    continue
                if col == "is_customized":
                    options = [
                        ("전체", None),
                        ("true", 1),
                        ("false", 0),
                    ]
                    selected = st.selectbox(
                        label,
                        options=options,
                        index=0,
                        format_func=lambda x: x[0],
                        key=f"{config.key}_filter_{col}_bool",
                    )
                    if selected[1] is not None:
                        series_bool = df[col].map(_to_bool_int)
                        df = df[series_bool == selected[1]]
                    continue
                if col == "is_rep":
                    options = [
                        ("전체", None),
                        ("true", 1),
                        ("false", 0),
                    ]
                    selected = st.selectbox(
                        label,
                        options=options,
                        index=0,
                        format_func=lambda x: x[0],
                        key=f"{config.key}_filter_{col}_bool",
                    )
                    if selected[1] is not None:
                        series_bool = df[col].map(_to_bool_int)
                        df = df[series_bool == selected[1]]
                    continue

                options = sorted([x for x in df[col].dropna().unique().tolist()])
                selected = st.selectbox(
                    label,
                    options=["전체"] + options,
                    index=0,
                    key=f"{config.key}_filter_{col}_eq",
                )
                if selected != "전체":
                    df = df[df[col] == selected]

        if config.key == "courses":
            search = st.text_input("검색 (코스 ID)", key=f"{config.key}_filter_search")
            if search:
                if "id" in df.columns:
                    df = df[df["id"].astype(str).str.contains(search, case=False, na=False)]
        elif config.key == "images":
            search = st.text_input("검색 (original_name)", key=f"{config.key}_filter_search")
            if search and "original_name" in df.columns:
                df = df[df["original_name"].astype(str).str.contains(search, case=False, na=False)]
        elif config.key == "members":
            member_filters = [
                ("gender", "성별"),
                ("status", "상태"),
                ("role", "권한"),
                ("age_range", "연령대"),
            ]
            for col, label in member_filters:
                if col not in df.columns:
                    continue
                options = sorted([x for x in df[col].dropna().unique().tolist()])
                selected = st.selectbox(
                    label,
                    options=["전체"] + options,
                    index=0,
                    key=f"{config.key}_filter_{col}_eq",
                )
                if selected != "전체":
                    df = df[df[col] == selected]
            nickname_search = st.text_input("닉네임 검색", key=f"{config.key}_filter_nickname")
            if nickname_search and "nickname" in df.columns:
                df = df[df["nickname"].astype(str).str.contains(nickname_search, case=False, na=False)]
        elif config.key == "places":
            if "region_id" in df.columns:
                options = sorted([x for x in df["region_id"].dropna().unique().tolist()])
                selected = st.selectbox(
                    "지역 ID",
                    options=["전체"] + options,
                    index=0,
                    key=f"{config.key}_filter_region_id",
                )
                if selected != "전체":
                    df = df[df["region_id"] == selected]
            if "place_category" in df.columns:
                options = sorted([x for x in df["place_category"].dropna().unique().tolist()])
                selected = st.selectbox(
                    "카테고리",
                    options=["전체"] + options,
                    index=0,
                    key=f"{config.key}_filter_place_category",
                )
                if selected != "전체":
                    df = df[df["place_category"] == selected]
            place_name_search = st.text_input("장소명 검색", key=f"{config.key}_filter_place_name")
            if place_name_search and "place_name" in df.columns:
                df = df[df["place_name"].astype(str).str.contains(place_name_search, case=False, na=False)]
        else:
            search = st.text_input("통합 검색", key=f"{config.key}_filter_search")
            if search:
                mask = pd.Series([False] * len(df))
                for col in df.columns:
                    mask = mask | df[col].astype(str).str.contains(search, case=False, na=False)
                df = df[mask]

    return df


def _get_required_columns(schema_rows: List[Dict[str, Any]], config: EntityConfig) -> List[str]:
    if config.required_columns:
        return config.required_columns
    required = []
    for row in schema_rows:
        field = row["Field"]
        if row["Null"] == "NO" and row["Default"] is None and "auto_increment" not in row["Extra"]:
            if field not in READ_ONLY_DEFAULTS:
                required.append(field)
    return required


def _render_input(
    col_name: str,
    col_type: str,
    config: EntityConfig,
    value: Any = None,
    required: bool = False,
    key: Optional[str] = None,
):
    if config.key == "courses" and col_name in ("is_rep", "is_customized"):
        options = [1, 0]
        val_str = str(value).strip().lower() if value is not None else "false"
        if isinstance(value, (bytes, bytearray)):
            val_str = "true" if value in (b"\x01", b"1", b"true", b"True") else "false"
        elif isinstance(value, bool):
            val_str = "true" if value else "false"
        elif isinstance(value, (int, float)):
            val_str = "true" if int(value) == 1 else "false"
        idx = 0 if val_str == "true" else 1
        selected = st.selectbox(
            col_name,
            options=options,
            index=idx,
            format_func=lambda x: "true" if x == 1 else "false",
            key=key,
        )
        return selected

    if config.key == "images" and col_name == "file_size":
        return st.text_input(col_name, value="", disabled=True, key=key)

    if col_name in config.enum_columns:
        options = config.enum_columns[col_name]
        index = options.index(value) if value in options else 0
        return st.selectbox(col_name, options=options, index=index, key=key)

    if col_name in config.foreign_keys:
        fk = config.foreign_keys[col_name]
        options = fetch_fk_options(fk.table, fk.id_column, fk.label_column, fk.limit)
        ids = [row["id"] for row in options]
        if not ids:
            return st.number_input(col_name, value=int(value) if value is not None else 0, step=1, key=key)
        allow_null = config.key == "courses" and col_name in ("original_course_id",)
        if allow_null:
            ids = [None] + ids
        if value in ids:
            idx = ids.index(value)
        else:
            idx = 0
        selected = st.selectbox(
            col_name,
            options=ids,
            format_func=lambda x: "NULL" if x is None else f"{x} | {options[[o['id'] for o in options].index(x)]['label']}",
            index=idx,
            key=key,
        )
        return selected

    norm = _normalize_type(col_type)
    if norm == "int":
        if required:
            return st.number_input(col_name, value=int(value) if value is not None else 0, step=1, key=key)
        return st.text_input(col_name, value=str(value) if value is not None else "", key=key)
    if norm == "float":
        if required:
            return st.number_input(col_name, value=float(value) if value is not None else 0.0, key=key)
        return st.text_input(col_name, value=str(value) if value is not None else "", key=key)
    if norm == "bool":
        return st.checkbox(col_name, value=bool(value) if value is not None else False, key=key)
    if norm == "date":
        if value:
            try:
                return pd.to_datetime(value).date()
            except Exception:
                return None
        return st.date_input(col_name, key=key)
    if norm == "datetime":
        return st.text_input(col_name, value=str(value) if value is not None else "", key=key)
    return st.text_input(col_name, value=str(value) if value is not None else "", key=key)


def render_entity_page(config: EntityConfig):
    st.title(f"{config.label} 관리")
    st.markdown("---")

    try:
        schema_rows = get_table_schema(config.table)
    except Exception as exc:
        st.error(f"스키마 조회 실패: {exc}")
        return
    schema_map = _get_schema_map(schema_rows)
    display_columns = config.display_columns or [row["Field"] for row in schema_rows]
    required_columns = _get_required_columns(schema_rows, config)

    if config.key == "courses":
        tabs = st.tabs(["조회", "수정"])
    elif config.key == "regions":
        tabs = st.tabs(["조회", "추가", "수정", "지역이미지 추가"])
    elif config.key in ("members", "images", "places"):
        tabs = st.tabs(["조회", "추가", "수정"])
    else:
        tabs = st.tabs(["조회", "추가", "수정", "삭제"])

    with tabs[0]:
        total = count_rows(config.table)
        metric_col, limit_col, page_col = st.columns([2, 1, 1])
        metric_col.metric("총 건수", total)

        limit = limit_col.selectbox(
            "표시 개수",
            options=[50, 100, 200, 500],
            index=2,
            key=f"{config.key}_limit",
        )
        page_count = max(1, (total + limit - 1) // limit)
        page = page_col.number_input(
            "페이지",
            min_value=1,
            max_value=page_count,
            value=1,
            step=1,
            key=f"{config.key}_page",
        )

        if config.key == "courses":
            if "id" in [r["Field"] for r in schema_rows]:
                sort_col = "id"
            else:
                sort_col = [r["Field"] for r in schema_rows][0]
            sort_desc = True
        elif config.key == "members":
            if "id" in [r["Field"] for r in schema_rows]:
                sort_col = "id"
            else:
                sort_col = [r["Field"] for r in schema_rows][0]
            sort_desc = True
        elif config.key == "images":
            if "id" in [r["Field"] for r in schema_rows]:
                sort_col = "id"
            else:
                sort_col = [r["Field"] for r in schema_rows][0]
            sort_desc = True
        elif config.key == "places":
            if "id" in [r["Field"] for r in schema_rows]:
                sort_col = "id"
            else:
                sort_col = [r["Field"] for r in schema_rows][0]
            sort_desc = True
        elif config.key == "regions":
            if "id" in [r["Field"] for r in schema_rows]:
                sort_col = "id"
            else:
                sort_col = [r["Field"] for r in schema_rows][0]
            sort_desc = True
        else:
            sort_col = st.selectbox(
                "정렬 컬럼",
                options=[c for c in display_columns if c in [r["Field"] for r in schema_rows]],
                index=0 if "id" not in display_columns else display_columns.index("id"),
                key=f"{config.key}_sort_col",
            )
            sort_desc = st.checkbox("내림차순", value=True, key=f"{config.key}_sort_desc")

        offset = (int(page) - 1) * int(limit)
        rows = fetch_table_rows(config.table, limit=limit, offset=offset, order_by=sort_col, desc=sort_desc)
        if rows:
            df = pd.DataFrame(rows)
            for col in df.columns:
                if col.endswith("_at"):
                    try:
                        df[col] = pd.to_datetime(df[col])
                    except Exception:
                        pass

            available_columns = [c for c in display_columns if c in df.columns]
            selected_columns = st.multiselect(
                "표시 컬럼",
                options=df.columns.tolist(),
                default=available_columns,
                key=f"{config.key}_visible_cols",
            )
            if selected_columns:
                df = df[selected_columns]

            df = _apply_filters(df, config, schema_map)
            st.dataframe(df, use_container_width=True, hide_index=True)
            csv = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button("CSV 다운로드", data=csv, file_name=f"{config.table}.csv")
        else:
            st.info("데이터가 없습니다.")

    if config.key != "courses":
        with tabs[1]:
            st.subheader("데이터 추가")
            with st.form(f"create_{config.key}"):
                input_data = {}
                for row in schema_rows:
                    field = row["Field"]
                    if field in config.read_only_columns or field in READ_ONLY_DEFAULTS:
                        continue
                    input_data[field] = _render_input(
                        field,
                        row["Type"],
                        config,
                        required=field in required_columns,
                        key=f"{config.key}_create_{field}",
                    )
                submitted = st.form_submit_button("저장")
                if submitted:
                    for key, val in list(input_data.items()):
                        input_data[key] = _coerce_value(val, schema_map[key]["Type"])
                    for col in ["created_at", "updated_at"]:
                        if col in schema_map and col not in input_data:
                            input_data[col] = datetime.now()
                    missing = [c for c in required_columns if _is_missing(input_data.get(c))]
                    if missing:
                        st.error(f"필수 값이 누락되었습니다: {', '.join(missing)}")
                    else:
                        inserted = insert_rows(config.table, list(input_data.keys()), [input_data])
                        if inserted:
                            st.success("저장 완료")
                        else:
                            st.error("저장 실패")

    with tabs[1 if config.key == "courses" else 2]:
        st.subheader("데이터 수정")
        rows = fetch_table_rows(config.table, limit=200, offset=0, order_by=config.pk)
        if not rows:
            st.info("수정할 데이터가 없습니다.")
        else:
            df = pd.DataFrame(rows)
            ids = df[config.pk].tolist()
            selected_id = st.selectbox("수정할 ID 선택", options=ids, key=f"{config.key}_update_id")
            selected_row = df[df[config.pk] == selected_id].iloc[0].to_dict()

            with st.form(f"update_{config.key}"):
                update_data = {}
                for row in schema_rows:
                    field = row["Field"]
                    if field == config.pk:
                        continue
                    if config.key == "courses" and field == "deleted_at":
                        continue
                    if config.key == "members" and field == "deleted_at":
                        display_val = selected_row.get(field)
                        st.text_input(field, value=str(display_val) if display_val is not None else "", disabled=True, key=f"{config.key}_ro_{field}")
                        update_data[field] = selected_row.get(field)
                        continue
                    if field in config.read_only_columns or field in READ_ONLY_DEFAULTS:
                        continue
                    update_data[field] = _render_input(
                        field,
                        row["Type"],
                        config,
                        selected_row.get(field),
                        required=field in required_columns,
                        key=f"{config.key}_update_{field}",
                    )
                submitted = st.form_submit_button("수정")
                if submitted:
                    for key, val in list(update_data.items()):
                        update_data[key] = _coerce_value(val, schema_map[key]["Type"])
                    if config.key == "courses":
                        for bcol in ("is_customized", "is_rep"):
                            if bcol in update_data:
                                v = update_data[bcol]
                                if isinstance(v, str):
                                    v = v.strip().lower() in ("1", "true", "t", "y", "yes")
                                if isinstance(v, bool):
                                    update_data[bcol] = b"\x01" if v else b"\x00"
                                elif isinstance(v, (int, float)):
                                    update_data[bcol] = b"\x01" if int(v) == 1 else b"\x00"
                    missing = [c for c in required_columns if _is_missing(update_data.get(c))]
                    if missing:
                        st.error(f"필수 값이 누락되었습니다: {', '.join(missing)}")
                        st.stop()
                    if "updated_at" in schema_map:
                        update_data["updated_at"] = datetime.now()
                    updated = update_row(config.table, config.pk, selected_id, update_data)
                    if updated:
                        st.success("수정 완료")
                    else:
                        st.error("수정 실패")

            if config.key == "courses":
                st.divider()
                st.subheader("삭제")
                if _confirm_delete(
                    f"{config.key}_update_delete",
                    "이 코스 삭제",
                    "정말로 이 코스를 삭제할까요?",
                ):
                    deleted = delete_row(config.table, config.pk, selected_id)
                    if deleted:
                        st.success("삭제 완료")
                        st.rerun()
                    else:
                        st.error("삭제 실패")
            if config.key == "members":
                st.divider()
                st.subheader("삭제")
                if _confirm_delete(
                    f"{config.key}_update_delete",
                    "이 멤버 삭제",
                    "정말로 이 멤버를 삭제할까요?",
                ):
                    deleted = delete_row(config.table, config.pk, selected_id)
                    if deleted:
                        st.success("삭제 완료")
                        st.rerun()
                    else:
                        st.error("삭제 실패")
            if config.key == "regions":
                st.divider()
                st.subheader("삭제")
                if _confirm_delete(
                    f"{config.key}_update_delete",
                    "이 지역 삭제",
                    "정말로 이 지역을 삭제할까요?",
                ):
                    deleted = delete_row(config.table, config.pk, selected_id)
                    if deleted:
                        st.success("삭제 완료")
                        st.rerun()
                    else:
                        st.error("삭제 실패")
            if config.key == "images":
                st.divider()
                st.subheader("삭제")
                if _confirm_delete(
                    f"{config.key}_update_delete",
                    "이 이미지 삭제",
                    "정말로 이 이미지를 삭제할까요?",
                ):
                    deleted = delete_row(config.table, config.pk, selected_id)
                    if deleted:
                        st.success("삭제 완료")
                        st.rerun()
                    else:
                        st.error("삭제 실패")
            if config.key == "places":
                st.divider()
                st.subheader("삭제")
                if _confirm_delete(
                    f"{config.key}_update_delete",
                    "이 장소 삭제",
                    "정말로 이 장소를 삭제할까요?",
                ):
                    deleted = delete_row(config.table, config.pk, selected_id)
                    if deleted:
                        st.success("삭제 완료")
                        st.rerun()
                    else:
                        st.error("삭제 실패")

    if config.key not in ("courses", "members", "regions", "images", "places"):
        with tabs[3]:
            st.subheader("데이터 삭제")
            rows = fetch_table_rows(config.table, limit=200, offset=0, order_by=config.pk)
            if not rows:
                st.info("삭제할 데이터가 없습니다.")
            else:
                df = pd.DataFrame(rows)
                ids = df[config.pk].tolist()
                selected_id = st.selectbox("삭제할 ID 선택", options=ids, key=f"{config.key}_delete_id")
                if _confirm_delete(
                    f"{config.key}_delete",
                    "삭제",
                    "정말로 삭제할까요?",
                ):
                    deleted = delete_row(config.table, config.pk, selected_id)
                    if deleted:
                        st.success("삭제 완료")
                    else:
                        st.error("삭제 실패")

    if config.key == "regions":
        with tabs[3]:
            st.subheader("지역 이미지 추가")
            rows = fetch_table_rows(config.table, limit=200, offset=0, order_by=config.pk)
            if not rows:
                st.info("등록된 지역이 없습니다.")
            else:
                df = pd.DataFrame(rows)
                id_name_rows = (
                    df[[config.pk, "region_name"]].dropna()
                    if "region_name" in df.columns
                    else df[[config.pk]]
                )
                options = id_name_rows[config.pk].tolist()
                selected_id = st.selectbox(
                    "지역 선택",
                    options=options,
                    format_func=lambda x: f"{x} | {id_name_rows[id_name_rows[config.pk] == x]['region_name'].iloc[0]}" if "region_name" in id_name_rows.columns else str(x),
                    key=f"{config.key}_image_region_id",
                )
                github_url = st.text_input(
                    "GitHub 이미지 URL",
                    placeholder="https://github.com/user/repo/blob/main/path/to/image.jpg",
                )
                running_key = f"{config.key}_image_upload_running"
                msg_key = f"{config.key}_image_upload_message"
                status_key = f"{config.key}_image_upload_status"
                payload_key = f"{config.key}_image_upload_payload"

                is_running = st.session_state.get(running_key, False)
                if is_running:
                    st.info("업로드 중... 잠시만 기다려주세요.")
                    st.button("업로드 중...", disabled=True)
                else:
                    if st.button("S3 업로드 및 이미지 등록", type="primary", key=f"{config.key}_image_upload_btn"):
                        st.session_state[msg_key] = ""
                        st.session_state[status_key] = ""
                        st.session_state[running_key] = True
                        st.session_state[payload_key] = {
                            "selected_id": selected_id,
                            "github_url": github_url,
                        }
                        st.rerun()

                if is_running and st.session_state.get(payload_key):
                    payload = st.session_state.get(payload_key, {})
                    try:
                        input_url = (payload.get("github_url", "") or "").strip()
                        raw_url = _normalize_github_url(input_url)
                        filename = os.path.basename(raw_url.split("?")[0].split("#")[0]) or "region-image.jpg"
                        key = f"images/regions/{filename}"
                        s3_url = _upload_image_from_url_to_s3(raw_url, key)

                        # regions.image_url 업데이트 (S3 URL 저장)
                        update_row(
                            config.table,
                            config.pk,
                            payload["selected_id"],
                            {"image_url": s3_url, "updated_at": datetime.now()},
                        )

                        # images 엔티티 추가 (중복 방지: original_name)
                        original_name = os.path.splitext(filename)[0]
                        existing = fetch_one("SELECT id FROM images WHERE original_name = %s LIMIT 1", [original_name])
                        if not existing:
                            insert_rows(
                                "images",
                                ["image_url", "original_name", "created_at", "updated_at"],
                                [
                                    {
                                        "image_url": s3_url,
                                        "original_name": original_name,
                                        "created_at": datetime.now(),
                                        "updated_at": datetime.now(),
                                    }
                                ],
                            )

                        st.session_state[msg_key] = "지역 이미지가 업데이트되었습니다."
                        st.session_state[status_key] = "success"
                    except Exception as exc:
                        st.session_state[msg_key] = f"이미지 업로드 실패: {exc}"
                        st.session_state[status_key] = "error"
                    finally:
                        st.session_state[running_key] = False
                        st.session_state[payload_key] = None
                        st.rerun()

                status = st.session_state.get(status_key)
                message = st.session_state.get(msg_key)
                if status == "success":
                    st.success(message)
                elif status == "error":
                    st.error(message)


def render_csv_upload(config: EntityConfig):
    st.title("CSV 업로드")
    st.markdown("---")
    st.write(f"대상 엔티티: {config.label} ({config.table})")

    try:
        schema_rows = get_table_schema(config.table)
    except Exception as exc:
        st.error(f"테이블 조회 실패: {exc}")
        return
    schema_map = _get_schema_map(schema_rows)
    required_columns = _get_required_columns(schema_rows, config)
    read_only = set(config.read_only_columns or []) | READ_ONLY_DEFAULTS

    uploaded = st.file_uploader("CSV 파일 업로드", type=["csv"])
    if not uploaded:
        st.info("CSV 파일을 업로드하세요.")
        return

    df = pd.read_csv(uploaded)
    st.subheader("미리보기")
    st.dataframe(df.head(20), use_container_width=True)

    st.subheader("컬럼 매핑")
    csv_cols = list(df.columns)
    mapping = {}
    for col in required_columns:
        options = ["(미지정)"] + csv_cols
        default_value = col if col in csv_cols else "(미지정)"
        mapping[col] = st.selectbox(
            f"{col} (필수)",
            options=options,
            index=options.index(default_value) if default_value in options else 0,
            key=f"map_required_{col}",
        )

    optional_cols = [
        c
        for c in schema_map.keys()
        if c not in required_columns and c not in read_only
    ]
    with st.expander("선택 컬럼 매핑", expanded=False):
        for col in optional_cols:
            options = ["(사용 안함)"] + csv_cols
            default_value = col if col in csv_cols else "(사용 안함)"
            mapping[col] = st.selectbox(
                col,
                options=options,
                index=options.index(default_value) if default_value in options else 0,
                key=f"map_optional_{col}",
            )

    if st.button("업로드"):
        missing_required = [c for c in required_columns if mapping.get(c) in (None, "(미지정)")]
        if missing_required:
            st.error(f"필수 컬럼 매핑이 누락되었습니다: {', '.join(missing_required)}")
            return
        rows = []
        for _, row in df.iterrows():
            data = {}
            for db_col, csv_col in mapping.items():
                if csv_col in ("(사용 안함)", "(미지정)"):
                    continue
                value = row.get(csv_col)
                data[db_col] = _coerce_value(value, schema_map[db_col]["Type"])
            for col in ["created_at", "updated_at"]:
                if col in schema_map and col not in data:
                    data[col] = datetime.now()
            rows.append(data)

        if rows:
            columns = list(rows[0].keys())
            inserted = insert_rows(config.table, columns, rows)
            st.success(f"{inserted}건 업로드 완료")
        else:
            st.warning("업로드할 데이터가 없습니다.")
