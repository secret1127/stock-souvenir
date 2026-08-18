import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="股東會紀念品查詢系統", layout="wide")

st.title("🎁 全台股東會紀念品查詢系統")

# 讀取 JSON 資料
data = []
if os.path.exists("data.json"):
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        st.error(f"讀取 data.json 失敗：{e}")

if not data:
    st.warning("⚠️ 目前尚無資料，請確認 GitHub Actions 是否已順利執行並更新 data.json！")
else:
    df = pd.DataFrame(data)

    # 1. 欄位自動相容對映（防止名稱不一致）
    col_mapping = {
        "code": "股票代碼", "stock_code": "股票代碼", "代號": "股票代碼",
        "name": "股票名稱", "stock_name": "股票名稱", "名稱": "股票名稱",
        "gift": "紀念品", "souvenir": "紀念品", "紀念品名稱": "紀念品",
        "price": "當前股價", "股價": "當前股價",
        "cost": "買1股成本", "成本": "買1股成本",
        "last_day": "最後買進日", "最後買進日": "最後買進日",
        "condition": "零股條件", "零股條件": "零股條件"
    }
    df.rename(columns=col_mapping, inplace=True)

    # 確保關鍵欄位存在
    for required_col in ["股票代碼", "股票名稱", "紀念品", "零股條件"]:
        if required_col not in df.columns:
            df[required_col] = ""

    # 側邊欄篩選功能
    st.sidebar.header("🔍 篩選條件")
    
    # 關鍵字搜尋
    search_keyword = st.sidebar.text_input("搜尋股票代碼 / 名稱 / 紀念品", "")

    # 分類快捷勾選
    st.sidebar.subheader("快捷類別篩選")
    filter_gift_card = st.sidebar.checkbox("便利商店 / 商品禮券 / 商品卡")
    filter_odd_lots = st.sidebar.checkbox("零股可領（電子投票即可）")

    filtered_df = df.copy()

    # 1. 關鍵字搜尋
    if search_keyword:
        filtered_df = filtered_df[
            filtered_df["股票代碼"].astype(str).str.contains(search_keyword, case=False, na=False) |
            filtered_df["股票名稱"].astype(str).str.contains(search_keyword, case=False, na=False) |
            filtered_df["紀念品"].astype(str).str.contains(search_keyword, case=False, na=False)
        ]

    # 2. 禮券 / 商品卡 快捷篩選
    if filter_gift_card:
        keywords = ["禮券", "商品卡", "禮卡", "7-11", "全家", "7-ELEVEN", "超商", "商品券", "卡", "券"]
        pattern = "|".join(keywords)
        filtered_df = filtered_df[filtered_df["紀念品"].astype(str).str.contains(pattern, case=False, na=False)]

    # 3. 零股條件篩選
    if filter_odd_lots:
        filtered_df = filtered_df[filtered_df["零股條件"].astype(str).str.contains("電子投票|即可|可|同意", case=False, na=False)]

    st.write(f"📊 共找到 **{len(filtered_df)}** 筆紀念品資料")

    # 顯示表格
    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )
