import streamlit as st

from utils import display_base64_gif

# 使用箇所
display_base64_gif("gif_assets/start_banner.gif.txt", width=600)

# 起動画面のビジュアル演出
if "started" not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    display_base64_gif("gif_assets/start_banner.gif.txt", width=600)  # Base64テキストを参照
    st.markdown("## - tap to start -")
    if st.button("▶️ はじめる"):
        st.session_state.started = True
    st.stop()

else:
    st.markdown("### メニューから入力画面などを選んでください")