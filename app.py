import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets連携設定
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"], scope)
client = gspread.authorize(creds)
sheet = client.open("care_log").worksheet("2025")

# 定数定義
GOOD_SIGNS = ["よく眠れた", "体が軽い"]
WARNING_SIGNS = ["肩が重い", "集中しづらい", "眠気がある"]
BAD_SIGNS = ["胃の調子が悪い", "頭痛がある"]

SYMPTOMS = {}
for sign in GOOD_SIGNS + WARNING_SIGNS + BAD_SIGNS:
    SYMPTOMS[sign] = {
        1: ["1の場合のセルフケア"],
        2: ["2の場合のセルフケア"],
        3: ["3の場合のセルフケア"],
        4: ["4の場合のセルフケア"],
        5: ["5の場合のセルフケア"]
    }

# 関数定義
def calculate_sleep_duration(sleep_time, wake_time):
    try:
        fmt_sleep = datetime.strptime(sleep_time, "%H:%M")
        fmt_wake = datetime.strptime(wake_time, "%H:%M")
        if fmt_wake < fmt_sleep:
            fmt_wake += timedelta(days=1)
        duration = (fmt_wake - fmt_sleep).seconds / 3600
        return round(duration, 2)
    except:
        return None

def generate_advice(scores):
    results = []
    for symptom, score in scores.items():
        options = SYMPTOMS.get(symptom, {}).get(score, [])
        sample_size = 1 if symptom in GOOD_SIGNS else 3
        sampled = random.sample(options, min(sample_size, len(options)))
        for advice in sampled:
            results.append(f"{symptom}（{score}）→ {advice}")
    return "\n".join(results) if results else "（セルフケア提案はありません）"

def append_to_sheet(row):
    values = [
        row["日付"], row["就寝"], row["起床"], row["睡眠時間"],
        row["何があったか"], row["どう感じたか"], row["何をしたか"],
        row["今日の調子"]
    ]
    sheet.append_row(values)

# UI構築
st.set_page_config(layout="wide")
st.title("セルフケア＆自己成長アプリ")

if 'started' not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    if st.button("今日の体調を入力"):
        st.session_state.started = True
else:
    tabs = st.tabs(["体調管理", "振り返り"])

    with tabs[0]:
        st.subheader("体調管理")
        sleep_time_raw = st.text_input("就寝時間（例：2345）", max_chars=4)
        wake_time_raw = st.text_input("起床時間（例：0645）", max_chars=4)

        st.markdown("**📝 今日の出来事メモ**")
        what_happened = st.text_area("何があったか")
        how_felt = st.text_area("どう感じたか")
        what_did = st.text_area("何をしたか")

        sleep_time_raw = sleep_time_raw.translate(str.maketrans('０１２３４５６７８９：', '0123456789:'))
        wake_time_raw = wake_time_raw.translate(str.maketrans('０１２３４５６７８９：', '0123456789:'))

        try:
            sleep_time = f"{int(sleep_time_raw[:2]):02}:{sleep_time_raw[2:]}"
            wake_time = f"{int(wake_time_raw[:2]):02}:{wake_time_raw[2:]}"
            sleep_duration = calculate_sleep_duration(sleep_time, wake_time)
            st.markdown(f"**睡眠時間**: {sleep_duration} 時間")
        except:
            sleep_time = "--:--"
            wake_time = "--:--"
            sleep_duration = None

        st.markdown("### 😐 今日の調子")
        condition_emojis = {
            "とてもいい": "😄",
            "いい": "🙂",
            "普通": "😐",
            "悪い": "😕",
            "とても悪い": "😫"
        }
        condition = st.radio("今日の調子を選んでください", list(condition_emojis.keys()), horizontal=True)
        condition_display = condition_emojis[condition]
        st.markdown(f"### 今日の調子: {condition_display}")

        scores = {}

        st.markdown("### 🟢 好調サイン")
        for symptom in GOOD_SIGNS:
            scores[symptom] = st.radio(f"{symptom}（1〜5）", [1,2,3,4,5], horizontal=True, key=symptom)

        st.markdown("### ⚠️ 注意サイン")
        for symptom in WARNING_SIGNS:
            scores[symptom] = st.radio(f"{symptom}（1〜5）", [1,2,3,4,5], horizontal=True, key=symptom)

        st.markdown("### 🔴 悪化サイン")
        for symptom in BAD_SIGNS:
            scores[symptom] = st.radio(f"{symptom}（1〜5）", [1,2,3,4,5], horizontal=True, key=symptom)

        if st.button("保存（体調）"):
            today = datetime.today().strftime('%Y-%m-%d')
            row = {
                "日付": today,
                "就寝": sleep_time,
                "起床": wake_time,
                "睡眠時間": sleep_duration,
                "何があったか": what_happened,
                "どう感じたか": how_felt,
                "何をしたか": what_did,
                "今日の調子": condition
            }
            append_to_sheet(row)
            advice = generate_advice(scores)
            st.markdown(f"""
                <div style='position: fixed; top: 10px; right: 10px; background-color: #fafafa; border: 1px solid #ddd; padding: 15px; border-radius: 10px; z-index: 1000;'>
                    <b>💡 今日のアドバイス</b><br>{advice}<br>
                    <button onclick=\"this.parentElement.style.display='none';\" style='margin-top:5px;'>✖️ 閉じる</button>
                </div>
            """, unsafe_allow_html=True)

    with tabs[1]:
        st.subheader("振り返り")
        all_data = sheet.get_all_records()
        if all_data:
            df = pd.DataFrame(all_data)
            df = df.sort_values("日付", ascending=False)
            selected_date = st.selectbox("日付を選択", df["日付"].tolist())
            selected_row = df[df["日付"] == selected_date].iloc[0]
            st.markdown("### 🕒 睡眠時間")
            st.markdown(f"**就寝**: {selected_row['就寝']}　**起床**: {selected_row['起床']}")
            st.markdown("### 📓 メモ")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.text_area("何があったか", selected_row["何があったか"], height=100)
            with col2:
                st.text_area("どう感じたか", selected_row["どう感じたか"], height=100)
            with col3:
                st.text_area("何をしたか", selected_row["何をしたか"], height=100)
        else:
            st.info("記録がまだありません")

