# -*- coding: utf-8 -*-
"""
大乐透对比分析：30 期 vs 100 期 vs 500 期
"""

import json
import numpy as np
from collections import Counter
from typing import Dict, List, Tuple


class DLTComparator:
    """大乐透多周期对比分析器"""

    def __init__(self):
        self.data_30 = self._load('dlt_complete.json')[:30]
        self.data_100 = self._load('dlt_100.json')[:100]
        self.data_500 = self._load('dlt_500.json')[:500]

    def _load(self, file: str) -> List[Dict]:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []

    def _extract_balls(self, data: List[Dict]) -> Tuple[np.array, np.array]:
        """提取前后区号码"""
        front = []
        back = []
        for item in data:
            front.append([int(x) for x in item['front_balls']])
            back.append([int(x) for x in item['back_balls']])
        return np.array(front), np.array(back)

    def compare_frequency(self) -> Dict:
        """对比频率分析"""
        results = {}

        for name, data in [('30 期', self.data_30), ('100 期', self.data_100), ('500 期', self.data_500)]:
            if not data:
                continue

            front, back = self._extract_balls(data)
            front_all = front.flatten()
            back_all = back.flatten()

            front_counter = Counter(front_all)
            back_counter = Counter(back_all)

            front_freq = {i: front_counter.get(i, 0) for i in range(1, 36)}
            back_freq = {i: back_counter.get(i, 0) for i in range(1, 13)}

            # 找出 TOP5 热号
            front_top = sorted(front_freq.items(), key=lambda x: x[1], reverse=True)[:5]
            back_top = sorted(back_freq.items(), key=lambda x: x[1], reverse=True)[:3]

            results[name] = {
                'front_top': front_top,
                'back_top': back_top,
                'front_avg': np.mean([v for v in front_freq.values()]),
                'back_avg': np.mean([v for v in back_freq.values()]),
            }

        return results

    def compare_hot_cold(self) -> Dict:
        """对比冷热号"""
        results = {}

        for name, data in [('30 期', self.data_30[-30:]), ('100 期', self.data_100[-100:]), ('500 期', self.data_500[-100:])]:
            if not data:
                continue

            # 只看最近 N 期的冷热
            window = min(len(data), 30)
            front_recent = np.array([[int(x) for x in item['front_balls']] for item in data[-window:]])
            back_recent = np.array([[int(x) for x in item['back_balls']] for item in data[-window:]])

            front_all = front_recent.flatten()
            back_all = back_recent.flatten()

            front_hot = Counter(front_all).most_common(5)
            back_hot = Counter(back_all).most_common(2)

            results[name] = {
                'front_hot': [x[0] for x in front_hot],
                'back_hot': [x[0] for x in back_hot],
            }

        return results

    def compare_sum_stats(self) -> Dict:
        """对比和值统计"""
        results = {}

        for name, data in [('30 期', self.data_30), ('100 期', self.data_100), ('500 期', self.data_500)]:
            if not data:
                continue

            front_sums = [sum(int(x) for x in item['front_balls']) for item in data]
            back_sums = [sum(int(x) for x in item['back_balls']) for item in data]

            results[name] = {
                'front_sum_mean': np.mean(front_sums),
                'front_sum_std': np.std(front_sums),
                'front_sum_min': min(front_sums),
                'front_sum_max': max(front_sums),
                'back_sum_mean': np.mean(back_sums),
            }

        return results

    def compare_odd_even(self) -> Dict:
        """对比奇偶比"""
        results = {}

        for name, data in [('30 期', self.data_30), ('100 期', self.data_100), ('500 期', self.data_500)]:
            if not data:
                continue

            front_odd = [sum(1 for x in item['front_balls'] if int(x) % 2 == 1) for item in data]
            odd_ratio = Counter(front_odd)

            results[name] = {
                'odd_ratio': dict(odd_ratio),
                'most_common': odd_ratio.most_common(1)[0] if odd_ratio else (0, 0),
            }

        return results

    def generate_predictions(self) -> Dict:
        """为每个周期生成推荐号码"""
        predictions = {}

        for name, data in [('30 期', self.data_30), ('100 期', self.data_100), ('500 期', self.data_500)]:
            if not data:
                continue

            # 频率评分
            front_all = np.array([int(x) for item in data for x in item['front_balls']])
            back_all = np.array([int(x) for item in data for x in item['back_balls']])

            front_counter = Counter(front_all)
            back_counter = Counter(back_all)

            # 归一化评分
            front_scores = {i: front_counter.get(i, 0) for i in range(1, 36)}
            back_scores = {i: back_counter.get(i, 0) for i in range(1, 13)}

            front_sorted = sorted(front_scores.items(), key=lambda x: x[1], reverse=True)[:10]
            back_sorted = sorted(back_scores.items(), key=lambda x: x[1], reverse=True)[:5]

            predictions[name] = {
                'front_recommend': [x[0] for x in front_sorted],
                'back_recommend': [x[0] for x in back_sorted],
                'front_hot': front_sorted[:5],
                'back_hot': back_sorted[:3],
            }

        return predictions


