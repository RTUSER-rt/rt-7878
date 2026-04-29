import json
from datetime import datetime

def run_scraper():
    # 這是目前的模擬資料，之後我們可以改寫成自動抓取 104
    data = {
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "jobs": [
            {
                "hospital": "台中榮民總醫院",
                "title": "契約呼吸治療師 (RT)",
                "location": "台中市西屯區",
                "salary": "23-37 級薪資制",
                "link": "https://www.vghtc.gov.tw/UnitPage/UnitArcticle?WebMenuID=2d99905d-e85d-4f81-9b19-c09a3653f538"
            },
            {
                "hospital": "台北榮民總醫院",
                "title": "呼吸治療師",
                "location": "台北市北投區",
                "salary": "面議",
                "link": "https://www.vghtpe.gov.tw"
            }
        ]
    }
    
    with open('jobs.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("職缺資料更新成功！")

if __name__ == "__main__":
    run_scraper()
