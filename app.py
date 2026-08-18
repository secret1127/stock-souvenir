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

    # 2. 身分證件需求篩選
    id_req_filter = st.sidebar.radio(
        "身分證件需求",
        ["不限", "免身分證件（排除需正/影本）", "需身分證正本", "需身分證影本"]
    )

    # 3. 快捷勾選類別
    st.sidebar.subheader("快捷類別篩選")
    filter_gift_card = st.sidebar.checkbox("便利商店 / 商品禮券 / 商品卡")
    filter_odd_lots = st.sidebar.checkbox("零股可領（電子投票即可）")
    exclude_id_req = st.sidebar.checkbox("排除需身分證件（正/影本）")

    filtered_df = df.copy()

    # 建立全文字段以利比對身分證條件
    text_corpus = (
        filtered_df.get("零股條件", "").astype(str) + " " +
        filtered_df.get("紀念品", "").astype(str) + " " +
        filtered_df.get("備註", "").astype(str)
    )

    # 身分證件需求過濾邏輯
    id_pattern = r"(正本|影本|印本|檢附|身分證|證件)"
    
    if exclude_id_req or id_req_filter == "免身分證件（排除需正/影本）":
        filtered_df = filtered_df[~text_corpus.str.contains(id_pattern, flags=re.IGNORECASE, na=False)]
    elif id_req_filter == "需身分證正本":
        filtered_df = filtered_df[text_corpus.str.contains(r"(正本|核對正本)", flags=re.IGNORECASE, na=False)]
    elif id_req_filter == "需身分證影本":
        filtered_df = filtered_df[text_corpus.str.contains(r"(影本|印本)", flags=re.IGNORECASE, na=False)]

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

    # 計算統計金額（轉為數值型態計算）
    total_count = len(filtered_df)
    stock_prices = pd.to_numeric(filtered_df.get("當前股價", 0), errors='coerce').fillna(0)
    cost_1share = pd.to_numeric(filtered_df.get("買1股成本", 0), errors='coerce').fillna(0)
    
    total_stock_price = stock_prices.sum()
    total_cost_1share = cost_1share.sum()
    avg_cost = (total_cost_1share / total_count) if total_count > 0 else 0

    # 顯示頂部統計資訊卡片（完整整數顯示）
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("符合條件檔數", f"{total_count:,} 檔")
    col2.metric("股價合計", f"${int(total_stock_price):,} 元")
    col3.metric("買1股總成本", f"${int(total_cost_1share):,} 元")
    col4.metric("平均每股成本", f"${avg_cost:.2f} 元")

    st.markdown("---")

    # 資料表格顯示
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )
