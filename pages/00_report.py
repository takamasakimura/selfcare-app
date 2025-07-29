
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

st.set_page_config(page_title="内省レポート", layout="wide")

# Google Sheets 連携部分は utils.py の関数を使う前提
from utils import load_data

# データ読み込み
df = load_data()

# 日付をdatetime型に変換
df["日付"] = pd.to_datetime(df["日付"])

# 表示期間の選択
min_date = df["日付"].min()
max_date = df["日付"].max()
default_start = max_date - pd.Timedelta(days=30)

start_date = st.date_input("表示開始日", default_start.date(), min_value=min_date.date(), max_value=max_date.date())
end_date = st.date_input("表示終了日", max_date.date(), min_value=min_date.date(), max_value=max_date.date())

filtered_df = df[(df["日付"] >= pd.to_datetime(start_date)) & (df["日付"] <= pd.to_datetime(end_date))]

# タブで表示切り替え
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🛏️ 睡眠傾向", "📊 TLX分析", "🔄 TLX×睡眠相関", "🏷️ タグ傾向", "📓 内省ログ"])

with tab1:
    st.subheader("睡眠傾向")
    sleep_chart = alt.Chart(filtered_df).transform_fold(
        ["睡眠時間"]
    ).mark_line(point=True).encode(
        x="日付:T",
        y="value:Q",
        color="key:N"
    ).properties(width=800, height=400)
    st.altair_chart(sleep_chart, use_container_width=True)

with tab2:
    st.subheader("NASA-TLX分析")
    tlx_items = [
        "精神的要求（Mental Demand）",
        "身体的要求（Physical Demand）",
        "時間的要求（Temporal Demand）",
        "努力度（Effort）",
        "成果満足度（Performance）",
        "フラストレーション（Frustration）"
    ]
    tlx_chart = alt.Chart(filtered_df).transform_fold(
        tlx_items
    ).mark_line(point=True).encode(
        x="日付:T",
        y="value:Q",
        color="key:N"
    ).properties(width=800, height=400)
    st.altair_chart(tlx_chart, use_container_width=True)

with tab3:
    st.subheader("TLX合計スコアと睡眠の相関")
    filtered_df["TLX合計"] = filtered_df[tlx_items].sum(axis=1)
    corr_chart = alt.Chart(filtered_df).mark_circle(size=100).encode(
        x="睡眠時間:Q",
        y="TLX合計:Q",
        tooltip=["日付", "睡眠時間", "TLX合計"]
    ).interactive().properties(width=700, height=400)
    st.altair_chart(corr_chart, use_container_width=True)

with tab4:
    st.subheader("タグ傾向（出現頻度）")
    tags = filtered_df["体調サイン"].str.extractall(r"＜タグ：(.*?)＞")[0]
    tag_counts = tags.value_counts().reset_index()
    tag_counts.columns = ["タグ", "件数"]
    tag_bar = alt.Chart(tag_counts).mark_bar().encode(
        x=alt.X("件数:Q"),
        y=alt.Y("タグ:N", sort='-x')
    ).properties(width=600, height=400)
    st.altair_chart(tag_bar, use_container_width=True)

with tab5:
    st.subheader("内省ログ")
    for _, row in filtered_df.iterrows():
        st.markdown(f"### {row['日付'].date()}")
        st.markdown(f"- **取り組んだこと**: {row['取り組んだこと']}")
        st.markdown(f"- **気づいたこと**: {row['気づいたこと']}")
        st.markdown(f"- **GPTアドバイス**: {row['アドバイス']}")
        st.markdown("---")
