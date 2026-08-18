import cloudscraper
from bs4 import BeautifulSoup
import json
import re

def fetch_data():
    raw_data = []
    
    # 建立可繞過 Cloudflare 防禦的 Scraper 實例
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )

    targets = [
        "https://stock.gift/list",
        "https://histock.tw/stock/gift.aspx"
    ]

    for url in targets:
        try:
            print(f"正在嘗試抓取全台紀念品清單: {url}")
            res = scraper.get(url, timeout=20)
            res.encoding = "utf-8"

            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                rows = soup.find_all("tr")

                for row in rows:
                    cols = [td.text.strip() for td in row.find_all(["td", "th"])]
                    if len(cols) >= 4:
                        code = cols[0]
                        # 檢查是否為 4 位數股票代碼
                        if re.match(r"^\d{4}$", code):
                            name = cols[1] if len(cols) > 1 else ""
                            price_str = re.sub(r"[^\d.]", "", cols[2]) if len(cols) > 2 else "0"
                            price = float(price_str) if price_str else 0.0
                            gift = cols[3] if len(cols) > 3 else ""
                            last_buy = cols[4] if len(cols) > 4 else "依公告"
                            cond = cols[5] if len(cols) > 5 else "完成電子投票即可"

                            # 過濾掉「無紀念品」或「尚無」的項目，只保留確認可領的股票
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

                # 若成功抓取到大量資料，跳出循環
                if len(raw_data) > 20:
                    print(f"成功抓取全台發放紀念品股票，共 {len(raw_data)} 檔！")
                    break

        except Exception as e:
            print(f"抓取 {url} 失敗: {e}")

    # 去重（依據股票代碼）
    unique_data = {}
    for item in raw_data:
        unique_data[item["股票代碼"]] = item
    final_list = list(unique_data.values())

    # 寫入 json
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(final_list, f, ensure_ascii=False, indent=4)

    print(f"最終寫入 data.json 的紀念品股票數量：{len(final_list)} 檔")

if __name__ == "__main__":
    fetch_data()
