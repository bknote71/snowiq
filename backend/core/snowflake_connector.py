import os
from dotenv import load_dotenv

load_dotenv()

import re
import threading
import time
from typing import Callable, Optional
import pandas as pd
import snowflake.connector
from .cache import cache
from utils.logger import logger


def _normalize_account(raw: str) -> str:
    """snowflake.connector에 필요한 account 형식으로 변환"""
    if not raw:
        return raw

    raw = raw.replace("https://", "").replace("http://", "")
    raw = raw.replace(".snowflakecomputing.com", "")
    return raw


def connect():
    account = os.getenv("SNOWFLAKE_ACCOUNT", "")
    user = os.getenv("SNOWFLAKE_USER", "")
    password = os.getenv("SNOWFLAKE_PASSWORD", "")
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE", "")
    database = os.getenv("SNOWFLAKE_DATABASE", "")
    schema = os.getenv("SNOWFLAKE_SCHEMA", "")  # todo: user select

    if not all([account, user, password, warehouse, database, schema]):
        raise RuntimeError("Snowflake 환경변수가 부족합니다.")

    conn = snowflake.connector.connect(
        account=account,
        user=user,
        password=password,
        warehouse=warehouse,
        database=database,
        schema=schema,
        # role=os.getenv("SNOWFLAKE_ROLE") or None,
        client_session_keep_alive=True,
    )

    return conn


def fetch_df(query: str, params: Optional[dict] = None) -> pd.DataFrame:
    """쿼리 -> DataFrame"""
    conn = None
    try:
        # todo: connection pool?
        conn = connect()
        cursor = conn.cursor()
        cursor.execute(query, params or {})
        df = cursor.fetch_pandas_all()
        return df
    finally:
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            if conn:
                conn.close()
        except Exception:
            pass


def start_periodic_fetch(thread_id: str, query_factory: Callable[[], str], interval_sec: int = 3600 * 24):
    """
    주기적 fetch 실행
    - name: 캐시에 저장할 키
    - query_factory: 매 주기마다 실행할 SQL(문자열) 생성 함수
    - interval_sec: 주기(초)
    """

    def _loop():
        while True:
            try:
                sql = query_factory()
                if not sql:
                    return None

                df = fetch_df(sql)
                cache.set(f"live_df_{thread_id}", df)
            except Exception as e:
                pass
            time.sleep(max(1, interval_sec))

    t = threading.Thread(target=_loop, daemon=True)
    t.start()
    return t


# fetch test
if __name__ == "__main__":
    import os

    # Snowflake 연결 테스트
    print("Connecting to Snowflake...")
    table = "maple_logs"
    df = fetch_df(f"SELECT * FROM {table};")
    print(df)
