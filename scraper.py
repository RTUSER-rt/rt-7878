import requests
import json
from datetime import datetime

def fetch_essential_jobs():
    # 搜尋「呼吸治療師」
    url = "https://www.104.com.tw/jobs/search/list?ro=0&kw=呼吸治療師&mode=s"
    headers = {'Referer': 'https://www.104.com.tw/', 'User-Agent': 'Mozilla/5.0'}
    
    clean_jobs = []
    try:
        res = requests.get(url, headers=headers)
        items = res.json().get('data', {}).get('list', [])
        for i in items:
            clean_jobs.append({
                "hospital": i['custName'],
                "location": i['jobAddrNoDesc'], # 例如：台中市西屯區
                "city": i['jobAddrNoDesc'][:3], # 提取「台中市」
                "salary": i['salaryDesc'],      # 例如：月薪 45,000 元以上
                "link": f"https:{i['link']['job']}"
            })
    except:
        pass
    
    output = {
        "last_update": datetime.now().strftime("%Y-%m-%d"),
        "jobs": clean_jobs
    }
    with open('jobs.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    fetch_essential_jobs()
