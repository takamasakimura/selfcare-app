import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import gspread
from google.oauth2.service_account import Credentials

# Google Sheets連携設定
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
client = gspread.authorize(creds)
sheet = client.open("care-log").worksheet("2025")

st.set_page_config(
    page_title="セルフケアアプリ",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.markdown("# セルフケア・メイン画面")
st.markdown("左側メニューからページを選択してください")

# セッション制御とGIF表示
if "started" not in st.session_state:
    st.session_state.started = False

else:
    st.markdown("### メニューからページを選択してください")

if not st.session_state.started:
    display_base64_gif("gif_assets/start_banner.gif.txt", width=600)
    st.markdown("## - tap to start -")
    if st.button("▶️ はじめる"):
        st.session_state.started = True
    st.stop()

else:
    st.markdown("### 左のメニューからページを選んでください")