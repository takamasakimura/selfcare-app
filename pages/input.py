# 定数定義
WARNING_SIGNS = ["肩が重い", "集中しづらい", "眠気がある"]
BAD_SIGNS = ["胃の調子が悪い", "頭痛がある"]

SYMPTOMS = {
    "肩が重い": {
        1: [{"text": "ストレッチを行う", "tags": ["身体的疲労"]}],
        2: [{"text": "肩を温める", "tags": ["身体的疲労"]}],
        3: [{"text": "マッサージを受ける", "tags": ["身体的疲労"]}],
        4: [{"text": "整体に相談", "tags": ["身体的疲労"]}],
        5: [{"text": "早退を検討", "tags": ["身体的疲労"]}]
    },
    "集中しづらい": {
        1: [{"text": "軽い散歩", "tags": ["精神的疲労"]}],
        2: [{"text": "ガムを噛む", "tags": ["精神的疲労"]}],
        3: [{"text": "作業の切り替え", "tags": ["精神的疲労"]}],
        4: [{"text": "15分の仮眠", "tags": ["精神的疲労"]}],
        5: [{"text": "休養の検討", "tags": ["精神的疲労"]}]
    },
    "眠気がある": {
        1: [{"text": "顔を洗う", "tags": ["睡眠不足"]}],
        2: [{"text": "カフェイン摂取", "tags": ["睡眠不足"]}],
        3: [{"text": "短時間の昼寝", "tags": ["睡眠不足"]}],
        4: [{"text": "休憩を取る", "tags": ["睡眠不足"]}],
        5: [{"text": "無理せず横になる", "tags": ["睡眠不足"]}]
    },
    "胃の調子が悪い": {
        1: [{"text": "胃に優しい食事を取る", "tags": ["身体的不調"]}],
        2: [{"text": "消化に良いスープを", "tags": ["身体的不調"]}],
        3: [{"text": "食事を控えめに", "tags": ["身体的不調"]}],
        4: [{"text": "市販薬を服用", "tags": ["身体的不調"]}],
        5: [{"text": "医師に相談", "tags": ["身体的不調"]}]
    },
    "頭痛がある": {
        1: [{"text": "こめかみを冷やす", "tags": ["身体的不調"]}],
        2: [{"text": "目を閉じて休む", "tags": ["身体的不調"]}],
        3: [{"text": "静かな場所で休む", "tags": ["身体的不調"]}],
        4: [{"text": "痛み止めを検討", "tags": ["身体的不調"]}],
        5: [{"text": "医療機関へ", "tags": ["身体的不調"]}]
    }
}

NASA_TLX_ITEMS = {
    "精神的要求（Mental Demand）": "どの程度，精神的かつ知覚的活動が要求されましたか？（例．思考，記憶，観察，検索など）",
    "身体的要求（Physical Demand）": "どの程度，身体的活動が必要でしたか？（例，押す，引く，回す，操作，活動するなど）",
    "時間的要求（Temporal Demand）": "作業や要素作業の頻度や速さにどの程度，時間的圧迫感を感じましたか？",
    "努力度（Effort）": "作業達成レベルに到達するのにどのくらい努力しましたか？",
    "成果満足度（Performance）": "設定された作業の達成目標について，どの程度成功したと思いますか？",
    "フラストレーション（Frustration）": "作業中，どのくらいストレス，不快感，苛立ちを感じましたか？"
}

@st.cache_data
def load_guide_column(item):
    df = pd.read_csv("nasa_tlx_guide.csv", usecols=["スコア", item])
    return df.dropna()

today = datetime.today().strftime("%Y-%m-%d")
header = sheet.row_values(1)
required_cols = ["日付"] + list(NASA_TLX_ITEMS.keys()) + WARNING_SIGNS + BAD_SIGNS + ["就寝", "起床", "睡眠時間", "何があったか", "どう感じたか", "何をしたか"]
missing = [col for col in required_cols if col not in header]
if missing:
    sheet.insert_row(header + missing[len(header):], 1)

def render_nasa_tlx_slider(label):
    with st.expander(f"{label}（説明を見る）"):
        st.markdown(NASA_TLX_ITEMS[label])
        guide = load_guide_column(label)
        st.dataframe(guide, height=200)
    return st.slider(f"{label}（0〜10）", 0, 10, 5, key=label)

