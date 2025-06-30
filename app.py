import streamlit as st

# Google Sheets連携設定
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
client = gspread.authorize(creds)
sheet = client.open("care_log").worksheet("2025")


st.set_page_config(page_title="セルフケアアプリ", layout="centered")

st.markdown("# セルフケア・メイン画面")
st.markdown("左側メニューからページを選択してください")

