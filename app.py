import streamlit as st
import pandas as pd
import json
import os

st.title("🛠️ 資料診斷模式")

if not os.path.exists("data.json"):
    st.error("❌ 找不到 data.json 檔案！請檢查 GitHub 根目錄是否有此檔案。")
else:
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        st.success(f"✅ 成功讀取 data.json，共有 {len(data)} 筆資料")
        
        if len(data) > 0:
            df = pd.DataFrame(data)
            
            st.subheader("1. 抓到的資料欄位 (Columns)")
            st.write(list(df.columns))
            
            st.subheader("2. 前 3 筆原始資料預覽")
            st.json(data[:3])
        else:
            st.warning("⚠️ data.json 檔案存在，但內容是空的 []！")
            
    except Exception as e:
        st.error(f"❌ 讀取 json 發生錯誤：{e}")
