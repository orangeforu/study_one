# -*- coding: utf-8 -*-
"""
大乐透历史数据分析与号码预测
注意：彩票是随机事件，以下分析仅供娱乐参考
"""

import json
import pandas as pd
import numpy as np
from collections import Counter
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')


class DLTAnalyzer:
    """大乐透数据分析器"""

    def __init__(self, data_file: str):
        """初始化分析器"""
        with open(data_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

        # 提取前区和后区号码
        self.front_balls = []
        self.back_balls = []
        self.issues = []
        self.dates = []

        for item in self.data:
            self.front_balls.append([int(x) for x in item['front_balls']])
            self.back_balls.append([int(x) for x in item['back_balls']])
            self.issues.append(item['issue_number'])
            self.dates.append(item['draw_date'])

        # 转换为 numpy 数组
        self.front_array = np.array(self.front_balls)
        self.back_array = np.array(self.back_balls)

        # 统计指标
        self.front_stats = {}
        self.back_stats = {}

    def analyze_frequency(self) -> Dict:
        """分析号码频率"""
        # 前区频率统计（35 选 5）
        front_all = np.concatenate(self.front_balls)
        front_counter = Counter(front_all)
        front_freq = {i: front_counter.get(i, 0) for i in range(1, 36)}

        # 后区频率统计（12 选 2）
        back_all = np.concatenate(self.back_balls)
        back_counter = Counter(back_all)
        back_freq = {i: back_counter.get(i, 0) for i in range(1, 13)}

        self.front_stats['frequency'] = front_freq
        self.back_stats['frequency'] = back_freq

        return {
            'front': front_freq,
            'back': back_freq
        }

    def analyze_hot_cold(self, window: int = 10) -> Dict:
        """分析冷热号码（最近 N 期）"""
        # 前区冷热
        front_recent = np.concatenate(self.front_balls[:window])
        front_hot = Counter(front_recent).most_common(5)
        front_cold = sorted([(k, v) for k, v in Counter({i: 0 for i in range(1, 36)}.items())],
                           key=lambda x: x[1])[:5]

        # 计算实际的冷号
        front_counts = Counter(front_recent)
        front_cold = [(i, front_counts.get(i, 0)) for i in range(1, 36)]
        front_cold = sorted(front_cold, key=lambda x: x[1])[:5]

        # 后区冷热
        back_recent = np.concatenate(self.back_balls[:window])
        back_counts = Counter(back_recent)
        back_hot = back_counts.most_common(2)
        back_cold = [(i, back_counts.get(i, 0)) for i in range(1, 13)]
        back_cold = sorted(back_cold, key=lambda x: x[1])[:2]

        return {
            'front_hot': front_hot,
            'front_cold': front_cold,
            'back_hot': back_hot,
            'back_cold': back_cold
        }

    def analyze_missing(self) -> Dict:
        """分析遗漏值（号码多少期未出现）"""
        # 前区遗漏
        front_missing = {}
        for num in range(1, 36):
            missing = 0
            for balls in self.front_balls:
                if num in balls:
                    break
                missing += 1
            front_missing[num] = missing

        # 后区遗漏
        back_missing = {}
        for num in range(1, 13):
            missing = 0
            for balls in self.back_balls:
                if num in balls:
                    break
                missing += 1
            back_missing[num] = missing

        return {
            'front': front_missing,
            'back': back_missing
        }

    def analyze_sum_range(self) -> Dict:
        """分析和值分析"""
        # 前区和值
        front_sums = [sum(balls) for balls in self.front_balls]
        # 后区和值
        back_sums = [sum(balls) for balls in self.back_balls]

        return {
            'front_sum_avg': np.mean(front_sums),
            'front_sum_std': np.std(front_sums),
            'front_sum_min': min(front_sums),
            'front_sum_max': max(front_sums),
            'back_sum_avg': np.mean(back_sums),
            'back_sum_std': np.std(back_sums),
        }

    def analyze_odd_even(self) -> Dict:
        """分析奇偶比"""
        front_odd_counts = []
        for balls in self.front_balls:
            odd_count = sum(1 for x in balls if x % 2 == 1)
            front_odd_counts.append(odd_count)

        back_odd_counts = []
        for balls in self.back_balls:
            odd_count = sum(1 for x in balls if x % 2 == 1)
            back_odd_counts.append(odd_count)

        return {
            'front_odd_ratio': Counter(front_odd_counts),
            'back_odd_ratio': Counter(back_odd_counts)
        }

    def analyze_big_small(self) -> Dict:
        """分析大小比（前区 1-17 为小，18-35 为大）"""
        front_big_counts = []
        for balls in self.front_balls:
            big_count = sum(1 for x in balls if x >= 18)
            front_big_counts.append(big_count)

        return {
            'front_big_ratio': Counter(front_big_counts)
        }

    def analyze_consecutive(self) -> Dict:
        """分析连号情况"""
        consecutive_count = 0
        consecutive_groups = []

        for balls in self.front_balls:
            sorted_balls = sorted(balls)
            for i in range(len(sorted_balls) - 1):
                if sorted_balls[i + 1] - sorted_balls[i] == 1:
                    consecutive_count += 1
                    consecutive_groups.append((sorted_balls[i], sorted_balls[i + 1]))

        return {
            'consecutive_rate': consecutive_count / len(self.front_balls),
            'recent_consecutive': consecutive_groups[-5:] if consecutive_groups else []
        }

    def generate_prediction(self) -> Dict:
        """
        基于统计分析生成推荐号码
        注意：这仅供娱乐，彩票是随机事件
        """
        # 综合评分系统
        freq_data = self.analyze_frequency()
        missing_data = self.analyze_missing()
        hot_cold = self.analyze_hot_cold()

        # 前区评分
        front_scores = {}
        for num in range(1, 36):
            score = 0
            # 频率分（历史总出现次数）
            score += freq_data['front'].get(num, 0) * 2
            # 遗漏分（遗漏越久越可能出）
            score += missing_data['front'].get(num, 0) * 3
            # 热号加分
            if num in [x[0] for x in hot_cold['front_hot']]:
                score += 10

            front_scores[num] = score

        # 后区评分
        back_scores = {}
        for num in range(1, 13):
            score = 0
            score += freq_data['back'].get(num, 0) * 2
            score += missing_data['back'].get(num, 0) * 3
            if num in [x[0] for x in hot_cold['back_hot']]:
                score += 10

            back_scores[num] = score

        # 排序选出高分号码
        front_sorted = sorted(front_scores.items(), key=lambda x: x[1], reverse=True)
        back_sorted = sorted(back_scores.items(), key=lambda x: x[1], reverse=True)

        # 选取推荐号码
        front_recommend = [x[0] for x in front_sorted[:10]]
        back_recommend = [x[0] for x in back_sorted[:4]]

        # 生成组合（考虑和值、奇偶等）
        predictions = self._generate_combinations(front_recommend, back_recommend)

        return {
            'front_hot_numbers': [x[0] for x in hot_cold['front_hot']],
            'front_cold_numbers': [x[0] for x in hot_cold['front_cold']],
            'back_hot_numbers': [x[0] for x in hot_cold['back_hot']],
            'back_cold_numbers': [x[0] for x in hot_cold['back_cold']],
            'front_recommend': front_recommend,
            'back_recommend': back_recommend,
            'predictions': predictions
        }

    def _generate_combinations(self, front_pool: List[int], back_pool: List[int]) -> List[Dict]:
        """生成推荐组合"""
        import random

        combinations = []
        sum_avg = 85  # 前区和值平均约 85-95

        for _ in range(5):
            # 尝试生成符合统计规律的组合
            for _ in range(100):
                front = random.sample(front_pool, 5)
                back = random.sample(back_pool, 2)

                front_sum = sum(front)
                odd_count = sum(1 for x in front if x % 2 == 1)

                # 检查和值是否在合理范围（70-120）
                if 70 <= front_sum <= 120:
                    # 检查奇偶比（2-3 个奇数较常见）
                    if 2 <= odd_count <= 3:
                        combinations.append({
                            'front': sorted(front),
                            'back': sorted(back),
                            'sum': front_sum,
                            'odd_count': odd_count
                        })
                        break

            if len(combinations) >= 5:
                break

        return combinations


def print_analysis_report(analyzer: DLTAnalyzer):
    """打印分析报告"""
    print("=" * 80)
    print(" " * 25 + "超级大乐透历史数据分析报告")
    print("=" * 80)

    # 1. 频率分析
    print("\n【1. 号码频率分析】")
    print("-" * 60)
    freq = analyzer.analyze_frequency()

    front_top = sorted(freq['front'].items(), key=lambda x: x[1], reverse=True)[:5]
    front_bottom = sorted(freq['front'].items(), key=lambda x: x[1])[:5]
    back_top = sorted(freq['back'].items(), key=lambda x: x[1], reverse=True)[:2]

    print(f"前区最热号码：{[x[0] for x in front_top]} (出现次数：{[x[1] for x in front_top]})")
    print(f"前区最冷号码：{[x[0] for x in front_bottom]} (出现次数：{[x[1] for x in front_bottom]})")
    print(f"后区最热号码：{[x[0] for x in back_top]} (出现次数：{[x[1] for x in back_top]})")

    # 2. 冷热分析
    print("\n【2. 冷热分析（最近 10 期）】")
    print("-" * 60)
    hot_cold = analyzer.analyze_hot_cold(10)
    print(f"前区热号：{[x[0] for x in hot_cold['front_hot']]}")
    print(f"前区冷号：{[x[0] for x in hot_cold['front_cold']]}")
    print(f"后区热号：{[x[0] for x in hot_cold['back_hot']]}")
    print(f"后区冷号：{[x[0] for x in hot_cold['back_cold']]}")

    # 3. 遗漏分析
    print("\n【3. 遗漏分析】")
    print("-" * 60)
    missing = analyzer.analyze_missing()
    front_missing_top = sorted(missing['front'].items(), key=lambda x: x[1], reverse=True)[:5]
    back_missing_top = sorted(missing['back'].items(), key=lambda x: x[1], reverse=True)[:2]
    print(f"前区最大遗漏：{[(x[0], f'{x[1]}期') for x in front_missing_top]}")
    print(f"后区最大遗漏：{[(x[0], f'{x[1]}期') for x in back_missing_top]}")

    # 4. 和值分析
    print("\n【4. 和值分析】")
    print("-" * 60)
    sum_stats = analyzer.analyze_sum_range()
    print(f"前区和值平均：{sum_stats['front_sum_avg']:.1f}")
    print(f"前区和值标准差：{sum_stats['front_sum_std']:.1f}")
    print(f"前区和值范围：{sum_stats['front_sum_min']} - {sum_stats['front_sum_max']}")

    # 5. 奇偶比分析
    print("\n【5. 奇偶比分析】")
    print("-" * 60)
    odd_even = analyzer.analyze_odd_even()
    print("前区奇数个数分布:")
    for odd, count in sorted(odd_even['front_odd_ratio'].items()):
        print(f"  {odd}个奇数：{count}期 ({count/len(analyzer.data)*100:.1f}%)")

    # 6. 大小比分析
    print("\n【6. 大小比分析】")
    print("-" * 60)
    big_small = analyzer.analyze_big_small()
    print("前区大数个数分布（18-35 为大）:")
    for big, count in sorted(big_small['front_big_ratio'].items()):
        print(f"  {big}个大数：{count}期 ({count/len(analyzer.data)*100:.1f}%)")

    # 7. 连号分析
    print("\n【7. 连号分析】")
    print("-" * 60)
    consecutive = analyzer.analyze_consecutive()
    print(f"连号出现率：{consecutive['consecutive_rate']*100:.1f}%")
    if consecutive['recent_consecutive']:
        print(f"最近连号组合：{consecutive['recent_consecutive']}")

    # 8. 预测推荐
    print("\n【8. 预测推荐（仅供娱乐参考）】")
    print("=" * 60)
    prediction = analyzer.generate_prediction()

    print(f"\n前区热码推荐：{prediction['front_hot_numbers']}")
    print(f"前区冷码关注：{prediction['front_cold_numbers']}")
    print(f"后区热码推荐：{prediction['back_hot_numbers']}")
    print(f"后区冷码关注：{prediction['back_cold_numbers']}")

    print("\n【推荐号码组合】")
    print("-" * 60)
    for i, combo in enumerate(prediction['predictions'], 1):
        front_str = ' '.join(f"{x:02d}" for x in combo['front'])
        back_str = ' '.join(f"{x:02d}" for x in combo['back'])
        print(f"组合{i}: 前区 [{front_str}] 后区 [{back_str}] 和值={combo['sum']} 奇偶比={combo['odd_count']}: {5-combo['odd_count']}")

    print("\n" + "=" * 80)
    print(" 特别提醒：彩票是随机事件，所有号码中奖概率相同！")
    print(" 本分析仅供娱乐参考，请理性购彩，量力而行！")
    print("=" * 80)


def main():
    """主函数"""
    data_file = 'dlt_complete.json'

    try:
        analyzer = DLTAnalyzer(data_file)
        print(f"成功加载 {len(analyzer.data)} 期大乐透数据")
        print(f"数据范围：{analyzer.issues[-1]} 期 ({analyzer.dates[-1]}) 至 {analyzer.issues[0]} 期 ({analyzer.dates[0]})")
        print()

        print_analysis_report(analyzer)

    except FileNotFoundError:
        print(f"错误：找不到数据文件 {data_file}")
        print("请先运行爬虫获取数据")


if __name__ == "__main__":
    main()
