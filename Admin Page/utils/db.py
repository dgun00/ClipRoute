import os
from contextlib import contextmanager
from urllib.parse import urlparse

import pymysql


def _parse_db_url():
    raw_url = os.getenv("DB_URL") or os.getenv("DATABASE_URL") or ""
    if raw_url.startswith("jdbc:"):
        raw_url = raw_url[len("jdbc:"):]
    if not raw_url:
        return None

    parsed = urlparse(raw_url)
    if parsed.scheme not in ("mysql", "mariadb"):
        return None

    return {
        "host": parsed.hostname,
        "port": parsed.port or 3306,
        "db": (parsed.path or "").lstrip("/"),
        "user": parsed.username,
        "password": parsed.password,
    }


def get_db_config():
    url_cfg = _parse_db_url() or {}
    host = url_cfg.get("host") or os.getenv("DB_HOST")
    port = int(url_cfg.get("port") or os.getenv("DB_PORT", "3306"))
    db = url_cfg.get("db") or os.getenv("DB_NAME")
    user = url_cfg.get("user") or os.getenv("DB_USERNAME")
    password = url_cfg.get("password") or os.getenv("DB_PASSWORD")

    if not all([host, db, user, password]):
        return None
    return {
        "host": host,
        "port": port,
        "db": db,
        "user": user,
        "password": password,
    }


def is_db_configured():
    return get_db_config() is not None


@contextmanager
def get_connection():
    cfg = get_db_config()
    if cfg is None:
        raise RuntimeError("DB 설정이 없습니다. .env에 DB 정보를 입력하세요.")

    conn = pymysql.connect(
        host=cfg["host"],
        port=cfg["port"],
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["db"],
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )
    try:
        yield conn
    finally:
        conn.close()


def fetch_all(sql, params=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or [])
            return cur.fetchall()


def fetch_one(sql, params=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or [])
            return cur.fetchone()


def execute(sql, params=None):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or [])
            return cur.rowcount


def executemany(sql, params_list):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.executemany(sql, params_list)
            return cur.rowcount


def get_table_schema(table_name):
    return fetch_all(f"SHOW COLUMNS FROM `{table_name}`")


def count_rows(table_name):
    row = fetch_one(f"SELECT COUNT(*) AS cnt FROM `{table_name}`")
    return int(row["cnt"]) if row else 0


def fetch_table_rows(table_name, limit=200, offset=0, order_by="id"):
    return fetch_all(
        f"SELECT * FROM `{table_name}` ORDER BY `{order_by}` DESC LIMIT %s OFFSET %s",
        [int(limit), int(offset)],
    )


def insert_rows(table_name, columns, rows):
    if not rows:
        return 0
    col_sql = ", ".join([f"`{c}`" for c in columns])
    placeholders = ", ".join(["%s"] * len(columns))
    sql = f"INSERT INTO `{table_name}` ({col_sql}) VALUES ({placeholders})"
    params_list = [[row.get(col) for col in columns] for row in rows]
    return executemany(sql, params_list)


def update_row(table_name, pk_column, pk_value, update_data):
    set_sql = ", ".join([f"`{k}` = %s" for k in update_data.keys()])
    params = list(update_data.values()) + [pk_value]
    sql = f"UPDATE `{table_name}` SET {set_sql} WHERE `{pk_column}` = %s"
    return execute(sql, params)


def delete_row(table_name, pk_column, pk_value):
    sql = f"DELETE FROM `{table_name}` WHERE `{pk_column}` = %s"
    return execute(sql, [pk_value])


def fetch_fk_options(table_name, id_column, label_column, limit=5000):
    rows = fetch_all(
        f"SELECT `{id_column}` AS id, `{label_column}` AS label FROM `{table_name}` ORDER BY `{id_column}` DESC LIMIT %s",
        [int(limit)],
    )
    return rows
