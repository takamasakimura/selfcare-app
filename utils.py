import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import base64
import gspread
from google.oauth2.service_account import Credentials
import gspread
from google.oauth2.service_account import Credentials
import streamlit as st

@st.cache_resource
def get_google_sheet():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("care-log").worksheet("2025")
    return sheet

# NASA-TLX ガイド読み込み
@st.cache_data
def load_guide_column(item):
    df = pd.read_csv("nasa_tlx_guide.csv", usecols=["スコア", item])
    return df.dropna()

# NASA-TLX スライダー描画
def render_nasa_tlx_slider(label, default):
    with st.expander(f"{label}（説明を見る）"):
        st.markdown(label)  # ツールチップ的説明があれば差し替え
        guide = load_guide_column(label)
        st.dataframe(guide, height=200)
    return st.slider(f"{label}（0〜10）", 0, 10, default, key=f"nasa_{label}")

# 睡眠時間の計算
def calc_sleep_hours(sleep, wake):
    dt_today = datetime.today()
    sleep_dt = datetime.combine(dt_today, sleep)
    wake_dt = datetime.combine(dt_today, wake)
    if wake_dt <= sleep_dt:
        wake_dt += timedelta(days=1)
    return round((wake_dt - sleep_dt).seconds / 3600, 2)

# アドバイス生成（重み付き）
def generate_advice(scores, nasa_scores):
    # ここは必要に応じて `SYMPTOMS` を別ファイルでインポートしてもよい
    return "（アドバイス生成ロジックは後で定義）"

# 時刻文字列→time型に変換
from datetime import time
def parse_time(s):
    try:
        return datetime.strptime(s, "%H:%M").time() if s else None
    except:
        return None

# スプレッドシートから今日の行を復元
def get_existing_data_row(sheet):
    today = datetime.today().strftime("%Y-%m-%d")
    headers = sheet.row_values(1)
    all_data = sheet.get_all_records()
    for row in all_data:
        if str(row.get("日付", "")) == today:
            return row
    return None

def display_base64_gif(file_path, width=600):
    """Base64エンコードされたGIFを画面に表示する"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            base64_gif = f.read().replace("\n", "")
        st.markdown(
            f"""
            <img src="data:image/gif;base64,{base64_gif}" width="{width}" />
            """,
            unsafe_allow_html=True,
        )
    except Exception as e:
        st.error("GIFの表示に失敗しました")
        st.exception(e)

def encode_gif_to_base64(gif_path, output_txt_path):
    """ローカルGIFファイルをBase64に変換してテキストで保存"""
    try:
        with open(gif_path, "rb") as gif_file:
            encoded = base64.b64encode(gif_file.read()).decode("utf-8")
        with open(output_txt_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(encoded)
        print(f"✅ {output_txt_path} にエンコード済みデータを保存しました")
    except Exception as e:
        print("❌ Base64変換失敗:")
        print(e)

def validate_headers(sheet, expected_headers, header_row=1):
    """
    指定されたヘッダー行と `expected_headers` を比較し、完全一致しない場合は ValueError を出す
    """
    sheet_headers = sheet.row_values(header_row)
    if sheet_headers[:len(expected_headers)] != expected_headers:
        raise ValueError(
            f"Google Sheetsのヘッダーと定義が一致しません。\n"
            f"想定: {expected_headers}\n取得: {sheet_headers}"
        )