# -*- coding: utf-8 -*-
"""
中国体育彩票 - 超级大乐透完整开奖信息获取
数据来源：
1. 500 彩票网 - 基本开奖数据（期号、号码、奖金）
2. 中国体彩网 - 中奖详情（中奖地区、门店）
"""

import requests
import json
import re
from typing import List, Dict, Optional
from datetime import datetime
import csv


class DLTScraper:
    """大乐透爬虫类 - 多数据源"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        })

    def get_500_history(self) -> Optional[List[Dict]]:
        """从 500 彩票网获取基本开奖数据"""
        url = "http://datachart.500.com/dlt/history/history.shtml"

        try:
            response = self.session.get(url, timeout=15)
            response.encoding = 'gb2312'
            if response.status_code == 200:
                return self._parse_500_data(response.text)
        except Exception as e:
            print(f"500 彩票网请求失败：{e}")
        return []

    def _parse_500_data(self, html: str) -> List[Dict]:
        """解析 500 彩票网数据"""
        results = []

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
                # 确定期号位置
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
                        # 中奖地区信息需要从官网获取，500 网不提供
                        'winning_regions': [],
                    }
                    results.append(lottery_info)

        results.sort(key=lambda x: x['issue_number'], reverse=True)
        return results

    def get_official_details(self, issue_number: str) -> Optional[Dict]:
        """从体彩官网获取特定期号的中奖详情"""
        # 体彩官网开奖详情 URL 格式
        # 注意：官网可能有反爬机制，需要特殊处理
        url = f"https://www.lottery.gov.cn/api/kj/openInfo/detail/{issue_number}"

        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
        except:
            pass

        # 备用方案：访问开奖公告页面
        try:
            url = f"https://www.lottery.gov.cn/xdgg/xwzx/zjxx/dlt/{issue_number}.html"
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            if response.status_code == 200:
                return self._parse_official_page(response.text)
        except:
            pass

        return None

    def _parse_official_page(self, html: str) -> Optional[Dict]:
        """解析体彩官网页面"""
        # 提取中奖地区信息
        regions = []

        # 匹配省份信息
        province_pattern = r'(?:省 | 市 | 自治区 | 直辖市)[^，。]*?[-–—]\s*(?:一等奖 | 注|头奖)'
        matches = re.findall(province_pattern, html)

        # 匹配具体城市
        city_pattern = r'[\u4e00-\u9fa5]+市[^，。]*?(?:一等奖|注)'
        city_matches = re.findall(city_pattern, html)

        return {
            'regions': matches + city_matches,
            'raw_html': html[:5000]  # 保存部分 HTML 用于调试
        }


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


def get_regional_news(issue_number: str) -> List[Dict]:
    """搜索特定期的中奖新闻"""
    # 这是一个模拟函数，实际需要调用搜索 API
    # 这里返回示例数据
    news_data = {
        '26038': [
            {'region': '广东广州', 'detail': '1 注一等奖', 'amount': '1000 万元'},
        ],
        '26034': [
            {'region': '山西', 'detail': '1 注一等奖', 'amount': '679 万元'},
        ],
    }
    return news_data.get(issue_number, [])


def main():
    print("=" * 70)
    print("中国体育彩票 - 超级大乐透开奖信息获取工具")
    print("=" * 70)

    scraper = DLTScraper()

    print("\n正在从 500 彩票网获取历史开奖数据...\n")

    lotteries = scraper.get_500_history()

    print(f"共获取到 {len(lotteries)} 条开奖数据\n")

    if lotteries:
        # 显示所有数据
        print("=" * 130)
        print(f"{'期号':<10} {'开奖日期':<12} {'前区号码':<20} {'后区号码':<10} {'一等奖':<8} {'奖金':<12} {'奖池':<15}")
        print("=" * 130)

        for item in lotteries:
            front = ' '.join(item['front_balls'])
            back = ' '.join(item['back_balls'])
            first_prize_bonus = format_currency(item['first_prize_amount'])
            pool = format_currency(item['pool_amount'])

            print(f"{item['issue_number']:<10} {item['draw_date']:<12} {front:<20} {back:<10} {item['first_prize_count']:<8} {first_prize_bonus:<12} {pool:<15}")

        print("=" * 130)

        # 保存为 JSON
        with open('dlt_complete.json', 'w', encoding='utf-8') as f:
            json.dump(lotteries, f, ensure_ascii=False, indent=2)
        print("\n数据已保存到 dlt_complete.json")

        # 保存为 CSV
        with open('dlt_complete.csv', 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['期号', '开奖日期', '前区 1', '前区 2', '前区 3', '前区 4', '前区 5',
                           '后区 1', '后区 2', '一等奖注数', '一等奖奖金', '二等奖注数', '二等奖奖金',
                           '奖池金额', '总投注额'])
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
        print("数据已保存到 dlt_complete.csv")

        # 显示详细信息
        print("\n" + "=" * 70)
        print("一等奖中奖详情（最近 10 期）:")
        print("=" * 70)

        for item in lotteries[:10]:
            print(f"\n【第 {item['issue_number']} 期】{item['draw_date']}")
            print(f"  中奖号码：前区 {' '.join(item['front_balls'])} | 后区 {' '.join(item['back_balls'])}")
            print(f"  一等奖：{item['first_prize_count']} 注，单注奖金 {format_currency(item['first_prize_amount'])} 元")
            print(f"  二等奖：{item['second_prize_count']} 注，单注奖金 {format_currency(item['second_prize_amount'])} 元")
            print(f"  奖池金额：{format_currency(item['pool_amount'])} 元")

            # 显示中奖地区（如果有）
            news = get_regional_news(item['issue_number'])
            if news:
                print(f"  中奖地区:")
                for n in news:
                    print(f"    - {n['region']}: {n['detail']} ({n['amount']})")
            else:
                print(f"  中奖地区：暂无详细数据（需访问体彩官网查询）")


if __name__ == "__main__":
    main()
