import cloudscraper
from bs4 import BeautifulSoup
import json
import re

def fetch_data():
    raw_data = []
    
    try:
        scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
        )
        url = "https://histock.tw/stock/gift.aspx"
        print(f"開始抓取全台紀念品清單: {url}")
        res = scraper.get(url, timeout=15)
        res.encoding = "utf-8"

        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            rows = soup.find_all("tr")

            for row in rows:
                cols = [td.text.strip() for td in row.find_all(["td", "th"])]
                
                # 確保是股票資料列（第一欄為4位數股票代號）
                if len(cols) >= 4 and re.match(r"^\d{4}$", cols[0]):
                    code = cols[0]
                    name = cols[1] if len(cols) > 1 else ""
                    
                    # 股價處理
                    price_str = re.sub(r"[^\d.]", "", cols[2]) if len(cols) > 2 else "0"
                    price = float(price_str) if price_str else 0.0

                    gift = ""
                    last_buy = "依公告處理"
                    cond = "完成電子投票即可"

                    # 針對剩餘欄位進行類型判斷，避免欄位錯位
                    for val in cols[3:]:
                        if not val:
                            continue
                        # 1. 判斷是否為日期 (例如 04/28)
                        if re.search(r"\d{1,2}/\d{1,2}", val):
                            if last_buy == "依公告處理":
                                last_buy = val
                        # 2. 判斷是否為投票/零股條件
                        elif any(k in val for k in ["親自", "電子", "投票", "限", "發放", "不限"]):
                            cond = val
                        # 3. 排除開會類型後，其餘長度合理的文字視為真正的紀念品名稱
                        elif val not in ["常會", "臨時會"] and len(val) >= 2:
                            if not gift:
                                gift = val

                    # 過濾無紀念品之資料
                    if gift and not any(k in gift for k in ["無紀念品", "不發放", "無", "尚未公佈", "尚無"]):
                        raw_data.append({
                            "股票代碼": code,
                            "股票名稱": name,
                            "當前股價": price,
                            "買1股成本": round(price + 1, 1),
                            "紀念品": gift,
                            "最後買進日": last_buy,
                            "零股條件": cond
                        })

    except Exception as e:
        print(f"爬取發生例外狀況: {e}")

    if len(raw_data) == 0:
        print("⚠️ 未抓取到任何資料，取消寫入！")
        return

    # 去重
    unique_data = {item["股票代碼"]: item for item in raw_data}
    final_list = list(unique_data.values())

    # 寫入 json
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(final_list, f, ensure_ascii=False, indent=4)

    print(f"成功寫入 {len(final_list)} 檔紀念品股票至 data.json！")

if __name__ == "__main__":
    fetch_data()
