# -*- coding: utf-8 -*-
"""
超级大乐透开奖信息获取 - 500 彩票网版本 (修复版)
数据来源：500 彩票网历史开奖数据
获取：中奖日期、中奖期数、中奖号码、一等奖注数、一等奖奖金
"""

import requests
import json
import re
from typing import List, Dict, Optional
from datetime import datetime
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
        url = "http://datachart.500.com/dlt/history/history.shtml"

        try:
            response = self.session.get(url, timeout=15)
            response.encoding = 'gb2312'
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print(f"请求失败：{e}")
        return None

    def parse_lottery_data(self, html: str) -> List[Dict]:
        """解析开奖数据 - 使用正则表达式"""
        results = []

        if not html:
            return results

        # 查找 #tdata 表格中的数据行
        # 匹配格式：<tr class="t_tr1">...<td>期号</td><td>球 1</td>...</tr>
        tr_pattern = r'<tr class="t_tr1">(.*?)</tr>'
        td_pattern = r'<td[^>]*>([^<]*)</td>'

        matches = re.findall(tr_pattern, html, re.DOTALL)

        print(f"找到 {len(matches)} 条数据记录")

        for match in matches:
            cells = re.findall(td_pattern, match)

            if len(cells) >= 16:  # 确保有足够的数据列
                try:
                    issue_num = cells[0].strip()
                    # 期号应该是数字，如 26041
                    if issue_num and issue_num.isdigit():
                        lottery_info = {
                            'issue_number': issue_num,  # 期号
                            'front_balls': [cells[i].strip() for i in range(1, 6)],  # 前区 5 个球
                            'back_balls': [cells[i].strip() for i in range(6, 8)],  # 后区 2 个球
                            'pool_amount': cells[8].strip().replace(',', ''),  # 奖池奖金
                            'first_prize_count': cells[9].strip(),  # 一等奖注数
                            'first_prize_amount': cells[10].strip().replace(',', ''),  # 一等奖奖金
                            'second_prize_count': cells[11].strip(),  # 二等奖注数
                            'second_prize_amount': cells[12].strip().replace(',', ''),  # 二等奖奖金
                            'total_bet': cells[14].strip().replace(',', ''),  # 总投注额
                            'draw_date': cells[15].strip(),  # 开奖日期
                        }
                        results.append(lottery_info)
                except Exception as e:
                    print(f"解析数据失败：{e}")
                    continue

        # 按期号排序（最新的在前）
        results.sort(key=lambda x: x['issue_number'], reverse=True)

        return results

    def get_all_history(self) -> List[Dict]:
        """获取所有历史数据"""
        html = self.get_history_page()
        if html:
            print(f"获取到 HTML，长度：{len(html)}")
            return self.parse_lottery_data(html)
        return []


def format_currency(amount: str) -> str:
    """格式化金额显示"""
    try:
        value = float(amount)
        if value >= 100000000:
            return f"{value / 100000000:.2f}亿"
        elif value >= 10000:
            return f"{value / 10000:.2f}万"
        else:
            return f"{value:.2f}"
    except:
        return amount


def main():
    print("=" * 60)
    print("超级大乐透开奖信息获取 - 500 彩票网")
    print("数据来源：500 彩票网 (http://datachart.500.com/)")
    print("=" * 60)

    scraper = DLT500Scraper()

    print("\n正在获取历史开奖数据...\n")

    lotteries = scraper.get_all_history()

    print(f"\n共获取到 {len(lotteries)} 条开奖数据\n")

    if lotteries:
        # 显示前 10 条数据
        print("=" * 100)
        print(f"{'期号':<8} {'开奖日期':<12} {'前区号码':<20} {'后区号码':<10} {'一等奖注数':<10} {'单注奖金':<12} {'奖池金额':<15}")
        print("=" * 100)

        for i, item in enumerate(lotteries[:10]):
            front = ' '.join(item['front_balls'])
            back = ' '.join(item['back_balls'])
            first_prize_bonus = format_currency(item['first_prize_amount'])
            pool = format_currency(item['pool_amount'])

            print(f"{item['issue_number']:<8} {item['draw_date']:<12} {front:<20} {back:<10} {item['first_prize_count']:<10} {first_prize_bonus:<12} {pool:<15}")

        print("=" * 100)

        # 保存为 JSON
        with open('dlt_history.json', 'w', encoding='utf-8') as f:
            json.dump(lotteries, f, ensure_ascii=False, indent=2)
        print("\n数据已保存到 dlt_history.json")

        # 保存为 CSV
        with open('dlt_history.csv', 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['期号', '开奖日期', '前区号码 1', '前区号码 2', '前区号码 3', '前区号码 4', '前区号码 5',
                           '后区号码 1', '后区号码 2', '一等奖注数', '一等奖奖金 (元)', '二等奖注数', '二等奖奖金 (元)',
                           '奖池金额 (元)', '总投注额 (元)'])
            for item in lotteries:
                writer.writerow([
                    item['issue_number'],
                    item['draw_date'],
                    item['front_balls'][0],
                    item['front_balls'][1],
                    item['front_balls'][2],
                    item['front_balls'][3],
                    item['front_balls'][4],
                    item['back_balls'][0],
                    item['back_balls'][1],
                    item['first_prize_count'],
                    item['first_prize_amount'],
                    item['second_prize_count'],
                    item['second_prize_amount'],
                    item['pool_amount'],
                    item['total_bet']
                ])
        print("数据已保存到 dlt_history.csv")

        # 显示一等奖详细信息
        print("\n" + "=" * 100)
        print("一等奖中奖详情（最近 10 期）:")
        print("=" * 100)
        for i, item in enumerate(lotteries[:10]):
            print(f"\n第 {item['issue_number']} 期 ({item['draw_date']}):")
            print(f"  中奖号码：前区 {' '.join(item['front_balls'])} 后区 {' '.join(item['back_balls'])}")
            print(f"  一等奖：{item['first_prize_count']} 注，单注奖金 {format_currency(item['first_prize_amount'])} 元")
            print(f"  奖池金额：{format_currency(item['pool_amount'])} 元")


if __name__ == "__main__":
    main()
