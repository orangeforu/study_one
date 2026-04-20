# -*- coding: utf-8 -*-
"""
大乐透历史数据分析与号码预测（优化版）
注意：彩票是随机事件，以下分析仅供娱乐参考
"""

import json
import numpy as np
from collections import Counter
from typing import List, Dict, Tuple
import random


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

        return {'front': front_freq, 'back': back_freq}

    def analyze_hot_cold(self, window: int = 10) -> Dict:
        """分析冷热号码（最近 N 期）"""
        # 前区冷热
        front_recent = np.concatenate(self.front_balls[:window])
        front_counts = Counter(front_recent)
        front_hot = front_counts.most_common(5)
        front_cold = [(i, front_counts.get(i, 0)) for i in range(1, 36)]
        front_cold = sorted(front_cold, key=lambda x: (x[1], x[0]))[:5]

        # 后区冷热
        back_recent = np.concatenate(self.back_balls[:window])
        back_counts = Counter(back_recent)
        back_hot = back_counts.most_common(2)
        back_cold = [(i, back_counts.get(i, 0)) for i in range(1, 13)]
        back_cold = sorted(back_cold, key=lambda x: (x[1], x[0]))[:2]

        return {
            'front_hot': [x[0] for x in front_hot],
            'front_cold': [x[0] for x in front_cold],
            'back_hot': [x[0] for x in back_hot],
            'back_cold': [x[0] for x in back_cold]
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

        return {'front': front_missing, 'back': back_missing}

    def analyze_sum_range(self) -> Dict:
        """分析和值分析"""
        front_sums = [sum(balls) for balls in self.front_balls]
        back_sums = [sum(balls) for balls in self.back_balls]

        return {
            'front_sum_avg': np.mean(front_sums),
            'front_sum_std': np.std(front_sums),
            'front_sum_min': min(front_sums),
            'front_sum_max': max(front_sums),
        }

    def analyze_odd_even(self) -> Dict:
        """分析奇偶比"""
        front_odd_counts = [sum(1 for x in balls if x % 2 == 1) for balls in self.front_balls]
        back_odd_counts = [sum(1 for x in balls if x % 2 == 1) for balls in self.back_balls]

        return {
            'front_odd_ratio': Counter(front_odd_counts),
            'back_odd_ratio': Counter(back_odd_counts)
        }

    def analyze_big_small(self) -> Dict:
        """分析大小比（前区 1-17 为小，18-35 为大）"""
        front_big_counts = [sum(1 for x in balls if x >= 18) for balls in self.front_balls]
        return {'front_big_ratio': Counter(front_big_counts)}

    def generate_prediction(self) -> Dict:
        """基于统计分析生成推荐号码"""
        freq_data = self.analyze_frequency()
        missing_data = self.analyze_missing()
        hot_cold = self.analyze_hot_cold()

        # 前区综合评分
        front_scores = {}
        for num in range(1, 36):
            score = 0
            score += freq_data['front'].get(num, 0) * 2  # 频率分
            score += missing_data['front'].get(num, 0) * 3  # 遗漏分
            if num in hot_cold['front_hot']:
                score += 15  # 热号加分
            if num in [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33]:  # 3 的倍数
                score += 3  # 3 的倍数常有惊喜
            front_scores[num] = score

        # 后区综合评分
        back_scores = {}
        for num in range(1, 13):
            score = 0
            score += freq_data['back'].get(num, 0) * 2
            score += missing_data['back'].get(num, 0) * 3
            if num in hot_cold['back_hot']:
                score += 15
            back_scores[num] = score

        # 排序选出高分号码
        front_sorted = sorted(front_scores.items(), key=lambda x: x[1], reverse=True)
        back_sorted = sorted(back_scores.items(), key=lambda x: x[1], reverse=True)

        front_recommend = [x[0] for x in front_sorted[:12]]
        back_recommend = [x[0] for x in back_sorted[:5]]

        # 生成组合
        predictions = self._generate_combinations(front_recommend, back_recommend, hot_cold)

        return {
            'front_hot': hot_cold['front_hot'],
            'front_cold': hot_cold['front_cold'],
            'back_hot': hot_cold['back_hot'],
            'back_cold': hot_cold['back_cold'],
            'front_recommend': front_recommend,
            'back_recommend': back_recommend,
            'predictions': predictions,
            'front_scores': front_sorted[:10],
            'back_scores': back_sorted[:5]
        }

    def _generate_combinations(self, front_pool: List[int], back_pool: List[int], hot_cold: Dict) -> List[Dict]:
        """生成推荐组合 - 基于统计规律"""
        combinations = []

        # 策略 1: 热号为主
        hot_combo = self._generate_one(hot_cold['front_hot'][:7], hot_cold['back_hot'][:3])
        if hot_combo:
            combinations.append(hot_combo)

        # 策略 2: 冷热搭配
        mix_pool = hot_cold['front_hot'][:4] + hot_cold['front_cold'][:4] + random.sample([x for x in front_pool if x not in hot_cold['front_hot']], 4)
        mix_combo = self._generate_one(mix_pool, back_pool[:3])
        if mix_combo:
            combinations.append(mix_combo)

        # 策略 3: 遗漏回补
        missing_combo = self._generate_one(hot_cold['front_cold'][:6] + front_pool[:6], back_pool)
        if missing_combo:
            combinations.append(missing_combo)

        # 策略 4: 随机优化
        for _ in range(3):
            combo = self._generate_one(front_pool, back_pool)
            if combo and combo not in combinations:
                combinations.append(combo)

        return combinations[:5]

    def _generate_one(self, front_candidates: List[int], back_candidates: List[int]) -> Dict:
        """生成单个组合"""
        try:
            front = random.sample(list(set(front_candidates)), 5)
            back = random.sample(list(set(back_candidates)), 2)
        except ValueError:
            return None

        front_sum = sum(front)
        odd_count = sum(1 for x in front if x % 2 == 1)

        return {
            'front': sorted(front),
            'back': sorted(back),
            'sum': front_sum,
            'odd_count': odd_count
        }


def print_report(analyzer: DLTAnalyzer):
    """打印分析报告"""
    print("\n" + "=" * 80)
    print(" " * 22 + "超级大乐透历史数据分析与预测")
    print("=" * 80)

    print(f"\n数据来源：500 彩票网 | 分析期数：{len(analyzer.data)}期 | 范围：{analyzer.issues[-1]}~{analyzer.issues[0]}期")

    # 1. 频率分析
    print("\n" + "=" * 80)
    print("【1. 号码频率分析】")
    print("-" * 80)
    freq = analyzer.analyze_frequency()
    front_top = sorted(freq['front'].items(), key=lambda x: x[1], reverse=True)[:5]
    front_bottom = sorted(freq['front'].items(), key=lambda x: x[1])[:5]
    back_top = sorted(freq['back'].items(), key=lambda x: x[1], reverse=True)[:3]

    print(f"前区最热 TOP5: {[f'{x[0]:02d}({x[1]}次)' for x in front_top]}")
    print(f"前区最冷 TOP5: {[f'{x[0]:02d}({x[1]}次)' for x in front_bottom]}")
    print(f"后区最热 TOP3 : {[f'{x[0]:02d}({x[1]}次)' for x in back_top]}")

    # 2. 冷热分析
    print("\n" + "=" * 80)
    print("【2. 冷热分析（最近 10 期）】")
    print("-" * 80)
    hot_cold = analyzer.analyze_hot_cold(10)
    print(f"前区热号：{[f'{x:02d}' for x in hot_cold['front_hot']]} ← 近期活跃")
    print(f"前区冷号：{[f'{x:02d}' for x in hot_cold['front_cold']]} ← 关注回补")
    print(f"后区热号：{[f'{x:02d}' for x in hot_cold['back_hot']]} ← 近期活跃")
    print(f"后区冷号：{[f'{x:02d}' for x in hot_cold['back_cold']]} ← 关注回补")

    # 3. 遗漏分析
    print("\n" + "=" * 80)
    print("【3. 遗漏分析】")
    print("-" * 80)
    missing = analyzer.analyze_missing()
    front_missing_top = sorted(missing['front'].items(), key=lambda x: x[1], reverse=True)[:5]
    back_missing_top = sorted(missing['back'].items(), key=lambda x: x[1], reverse=True)[:3]
    print(f"前区遗漏 TOP5: {[f'{x[0]:02d}({x[1]}期未出)' for x in front_missing_top]}")
    print(f"后区遗漏 TOP3 : {[f'{x[0]:02d}({x[1]}期未出)' for x in back_missing_top]}")

    # 4. 和值分析
    print("\n" + "=" * 80)
    print("【4. 和值与形态分析】")
    print("-" * 80)
    sum_stats = analyzer.analyze_sum_range()
    odd_even = analyzer.analyze_odd_even()
    big_small = analyzer.analyze_big_small()

    print(f"前区和值平均：{sum_stats['front_sum_avg']:.0f} (范围:{sum_stats['front_sum_min']}-{sum_stats['front_sum_max']})")

    # 找最高频的奇偶比
    best_odd = max(odd_even['front_odd_ratio'].items(), key=lambda x: x[1])
    best_big = max(big_small['front_big_ratio'].items(), key=lambda x: x[1])
    print(f"最常见奇偶比：{best_odd[0]}奇:{5-best_odd[0]}偶 ({best_odd[1]}期)")
    print(f"最常见大小比：{best_big[0]}大:{5-best_big[0]}小 ({best_big[1]}期)")

    # 5. 综合评分
    print("\n" + "=" * 80)
    print("【5. 号码综合评分 TOP10】")
    print("-" * 80)
    prediction = analyzer.generate_prediction()
    print("前区:")
    for i, (num, score) in enumerate(prediction['front_scores'][:5], 1):
        bar = "█" * int(score / 3)
        print(f"  {i}. 号码 {num:02d} | 评分:{score:3d} | {bar}")

    print("后区:")
    for i, (num, score) in enumerate(prediction['back_scores'][:3], 1):
        bar = "█" * int(score / 3)
        print(f"  {i}. 号码 {num:02d} | 评分:{score:3d} | {bar}")

    # 6. 预测推荐
    print("\n" + "=" * 80)
    print("【6. 推荐号码组合】")
    print("=" * 80)

    for i, combo in enumerate(prediction['predictions'], 1):
        front_str = ' '.join(f"{x:02d}" for x in combo['front'])
        back_str = ' '.join(f"{x:02d}" for x in combo['back'])
        strategy = ["热号追踪", "冷热搭配", "遗漏回补", "随机优化 A", "随机优化 B"][i-1]
        print(f"\n★ 方案{i} [{strategy}]")
        print(f"  前区：{front_str}  (和值:{combo['sum']}, 奇偶:{combo['odd_count']}:{5-combo['odd_count']})")
        print(f"  后区：{back_str}")

    # 7. 胆拖推荐
    print("\n" + "=" * 80)
    print("【7. 胆拖复式推荐】")
    print("=" * 80)
    front_dan = prediction['front_scores'][:2]
    front_tuo = [x[0] for x in prediction['front_scores'][2:8]]
    back_dan = prediction['back_scores'][:1]
    back_tuo = [x[0] for x in prediction['back_scores'][1:4]]

    print(f"\n前区胆码：{[f'{x[0]:02d}' for x in front_dan]}")
    print(f"前区拖码：{[f'{x:02d}' for x in front_tuo]}")
    print(f"后区胆码：{[f'{x[0]:02d}' for x in back_dan]}")
    print(f"后区拖码：{[f'{x:02d}' for x in back_tuo]}")
    print(f"\n复式注数：C({len(front_tuo)},3) × C({len(back_tuo)},1) = {len(front_tuo)*(len(front_tuo)-1)//2 * len(back_tuo)}注")

    # 免责声明
    print("\n" + "=" * 80)
    print(" [重要提示] ")
    print("  彩票是独立随机事件，历史数据不能预测未来结果！")
    print("  本分析仅供娱乐参考，请理性购彩，量力而行！")
    print("  未满 18 岁请勿购买彩票！")
    print("=" * 80 + "\n")


def main():
    """主函数"""
    data_file = 'dlt_complete.json'

    try:
        analyzer = DLTAnalyzer(data_file)
        print_report(analyzer)

        # 保存推荐号码
        prediction = analyzer.generate_prediction()
        # 转换 numpy 类型为 Python 原生类型
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

        prediction = convert(prediction)
        with open('dlt_prediction.json', 'w', encoding='utf-8') as f:
            json.dump(prediction, f, ensure_ascii=False, indent=2)
        print("推荐号码已保存到 dlt_prediction.json")

    except FileNotFoundError:
        print(f"错误：找不到数据文件 {data_file}")


if __name__ == "__main__":
    main()
