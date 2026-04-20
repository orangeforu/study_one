# -*- coding: utf-8 -*-
"""
中国体育彩票 - 超级大乐透开奖信息爬虫
获取大乐透每期一等奖中奖信息
"""

import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Optional

# 请求头配置
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'https://www.lottery.gov.cn/',
}

# 体彩网开奖数据接口（通过开发者工具分析得出）
# 注意：这些接口可能会变化，需要定期更新
API_URLS = {
    'history': 'https://www.lottery.gov.cn/api/kj/openInfo/dlt/history',  # 历史开奖
    'detail': 'https://www.lottery.gov.cn/api/kj/openInfo/dlt/detail',    # 开奖详情
}

class DLTScraper:
    """大乐透开奖信息爬虫"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.base_url = "https://www.lottery.gov.cn"

    def get_history_lottery(self, page: int = 1, page_size: int = 30) -> Optional[Dict]:
        """获取历史开奖数据"""
        url = f"{self.base_url}/api/kj/openInfo/history/dlt/{page}/{page_size}"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败：{e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON 解析失败：{e}")
            return None

    def get_lottery_detail(self, issue_number: str) -> Optional[Dict]:
        """获取特定期号的开奖详情（包含一等奖中奖信息）"""
        url = f"{self.base_url}/api/kj/openInfo/detail/{issue_number}"

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"请求失败：{e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON 解析失败：{e}")
            return None

    def parse_history_data(self, data: Dict) -> List[Dict]:
        """解析历史开奖数据"""
        results = []

        if not data or 'result' not in data:
            return results

        lottery_list = data.get('result', [])

        for item in lottery_list:
            lottery_info = {
                'issue_number': item.get('issueNumber', ''),  # 期号
                'draw_date': item.get('openDate', ''),  # 开奖日期
                'front_numbers': item.get('winningNumbers', '').split()[:5] if item.get('winningNumbers') else [],  # 前区号码
                'back_numbers': item.get('winningNumbers', '').split()[5:] if item.get('winningNumbers') else [],  # 后区号码
                'front_numbers_str': ' '.join(item.get('winningNumbers', '').split()[:5]) if item.get('winningNumbers') else '',
                'back_numbers_str': ' '.join(item.get('winningNumbers', '').split()[5:]) if item.get('winningNumbers') else '',
            }
            results.append(lottery_info)

        return results

    def get_all_history(self, max_pages: int = 10) -> List[Dict]:
        """获取所有历史开奖数据（多页）"""
        all_lotteries = []

        for page in range(1, max_pages + 1):
            print(f"正在获取第 {page} 页数据...")
            data = self.get_history_lottery(page=page, page_size=30)

            if data and data.get('result'):
                lotteries = self.parse_history_data(data)
                all_lotteries.extend(lotteries)
                print(f"  获取到 {len(lotteries)} 条数据")

                # 如果没有更多数据，停止
                if len(lotteries) < 30:
                    break
            else:
                print(f"  第 {page} 页无数据")
                break

            time.sleep(0.5)  # 避免请求过快

        return all_lotteries


def main():
    """主函数"""
    print("=" * 60)
    print("中国体育彩票 - 超级大乐透开奖信息获取工具")
    print("=" * 60)

    scraper = DLTScraper()

    # 获取最近 5 期的开奖数据
    print("\n正在获取大乐透历史开奖数据...\n")

    # 尝试获取第 1 页数据
    data = scraper.get_history_lottery(page=1, page_size=10)

    if data:
        print("API 返回的原始数据:")
        print(json.dumps(data, indent=2, ensure_ascii=False))

        # 解析数据
        lotteries = scraper.parse_history_data(data)

        print("\n\n解析后的开奖信息:")
        print("-" * 80)

        for lottery in lotteries:
            print(f"期号：{lottery['issue_number']}")
            print(f"开奖日期：{lottery['draw_date']}")
            print(f"前区号码：{lottery['front_numbers_str']}")
            print(f"后区号码：{lottery['back_numbers_str']}")
            print("-" * 80)
    else:
        print("无法获取数据，请检查网络连接或 API 地址")

        # 备用方案：尝试直接访问页面
        print("\n尝试备用方案...")
        try:
            response = scraper.session.get("https://www.lottery.gov.cn/kj/kjlb.html?dlt", timeout=10)
            print(f"页面状态码：{response.status_code}")
            print(f"页面内容长度：{len(response.text)}")
        except Exception as e:
            print(f"备用方案也失败：{e}")


if __name__ == "__main__":
    main()
