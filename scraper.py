import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup

class RTJobScraper:
        def __init__(self):
                    self.headers = {
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                                    'Accept-Language': 'zh-TW,zh;q=0.9'
                    }
                    self.all_jobs = []

        def clean_city(self, city_str):
                    if not city_str:
                                    return "未註明"
                                city = city_str.replace('臺', '台').strip()
                    return city[:3] if len(city) >= 3 else city

        def fetch_104(self):
                    """從 104 人力銀行 API 抓取呼吸治療師職缺"""
                    url = "https://www.104.com.tw/jobs/search/list"
                    params = {
                        'ro': '0',
                        'kwop': '7',
                        'keyword': '呼吸治療師',
                        'order': '15',
                        'asc': '0',
                        'page': '1',
                        'mode': 's',
                        'jobsource': 'index_s'
                    }
                    custom_headers = {
                        **self.headers,
                        'Referer': 'https://www.104.com.tw/jobs/search/?keyword=%E5%91%BC%E5%90%B8%E6%B2%BB%E7%99%82%E5%B8%AB'
                    }
                    try:
                                    res = requests.get(url, params=params, headers=custom_headers, timeout=20)
                                    data = res.json()
                                    items = data.get('data', {}).get('list', [])
                                    for i in items:
                                                        job_name = i.get('jobName', '')
                                                        cust_name = i.get('custName', '')
                                                        addr = i.get('jobAddrNoDesc', '')
                                                        salary = i.get('salaryDesc', '面議')
                                                        job_link = i.get('link', {}).get('job', '')
                                                        if job_link and not job_link.startswith('http'):
                                                                                job_link = 'https:' + job_link
                                                                            self.all_jobs.append({
                                                            "title": job_name,
                                                            "hospital": cust_name,
                                                            "city": self.clean_city(addr),
                                                            "location": addr,
                                                            "salary": salary,
                                                            "link": job_link,
                                                            "source": "104",
                                                            "date": datetime.now().strftime("%Y-%m-%d")
                                                        })
                                                    print(f"[104] 共抓到 {len(items)} 筆職缺")
except Exception as e:
            print(f"[104] 抓取失敗: {e}")

    def fetch_1111(self):
                """從 1111 人力銀行抓取呼吸治療師職缺"""
                url = "https://www.1111.com.tw/search/job"
                params = {
                    'ks': '呼吸治療師',
                    'order': '1',
                    'page': '1'
                }
                try:
                                res = requests.get(url, params=params, headers=self.headers, timeout=20)
                                soup = BeautifulSoup(res.text, 'html.parser')

                    # 嘗試多種選擇器
                                cards = soup.select('article.job-list-item') or \
                                        soup.select('.job_item') or \
                                        soup.select('[data-job-no]') or \
                                        soup.select('.b-block--sticktop')

                    count = 0
            for card in cards:
                                # 職稱
                                title_el = card.select_one('h2 a') or card.select_one('.job-title a') or card.select_one('a[title]')
                                if not title_el:
                                                        continue
                                                    title = title_el.get_text(strip=True)
                link = title_el.get('href', '')
                if link and not link.startswith('http'):
                                        link = 'https://www.1111.com.tw' + link

                # 公司名
                company_el = card.select_one('.company-name') or card.select_one('.b-tag--quaternary') or card.select_one('h3')
                company = company_el.get_text(strip=True) if company_el else '未知公司'

                # 地點
                location_el = card.select_one('.job-address') or card.select_one('[data-v-location]')
                location = location_el.get_text(strip=True) if location_el else '全台各地'

                # 薪資
                salary_el = card.select_one('.job-salary') or card.select_one('.salary')
                salary = salary_el.get_text(strip=True) if salary_el else '面議'

                self.all_jobs.append({
                                        "title": title,
                                        "hospital": company,
                                        "city": self.clean_city(location),
                                        "location": location,
                                        "salary": salary,
                                        "link": link,
                                        "source": "1111",
                                        "date": datetime.now().strftime("%Y-%m-%d")
                })
                count += 1
            print(f"[1111] 共抓到 {count} 筆職缺")
except Exception as e:
            print(f"[1111] 抓取失敗: {e}")

    def run(self):
                print(f"開始抓取職缺... {datetime.now()}")
        self.fetch_104()
        self.fetch_1111()

        # 去重（以 hospital + title 為 key）
        seen = set()
        unique_jobs = []
        for j in self.all_jobs:
                        key = f"{j['hospital']}_{j['title']}"
            if key not in seen:
                                seen.add(key)
                unique_jobs.append(j)

        output = {
                        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "total": len(unique_jobs),
                        "jobs": unique_jobs
        }

        with open('jobs.json', 'w', encoding='utf-8') as f:
                        json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"完成！共 {len(unique_jobs)} 筆職缺已寫入 jobs.json")

if __name__ == "__main__":
        RTJobScraper().run()