def print_comparison(comparator: DLTComparator):
    """打印对比报告"""
    print("\n" + "=" * 90)
    print(" " * 25 + "大乐透多周期对比分析报告")
    print("=" * 90)

    # 1. 数据概况
    print("\n【1. 数据概况】")
    print("-" * 90)
    print(f"  30 期数据：{len(comparator.data_30)}期 | {comparator.data_30[-1]['issue_number'] if comparator.data_30 else 'N/A'} ~ {comparator.data_30[0]['issue_number'] if comparator.data_30 else 'N/A'}")
    print(f" 100 期数据：{len(comparator.data_100)}期 | {comparator.data_100[-1]['issue_number'] if comparator.data_100 else 'N/A'} ~ {comparator.data_100[0]['issue_number'] if comparator.data_100 else 'N/A'}")
    print(f" 500 期数据：{len(comparator.data_500)}期 | {comparator.data_500[-1]['issue_number'] if comparator.data_500 else 'N/A'} ~ {comparator.data_500[0]['issue_number'] if comparator.data_500 else 'N/A'}")

    # 2. 频率对比
    print("\n【2. 频率分析对比】")
    print("-" * 90)
    freq = comparator.compare_frequency()

    for period, stats in freq.items():
        print(f"\n {period}:")
        front_str = ' '.join([f"{x[0]:02d}({x[1]}次)" for x in stats['front_top']])
        back_str = ' '.join([f"{x[0]:02d}({x[1]}次)" for x in stats['back_top']])
        print(f"   前区热号 TOP5: {front_str}")
        print(f"   后区热号 TOP3 : {back_str}")

    # 3. 冷热对比
    print("\n【3. 冷热号对比（最近 30 期）】")
    print("-" * 90)
    hot_cold = comparator.compare_hot_cold()
    for period, stats in hot_cold.items():
        print(f" {period}: 前区热号 {[f'{x:02d}' for x in stats['front_hot']]} | 后区热号 {[f'{x:02d}' for x in stats['back_hot']]}")

    # 4. 和值对比
    print("\n【4. 和值统计对比】")
    print("-" * 90)
    sum_stats = comparator.compare_sum_stats()
    print(f" {'周期':<10} {'平均和值':<12} {'标准差':<10} {'最小值':<10} {'最大值':<10}")
    print("-" * 90)
    for period, stats in sum_stats.items():
        print(f" {period:<10} {stats['front_sum_mean']:<12.1f} {stats['front_sum_std']:<10.1f} {stats['front_sum_min']:<10} {stats['front_sum_max']:<10}")

    # 5. 奇偶比对比
    print("\n【5. 奇偶比对比】")
    print("-" * 90)
    odd_even = comparator.compare_odd_even()
    for period, stats in odd_even.items():
        most = stats['most_common']
        print(f" {period}: 最常见奇偶比为 {most[0]}奇:{5-most[0]}偶 ({most[1]}期，{most[1]/len(comparator.data_30)*100:.1f}%)")

    # 6. 各周期推荐
    print("\n【6. 各周期推荐号码】")
    print("-" * 90)
    predictions = comparator.generate_predictions()

    for period, pred in predictions.items():
        print(f"\n {period}推荐:")
        print(f"   前区热号：{[f'{x[0]:02d}({x[1]}次)' for x in pred['front_hot']]}")
        print(f"   后区热号：{[f'{x[0]:02d}({x[1]}次)' for x in pred['back_hot']]}")

    # 7. 综合推荐
    print("\n【7. 综合推荐（取交集）】")
    print("=" * 90)

    # 找出在所有周期中都热的号码
    front_hot_30 = set(predictions.get('30 期', {}).get('front_recommend', [])[:5])
    front_hot_100 = set(predictions.get('100 期', {}).get('front_recommend', [])[:5])
    front_hot_500 = set(predictions.get('500 期', {}).get('front_recommend', [])[:5])

    # 交集
    common_front = front_hot_30 & front_hot_100
    all_common = common_front & front_hot_500

    print(f"\n 30 期 & 100 期 共同热号：{sorted([f'{x:02d}' for x in common_front])}")
    print(f" 3 周期共同热号：{sorted([f'{x:02d}' for x in all_common]) if all_common else '无'}")

    # 最终推荐组合
    print("\n【8. 最终推荐组合】")
    print("=" * 90)

    # 综合 3 个周期的数据
    all_front_rec = []
    all_back_rec = []

    for period in ['30 期', '100 期', '500 期']:
        if period in predictions:
            all_front_rec.extend(predictions[period]['front_recommend'][:5])
            all_back_rec.extend(predictions[period]['back_recommend'][:3])

    # 计算出现次数
    front_counter = Counter(all_front_rec)
    back_counter = Counter(all_back_rec)

    final_front = [x[0] for x in front_counter.most_common(10)]
    final_back = [x[0] for x in back_counter.most_common(4)]

    print(f"\n 前区推荐：{[f'{x:02d}' for x in sorted(final_front)]}")
    print(f" 后区推荐：{[f'{x:02d}' for x in sorted(final_back)]}")

    # 生成 5 注
    import random
    print("\n 推荐 5 注:")
    for i in range(5):
        f = sorted(random.sample(final_front, 5))
        b = sorted(random.sample(final_back, 2))
        print(f"   {i+1}. 前区 [{f[0]:02d} {f[1]:02d} {f[2]:02d} {f[3]:02d} {f[4]:02d}] 后区 [{b[0]:02d} {b[1]:02d}]")

    print("\n" + "=" * 90)
    print("  重要提示：彩票是随机事件，历史数据不能预测未来！")
    print("  本分析仅供娱乐参考，请理性购彩！")
    print("=" * 90 + "\n")


def main():
    comparator = DLTComparator()
    print_comparison(comparator)

    # 保存对比结果
    result = {
        'frequency': comparator.compare_frequency(),
        'hot_cold': comparator.compare_hot_cold(),
        'sum_stats': comparator.compare_sum_stats(),
        'odd_even': comparator.compare_odd_even(),
        'predictions': comparator.generate_predictions(),
    }

    # 转换 numpy 类型
    def convert(obj):
        if isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert(x) for x in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        return obj

    result = convert(result)

    with open('dlt_comparison.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print("\n对比结果已保存到 dlt_comparison.json")


if __name__ == "__main__":
    main()
