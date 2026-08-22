import json
import os
import requests
import google.generativeai as genai
from datetime import datetime, timezone, timedelta

def get_ai_quote(today_str):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return {
            "date": today_str,
            "quote": "投資的第一條準則就是保證本金安全。",
            "author": "華倫·巴菲特",
            "explanation": "無法連線至 AI 大腦，請檢查 GitHub Secrets 是否正確設定 GEMINI_API_KEY。",
            "reminder": "這是一條系統預設金句。"
        }
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
    
    # 稍微調整 Prompt，讓輸出的 key 對齊 Grok 要的格式
    prompt = """
    請扮演精通華爾街歷史的財經大師。從巴菲特、蒙格、李佛摩、科斯托蘭尼、約翰·柏格中隨機挑選一位，提供一句經典名言。
    並針對投資新手寫出「白話解讀」與「誠懇提醒」。
    嚴格輸出為以下 JSON 格式：
    {"quote": "大師名言", "author": "作者", "explanation": "白話解讀", "reminder": "誠懇提醒"}
    """
    try:
        response = model.generate_content(prompt)
        data = json.loads(response.text)
        data["date"] = today_str # 補上 Grok 要求的日期
        return data
    except Exception as e:
        print(f"AI 生成失敗: {e}")
        return {"date": today_str, "quote": "AI 連線中...", "author": "系統", "explanation": "網路稍有延遲", "reminder": "請稍後重試"}

def fetch_activities(today_str):
    # 抓取文化部最新講座
    url = "https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindTypeJ&category=7"
    activities = []
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        for item in data:
            show_info = item.get('showInfo', [{}])[0]
            location = show_info.get('location', '地點未提供')
            location_name = show_info.get('locationName', '未提供場地')
            
            # 處理日期格式 (Grok 需要 YYYY-MM-DD)
            start_time = show_info.get('time', today_str)[:10].replace("/", "-")
            end_time = show_info.get('endTime', start_time)[:10].replace("/", "-")
            
            # 簡單判斷縣市
            city = "線上"
            if len(location) >= 3:
                city = location[:3]

            activities.append({
                "event_date": start_time,
                "end_date": end_time,
                "title": item.get('title', '未命名活動'),
                "category": "講座",
                "venue": location_name,
                "city": city,
                "summary": "文化部開放資料自動抓取",
                "url": item.get('sourceWebPromote', ''),
                "organizer": item.get('showUnit', '主辦單位未知')
                # 注意：這裡故意不寫 "auto": "publish"，讓 Grok 把活動送進你的審核後台！
            })
            if len(activities) >= 15: 
                break
        return activities
    except Exception as e:
        print(f"爬取活動失敗: {e}")
        return []

def main():
    tz = timezone(timedelta(hours=8))
    today = datetime.now(tz)
    today_str = today.strftime("%Y-%m-%d")

    selected_quote = get_ai_quote(today_str)
    real_activities = fetch_activities(today_str)
    
    # 加入一筆詐騙測試資料 (Grok 的 fraud.ts 應該要在前端自動把它擋掉！)
    real_activities.append({
        "event_date": today_str,
        "end_date": today_str,
        "title": "無腦保證獲利！快加LINE領飆股",
        "category": "理財",
        "venue": "線上群組",
        "city": "線上",
        "summary": "詐騙測試，不該出現在前台",
        "url": "",
        "organizer": "不明"
    })

    # 重大金融事件
    finance_events = [
        {"date": "2026-08-10", "title": "美國 CPI 消費者物價指數", "category": "CPI"},
        {"date": "2026-08-19", "title": "台指期結算", "category": "期貨"},
        {"date": "2026-09-18", "title": "Fed 利率決議", "category": "Fed"}
    ]
    
    # 完美組合 Grok 指定的 JSON 結構
    final_data = {
        "generated_at": today.isoformat(),
        "source": "github-actions",
        "wisdom": [selected_quote],
        "activities": real_activities,
        "events": finance_events
    }

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
