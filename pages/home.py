import streamlit as st

def display_base64_gif(gif_path_txt, width=600):
    with open(gif_path_txt, "r") as f:
        base64_gif = f.read().replace("\n", "")  # 改行除去
    st.markdown(
        f"""
        <img src="data:image/gif;base64,{base64_gif}" width="{width}" />
        """,
        unsafe_allow_html=True,
    )

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