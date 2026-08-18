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
            table = soup.find("table") or soup
            rows = table.find_all("tr")

            for row in rows:
                # 取得所有單元格
                cols = [td.text.strip() for td in row.find_all(["td", "th"])]
                
                # HiStock 的標準表格通常有 8-10 欄
                # [0]代號, [1]名稱, [2]股價, [3]紀念品, [4]最後買進日, [5]會議日期, [6]零股/電子投票條件...
                if len(cols) >= 4:
                    code = cols[0]
                    # 確認第一欄是4位數股票代號
                    if re.match(r"^\d{4}$", code):
                        name = cols[1] if len(cols) > 1 else ""
                        
                        # 股價處理
                        price_str = re.sub(r"[^\d.]", "", cols[2]) if len(cols) > 2 else "0"
                        price = float(price_str) if price_str else 0.0
                        
                        # 尋找真正的紀念品欄位 (通常是包含中文描述且不是日期的那一欄)
                        gift = ""
                        last_buy = "依公告處理"
                        cond = "完成電子投票即可"

                        # 掃描剩餘欄位精準判定
                        for idx, val in enumerate(cols[3:], start=3):
                            # 如果格式像日期 (例如 04/28, 2026/04/28)，判定為最後買進日或會議日
                            if re.search(r"\d{1,2}/\d{1,2}", val):
                                if last_buy == "依公告處理":
                                    last_buy = val
                            # 如果包含投票/零股相關關鍵字
                            elif any(k in val for k in ["親自", "電子", "投票", "限", "發放", "不限"]):
                                cond = val
                            # 否則作為紀念品名稱
                            elif not gift and val and val not in ["常會", "臨時會"]:
                                gift = val

                        # 避免抓到「無紀念品」或空值
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

    # 去重
    unique_data = {item["股票代碼"]: item for item in raw_data}
    final_list = list(unique_data.values())

    # 寫入 json
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(final_list, f, ensure_ascii=False, indent=4)

    print(f"成功寫入 {len(final_list)} 檔紀念品股票至 data.json！")

if __name__ == "__main__":
    fetch_data()
