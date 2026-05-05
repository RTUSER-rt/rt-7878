import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup

class RTJobEngine:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.all_jobs = []
        # 這裡是你可以手動維護的評論庫，會根據醫院名稱自動匹配
        self.reviews = {
            "台中榮民總醫院": "醫中制度紮實，適合新鮮人練功，薪資級別透明。",
            "台北榮民總醫院": "案源豐富，重症訓練紮實，適合應屆生挑戰。",
            "亞東紀念醫院": "單位氣氛友善，前輩很願意帶領新人。"
        }

    def fetch_104(self):
        url = "https://www.104.com.tw/jobs/search/list?ro=0&kw=呼吸治療師&mode=s"
        try:
            res = requests.get(url, headers={**self.headers, 'Referer': 'https://www.104.com.tw/'})
            items = res.json().get('data', {}).get('list', [])
            for i in items:
                name = i['custName']
                self.all_jobs.append({
                    "hospital": name,
                    "city": i['jobAddrNoDesc'][:3],
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
                    self.all_jobs.append({
                        "hospital": name,
                        "city": card.select_one('.job_item_detail span').text.strip()[:3] if card.select_one('.job_item_detail span') else "未標註",
                        "location": card.select_one('.job_item_detail span').text.strip() if card.select_one('.job_item_detail span') else "未標註",
                        "salary": card.select_one('.job_item_features span').text.strip() if card.select_one('.job_item_features span') else "面議",
                        "link": h_element['href'] if h_element['href'].startswith('http') else f"https:{h_element['href']}",
                        "source": "1111",
                        "review": self.reviews.get(name, "目前暫無學長姐評論！")
                    })
        except: pass

    def run(self):
        self.fetch_104()
        self.fetch_1111()
        output = {"last_update": datetime.now().strftime("%Y-%m-%d %H:%M"), "jobs": self.all_jobs}
        with open('jobs.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    RTJobEngine().run()
