# -*- coding: utf-8 -*-
"""
超级大乐透开奖信息获取 - 使用第三方 API
"""

import requests
import json
from typing import List, Dict, Optional

# 第三方免费 API（来源：RollToolsApi）
# GitHub: https://github.com/zenodo/rolltoolsapi
API_URL = "https://api.zenodo.app/lottery"

# 其他可用的 API
ALT_APIS = {
    # 聚合数据（需要注册获取 key）
    'juhe': 'https://apis.juhe.cn/lottery/query',
    # 阿里云市场
    'aliyun': 'https://ali-market.logician.cn/api/lottery',
}


def get_dlt_history_api1(page: int = 1) -> Optional[Dict]:
    """使用 Zenodo API 获取大乐透数据"""
    url = f"https://api.zenodo.app/lottery/dlt/{page}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Zenodo API 请求失败：{e}")
        return None


def get_dlt_history_zhcw(page: int = 1) -> Optional[Dict]:
    """使用中彩网 API 获取大乐透数据"""
    # 中彩网 API 接口
    url = f"https://www.zhcw.com/open/index/index/json"

    params = {
        'type': 'dlt',  # 大乐透
        'page': page,
        'pageSize': 30,
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
        'Referer': 'https://www.zhcw.com/kjxx/dlt/',
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"中彩网 API 请求失败：{e}")
        return None


def get_dlt_from_kaijiangnet() -> Optional[List[Dict]]:
    """从开奖网获取大乐透数据"""
    url = "http://kaijiang.zhcw.com/zhcw/html/dlt/1.htm"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        return response.text
    except Exception as e:
        print(f"开奖网请求失败：{e}")
        return None


def test_all_apis():
    """测试所有可用的 API"""
    print("=" * 60)
    print("测试大乐透数据 API 接口")
    print("=" * 60)

    # 测试 Zenodo API
    print("\n[1] 测试 Zenodo API...")
    result = get_dlt_history_api1(page=1)
    if result:
        print(f"  成功！返回数据：{json.dumps(result, indent=2, ensure_ascii=False)[:500]}...")
    else:
        print("  失败")

    # 测试中彩网 API
    print("\n[2] 测试中彩网 API...")
    result = get_dlt_history_zhcw(page=1)
    if result:
        print(f"  成功！返回数据：{json.dumps(result, indent=2, ensure_ascii=False)[:500]}...")
    else:
        print("  失败")

    # 测试开奖网
    print("\n[3] 测试开奖网...")
    result = get_dlt_from_kaijiangnet()
    if result:
        print(f"  成功！页面内容长度：{len(result)}")
        print(f"  内容预览：{result[:500]}...")
    else:
        print("  失败")


if __name__ == "__main__":
    test_all_apis()
