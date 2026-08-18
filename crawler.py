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
            # 讀取網頁中所有表格
            dfs = pd.read_html(io.StringIO(res.text))
            
            target_df = None
            for df in dfs:
                # 若標頭為多重層級 (MultiIndex)，將其展平為單一層級字串
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = ['_'.join([str(c) for c in col if 'Unnamed' not in str(c)]).strip() for col in df.columns]
                else:
                    df.columns = [str(c).strip() for c in df.columns]

                # 尋找含有股票代號欄位的表格
                cols_str = "".join(df.columns)
                if "代號" in cols_str or "代碼" in cols_str or "名稱" in cols_str:
                    target_df = df
                    break

            if target_df is not None:
                # 自動對應欄位名稱
                code_col = [c for c in target_df.columns if "代號" in c or "代碼" in c][0]
                name_col = [c for c in target_df.columns if "名稱" in c][0]
                gift_col = [c for c in target_df.columns if "紀念品" in c][0]
                
                price_cols = [c for c in target_df.columns if "股價" in c or "價格" in c]
                price_col = price_cols[0] if price_cols else None
                
                last_buy_cols = [c for c in target_df.columns if "最後" in c or "買進" in c]
                last_buy_col = last_buy_cols[0] if last_buy_cols else None
                
                cond_cols = [c for c in target_df.columns if "條件" in c or "零股" in c or "發放" in c]
                cond_col = cond_cols[0] if cond_cols else None

                for _, row in target_df.iterrows():
                    code = str(row[code_col]).strip()
                    # 確保股票代號為 4 位數字
                    if re.match(r"^\d{4}$", code):
                        name = str(row[name_col]).strip()
                        gift = str(row[gift_col]).strip()
                        
                        price = 0.0
                        if price_col and pd.notna(row[price_col]):
                            p_str = re.sub(r"[^\d.]", "", str(row[price_col]))
                            price = float(p_str) if p_str else 0.0

                        last_buy = str(row[last_buy_col]).strip() if last_buy_col and pd.notna(row[last_buy_col]) else "依公告處理"
                        cond = str(row[cond_col]).strip() if cond_col and pd.notna(row[cond_col]) else "完成電子投票即可"

                        # 過濾無紀念品/無效資料
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
