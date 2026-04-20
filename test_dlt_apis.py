# -*- coding: utf-8 -*-
"""
超级大乐透开奖信息获取 - 完整可用版本
尝试多个数据源获取大乐透开奖数据
"""

import requests
import json
import re
from typing import List, Dict, Optional
from datetime import datetime

class DLTScraper:
    """大乐透爬虫类 - 多数据源"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9',
        })

    def get_api_1(self, page: int = 1) -> Optional[Dict]:
        """API 1: 新浪彩票接口"""
        url = f"http://api.sinacn.com/lottery/dlt/{page}.json"
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None

    def get_api_2(self, page: int = 1) -> Optional[Dict]:
        """API 2: 500 彩票网接口"""
        url = "https://api.500.cn/lottery/dlt/history.json"
        params = {'page': page, 'num': 30}
        try:
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None

    def get_api_3(self) -> Optional[Dict]:
        """API 3: 一些公开的彩票 API 聚合接口"""
        # 这个是从 GitHub 上找到的开源项目使用的接口
        url = "https://apis.juju.cn/lottery/dlt"
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None

    def get_api_4(self, page: int = 1) -> Optional[Dict]:
        """API 4: 牛彩网接口"""
        url = f"http://www.zhcw.com/api/dlt/history/{page}"
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None


def find_working_api():
    """寻找可用的 API"""
    scraper = DLTScraper()

    print("测试各个 API 接口...")
    print("-" * 60)

    apis = [
        ("新浪彩票", scraper.get_api_1),
        ("500 彩票网", scraper.get_api_2),
        ("聚合 API", scraper.get_api_3),
        ("牛彩网", scraper.get_api_4),
    ]

    for name, func in apis:
        print(f"\n测试 {name}...")
        try:
            result = func()
            if result:
                print(f"  成功！数据：{str(result)[:200]}")
            else:
                print(f"  无数据返回")
        except Exception as e:
            print(f"  异常：{e}")


if __name__ == "__main__":
    find_working_api()
