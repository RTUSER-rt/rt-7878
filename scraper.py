import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup

class RTGlobalScraper:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        self.all_jobs = []

    def fetch_104(self):
        url = "https://www.104.com.tw/jobs/search/list?ro=0&kw=呼吸治療師&mode=s"
        try:
            res = requests.get(url, headers={**self.headers, 'Referer': 'https://www.104.com.tw/'})
            items = res.json().get('data', {}).get('list', [])
            for i in items:
                self.all_jobs.append({
                    "hospital": i['custName'],
                    "city": i['jobAddrNoDesc'][:3],
                    "salary": i['salaryDesc'],
                    "link": f"https:{i['link']['job']}",
                    "source": "104"
                })
        except: pass

    def run(self):
        self.fetch_104()
        # 這裡可擴充 1111 抓取邏輯
        output = {"last_update": datetime.now().strftime("%Y-%m-%d %H:%M"), "jobs": self.all_jobs}
        with open('jobs.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    RTGlobalScraper().run()
