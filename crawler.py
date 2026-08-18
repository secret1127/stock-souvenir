import cloudscraper
import pandas as pd
import json
import re
import io

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
            # 使用 pandas 直接把網頁的所有 table 讀進來
            dfs = pd.read_html(io.StringIO(res.text))
            
            # 找到包含股票代號的那個表格
            target_df = None
            for df in dfs:
                df.columns = [str(c).strip() for c in df.columns]
                # 印出欄位名稱方便偵測 Log
                print("找到表格欄位:", list(df.columns))
                if any("代號" in str(c) or "代碼" in str(c) for c in df.columns):
                    target_df = df
                    break

            if target_df is not None:
                # 重新整理欄位名稱
                code_col = [c for c in target_df.columns if "代號" in c or "代碼" in c][0]
                name_col = [c for c in target_df.columns if "名稱" in c][0]
                gift_col = [c for c in target_df.columns if "紀念品" in c][0]
                price_col = [c for c in target_df.columns if "股價" in c or "價格" in c]
                price_col = price_col[0] if price_col else None
                last_buy_col = [c for c in target_df.columns if "最後" in c or "買進" in c]
                last_buy_col = last_buy_col[0] if last_buy_col else None
                cond_col = [c for c in target_df.columns if "條件" in c or "零股" in c or "發放" in c]
                cond_col = cond_col[0] if cond_col else None

                for _, row in target_df.iterrows():
                    code = str(row[code_col]).strip()
                    # 確保股票代號是 4 位數字
                    if re.match(r"^\d{4}$", code):
                        name = str(row[name_col]).strip()
                        gift = str(row[gift_col]).strip()
                        
                        # 股價處理
                        price = 0.0
                        if price_col and pd.notna(row[price_col]):
                            p_str = re.sub(r"[^\d.]", "", str(row[price_col]))
                            price = float(p_str) if p_str else 0.0

                        last_buy = str(row[last_buy_col]).strip() if last_buy_col and pd.notna(row[last_buy_col]) else "依公告處理"
                        cond = str(row[cond_col]).strip() if cond_col and pd.notna(row[cond_col]) else "完成電子投票即可"

                        # 過濾無紀念品之無效資料
                        if gift and gift != "nan" and not any(k in gift for k in ["無紀念品", "不發放", "無", "尚未公佈", "尚無"]):
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
