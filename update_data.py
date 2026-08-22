import json
import re
from datetime import datetime, timezone, timedelta

def main():
    # 這裡未來可以串接真實的免費金融 API，目前先建立核心的防詐騙過濾邏輯與資料結構
    
    # 1. 每日金句庫
    quotes = [{"text": "投資最重要的事，就是先確保不賠錢。", "author": "華倫·巴菲特"}]
    
    # 2. 總經重大事件 (模擬抓取過濾後的全球高影響力數據)
    finance_events = [
        {"title": "美國 CPI 消費者物價指數", "date": "2026-08-10", "impact": "高", "market": "全球"},
        {"title": "台灣央行理監事會", "date": "2026-09-19", "impact": "高", "market": "台股"}
    ]
    
    # 3. 台灣理財活動 (包含未過濾的原始資料)
    raw_activities = [
        {"title": "ETF 投資入門講座", "city": "台北", "price": "免費", "time": "8/26 19:00", "organizer": "證券公會"},
        {"title": "無腦保證獲利！快加LINE領飆股", "city": "線上", "price": "免費", "time": "8/27 20:00", "organizer": "飆股大師"}
    ]
    
    # --- 核心誠意機制：防詐騙過濾器 ---
    blacklist = r"保證獲利|飆股|加LINE|帶單|內線|財富自由密碼"
    clean_activities = []
    blocked_count = 0
    
    for act in raw_activities:
        content = f"{act['title']} {act['organizer']}"
        # 如果沒有命中黑名單，才加入乾淨的資料庫
        if not re.search(blacklist, content, re.IGNORECASE):
            clean_activities.append(act)
        else:
            blocked_count += 1

    # 4. 組合最終要傳給 App 的資料，並加上台灣時間的更新標記
    tz = timezone(timedelta(hours=8))
    final_data = {
        "quotes": quotes,
        "financeEvents": finance_events,
        "activities": clean_activities,
        "lastUpdated": datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    }

    # 5. 自動生成 data.json 檔案供 App 讀取
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
        
    print(f"資料更新完成！成功攔截 {blocked_count} 筆詐騙活動，已生成 data.json")

if __name__ == "__main__":
    main()
