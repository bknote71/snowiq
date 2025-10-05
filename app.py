import os
from dotenv import load_dotenv

load_dotenv()

import time
import streamlit as st
import plotly.express as px
from data.snowflake_connector import start_periodic_fetch
from data.cache import cache
from utils.logger import logger

# Streamlit 기본 설정
st.set_page_config(page_titme="snowiq - Real-time Snowflake Intelligence", layout="wide")
st.title("❄️ snowiq")
st.caption("real-time analytics + on-demand insights (Snowflake + Streamlit)")

REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", "10"))

if "fetcher_started" not in st.session_state:

    def make_sql():
        # todo: 여기서 실제 운영 쿼리로 교체
        return """
        """

    start_periodic_fetch(name="live_df", query_factory=make_sql, interval_sec=REFRESH_INTERVAL)
    st.session_state["fetcher_started"] = True
    logger.info("periodic fetcher initialized")
