import streamlit as st
from datetime import datetime
from utils import (
    get_google_sheet,
    load_guide_column,
    render_nasa_tlx_slider,
    calc_sleep_hours,
    generate_advice,
    parse_time,
    get_existing_data_row
)

st.set_page_config(
    page_title="セルフケアアプリ",
    layout="centered",
    initial_sidebar_state="expanded"
)

if not st.session_state.get("started", False):
    st.warning("起動画面から開始してください。左側のメニューに戻ってください。")
    st.stop()

sheet = get_google_sheet()

WARNING_SIGNS = ["肩が重い", "集中しづらい", "眠気がある"]
BAD_SIGNS = ["胃の調子が悪い", "頭痛がある"]
NASA_TLX_ITEMS = {
    "精神的要求（Mental Demand）": "どの程度，精神的かつ知覚的活動が要求されましたか？（例．思考，記憶，観察，検索など）",
    "身体的要求（Physical Demand）": "どの程度，身体的活動が必要でしたか？（例，押す，引く，回す，操作，活動するなど）",
    "時間的要求（Temporal Demand）": "作業や要素作業の頻度や速さにどの程度，時間的圧迫感を感じましたか？",
    "努力度（Effort）": "作業達成レベルに到達するのにどのくらい努力しましたか？",
    "成果満足度（Performance）": "設定された作業の達成目標について，どの程度成功したと思いますか？",
    "フラストレーション（Frustration）": "作業中，どのくらいストレス，不快感，苛立ちを感じましたか？"
}

st.header("NASA-TLX評価とセルフケア")

# 復元データ取得
row_data = get_existing_data_row(sheet)

# 就寝・起床入力
sleep_default = parse_time(row_data.get("就寝時間")) if row_data else None
wake_default = parse_time(row_data.get("起床時間")) if row_data else None

sleep_time = st.time_input("就寝時間", value=sleep_default, key="sleep")
wake_time = st.time_input("起床時間", value=wake_default, key="wake")
sleep_hours = calc_sleep_hours(sleep_time, wake_time)

if sleep_hours is not None:
    st.write(f"🕒 睡眠時間: {sleep_hours} 時間")

# NASA-TLX スコア入力
nasa_scores = {}
for item in NASA_TLX_ITEMS:
    default = int(row_data.get(item)) if row_data and row_data.get(item, '').isdigit() else 5
    nasa_scores[item] = render_nasa_tlx_slider(item, default)

# 注意・悪化サイン入力
st.markdown("---")
st.subheader("注意・悪化サイン入力")
scores = {}
for symptom in WARNING_SIGNS + BAD_SIGNS:
    default = int(row_data.get(symptom)) if row_data and row_data.get(symptom, '').isdigit() else 3
    scores[symptom] = st.radio(
        f"{symptom}（1〜5）",
        [1, 2, 3, 4, 5],
        index=default - 1,
        horizontal=True,
        key=f"symptom_{symptom}"
    )

# メモ入力
st.subheader("今日のメモ")
memo_what = st.text_area("何があったか？", value=row_data.get("何があったか？") if row_data else "", key="memo_what")
memo_feel = st.text_area("どう感じたか？", value=row_data.get("どう感じたか？") if row_data else "", key="memo_feel")
memo_did = st.text_area("何をしたか？", value=row_data.get("何をしたか？") if row_data else "", key="memo_did")

# 保存とアドバイス表示
if "show_advice" not in st.session_state:
    st.session_state["show_advice"] = False

if st.button("保存してアドバイス表示"):
    try:
        today = datetime.today().strftime("%Y-%m-%d")
        existing_dates = sheet.col_values(1)
        update_values = [
            sleep_time.strftime("%H:%M"), wake_time.strftime("%H:%M")
        ] + [nasa_scores[k] for k in NASA_TLX_ITEMS] \
          + [scores[k] for k in WARNING_SIGNS + BAD_SIGNS] \
          + [sleep_hours, memo_what, memo_feel, memo_did]

        if today in existing_dates:
            idx = existing_dates.index(today) + 1
            sheet.update(f"B{idx}:{chr(65 + len(update_values))}{idx}", [update_values])
        else:
            sheet.append_row([today] + update_values)

        st.session_state["advice_text"] = generate_advice(scores, nasa_scores)
        st.session_state["show_advice"] = True
    except Exception as e:
        st.error("保存中にエラーが発生しました")
        st.exception(e)

if st.session_state.get("show_advice", False):
    st.markdown("### ✨ 今日のセルフケアアドバイス ✨")
    st.info(st.session_state["advice_text"])
    if st.button("❌ 閉じる"):
        st.session_state["show_advice"] = False