def generate_advice(scores, nasa_scores):
    tags_weight = {
        "精神的疲労": nasa_scores.get("精神的要求（Mental Demand）", 0),
        "身体的疲労": nasa_scores.get("身体的要求（Physical Demand）", 0),
        "睡眠不足": nasa_scores.get("時間的要求（Temporal Demand）", 0),
        "身体的不調": nasa_scores.get("フラストレーション（Frustration）", 0)
    }
    weighted_advice = []
    for symptom, score in scores.items():
        options = SYMPTOMS.get(symptom, {}).get(score, [])
        for option in options:
            weight = sum(tags_weight.get(tag, 0) for tag in option["tags"])
            weighted_advice.append((option["text"], weight))
    weighted_advice.sort(key=lambda x: -x[1])
    top = random.sample(weighted_advice[:10], min(3, len(weighted_advice)))
    return "\n".join([f"💡 {advice}" for advice, _ in top]) if top else "（アドバイスがありません）"

st.header("NASA-TLX 評価とセルフケア")
nasa_scores = {}
scores = {}
sleep_time = None
wake_time = None
sleep_hours = None
memo_what = ""
memo_feel = ""
memo_did = ""

try:
    existing_dates = sheet.col_values(1)
    if today in existing_dates:
        idx = existing_dates.index(today) + 1
        row = sheet.row_values(idx)
        for i, key in enumerate(NASA_TLX_ITEMS.keys(), start=1):
            nasa_scores[key] = int(row[i]) if row[i].isdigit() else 5
        for i, key in enumerate(WARNING_SIGNS + BAD_SIGNS, start=1+len(NASA_TLX_ITEMS)):
            scores[key] = int(row[i]) if row[i].isdigit() else 3
        sleep_time = datetime.strptime(row[-6], "%H:%M").time()
        wake_time = datetime.strptime(row[-5], "%H:%M").time()
        sleep_hours = float(row[-4])
        memo_what = row[-3]
        memo_feel = row[-2]
        memo_did = row[-1]
    else:
        for item in NASA_TLX_ITEMS:
            nasa_scores[item] = render_nasa_tlx_slider(item)
        st.markdown("---")
        st.subheader("注意・悪化サイン入力")
        for symptom in WARNING_SIGNS + BAD_SIGNS:
            scores[symptom] = st.radio(f"{symptom}（1〜5）", [1,2,3,4,5], horizontal=True, key=symptom)
        st.subheader("睡眠時間の記録")
        sleep_time = st.time_input("就寝時間", key="sleep")
        wake_time = st.time_input("起床時間", key="wake")
        def calc_sleep_hours(start, end):
            if start and end:
                duration = (datetime.combine(datetime.today(), end) - datetime.combine(datetime.today(), start)).seconds
                return round(duration / 3600, 2)
            return None
        sleep_hours = calc_sleep_hours(sleep_time, wake_time)
        if sleep_hours is not None:
            st.write(f"🕒 睡眠時間: {sleep_hours} 時間")
        st.subheader("今日のメモ")
        memo_what = st.text_area("何があったか？", key="memo_what")
        memo_feel = st.text_area("どう感じたか？", key="memo_feel")
        memo_did = st.text_area("何をしたか？", key="memo_did")
except Exception as e:
    st.warning("既存データの読み込みに失敗しました")
    st.exception(e)

if st.button("保存してアドバイス表示"):
    try:
        update_values = [nasa_scores[k] for k in NASA_TLX_ITEMS] + [scores[k] for k in WARNING_SIGNS + BAD_SIGNS] + [
            sleep_time.strftime("%H:%M"), wake_time.strftime("%H:%M"), sleep_hours,
            memo_what, memo_feel, memo_did
        ]
        if today in existing_dates:
            idx = existing_dates.index(today) + 1
            sheet.update(f"B{idx}:{chr(65+len(update_values))}{idx}", [update_values])
        else:
            sheet.append_row([today] + update_values)
        advice = generate_advice(scores, nasa_scores)
        st.markdown(f"""
            <div style='position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background-color: #f0f0f0; border: 2px solid #ccc; padding: 20px; border-radius: 10px; z-index: 1000;'>
                <h4>✨ 今日のセルフケアアドバイス ✨</h4>
                <p>{advice}</p>
                <button onclick=\"this.parentElement.style.display='none';\">閉じる</button>
            </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error("保存中にエラーが発生しました")
        st.exception(e)
