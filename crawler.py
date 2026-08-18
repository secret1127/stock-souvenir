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
        print(f"伺服器回應狀態碼: {res.status_code}")
        res.encoding = "utf-8"

        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            tables = soup.find_all("table")
            print(f"頁面中共找到 {len(tables)} 個表格")

            target_table = None
            for table in tables:
                text = table.get_text()
                if "紀念品" in text and ("代號" in text or "代碼" in text):
                    target_table = table
                    break

            if target_table:
                rows = target_table.find_all("tr")
                print(f"目標表格共有 {len(rows)} 行")
                
                header_idx = {}
                for row in rows:
                    th_cols = [th.text.strip() for th in row.find_all(["th", "td"])]
                    if any("紀念品" in c for c in th_cols):
                        for i, col_name in enumerate(th_cols):
                            if "代號" in col_name or "代碼" in col_name:
                                header_idx["code"] = i
                            elif "名稱" in col_name:
                                header_idx["name"] = i
                            elif "紀念品" in col_name:
                                header_idx["gift"] = i
                            elif "股價" in col_name or "價格" in col_name:
                                header_idx["price"] = i
                            elif "最後" in col_name or "買進" in col_name:
                                header_idx["last_buy"] = i
                            elif "條件" in col_name or "零股" in col_name or "發放" in col_name:
                                header_idx["cond"] = i
                        break

                idx_code = header_idx.get("code", 0)
                idx_name = header_idx.get("name", 1)
                idx_price = header_idx.get("price", 2)
                idx_gift = header_idx.get("gift", 3)
                idx_last_buy = header_idx.get("last_buy", 4)
                idx_cond = header_idx.get("cond", 5)

                for row in rows:
                    tds = [td.text.strip() for td in row.find_all("td")]
                    if len(tds) > max(idx_code, idx_name, idx_gift):
                        code = tds[idx_code]
                        if re.match(r"^\d{4}$", code):
                            name = tds[idx_name]
                            gift = tds[idx_gift]

                            price_val = tds[idx_price] if len(tds) > idx_price else "0"
                            p_str = re.sub(r"[^\d.]", "", price_val)
                            price = float(p_str) if p_str else 0.0

                            last_buy = tds[idx_last_buy] if len(tds) > idx_last_buy else "依公告處理"
                            cond = tds[idx_cond] if len(tds) > idx_cond else "完成電子投票即可"

                            if gift and not any(k in gift for k in ["無紀念品", "不發放", "尚未公佈", "尚無"]):
                                raw_data.append({
                                    "股票代碼": code,
                                    "股票名稱": name,
                                    "當前股價": price,
                                    "買1股成本": round(price + 1, 1),
                                    "紀念品": gift,
                                    "最後買進日": last_buy,
                                    "零股條件": cond
                                })
            else:
                print("⚠️ 警告：找不到目標表格，可能被 Cloudflare 攔截或 HTML 結構變更。")
        else:
            print(f"⚠️ 請求失敗，狀態碼非 200: {res.status_code}")

    except Exception as e:
        print(f"❌ 爬取發生例外狀況: {e}")
        import traceback
        traceback.print_exc()

    if len(raw_data) == 0:
        print("⚠️ 未抓取到任何資料，取消寫入，保留原本的 data.json！")
        return

    unique_data = {item["股票代碼"]: item for item in raw_data}
    final_list = list(unique_data.values())

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(final_list, f, ensure_ascii=False, indent=4)

    print(f"✅ 成功寫入 {len(final_list)} 檔紀念品股票至 data.json！")

if __name__ == "__main__":
    fetch_data()
