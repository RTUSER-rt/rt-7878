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

    def fetch_104(self):
        """抓取 104 呼吸治療師職缺"""
        print("正在從 104 獲取職缺...")
        url = "https://www.104.com.tw/jobs/search/list?ro=0&kw=呼吸治療師&mode=s"
        try:
            # 104 需要帶 Referer 才能正確獲取 JSON
            res = requests.get(url, headers={**self.headers, 'Referer': 'https://www.104.com.tw/'})
            data = res.json().get('data', {}).get('list', [])
            for item in data:
                self.all_jobs.append({
                    "hospital": item['custName'],
                    "city": item['jobAddrNoDesc'][:3],
                    "location": item['jobAddrNoDesc'],
                    "salary": item['salaryDesc'],
                    "link": f"https:{item['link']['job']}",
                    "source": "104"
                })
        except Exception as e:
            print(f"104 抓取失敗: {e}")

    def fetch_1111(self):
        """抓取 1111 呼吸治療師職缺"""
        print("正在從 1111 獲取職缺...")
        # 1111 的搜尋連結
        url = "https://www.1111.com.tw/search/job?ks=呼吸治療師"
        try:
            res = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            # 1111 的職缺卡片通常在特定的 class 中
            cards = soup.select('.job_item') 
            for card in cards:
                title = card.select_one('.job_item_info h3')
                hospital = card.select_one('.job_item_info a')
                salary = card.select_one('.job_item_features span') # 薪資通常在標籤內
                addr = card.select_one('.job_item_detail span') # 地址
                link = card.select_one('.job_item_info a')['href']

                if hospital:
                    self.all_jobs.append({
                        "hospital": hospital.text.strip(),
                        "city": addr.text.strip()[:3] if addr else "未註明",
                        "location": addr.text.strip() if addr else "未註明",
                        "salary": salary.text.strip() if salary else "面議",
                        "link": link if link.startswith('http') else f"https:{link}",
                        "source": "1111"
                    })
        except Exception as e:
            print(f"1111 抓取失敗: {e}")

    def run(self):
        self.fetch_104()
        self.fetch_1111()
        
        # 存檔
        output = {
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "jobs": self.all_jobs
        }
        with open('jobs.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=4)
        print(f"更新完成！共抓取 {len(self.all_jobs)} 筆職缺。")

if __name__ == "__main__":
    engine = RTJobEngine()
    engine.run()
