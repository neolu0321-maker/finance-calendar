import json
import os
import requests
import calendar
from google import genai
from datetime import datetime, timezone, timedelta

def get_recurring_events(year, month):
    events = []
    c = calendar.monthcalendar(year, month)
    
    wednesdays = [week[calendar.WEDNESDAY] for week in c if week[calendar.WEDNESDAY] != 0]
    tx_date = f"{year}-{month:02d}-{wednesdays[2]:02d}"
    events.append({"date": tx_date, "title": "台指期與選擇權結算", "category": "期貨"})
    
    fridays = [week[calendar.FRIDAY] for week in c if week[calendar.FRIDAY] != 0]
    nfp_date = f"{year}-{month:02d}-{fridays[0]:02d}"
    events.append({"date": nfp_date, "title": "美國非農就業報告 (NFP)", "category": "總經"})
    
    return events

def get_ai_data(today_str, year, month):
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        api_key = api_key.strip()
        
    if not api_key:
        return {"date": today_str, "quote": "本金安全第一。", "author": "巴菲特", "explanation": "無API", "reminder": "請檢查金鑰"}, []
    
    # 使用 Google 全新升級的 SDK 寫法
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    今天是 {today_str}。請扮演精通華爾街歷史與總體經濟的財經大師。
    執行兩個任務：
    1. 從巴菲特、蒙格、李佛摩、科斯托蘭尼、約翰·柏格中隨機挑選一位，提供一句經典名言與白話解讀。
    2. 推算 {year}年{month}月 的「美國 CPI 消費者物價指數」預計公布日(通常在每月10-15日之間)。
    
    ⚠️ 絕對禁止：不要輸出「非農就業」或其他未要求的事件！
    
    嚴格輸出為以下 JSON 格式，不要加 ```json 標籤，直接輸出大括號開頭：
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
        # 指定使用最新的 gemini-2.5-flash 模型
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        text = response.text.strip()
        
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        
        data = json.loads(text)
        wisdom = data.get("wisdom", {})
        wisdom["date"] = today_str
        
        clean_events = []
        for evt in data.get("dynamic_events", []):
            if "非農" not in evt.get("title", ""):
                clean_events.append(evt)
                
        return wisdom, clean_events
    except Exception as e:
        print(f"AI 生成失敗: {e}")
        return {"date": today_str, "quote": "等待 AI 靈感中...", "author": "系統", "explanation": "大腦正在升級", "reminder": "請稍後重試"}, []

def fetch_activities(today_str):
    api_urls = {
        "音樂戲劇": "[https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindTypeJ&category=1](https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindTypeJ&category=1)",
        "展覽": "[https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindTypeJ&category=6](https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindTypeJ&category=6)",
        "講座": "[https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindTypeJ&category=7](https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindTypeJ&category=7)",
        "親子與綜合": "[https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindTypeJ&category=15](https://cloud.culture.tw/frontsite/trans/SearchShowAction.do?method=doFindTypeJ&category=15)"
    }
    finance_keywords = ['理財', '投資', '財經', '股票', '股市', 'ETF', '金融', '經濟', '資產配置', '退休規劃', '基金']
    activities = []
    for base_cat, url in api_urls.items():
        try:
            response = requests.get(url, timeout=15)
            for item in response.json()[:100]:
                event_url = item.get('sourceWebPromote', '').strip()
                if not event_url: continue
                title = item.get('title') or '未命名活動'
                show_info = item.get('showInfo', [{}])[0] if item.get('showInfo') else {}
                location = show_info.get('location') or '地點未提供'
                location_name = show_info.get('locationName') or '未提供場地'
                start_time = show_info.get('time', today_str)[:10].replace("/", "-")
                end_time = show_info.get('endTime', start_time)[:10].replace("/", "-")
                if end_time < today_str: continue
                city = location[:3] if len(location) >= 3 else "線上"
                is_finance = any(kw in title for kw in finance_keywords)
                if is_finance:
                    venue_type = "財經讀書會" if any(k in title for k in ['讀書', '導讀', '沙龍']) else "投資理財課程"
                elif any(kw in location_name for kw in ['美術館', '藝廊', '畫廊', '藝術中心']): venue_type = "美術館展覽"
                elif any(kw in location_name for kw in ['圖書館', '閱覽室']): venue_type = "圖書館講座"
                elif any(kw in location_name for kw in ['博物館', '紀念館', '科博館', '科工館', '天文館', '史前']): venue_type = "博物館活動"
                else: venue_type = "文化中心活動"
                activities.append({
                    "event_date": start_time,
                    "end_date": end_time,
                    "title": title,
                    "category": venue_type,
                    "venue": location_name,
                    "city": city,
                    "summary": f"文化部開放資料 ({base_cat})",
                    "url": event_url,
                    "organizer": item.get('showUnit', '主辦單位未知')
                })
        except Exception:
            pass
    activities.sort(key=lambda x: x["event_date"], reverse=True)
    return activities[:150]

def main():
    tz = timezone(timedelta(hours=8))
    today = datetime.now(tz)
    today_str = today.strftime("%Y-%m-%d")
    math_events = get_recurring_events(today.year, today.month)
    next_month = today.month + 1 if today.month < 12 else 1
    next_year = today.year if today.month < 12 else today.year + 1
    math_events.extend(get_recurring_events(next_year, next_month))
    wisdom_data, ai_events = get_ai_data(today_str, today.year, today.month)
    all_finance_events = math_events + ai_events
    all_finance_events.sort(key=lambda x: x["date"])
    real_activities = fetch_activities(today_str)
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
