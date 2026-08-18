import streamlit as st
import pandas as pd
import json
import os
import re

st.set_page_config(page_title="全台股東會紀念品查詢系統", layout="wide", page_icon="🎁")

st.title("🎁 全台股東會紀念品查詢系統")

# 讀取 JSON 資料
if os.path.exists("data.json"):
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        data = []
        st.error(f"讀取資料失敗：{e}")
else:
    data = []

if not data:
    st.warning("⚠️ 目前尚無資料，請至 GitHub Actions 執行爬蟲重新抓取數據！")
else:
    df = pd.DataFrame(data)

    # 側邊欄篩選區
    st.sidebar.header("🔍 篩選與搜尋")
    
    # 1. 文字關鍵字搜尋
    search_keyword = st.sidebar.text_input("搜尋股票代碼 / 名稱 / 紀念品", "")

    # 2. 身分證件需求篩選 (正本 / 影本)
    id_req_filter = st.sidebar.radio(
        "身分證件需求",
        ["不限", "需身分證正本", "需身分證影本"]
    )

    # 3. 快捷勾選類別
    st.sidebar.subheader("快捷類別篩選")
    filter_gift_card = st.sidebar.checkbox("便利商店 / 商品禮券 / 商品卡")
    filter_odd_lots = st.sidebar.checkbox("零股可領（電子投票即可）")

    filtered_df = df.copy()

    # 身分證件需求過濾
    if id_req_filter == "需身分證正本":
        filtered_df = filtered_df[filtered_df["零股條件"].astype(str).str.contains(r"(正本|檢附正本|核對正本)", flags=re.IGNORECASE, na=False)]
    elif id_req_filter == "需身分證影本":
        filtered_df = filtered_df[filtered_df["零股條件"].astype(str).str.contains(r"(影本|印本|檢附影本)", flags=re.IGNORECASE, na=False)]

    # 關鍵字過濾
    if search_keyword:
        filtered_df = filtered_df[
            filtered_df["股票代碼"].astype(str).str.contains(search_keyword, case=False, na=False) |
            filtered_df["股票名稱"].astype(str).str.contains(search_keyword, case=False, na=False) |
            filtered_df["紀念品"].astype(str).str.contains(search_keyword, case=False, na=False)
        ]

    # 商品禮券 / 卡 過濾
    if filter_gift_card:
        pattern = r"(禮券|商品卡|禮卡|7-11|7-Eleven|全家|超商|商品券|卡|券|全聯|莫凡彼|星巴克|提貨券)"
        filtered_df = filtered_df[filtered_df["紀念品"].astype(str).str.contains(pattern, flags=re.IGNORECASE, na=False)]

    # 零股條件過濾
    if filter_odd_lots:
        filtered_df = filtered_df[filtered_df["零股條件"].astype(str).str.contains(r"(電子|投票|即可|可|不限|同意)", flags=re.IGNORECASE, na=False)]

    # 數據統計與顯示
    st.write(f"📊 共找到 **{len(filtered_df)}** 筆符合條件的股東會紀念品")

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )
