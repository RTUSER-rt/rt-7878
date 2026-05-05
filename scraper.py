import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup

class RTGlobalScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.all_jobs = []
        # 應屆生評論庫
        self.reviews = {
            "台中榮民總醫院": "台中西屯區指標醫中，教學與薪資級別非常透明穩定。",
            "台北榮民總醫院": "重症訓練首選，對於應屆生打底非常有幫助。",
            "亞東紀念醫院": "單位氣氛友善，重視臨床新進人員教育。"
        }

    def clean_city_name(self, city_str):
        """統一將 臺 轉為 台，並取前兩個字"""
        if not city_str: return "未註明"
        city = city_str.replace('臺', '台')
        return city[:2] # 只取「台中」、「台北」

    def fetch_104(self):
        url = "https://www.104.com.tw/jobs/search/list?ro=0&kw=呼吸治療師&mode=s"
        try:
            res = requests.get(url, headers={**self.headers, 'Referer': 'https://www.104.com.tw/'})
            items = res.json().get('data', {}).get('list', [])
            for i in items:
                name = i['custName']
                self.all_jobs.append({
                    "hospital": name,
                    "city": self.clean_city_name(i['jobAddrNoDesc']),
                    "location": i['jobAddrNoDesc'],
                    "salary": i['salaryDesc'],
                    "link": f"https:{i['link']['job']}",
                    "source": "104",
                    "review": self.reviews.get(name, "目前暫無學長姐評論，歡迎應屆生回報！")
                })
        except: pass

    def fetch_1111(self):
        url = "https://www.1111.com.tw/search/job?ks=呼吸治療師"
        try:
            res = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            cards = soup.select('.job_item') 
            for card in cards:
                h_element = card.select_one('.job_item_info a')
                if h_element:
                    name = h_element.text.strip()
                    addr = card.select_one('.job_item_detail span').text.strip() if card.select_one('.job_item_detail span') else ""
                    self.all_jobs.append({
                        "hospital": name,
                        "city": self.clean_city_name(addr),
                        "location": addr if addr else "全台各地",
                        "salary": card.select_one('.job_item_features span').text.strip() if card.select_one('.job_item_features span') else "面議",
                        "link": h_element['href'] if h_element['href'].startswith('http') else f"https:{h_element['href']}",
                        "source": "1111",
                        "review": self.reviews.get(name, "新進職缺，建議詢問公會學長姐評論！")
                    })
        except: pass

    def run(self):
        self.fetch_104()
        self.fetch_1111()
        # 移除重複資料
        unique_jobs = {f"{j['hospital']}": j for j in self.all_jobs}.values()
        output = {
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "jobs": list(unique_jobs)
        }
        with open('jobs.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    RTGlobalScraper().run()
