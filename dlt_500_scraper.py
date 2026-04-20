# -*- coding: utf-8 -*-
"""
超级大乐透开奖信息获取 - 500 彩票网版本
数据来源：500 彩票网历史开奖数据
"""

import requests
import json
import re
from typing import List, Dict, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import csv


class DLT500Scraper:
    """大乐透爬虫类 - 500 彩票网"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'http://datachart.500.com/',
        })

    def get_history_page(self) -> Optional[str]:
        """获取历史开奖数据页面"""
        # 500 彩票网大乐透历史数据页面
        url = "http://datachart.500.com/dlt/history/history.shtml"

        try:
            response = self.session.get(url, timeout=15)
            response.encoding = 'gb2312'  # 500 网使用 gb2312 编码
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print(f"请求失败：{e}")
        return None

    def parse_lottery_data(self, html: str) -> List[Dict]:
        """解析开奖数据"""
        results = []

        if not html:
            return results

        # 使用正则表达式提取数据
        # 查找表格中的开奖数据行
        pattern = r'<tr[^>]*class=["\']?tr_max(?:\s+[^\>]*)?["\']?[^>]*>(.*?)</tr>'

        # 更宽松的匹配方式
        row_pattern = r'<td[^>]*>([^<]*)</td>'

        try:
            soup = BeautifulSoup(html, 'html.parser')

            # 查找数据表格
            table = soup.find('table', {'id': 'tdata'})
            if not table:
                # 尝试其他可能的表格
                table = soup.find('table', class_='table_datat')
            if not table:
                tables = soup.find_all('table')
                for t in tables:
                    if 'history' in str(t.get('class', '')) or 'tdata' in str(t.get('id', '')):
                        table = t
                        break

            if table:
                rows = table.find_all('tr')
                print(f"找到 {len(rows)} 行数据")

                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 10:
                        try:
                            issue_num = cells[0].get_text(strip=True)  # 期号
                            if issue_num and issue_num.isdigit() and len(issue_num) >= 5:
                                lottery_info = {
                                    'issue_number': issue_num,
                                    'ball_1': cells[1].get_text(strip=True),
                                    'ball_2': cells[2].get_text(strip=True),
                                    'ball_3': cells[3].get_text(strip=True),
                                    'ball_4': cells[4].get_text(strip=True),
                                    'ball_5': cells[5].get_text(strip=True),
                                    'ball_6': cells[6].get_text(strip=True),
                                    'ball_7': cells[7].get_text(strip=True),
                                    'details': cells[8].get_text(strip=True) if len(cells) > 8 else '',
                                    'raw_cells': [c.get_text(strip=True) for c in cells]
                                }
                                results.append(lottery_info)
                        except Exception as e:
                            print(f"解析行失败：{e}")
        except Exception as e:
            print(f"解析 HTML 失败：{e}")

        return results

    def get_all_history(self) -> List[Dict]:
        """获取所有历史数据"""
        html = self.get_history_page()
        if html:
            print(f"获取到 HTML，长度：{len(html)}")
            # 保存原始 HTML 以便调试
            with open('debug_500.html', 'w', encoding='utf-8') as f:
                f.write(html)
            return self.parse_lottery_data(html)
        return []


def main():
    print("=" * 60)
    print("超级大乐透开奖信息获取 - 500 彩票网")
    print("=" * 60)

    scraper = DLT500Scraper()

    print("\n正在获取历史开奖数据...\n")

    lotteries = scraper.get_all_history()

    print(f"\n共获取到 {len(lotteries)} 条开奖数据\n")

    if lotteries:
        print("=" * 80)
        for i, item in enumerate(lotteries[:5]):  # 只显示前 5 条
            print(f"[{i+1}] 期号：{item['issue_number']}")
            print(f"    号码：{item['ball_1']} {item['ball_2']} {item['ball_3']} {item['ball_4']} {item['ball_5']} | {item['ball_6']} {item['ball_7']}")
            print(f"    原始数据：{item['raw_cells']}")
            print("-" * 80)

        # 保存为 JSON
        with open('dlt_history.json', 'w', encoding='utf-8') as f:
            json.dump(lotteries, f, ensure_ascii=False, indent=2)
        print("\n数据已保存到 dlt_history.json")

        # 保存为 CSV
        with open('dlt_history.csv', 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['期号', '球 1', '球 2', '球 3', '球 4', '球 5', '球 6', '球 7', '详情'])
            for item in lotteries:
                writer.writerow([
                    item['issue_number'],
                    item['ball_1'],
                    item['ball_2'],
                    item['ball_3'],
                    item['ball_4'],
                    item['ball_5'],
                    item['ball_6'],
                    item['ball_7'],
                    item.get('details', '')
                ])
        print("数据已保存到 dlt_history.csv")


if __name__ == "__main__":
    main()
