# -*- coding: utf-8 -*-
"""
大乐透策略回测系统
用历史数据验证不同推荐策略的命中率
"""

import json
import numpy as np
from collections import Counter
from typing import List, Dict, Tuple
from itertools import combinations


class DLTBacktester:
    """大乐透回测器"""

    def __init__(self, data_file: str = 'dlt_500.json'):
        """初始化回测器"""
        with open(data_file, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        # 按时间正序排列（旧的在前）
        self.data.reverse()
        self.total_periods = len(self.data)

    def get_draw_result(self, index: int) -> Tuple[List[int], List[int]]:
        """获取某期的开奖结果"""
        item = self.data[index]
        front = [int(x) for x in item['front_balls']]
        back = [int(x) for x in item['back_balls']]
        return front, back

    def check_prize(self, predict_front: List[int], predict_back: List[int],
                    actual_front: List[int], actual_back: List[int]) -> Dict:
        """
        检查中奖情况
        返回中奖等级和注数
        """
        # 计算命中个数
        front_hit = len(set(predict_front) & set(actual_front))
        back_hit = len(set(predict_back) & set(actual_back))

        # 大乐透中奖规则
        prize_table = {
            (5, 2): "一等奖",
            (5, 1): "二等奖",
            (5, 0): "三等奖",
            (4, 2): "四等奖",
            (4, 1): "五等奖",
            (4, 0): "六等奖",
            (3, 2): "六等奖",
            (2, 2): "七等奖",
            (3, 1): "八等奖",
            (3, 0): "八等奖",
            (1, 2): "九等奖",
            (2, 1): "九等奖",
            (2, 0): "九等奖",
            (0, 2): "九等奖",
        }

        prize_level = prize_table.get((front_hit, back_hit), "未中奖")

        return {
            'front_hit': front_hit,
            'back_hit': back_hit,
            'prize_level': prize_level,
            'is_prize': prize_level != "未中奖"
        }

    def strategy_random(self, index: int) -> Tuple[List[int], List[int]]:
        """策略 1: 完全随机选号"""
        import random
        front = sorted(random.sample(range(1, 36), 5))
        back = sorted(random.sample(range(1, 13), 2))
        return front, back

    def strategy_hot_numbers(self, index: int, lookback: int = 30) -> Tuple[List[int], List[int]]:
        """策略 2: 追热号（基于前 N 期的热号）"""
        # 统计前 lookback 期的热号
        front_all = []
        back_all = []

        for i in range(max(0, index - lookback), index):
            front, back = self.get_draw_result(i)
            front_all.extend(front)
            back_all.extend(back)

        front_counter = Counter(front_all)
        back_counter = Counter(back_all)

        # 选最热的号码
        front_hot = [x[0] for x in front_counter.most_common(10)]
        back_hot = [x[0] for x in back_counter.most_common(5)]

        # 从热号中随机选
        import random
        if len(front_hot) >= 5:
            front = sorted(random.sample(front_hot, 5))
        else:
            front = sorted(random.sample(range(1, 36), 5))

        if len(back_hot) >= 2:
            back = sorted(random.sample(back_hot, 2))
        else:
            back = sorted(random.sample(range(1, 13), 2))

        return front, back

    def strategy_cold_numbers(self, index: int, lookback: int = 30) -> Tuple[List[int], List[int]]:
        """策略 3: 守冷号（遗漏最久的号码）"""
        # 统计前 lookback 期的遗漏
        front_count = {i: 0 for i in range(1, 36)}
        back_count = {i: 0 for i in range(1, 13)}

        for i in range(max(0, index - lookback), index):
            front, back = self.get_draw_result(i)
            for num in front:
                front_count[num] = lookback - (index - i)
            for num in back:
                back_count[num] = lookback - (index - i)

        # 选最冷的号码（出现次数最少）
        front_cold = sorted(front_count.items(), key=lambda x: x[1])[:10]
        back_cold = sorted(back_count.items(), key=lambda x: x[1])[:5]

        import random
        front = sorted([x[0] for x in front_cold])
        front = random.sample(front, min(5, len(front)))
        back = sorted([x[0] for x in back_cold])
        back = random.sample(back, min(2, len(back)))

        return sorted(front), sorted(back)

    def strategy_frequency_weighted(self, index: int, lookback: int = 50) -> Tuple[List[int], List[int]]:
        """策略 4: 频率加权随机（热号概率更高）"""
        front_all = []
        back_all = []

        for i in range(max(0, index - lookback), index):
            front, back = self.get_draw_result(i)
            front_all.extend(front)
            back_all.extend(back)

        front_counter = Counter(front_all)
        back_counter = Counter(back_all)

        # 频率加权选择
        import random
        front_pool = []
        for num, count in front_counter.items():
            front_pool.extend([num] * count)

        back_pool = []
        for num, count in back_counter.items():
            back_pool.extend([num] * count)

        # 加权随机选 5+2
        front = set()
        while len(front) < 5 and len(front_pool) >= 5:
            pick = random.choice(front_pool)
            front.add(pick)
            if len(front) < 5:
                front_pool = [x for x in front_pool if x != pick]

        back = set()
        while len(back) < 2 and len(back_pool) >= 2:
            pick = random.choice(back_pool)
            back.add(pick)
            if len(back) < 2:
                back_pool = [x for x in back_pool if x != pick]

        return sorted(list(front)), sorted(list(back))

    def strategy_sum_range(self, index: int) -> Tuple[List[int], List[int]]:
        """策略 5: 和值约束选号（和值 70-110）"""
        import random

        for _ in range(100):
            front = sorted(random.sample(range(1, 36), 5))
            if 70 <= sum(front) <= 110:
                back = sorted(random.sample(range(1, 13), 2))
                return front, back

        return sorted(random.sample(range(1, 36), 5)), sorted(random.sample(range(1, 13), 2))

    def strategy_odd_even_balanced(self, index: int) -> Tuple[List[int], List[int]]:
        """策略 6: 奇偶平衡（3 奇 2 偶或 2 奇 3 偶）"""
        import random

        odd_numbers = list(range(1, 36, 2))  # 1,3,5...35
        even_numbers = list(range(2, 36, 2))  # 2,4,6...34

        # 随机选择 3 奇 2 偶 或 2 奇 3 偶
        if random.random() < 0.5:
            front = sorted(random.sample(odd_numbers, 3) + random.sample(even_numbers, 2))
        else:
            front = sorted(random.sample(odd_numbers, 2) + random.sample(even_numbers, 3))

        back = sorted(random.sample(range(1, 13), 2))
        return front, back

    def run_backtest(self, strategy_func, strategy_name: str,
                     start_index: int = 100, periods: int = 100,
                     simulations: int = 10) -> Dict:
        """
        运行回测
        start_index: 从第几期开始回测（留出前面的数据做分析）
        periods: 回测多少期
        simulations: 每期模拟多少次（因为有些策略有随机性）
        """
        results = {
            'strategy': strategy_name,
            'total_bet': 0,
            'total_prize': 0,
            'prize_count': 0,
            'prize_details': Counter(),
            'front_hit_distribution': Counter(),
            'back_hit_distribution': Counter(),
        }

        # 奖金估算（元）
        prize_money = {
            "一等奖": 8000000,
            "二等奖": 500000,
            "三等奖": 10000,
            "四等奖": 3000,
            "五等奖": 300,
            "六等奖": 200,
            "七等奖": 100,
            "八等奖": 15,
            "九等奖": 5,
        }

        end_index = min(start_index + periods, self.total_periods)

        for i in range(start_index, end_index):
            actual_front, actual_back = self.get_draw_result(i)

            # 多次模拟取平均
            for _ in range(simulations):
                pred_front, pred_back = strategy_func(i)
                result = self.check_prize(pred_front, pred_back, actual_front, actual_back)

                results['total_bet'] += 1  # 每注 2 元，简化为 1
                results['front_hit_distribution'][result['front_hit']] += 1
                results['back_hit_distribution'][result['back_hit']] += 1

                if result['is_prize']:
                    results['prize_count'] += 1
                    results['prize_details'][result['prize_level']] += 1
                    results['total_prize'] += prize_money.get(result['prize_level'], 0)

        # 计算统计指标
        results['hit_rate'] = results['prize_count'] / results['total_bet'] * 100 if results['total_bet'] > 0 else 0
        results['roi'] = (results['total_prize'] - results['total_bet'] * 2) / (results['total_bet'] * 2) * 100 if results['total_bet'] > 0 else -100

        return results

    def compare_all_strategies(self, start_index: int = 100, periods: int = 100) -> List[Dict]:
        """对比所有策略"""
        strategies = [
            (self.strategy_random, "随机选号"),
            (self.strategy_hot_numbers, "追热号"),
            (self.strategy_cold_numbers, "守冷号"),
            (self.strategy_frequency_weighted, "频率加权"),
            (self.strategy_sum_range, "和值约束"),
            (self.strategy_odd_even_balanced, "奇偶平衡"),
        ]

        all_results = []

        for func, name in strategies:
            print(f"正在回测：{name}...")
            result = self.run_backtest(func, name, start_index, periods)
            all_results.append(result)

        # 按收益率排序
        all_results.sort(key=lambda x: x['roi'], reverse=True)

        return all_results


def print_backtest_report(backtester: DLTBacktester, results: List[Dict]):
    """打印回测报告"""
    print("\n" + "=" * 90)
    print(" " * 30 + "大乐透策略回测报告")
    print("=" * 90)

    print(f"\n回测数据：{backtester.total_periods}期历史数据")
    print(f"回测区间：第{results[0]['total_bet']//100}期 至 第{backtester.total_periods}期")
    print(f"每注成本：2 元")

    print("\n" + "-" * 90)
    print(f"{'策略名称':<15} {'中奖率':<10} {'总投入':<10} {'总奖金':<12} {'ROI':<10}")
    print("-" * 90)

    for r in results:
        cost = r['total_bet'] * 2
        print(f"{r['strategy']:<15} {r['hit_rate']:>6.2f}%    "
              f"{cost:>8}元    {r['total_prize']:>10}元    {r['roi']:>+8.1f}%")

    print("-" * 90)

    # 详细统计
    print("\n【详细统计】")
    print("-" * 90)

    for r in results:
        print(f"\n{r['strategy']}:")
        print(f"  总投注：{r['total_bet']}注")
        print(f"  中奖：{r['prize_count']}注 ({r['hit_rate']:.2f}%)")
        print(f"  前区命中分布：")
        for hit, count in sorted(r['front_hit_distribution'].items()):
            pct = count / r['total_bet'] * 100
            bar = "█" * int(pct)
            print(f"    中{hit}球：{count}次 ({pct:.1f}%) {bar}")
        print(f"  后区命中分布：")
        for hit, count in sorted(r['back_hit_distribution'].items()):
            pct = count / r['total_bet'] * 100
            bar = "█" * int(pct)
            print(f"    中{hit}球：{count}次 ({pct:.1f}%) {bar}")

        if r['prize_details']:
            print(f"  中奖明细：")
            for prize, count in r['prize_details'].most_common():
                print(f"    {prize}: {count}注")

    # 最佳策略
    print("\n" + "=" * 90)
    print("【结论】")
    print("=" * 90)

    best = results[0]
    worst = results[-1]

    print(f"\n最佳策略：{best['strategy']} (ROI: {best['roi']:+.1f}%)")
    print(f"最差策略：{worst['strategy']} (ROI: {worst['roi']:+.1f}%)")

    print("\n重要发现：")
    for r in results:
        if r['roi'] > -50:
            print(f"  [OK] {r['strategy']} 表现较好，亏损较少")

    print("\n" + "=" * 90)
    print(" 回测说明")
    print("  - 历史表现不代表未来结果")
    print("  - 所有策略长期来看都是负收益（彩票的期望值为负）")
    print("  - 回测仅用于娱乐和验证统计规律")
    print("=" * 90 + "\n")


def main():
    print("正在加载数据...")
    backtester = DLTBacktester('dlt_500.json')
    print(f"加载成功：{backtester.total_periods}期数据")

    # 运行回测（回测最近 100 期）
    results = backtester.compare_all_strategies(start_index=100, periods=300)

    # 打印报告
    print_backtest_report(backtester, results)

    # 保存结果
    def convert(obj):
        if isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert(x) for x in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, Counter):
            return dict(obj)
        return obj

    results_converted = convert(results)
    with open('dlt_backtest_result.json', 'w', encoding='utf-8') as f:
        json.dump(results_converted, f, ensure_ascii=False, indent=2)
    print("\n回测结果已保存到 dlt_backtest_result.json")


if __name__ == "__main__":
    main()
