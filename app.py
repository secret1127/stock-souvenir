import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="股東會紀念品聰明選", layout="wide", initial_sidebar_state="collapsed")
st.title("🎁 股東會紀念品速查篩選器")

# 讀取資料
if os.path.exists("data.json"):
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = []

df = pd.DataFrame(data)

if not df.empty:
    # 關鍵字過濾標籤
    voucher_keywords = ["禮券", "商品卡", "提貨券", "商品券", "7-11", "全家", "超商", "全聯"]
    hassle_keywords = ["身分證", "影本", "親自出席", "不發放", "無發放", "郵寄"]

    df["是禮券類"] = df["紀念品"].apply(lambda x: any(kw in str(x) for kw in voucher_keywords))
    df["門檻繁瑣"] = df["零股條件"].apply(lambda x: any(kw in str(x) for kw in hassle_keywords))

    st.subheader("⚙️ 快速過濾條件")
    col1, col2 = st.columns(2)
    with col1:
        only_vouchers = st.checkbox("🎟️ 只看「商品禮券」", value=True)
    with col2:
        hide_hassle = st.checkbox("🛡️ 隱藏「需身分證/親自出席/不發」", value=True)

    filtered_df = df.copy()
    if only_vouchers:
        filtered_df = filtered_df[filtered_df["是禮券類"] == True]
    if hide_hassle:
        filtered_df = filtered_df[filtered_df["門檻繁瑣"] == False]

    st.divider()
    
    # 顯示符合檔數與總花費預算
    total_cost = filtered_df["買1股成本"].sum() if "買1股成本" in filtered_df.columns else 0
    m1, m2 = st.columns(2)
    m1.metric(label="符合條件標的", value=f"{len(filtered_df)} 檔")
    m2.metric(label="全買 1 股預估總花費", value=f"${int(total_cost)} 元")

    # 呈現更新後的完整表格（含股價與1股成本）
    display_cols = ["股票代碼", "股票名稱", "當前股價", "買1股成本", "紀念品", "最後買進日", "零股條件"]
    existing_cols = [c for c in display_cols if c in filtered_df.columns]

    st.dataframe(
        filtered_df[existing_cols],
        use_container_width=True,
        hide_index=True,
        column_config={
            "當前股價": st.column_config.NumberColumn("當前股價", format="$%.1f"),
            "買1股成本": st.column_config.NumberColumn("買1股預估成本", format="$%.1f 元"),
        }
    )

    st.subheader("⚡ 一鍵複製股票代碼")
    codes = " ".join(filtered_df["股票代碼"].tolist())
    st.code(codes if codes else "無符合條件的標的", language="text")
