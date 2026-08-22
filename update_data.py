import json
import os
import requests
import calendar
import google.generativeai as genai
from datetime import datetime, timezone, timedelta

# --- 1. 精準數學演算法：計算固定週期的金融事件 ---
def get_recurring_events(year, month):
    events = []
    c = calendar.monthcalendar(year, month)
    
    # 台灣台指期結算日 (每個月第三個星期三)
    wednesdays = [week[calendar.WEDNESDAY] for week in c if week[calendar.WEDNESDAY] != 0]
    tx_date = f"{year}-{month:02d}-{wednesdays[2]:02d}"
    events.append({"date": tx_date, "title": "台指期與選擇權結算", "category": "期貨"})
    
    # 美國非農就業報告 (每個月第一個星期五)
    fridays = [week[calendar.FRIDAY] for week in c if week[calendar.FRIDAY] != 0]
    nfp_date = f"{year}-{month:02d}-{fridays[0]:02d}"
    events.append({"date": nfp_date, "title": "美國非農就業報告 (NFP)", "category": "總經"})
    
    return events

# --- 2. AI 雙引擎：生成大師金句與總經事件預測 ---
def get_ai_data(today_str, year, month):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("未設定 API Key，使用備用資料。")
        return {"date": today_str, "quote": "本金安全第一。", "author": "巴菲特", "explanation": "無API", "reminder": "無API"}, []
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
    
    prompt = f"""
    今天是 {today_str}。請扮演精通華爾街歷史與總體經濟的財經大師。
    執行兩個任務：
    1. 從巴菲特、蒙格、李佛摩、科斯托蘭尼、約翰·柏格中隨機挑選一位，提供一句經典名言與白話解讀。
    2. 推算 {year}年{month}月 的「美國 CPI 消費者物價指數」預計公布日(通常在每月10-15日之間)，以及是否遇到 Fed 利率決議。
    
    嚴格輸出為以下 JSON 格式：
    {{
      "wisdom": {{
        "quote": "大師名言",
        "author": "作者",
        "explanation": "白話解讀",
        "reminder": "誠懇提醒"
      }},
      "dynamic_events": [
        {{"date": "YYYY-MM-DD", "title": "美國 CPI 發布 (預估)", "category": "CPI"}}
      ]
    }}
    """
    try:
        response = model.generate_content(prompt)
        data = json.loads(response.text)
        wisdom = data.get("wisdom", {})
        wisdom["date"] = today_str # 確保有日期欄位
        return wisdom, data.get("dynamic_events", [])
    except Exception as e:
        print(f"AI 生成失敗: {e}")
        return {"date": today_str, "quote": "AI 連線中...", "author": "系統", "explanation": "網路稍有延遲", "reminder": "請稍後重試"}, []

# --- 3. 全域智慧檢索與財經雷達 (已加入嚴密防呆機制) ---
def fetch_activities(today_str):
    api_urls = {
        "音樂戲劇": "https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindTypeJ&category=1",
        "展覽": "https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindTypeJ&category=6",
        "講座": "https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindTypeJ&category=7",
        "親子與綜合": "https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindTypeJ&category=15"
    }
    
    finance_keywords = ['理財', '投資', '財經', '股票', '股市', 'ETF', '金融', '經濟', '資產配置', '退休規劃', '基金']
    activities = []
    
    for base_cat, url in api_urls.items():
        try:
            response = requests.get(url, timeout=15)
            for item in response.json()[:100]:
                title = item.get('title') or '未命名活動'
                show_info = item.get('showInfo', [{}])[0] if item.get('showInfo') else {}
                location = show_info.get('location') or '地點未提供'
                location_name = show_info.get('locationName') or '未提供場地'
                
                start_time = show_info.get('time', today_str)[:10].replace("/", "-")
                end_time = show_info.get('endTime', start_time)[:10].replace("/", "-")
                if end_time < today_str: continue # 剔除過期活動

                city = location[:3] if len(location) >= 3 else "線上"
                
                # 智慧標籤：精準對齊 Grok 的前端分類按鈕
                is_finance = any(kw in title for kw in finance_keywords)
                if is_finance:
                    venue_type = "財經讀書會" if any(k in title for k in ['讀書', '導讀', '沙龍']) else "投資理財課程"
                elif any(kw in location_name for kw in ['美術館', '藝廊', '畫廊', '藝術中心']):
                    venue_type = "美術館展覽"
                elif any(kw in location_name for kw in ['圖書館', '閱覽室']):
                    venue_type = "圖書館講座"
                elif any(kw in location_name for kw in ['博物館', '紀念館', '科博館', '科工館', '天文館', '史前']):
                    venue_type = "博物館活動"
                else:
                    # 凡是衛武營、駁二、演藝廳或是其他無特定分類的藝文活動，統整至文化中心活動
                    venue_type = "文化中心活動"

                activities.append({
                    "event_date": start_time,
                    "end_date": end_time,
                    "title": title,
                    "category": venue_type,
                    "venue": location_name,
                    "city": city,
                    "summary": f"文化部開放資料 ({base_cat})",
                    "url": item.get('sourceWebPromote', '') or "",
                    "organizer": item.get('showUnit', '主辦單位未知')
                })
        except Exception as e:
            print(f"爬取 {base_cat} 發生異常: {e}")
            
    activities.sort(key=lambda x: x["event_date"], reverse=True)
    return activities[:200] # 放寬到 200 筆，確保涵蓋全台

# --- 4. 主程式：打包所有資料並輸出 Grok 規格 ---
def main():
    tz = timezone(timedelta(hours=8))
    today = datetime.now(tz)
    today_str = today.strftime("%Y-%m-%d")
    
    # 獲取本月與下個月的精準演算法日期
    math_events = get_recurring_events(today.year, today.month)
    next_month = today.month + 1 if today.month < 12 else 1
    next_year = today.year if today.month < 12 else today.year + 1
    math_events.extend(get_recurring_events(next_year, next_month))

    # 獲取 AI 金句與 AI 預估總經事件
    wisdom_data, ai_events = get_ai_data(today_str, today.year, today.month)
    
    # 組合所有金融事件並排序
    all_finance_events = math_events + ai_events
    all_finance_events.sort(key=lambda x: x["date"])

    # 獲取爬蟲活動資料
    real_activities = fetch_activities(today_str)
    
    # 💡 保留詐騙測試資料，用來驗證 Grok 前端防詐機制是否正常運作！
    real_activities.append({
        "event_date": today_str,
        "end_date": today_str,
        "title": "無腦保證獲利！快加LINE私訊匯款領飆股",
        "category": "投資理財課程",
        "venue": "線上假群組",
        "city": "線上",
        "summary": "這是詐騙測試，如果防詐機制有效，這筆活動將被攔截！",
        "url": "",
        "organizer": "不明"
    })
    
    # 組合最終 JSON
    final_data = {
        "generated_at": today.isoformat(),
        "source": "github-actions",
        "wisdom": [wisdom_data],
        "activities": real_activities,
        "events": all_finance_events
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
