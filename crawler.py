import requests
from bs4 import BeautifulSoup
import json
import re

def fetch_data():
    url = "https://stock.gift/list"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    raw_data = []

    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")

        # 解析頁面上的所有股票表格欄位
        rows = soup.find_all("tr")
        
        for row in rows:
            cols = [td.text.strip() for td in row.find_all(["td", "th"])]
            
            if len(cols) >= 5:
                stock_code = cols[0]
                # 確保為 4 位數股票代碼
                if re.match(r"^\d{4}$", stock_code):
                    stock_name = cols[1]
                    price_str = re.sub(r"[^\d.]", "", cols[2]) if len(cols) > 2 else "0"
                    price = float(price_str) if price_str else 0.0
                    
                    gift_name = cols[3] if len(cols) > 3 else ""
                    last_buy_date = cols[4] if len(cols) > 4 else "未公佈"
                    condition = cols[5] if len(cols) > 5 else "依公告處理"

                    # 關鍵過濾條件：剔除「無」、「尚無」、「未發放」或空白的項目
                    if gift_name and not any(k in gift_name for k in ["無紀念品", "不發放", "尚未公佈", "無"]):
                        raw_data.append({
                            "股票代碼": stock_code,
                            "股票名稱": stock_name,
                            "當前股價": price,
                            "買1股成本": round(price + 1, 1), # 股價 + 1元最低零股手續費
                            "紀念品": gift_name,
                            "最後買進日": last_buy_date,
                            "零股條件": condition
                        })

    except Exception as e:
        print(f"爬取過程中發生錯誤: {e}")

    # 存檔至 data.json
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=4)
        
    print(f"爬蟲完成！共篩選出 {len(raw_data)} 檔有發放紀念品的股票並寫入 data.json")

if __name__ == "__main__":
    fetch_data()
