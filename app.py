import streamlit as st
import pandas as pd

# 頁面設定：針對手機瀏覽優化
st.set_page_config(
    page_title="股東會紀念品聰明選", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

st.title("🎁 股東會紀念品速查篩選器")
st.caption("自動排除繁瑣門檻（身分證/親自出席），一鍵篩選高 CP 值標的")

# 1. 模擬/讀取紀念品清單資料 (可替換為 Google Sheets 或爬蟲資料)
data = [
    {
        "股票代碼": "2303", 
        "股票名稱": "聯電", 
        "紀念品": "50元 7-11 商品卡", 
        "最後買進日": "2026-03-20", 
        "零股條件": "完成電子投票即可",
        "股東會日期": "2026-05-20"
    },
    {
        "股票代碼": "2002", 
        "股票名稱": "中鋼", 
        "紀念品": "精美鋼鐵餐具組", 
        "最後買進日": "2026-04-12", 
        "零股條件": "零股需親自出席驗身分證影本",
        "股東會日期": "2026-06-18"
    },
    {
        "股票代碼": "2891", 
        "股票名稱": "中信金", 
        "紀念品": "100元全家禮券", 
        "最後買進日": "2026-03-25", 
        "零股條件": "完成電子投票即可",
        "股東會日期": "2026-05-28"
    },
    {
        "股票代碼": "2330", 
        "股票名稱": "台積電", 
        "紀念品": "無發放紀念品", 
        "最後買進日": "2026-03-15", 
        "零股條件": "零股不發放",
        "股東會日期": "2026-06-05"
    },
    {
        "股票代碼": "2408", 
        "股票名稱": "南亞科", 
        "紀念品": "200元遠東百貨禮券", 
        "最後買進日": "2026-03-28", 
        "零股條件": "需親自出席或郵寄身分證影本",
        "股東會日期": "2026-05-29"
    },
]

df = pd.DataFrame(data)

# 2. 自動關鍵字解析與標記邏輯
voucher_keywords = ["禮券", "商品卡", "提貨券", "商品券", "7-11", "全家", "超商", "全聯"]
hassle_keywords = ["身分證", "影本", "親自出席", "不發放", "無發放", "郵寄", "現場"]

df["是禮券類"] = df["紀念品"].apply(lambda x: any(kw in str(x) for kw in voucher_keywords))
df["門檻繁瑣"] = df["零股條件"].apply(lambda x: any(kw in str(x) for kw in hassle_keywords))

# 3. 頂部大按鈕過濾器（適合手機手指點擊）
st.subheader("⚙️ 快速過濾條件")
col1, col2 = st.columns(2)

with col1:
    only_vouchers = st.checkbox("🎟️ 只看「商品禮券」", value=True)
with col2:
    hide_hassle = st.checkbox("🛡️ 隱藏「需身分證/親自出席/不發」", value=True)

# 4. 套用過濾邏輯
filtered_df = df.copy()

if only_vouchers:
    filtered_df = filtered_df[filtered_df["是禮券類"] == True]

if hide_hassle:
    filtered_df = filtered_df[filtered_df["門檻繁瑣"] == False]

# 5. 結果呈現與批次複製
st.divider()
st.metric(label="符合條件的優質標的", value=f"{len(filtered_df)} 檔")

# 表格呈現
st.dataframe(
    filtered_df[["股票代碼", "股票名稱", "紀念品", "最後買進日", "零股條件"]],
    use_container_width=True,
    hide_index=True
)

# 批次下單代碼複製區
st.subheader("⚡ 一鍵複製股票代碼")
codes = " ".join(filtered_df["股票代碼"].tolist())

if codes:
    st.code(codes, language="text")
    st.caption("💡 點選代碼方塊右上角圖示即可複製，可直接貼入券商預約下單軟體。")
else:
    st.warning("目前沒有符合所有條件的股票標的。")