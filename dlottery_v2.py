# -*- coding: utf-8 -*-
"""
超级大乐透开奖信息获取 - 完整版
数据来源：中国体育彩票官方网站
"""

import requests
import json
import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

class DLTScraper:
    """大乐透爬虫类"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })

    def get_zhcw_history(self, page: int = 1) -> Optional[List[Dict]]:
        """从中彩网获取大乐透历史开奖数据"""
        # 中彩网 API
        url = "https://www.zhcw.com/api/lottery/dlt/history"

        params = {
            'page': str(page),
            'pageSize': '30',
        }

        try:
            response = self.session.get(url, params=params, timeout=10)
            print(f"状态码：{response.status_code}")
            print(f"返回内容：{response.text[:500]}")
            return response.json()
        except Exception as e:
            print(f"请求失败：{e}")
            return None

    def get_51240_api(self) -> Optional[List[Dict]]:
        """从 51240.com 获取大乐透数据"""
        url = "https://www.51240.com/api/dlt/history"

        try:
            response = self.session.get(url, timeout=10)
            print(f"51240 状态码：{response.status_code}")
            return response.json()
        except Exception as e:
            print(f"51240 请求失败：{e}")
            return None

    def get_lottery_data(self) -> Optional[str]:
        """获取彩票数据 HTML"""
        # 尝试多个数据源
        urls = [
            "https://m.zhcw.com/kjxx/dlt/",  # 中彩网手机版
            "https://www.cwl.gov.cn/kjxx/dlt/",  # 中国福利彩票网（如果有）
        ]

        for url in urls:
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    print(f"成功获取：{url}")
                    return response.text
            except Exception as e:
                print(f"失败 {url}: {e}")

        return None


def test_connections():
    """测试各种连接方式"""
    scraper = DLTScraper()

    print("=" * 60)
    print("测试大乐透数据源")
    print("=" * 60)

    # 测试 1: 中彩网 API
    print("\n[1] 测试中彩网 API...")
    result = scraper.get_zhcw_history(page=1)

    # 测试 2: 51240
    print("\n[2] 测试 51240.com...")
    result = scraper.get_51240_api()

    # 测试 3: 直接获取 HTML
    print("\n[3] 测试直接获取 HTML...")
    html = scraper.get_lottery_data()
    if html:
        print(f"HTML 长度：{len(html)}")
        print(html[:1000])


if __name__ == "__main__":
    test_connections()
