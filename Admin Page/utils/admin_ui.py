from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

from utils.db import (
    count_rows,
    delete_row,
    fetch_fk_options,
    fetch_table_rows,
    get_table_schema,
    insert_rows,
    update_row,
)
from utils.entities import EntityConfig


READ_ONLY_DEFAULTS = {"id", "created_at", "updated_at"}


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

    st.subheader("필터")
    with st.expander("필터 옵션", expanded=False):
        search = st.text_input("전체 검색", key=f"{config.key}_filter_search")
        if search:
            mask = pd.Series([False] * len(df))
            for col in df.columns:
                mask = mask | df[col].astype(str).str.contains(search, case=False, na=False)
            df = df[mask]

        for col in df.columns:
            series = df[col]
            col_type = schema_map.get(col, {}).get("Type", "")
            norm = _normalize_type(col_type)

            if norm == "int":
                min_val = series.min()
                max_val = series.max()
                if pd.notna(min_val) and pd.notna(max_val):
                    min_input, max_input = st.slider(
                        f"{col} 범위",
                        int(min_val),
                        int(max_val),
                        (int(min_val), int(max_val)),
                        key=f"{config.key}_filter_{col}_range",
                    )
                    df = df[(df[col] >= min_input) & (df[col] <= max_input)]
                continue

            if norm == "float":
                min_val = series.min()
                max_val = series.max()
                if pd.notna(min_val) and pd.notna(max_val):
                    min_input, max_input = st.slider(
                        f"{col} 범위",
                        float(min_val),
                        float(max_val),
                        (float(min_val), float(max_val)),
                        key=f"{config.key}_filter_{col}_range",
                    )
                    df = df[(df[col] >= min_input) & (df[col] <= max_input)]
                continue

            if norm == "bool":
                selected = st.selectbox(
                    f"{col} 값",
                    options=["전체", "true", "false"],
                    index=0,
                    key=f"{config.key}_filter_{col}_bool",
                )
                if selected != "전체":
                    df = df[df[col].astype(str).str.lower() == selected]
                continue

            if norm in ("datetime", "date"):
                min_date = pd.to_datetime(series, errors="coerce").min()
                max_date = pd.to_datetime(series, errors="coerce").max()
                if pd.notna(min_date) and pd.notna(max_date):
                    start, end = st.date_input(
                        f"{col} 날짜 범위",
                        value=(min_date.date(), max_date.date()),
                        key=f"{config.key}_filter_{col}_date",
                    )
                    df = df[
                        (pd.to_datetime(df[col], errors="coerce") >= pd.to_datetime(start))
                        & (pd.to_datetime(df[col], errors="coerce") <= pd.to_datetime(end))
                    ]
                continue

            if col in config.enum_columns:
                options = config.enum_columns[col]
                selected = st.multiselect(
                    f"{col} 선택",
                    options=options,
                    default=options,
                    key=f"{config.key}_filter_{col}_enum",
                )
                if selected:
                    df = df[df[col].isin(selected)]
                continue

            unique_count = series.nunique(dropna=True)
            if unique_count <= 20:
                options = [x for x in series.dropna().unique().tolist()]
                selected = st.multiselect(
                    f"{col} 선택",
                    options=options,
                    default=options,
                    key=f"{config.key}_filter_{col}_multi",
                )
                if selected:
                    df = df[df[col].isin(selected)]

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
        if value in ids:
            idx = ids.index(value)
        else:
            idx = 0
        selected = st.selectbox(
            col_name,
            options=ids,
            format_func=lambda x: f"{x} | {options[ids.index(x)]['label']}" if x in ids else str(x),
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
        st.error(f"테이블 조회 실패: {exc}")
        return
    schema_map = _get_schema_map(schema_rows)
    display_columns = config.display_columns or [row["Field"] for row in schema_rows]
    required_columns = _get_required_columns(schema_rows, config)

    tabs = st.tabs(["목록", "추가", "수정", "삭제"])

    with tabs[0]:
        total = count_rows(config.table)
        st.metric("총 데이터", total)

        limit = st.selectbox(
            "표시 개수",
            options=[50, 100, 200, 500],
            index=2,
            key=f"{config.key}_limit",
        )
        rows = fetch_table_rows(config.table, limit=limit, offset=0, order_by=config.pk)
        if rows:
            df = pd.DataFrame(rows)
            for col in df.columns:
                if col.endswith("_at"):
                    df[col] = pd.to_datetime(df[col], errors="ignore")
            if display_columns:
                df = df[[col for col in display_columns if col in df.columns]]
            df = _apply_filters(df, config, schema_map)
            st.dataframe(df, use_container_width=True, hide_index=True)
            csv = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button("CSV 다운로드", data=csv, file_name=f"{config.table}.csv")
        else:
            st.info("데이터가 없습니다.")

    with tabs[1]:
        st.subheader("새 데이터 추가")
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
            submitted = st.form_submit_button("추가")
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
                        st.success("추가 완료")
                    else:
                        st.error("추가 실패")

    with tabs[2]:
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

    with tabs[3]:
        st.subheader("데이터 삭제")
        rows = fetch_table_rows(config.table, limit=200, offset=0, order_by=config.pk)
        if not rows:
            st.info("삭제할 데이터가 없습니다.")
        else:
            df = pd.DataFrame(rows)
            ids = df[config.pk].tolist()
            selected_id = st.selectbox("삭제할 ID 선택", options=ids, key=f"{config.key}_delete_id")
            if st.button("삭제", type="primary", key=f"{config.key}_delete_btn"):
                deleted = delete_row(config.table, config.pk, selected_id)
                if deleted:
                    st.success("삭제 완료")
                else:
                    st.error("삭제 실패")


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
        options = ["(미매핑)"] + csv_cols
        default_value = col if col in csv_cols else "(미매핑)"
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
            options = ["(사용 안 함)"] + csv_cols
            default_value = col if col in csv_cols else "(사용 안 함)"
            mapping[col] = st.selectbox(
                col,
                options=options,
                index=options.index(default_value) if default_value in options else 0,
                key=f"map_optional_{col}",
            )

    if st.button("업로드"):
        missing_required = [c for c in required_columns if mapping.get(c) in (None, "(미매핑)")]
        if missing_required:
            st.error(f"필수 컬럼 매핑이 누락되었습니다: {', '.join(missing_required)}")
            return
        rows = []
        for _, row in df.iterrows():
            data = {}
            for db_col, csv_col in mapping.items():
                if csv_col in ("(사용 안 함)", "(미매핑)"):
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
