import streamlit as st
from utils import display_base64_gif

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
    st.stop()

# ホーム画面のメッセージ
st.markdown("# セルフケア・メイン画面")
st.markdown("左側メニューからページを選択してください")
