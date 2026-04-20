# -*- coding: utf-8 -*-
"""
超级大乐透开奖信息获取 - 500 彩票网 (最终修复版)
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

        # 查找 tbody#tdata 中的数据
        tbody_match = re.search(r'<tbody id="tdata">(.*?)</tbody>', html, re.DOTALL)
        if not tbody_match:
            print("未找到 tdata 表格")
            return results

        tbody_html = tbody_match.group(1)

        # 匹配每一行 - tr class="t_tr1"
        tr_pattern = r'<tr class="t_tr1">(.*?)</tr>'

        # 匹配所有 td，包括不同 class 的
        # 注意：有些 td 是注释掉的<!--<td>2</td>-->，需要过滤
        td_pattern = r'<td[^>]*>([^<]*)</td>'

        matches = re.findall(tr_pattern, tbody_html, re.DOTALL)

        print(f"找到 {len(matches)} 条数据记录")

        for idx, match in enumerate(matches):
            # 提取该行所有 td 的内容
            cells_raw = re.findall(td_pattern, match)

            # 过滤掉空内容和注释标记
            cells = [c.strip() for c in cells_raw if c.strip()]

            # 数据结构应该是 16 列（第一个是注释中的序号）：
            # 0: 序号 (注释中的 2), 1: 期号，2-6: 前区，7-8: 后区，9: 奖池，10: 一等奖注数，11: 一等奖奖金
            # 12: 二等奖注数，13: 二等奖奖金，14: 总投注额，15: 开奖日期

            if len(cells) >= 15:
                try:
                    # 期号在 cells[0] 或 cells[1]，取决于是否有注释序号
                    # 如果 cells[0] 是 5 位数字，则是期号；否则 cells[1] 是期号
                    if len(cells[0]) >= 5 and cells[0].isdigit():
                        issue_num = cells[0].strip()
                        base_idx = 1
                    else:
                        issue_num = cells[1].strip()
                        base_idx = 2

                    # 验证期号是否合法（5 位数字）
                    if issue_num and issue_num.isdigit() and len(issue_num) >= 5:
                        lottery_info = {
                            'issue_number': issue_num,  # 期号
                            'front_balls': [cells[base_idx + i].strip() for i in range(5)],  # 前区 5 个球
                            'back_balls': [cells[base_idx + 5 + i].strip() for i in range(2)],  # 后区 2 个球
                            'pool_amount': cells[base_idx + 7].strip().replace(',', ''),  # 奖池奖金
                            'first_prize_count': cells[base_idx + 8].strip(),  # 一等奖注数
                            'first_prize_amount': cells[base_idx + 9].strip().replace(',', ''),  # 一等奖奖金
                            'second_prize_count': cells[base_idx + 10].strip(),  # 二等奖注数
                            'second_prize_amount': cells[base_idx + 11].strip().replace(',', ''),  # 二等奖奖金
                            'total_bet': cells[base_idx + 12].strip().replace(',', ''),  # 总投注额
                            'draw_date': cells[base_idx + 13].strip(),  # 开奖日期
                        }
                        results.append(lottery_info)
                except Exception as e:
                    print(f"解析第 {idx+1} 条数据失败：{e}")
                    print(f"  cells: {cells}")
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
            return f"{value / 10000:.0f}万"
        else:
            return f"{value:.0f}"
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
        print("=" * 130)
        print(f"{'期号':<10} {'开奖日期':<12} {'前区号码':<20} {'后区号码':<10} {'一等奖注数':<8} {'单注奖金':<12} {'奖池金额':<15}")
        print("=" * 130)

        for i, item in enumerate(lotteries[:10]):
            front = ' '.join(item['front_balls'])
            back = ' '.join(item['back_balls'])
            first_prize_bonus = format_currency(item['first_prize_amount'])
            pool = format_currency(item['pool_amount'])

            print(f"{item['issue_number']:<10} {item['draw_date']:<12} {front:<20} {back:<10} {item['first_prize_count']:<8} {first_prize_bonus:<12} {pool:<15}")

        print("=" * 130)

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
            print(f"  中奖号码：前区 {' '.join(item['front_balls'])} | 后区 {' '.join(item['back_balls'])}")
            print(f"  一等奖：{item['first_prize_count']} 注，单注奖金 {format_currency(item['first_prize_amount'])} 元")
            print(f"  二等奖：{item['second_prize_count']} 注，单注奖金 {format_currency(item['second_prize_amount'])} 元")
            print(f"  奖池金额：{format_currency(item['pool_amount'])} 元")
            print(f"  总投注额：{format_currency(item['total_bet'])} 元")


if __name__ == "__main__":
    main()
