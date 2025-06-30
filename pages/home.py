import streamlit as st

def display_base64_gif(gif_path_txt, width=600):
    with open(gif_path_txt, "r") as f:
        data = f.read()
    gif_html = f'''
        <img src="data:image/gif;base64,{data}" width="{width}" />
    '''
    st.markdown(gif_html, unsafe_allow_html=True)

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