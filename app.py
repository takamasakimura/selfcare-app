import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
from utils import display_base64_gif
import gspread
from google.oauth2.service_account import Credentials

# Google Sheets連携設定
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(creds)
sheet = client.open("care-log").worksheet("2025")

# ページ設定
st.set_page_config(
    page_title="セルフケアアプリ",
    layout="centered",
    initial_sidebar_state="expanded"
)

# セッション制御とGIF表示
if "started" not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    display_base64_gif("gif_assets/start_banner.gif.txt", width=600)
    st.markdown("## - tap to start -")
    if st.button("▶️ はじめる"):
        st.session_state.started = True
        st.experimental_rerun()
    st.stop()

# ホーム画面のメッセージ
else:
    st.markdown("# セルフケア・メイン画面")
    st.markdown("左側メニューからページを選択してください")

