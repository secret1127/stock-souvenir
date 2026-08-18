import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="股東會紀念品查詢系統", layout="wide")

st.title("🎁 全台股東會紀念品查詢系統")

# 讀取 JSON 資料
if os.path.exists("data.json"):
    with open("data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = []

if not data:
    st.warning("⚠️ 目前尚無資料，請先至 GitHub Actions 執行 Crawler！")
else:
    df = pd.DataFrame(data)

    # 側邊欄篩選功能
    st.sidebar.header("🔍 篩選條件")
    
    # 關鍵字搜尋
    search_keyword = st.sidebar.text_input("搜尋股票代碼 / 名稱 / 紀念品", "")

    # 分類快速勾選選項
    st.sidebar.subheader("快捷類別篩選")
    filter_gift_card = st.sidebar.checkbox("便利商店 / 商品禮券 / 商品卡")
    filter_odd_lots = st.sidebar.checkbox("零股可領（電子投票即可）")

    # 篩選邏輯
    filtered_df = df.copy()

    # 1. 關鍵字搜尋
    if search_keyword:
        filtered_df = filtered_df[
            filtered_df["股票代碼"].astype(str).str.contains(search_keyword) |
            filtered_df["股票名稱"].str.contains(search_keyword) |
            filtered_df["紀念品"].str.contains(search_keyword)
        ]

    # 2. 禮券 / 商品卡 快捷篩選（涵蓋各種常見禮券關鍵字）
    if filter_gift_card:
        keywords = ["禮券", "商品卡", "禮卡", "7-11", "全家", "7-ELEVEN", "超商", "商品券"]
        pattern = "|".join(keywords)
        filtered_df = filtered_df[filtered_df["紀念品"].str.contains(pattern, case=False, na=False)]

    # 3. 零股條件篩選
    if filter_odd_lots:
        filtered_df = filtered_df[filtered_df["零股條件"].str.contains("電子投票|即可|可", na=False)]

    st.write(f"📊 共找到 **{len(filtered_df)}** 筆紀念品資料")

    # 顯示表格
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )
