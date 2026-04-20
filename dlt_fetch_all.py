# -*- coding: utf-8 -*-
"""
超级大乐透历史数据获取 - 新版 URL
"""

import requests
import json
import re
from typing import List, Dict
import time


class DLTScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        })

    def get_all_history(self) -> List[Dict]:
        """获取所有历史数据 - 单个页面包含所有数据"""
        # 尝试获取包含全部数据的页面
        urls = [
            "http://datachart.500.com/dlt/history/history.shtml",  # 默认
            "http://datachart.500.com/dlt/history/newinc/history.php",  # PHP 版本
        ]

        for url in urls:
            try:
                print(f"尝试：{url}")
                response = self.session.get(url, timeout=15)
                response.encoding = 'gb2312'
                if response.status_code == 200 and len(response.text) > 50000:
                    return self._parse(response.text)
            except Exception as e:
                print(f"失败：{e}")
            time.sleep(1)

        return []

    def _parse(self, html: str) -> List[Dict]:
        results = []
        tbody_match = re.search(r'<tbody id="tdata">(.*?)</tbody>', html, re.DOTALL)
        if not tbody_match:
            return results

        tr_pattern = r'<tr class="t_tr1">(.*?)</tr>'
        td_pattern = r'<td[^>]*>([^<]*)</td>'
        matches = re.findall(tr_pattern, tbody_match.group(1), re.DOTALL)

        for match in matches:
            cells = [c.strip() for c in re.findall(td_pattern, match) if c.strip()]
            if len(cells) >= 15:
                idx = 0 if len(cells[0]) >= 5 and cells[0].isdigit() else 1
                issue = cells[idx]
                if issue.isdigit() and len(issue) >= 5:
                    results.append({
                        'issue_number': issue,
                        'draw_date': cells[idx + 13],
                        'front_balls': cells[idx:idx+5],
                        'back_balls': cells[idx+5:idx+7],
                        'pool_amount': cells[idx + 7].replace(',', ''),
                        'first_prize_count': cells[idx + 8],
                        'first_prize_amount': cells[idx + 9].replace(',', ''),
                    })

        results.sort(key=lambda x: x['issue_number'], reverse=True)
        return results


def fetch_from_api():
    """尝试从 API 获取"""
    # 一些公开的彩票 API
    apis = [
        "https://api.apihubs.com/lottery/dlt.php?size=500",
    ]

    for api in apis:
        try:
            print(f"尝试 API: {api}")
            resp = requests.get(api, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                print(f"成功：{len(data)}条")
                return data
        except:
            pass
    return None


def main():
    print("=" * 60)
    print("获取大乐透历史数据")
    print("=" * 60)

    scraper = DLTScraper()
    data = scraper.get_all_history()

    if data:
        print(f"\n成功获取 {len(data)} 期数据")
        print(f"范围：{data[-1]['issue_number']} ~ {data[0]['issue_number']}")

        # 保存全部
        with open('dlt_all.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # 生成 100 期和 500 期
        for count, fname in [(100, 'dlt_100.json'), (500, 'dlt_500.json')]:
            subset = data[:count] if len(data) >= count else data
            with open(fname, 'w', encoding='utf-8') as f:
                json.dump(subset, f, ensure_ascii=False, indent=2)
            print(f"已保存 {len(subset)} 期到 {fname}")
    else:
        print("未能获取数据")


if __name__ == "__main__":
    main()
