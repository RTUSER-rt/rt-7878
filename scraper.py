import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup

class RTJobEngine:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.seen_hospitals = set() # 用於去重
        self.all_jobs = []

    def fetch_104(self):
        print("正在抓取 104 職缺...")
        url = "https://www.104.com.tw/jobs/search/list?ro=0&kw=呼吸治療師&mode=s"
        try:
            res = requests.get(url, headers={**self.headers, 'Referer': 'https://www.104.com.tw/'})
            data = res.json().get('data', {}).get('list', [])
            for item in data:
                h_name = item['custName']
                if h_name not in self.seen_hospitals:
                    self.all_jobs.append({
                        "hospital": h_name,
                        "city": item['jobAddrNoDesc'][:3],
                        "location": item['jobAddrNoDesc'],
                        "salary": self.format_salary(item['salaryDesc']),
                        "link": f"https:{item['link']['job']}",
                        "source": "104"
                    })
                    self.seen_hospitals.add(h_name)
        except Exception as e: print(f"104 錯誤: {e}")

    def fetch_1111(self):
        print("正在抓取 1111 職缺...")
        url = "https://www.1111.com.tw/search/job?ks=呼吸治療師"
        try:
            res = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            # 根據 1111 結構抓取 (需配合 BeautifulSoup 4)
            for card in soup.select('.job_item'):
                h_name = card.select_one('.job_item_info a').text.strip()
                if h_name not in self.seen_hospitals:
                    salary = card.select_one('.job_item_features span').text.strip() if card.select_one('.job_item_features span') else "面議"
                    addr = card.select_one('.job_item_detail span').text.strip() if card.select_one('.job_item_detail span') else "未標註"
                    link = card.select_one('.job_item_info a')['href']
                    self.all_jobs.append({
                        "hospital": h_name,
                        "city": addr[:3],
                        "location": addr,
                        "salary": self.format_salary(salary),
                        "link": link if link.startswith('http') else f"https:{link}",
                        "source": "1111"
                    })
                    self.seen_hospitals.add(h_name)
        except Exception as e: print(f"1111 錯誤: {e}")

    def format_salary(self, salary_str):
        # 應屆生專屬邏輯：將「面議」優化
        if "面議" in salary_str:
            return "40,000+ (應屆建議詢問)"
        return salary_str

    def run(self):
        self.fetch_104()
        self.fetch_1111()
        output = {
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "jobs": self.all_jobs
        }
        with open('jobs.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    engine = RTJobEngine()
    engine.run()
