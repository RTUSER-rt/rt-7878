import requests
import json
import time
import random
from datetime import datetime
from bs4 import BeautifulSoup

class RTJobScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        self.all_jobs = []

    def clean_city(self, city_str):
        if not city_str:
            return '未註明'
        city = city_str.replace('臺', '台').strip()
        return city[:3] if len(city) >= 3 else city

    def fetch_104(self):
        try:
            # 先訪問搜尋頁面以取得 cookies
            search_url = 'https://www.104.com.tw/jobs/search/?keyword=%E5%91%BC%E5%90%B8%E6%B2%BB%E7%99%82%E5%B8%AB'
            self.session.headers.update({'Referer': 'https://www.104.com.tw/'})
            self.session.get(search_url, timeout=15)
            time.sleep(random.uniform(1, 2))

            # 呼叫 API
            api_url = 'https://www.104.com.tw/jobs/search/list'
            params = {
                'ro': '0',
                'kwop': '7',
                'keyword': '呼吸治療師',
                'order': '15',
                'asc': '0',
                'page': '1',
                'mode': 's',
                'jobsource': '2018indexpoc'
            }
            self.session.headers.update({
                'Referer': search_url,
                'Accept': 'application/json, text/plain, */*',
            })
            res = self.session.get(api_url, params=params, timeout=20)
            print(f'[104] HTTP status: {res.status_code}')
            print(f'[104] Content-Type: {res.headers.get("Content-Type", "")}' )
            print(f'[104] Response preview: {res.text[:200]}')

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
                    'title': job_name,
                    'hospital': cust_name,
                    'city': self.clean_city(addr),
                    'location': addr,
                    'salary': salary,
                    'link': job_link,
                    'source': '104',
                    'date': datetime.now().strftime('%Y-%m-%d')
                })
            print(f'[104] 共抓到 {len(items)} 筆職缺')
        except Exception as e:
            print(f'[104] 抓取失敗: {e}')

    def fetch_1111(self):
        try:
            url = 'https://www.1111.com.tw/search/job'
            params = {'ks': '呼吸治療師', 'order': '1', 'page': '1'}
            headers_1111 = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-TW,zh;q=0.9',
                'Referer': 'https://www.1111.com.tw/',
            }
            res = requests.get(url, params=params, headers=headers_1111, timeout=20)
            print(f'[1111] HTTP status: {res.status_code}')
            soup = BeautifulSoup(res.text, 'html.parser')

            # 嘗試多種選擇器 (1111 的 HTML 結構)
            selectors = [
                'article.job-list-item',
                '.job-list-item',
                '.b-block--sticktop',
                '[data-job-no]',
                '.job_item',
                'li.job-item',
            ]
            cards = []
            for sel in selectors:
                cards = soup.select(sel)
                if cards:
                    print(f'[1111] 使用選擇器: {sel}, 找到 {len(cards)} 個')
                    break

            if not cards:
                print(f'[1111] 所有選擇器均無結果，HTML 長度: {len(res.text)}')
                # 顯示部分 HTML 以便偵錯
                print(f'[1111] HTML 前 500 字元: {res.text[:500]}')

            count = 0
            for card in cards:
                title_el = (card.select_one('h2 a') or
                            card.select_one('.job-title a') or
                            card.select_one('a.job-name') or
                            card.select_one('a[title]') or
                            card.select_one('a'))
                if not title_el:
                    continue
                title = title_el.get_text(strip=True)
                link = title_el.get('href', '')
                if link and not link.startswith('http'):
                    link = 'https://www.1111.com.tw' + link

                company_el = (card.select_one('.company-name') or
                              card.select_one('h3') or
                              card.select_one('.b-tag--quaternary'))
                company = company_el.get_text(strip=True) if company_el else '未知公司'

                location_el = card.select_one('.job-address')
                location = location_el.get_text(strip=True) if location_el else '全台各地'

                salary_el = card.select_one('.job-salary') or card.select_one('.salary')
                salary = salary_el.get_text(strip=True) if salary_el else '面議'

                self.all_jobs.append({
                    'title': title,
                    'hospital': company,
                    'city': self.clean_city(location),
                    'location': location,
                    'salary': salary,
                    'link': link,
                    'source': '1111',
                    'date': datetime.now().strftime('%Y-%m-%d')
                })
                count += 1
            print(f'[1111] 共抓到 {count} 筆職缺')
        except Exception as e:
            print(f'[1111] 抓取失敗: {e}')

    def run(self):
        print(f'開始抓取職缺... {datetime.now()}')
        self.fetch_104()
        time.sleep(random.uniform(1, 2))
        self.fetch_1111()

        # 去重
        seen = set()
        unique_jobs = []
        for j in self.all_jobs:
            key = f"{j['hospital']}_{j['title']}"
            if key not in seen:
                seen.add(key)
                unique_jobs.append(j)

        # 若新資料為空，保留上次資料
        if not unique_jobs:
            print('警告：本次未抓到任何職缺，保留上次資料')
            try:
                with open('jobs.json', 'r', encoding='utf-8') as f:
                    old_data = json.load(f)
                old_data['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M') + ' (cached)'
                with open('jobs.json', 'w', encoding='utf-8') as f:
                    json.dump(old_data, f, ensure_ascii=False, indent=2)
                print(f'保留舊資料，共 {old_data.get("total", 0)} 筆')
                return
            except Exception as e:
                print(f'讀取舊資料失敗: {e}')

        output = {
            'last_update': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'total': len(unique_jobs),
            'jobs': unique_jobs
        }
        with open('jobs.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f'完成！共 {len(unique_jobs)} 筆職缺已寫入 jobs.json')

if __name__ == '__main__':
    RTJobScraper().run()
