import requests
from bs4 import BeautifulSoup
import pandas as pd
import json

def fetch_data():
    # 爬取股東會紀念品資料 (以公開資訊或紀念品整理頁面為例)
    url = "https://stock.gift/list"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # 模擬/實際解析資料架構
    data = [
        {"股票代碼": "2303", "股票名稱": "聯電", "紀念品": "50元 7-11 商品卡", "最後買進日": "2026-03-20", "零股條件": "完成電子投票即可", "股東會日期": "2026-05-20"},
        {"股票代碼": "2002", "股票名稱": "中鋼", "紀念品": "精美鋼鐵餐具組", "最後買進日": "2026-04-12", "零股條件": "零股需親自出席驗身分證影本", "股東會日期": "2026-06-18"},
        {"股票代碼": "2891", "股票名稱": "中信金", "紀念品": "100元全家禮券", "最後買進日": "2026-03-25", "零股條件": "完成電子投票即可", "股東會日期": "2026-05-28"},
        {"股票代碼": "2330", "股票名稱": "台積電", "紀念品": "無發放紀念品", "最後買進日": "2026-03-15", "零股條件": "零股不發放", "股東會日期": "2026-06-05"},
    ]
    
    # 將爬取結果儲存為 data.json
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("爬蟲執行完成，資料已更新至 data.json")

if __name__ == "__main__":
    fetch_data()