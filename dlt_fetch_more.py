# -*- coding: utf-8 -*-
"""
超级大乐透历史数据获取 - 多页面抓取
获取最近 100 期、500 期的完整数据
"""

import requests
import json
import re
from typing import List, Dict, Optional
from datetime import datetime
import csv
import time


class DLT500Scraper:
    """大乐透爬虫类 - 500 彩票网多页面"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        })

    def get_history_page(self, page: int = 1) -> Optional[str]:
        """获取指定页面的历史数据"""
        # 500 彩票网支持分页，每页 30 期
        if page == 1:
            url = "http://datachart.500.com/dlt/history/history.shtml"
        else:
            url = f"http://datachart.500.com/dlt/history/history_{page}.shtml"

        try:
            response = self.session.get(url, timeout=15)
            response.encoding = 'gb2312'
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print(f"第{page}页请求失败：{e}")
        return None

    def parse_lottery_data(self, html: str) -> List[Dict]:
        """解析单页开奖数据"""
        results = []

        if not html:
            return results

        tbody_match = re.search(r'<tbody id="tdata">(.*?)</tbody>', html, re.DOTALL)
        if not tbody_match:
            return results

        tbody_html = tbody_match.group(1)
        tr_pattern = r'<tr class="t_tr1">(.*?)</tr>'
        td_pattern = r'<td[^>]*>([^<]*)</td>'

        matches = re.findall(tr_pattern, tbody_html, re.DOTALL)

        for match in matches:
            cells_raw = re.findall(td_pattern, match)
            cells = [c.strip() for c in cells_raw if c.strip()]

            if len(cells) >= 15:
                if len(cells[0]) >= 5 and cells[0].isdigit():
                    issue_num = cells[0]
                    base_idx = 1
                else:
                    issue_num = cells[1]
                    base_idx = 2

                if issue_num.isdigit() and len(issue_num) >= 5:
                    lottery_info = {
                        'issue_number': issue_num,
                        'draw_date': cells[base_idx + 13].strip(),
                        'front_balls': [cells[base_idx + i].strip() for i in range(5)],
                        'back_balls': [cells[base_idx + 5 + i].strip() for i in range(2)],
                        'pool_amount': cells[base_idx + 7].strip().replace(',', ''),
                        'first_prize_count': cells[base_idx + 8].strip(),
                        'first_prize_amount': cells[base_idx + 9].strip().replace(',', ''),
                        'second_prize_count': cells[base_idx + 10].strip(),
                        'second_prize_amount': cells[base_idx + 11].strip().replace(',', ''),
                        'total_bet': cells[base_idx + 12].strip().replace(',', ''),
                    }
                    results.append(lottery_info)

        return results

    def get_multi_page_history(self, target_count: int = 100) -> List[Dict]:
        """获取多期历史数据"""
        all_lotteries = []
        page = 1
        per_page = 30
        max_pages = (target_count // per_page) + 2

        print(f"目标获取 {target_count} 期数据，预计需要 {max_pages} 页...")

        for page in range(1, max_pages + 1):
            print(f"正在获取第 {page} 页...")
            html = self.get_history_page(page)

            if html:
                lotteries = self.parse_lottery_data(html)
                if lotteries:
                    all_lotteries.extend(lotteries)
                    print(f"  获取到 {len(lotteries)} 条数据，累计 {len(all_lotteries)} 条")

                    if len(all_lotteries) >= target_count:
                        print(f"已达到目标期数 {target_count}")
                        break
                else:
                    print(f"  第 {page} 页无数据")
                    break
            else:
                print(f"  第 {page} 页获取失败")
                break

            time.sleep(0.5)

        # 截取目标数量
        all_lotteries = all_lotteries[:target_count]
        all_lotteries.sort(key=lambda x: x['issue_number'], reverse=True)

        return all_lotteries


def main():
    print("=" * 70)
    print("超级大乐透历史数据获取 - 多页面")
    print("=" * 70)

    scraper = DLT500Scraper()

    # 获取 100 期
    print("\n【1】获取最近 100 期数据...\n")
    lotteries_100 = scraper.get_multi_page_history(100)
    print(f"成功获取 100 期数据：{lotteries_100[-1]['issue_number']} ~ {lotteries_100[0]['issue_number']}")

    # 保存 100 期
    with open('dlt_100.json', 'w', encoding='utf-8') as f:
        json.dump(lotteries_100, f, ensure_ascii=False, indent=2)
    print("已保存到 dlt_100.json\n")

    # 等待
    time.sleep(1)

    # 获取 500 期
    print("\n【2】获取最近 500 期数据（需要更多时间）...\n")
    lotteries_500 = scraper.get_multi_page_history(500)
    print(f"成功获取 500 期数据：{lotteries_500[-1]['issue_number']} ~ {lotteries_500[0]['issue_number']}")

    # 保存 500 期
    with open('dlt_500.json', 'w', encoding='utf-8') as f:
        json.dump(lotteries_500, f, ensure_ascii=False, indent=2)
    print("已保存到 dlt_500.json\n")

    # 生成 CSV
    for data, name in [(lotteries_100, 'dlt_100.csv'), (lotteries_500, 'dlt_500.csv')]:
        with open(name, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['期号', '开奖日期', '前区 1', '前区 2', '前区 3', '前区 4', '前区 5',
                           '后区 1', '后区 2', '一等奖注数', '一等奖奖金', '奖池金额'])
            for item in data:
                writer.writerow([
                    item['issue_number'],
                    item['draw_date'],
                    item['front_balls'][0], item['front_balls'][1],
                    item['front_balls'][2], item['front_balls'][3],
                    item['front_balls'][4],
                    item['back_balls'][0], item['back_balls'][1],
                    item['first_prize_count'],
                    item['first_prize_amount'],
                    item['pool_amount']
                ])

    print(f"\n所有数据已保存!")
    print(f"  - dlt_100.json ({len(lotteries_100)}期)")
    print(f"  - dlt_500.json ({len(lotteries_500)}期)")


if __name__ == "__main__":
    main()
