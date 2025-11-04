from typing import Dict, List, Tuple
from ..core.base_analyzer import BaseAnalyzer
from ..core.data_structures import BaziData, AnalysisResult, AnalysisConfig
from ..core.utils import create_analysis_result, get_wuxing_by_tiangan, get_wuxing_by_dizhi
from ..core.constants import DIZHI_CANGGAN
from .sancai_analyzer import SancaiAnalyzer

class DitiansuiAnalyzer(BaseAnalyzer):
    """
    《滴天髓》统一分析器
    核心理论：
    1. 通根透干论强弱（本气、中气、余气有不同权重）
    2. 五行平衡论中和
    3. 得时得地得气论旺衰
    """

    def __init__(self, config: AnalysisConfig = None):
        super().__init__("滴天髓统一分析器", "滴天髓", config)
        # 初始化三才分析器
        self.sancai_analyzer = SancaiAnalyzer(config)

    def analyze(self, bazi_data: BaziData) -> AnalysisResult:
        """
        五行平衡分析，包含通根透干理论
        ✅ 已修复：
        1. 通根透干分强弱等级（本气1.0，中气0.5，余气0.2）
        2. 优化五行平衡评分公式
        3. 动态评分，不再硬编码70分
        """
        pillars = bazi_data.get_pillars()
        day_master = bazi_data.get_day_master()
        dm_wx = get_wuxing_by_tiangan(day_master)

        # 统计五行分布
        totals: Dict[str, float] = {'木':0,'火':0,'土':0,'金':0,'水':0}
        for pos, (gan, zhi) in pillars.items():
            totals[get_wuxing_by_tiangan(gan)] += 1.0
            for canggan, w in DIZHI_CANGGAN.get(zhi, []):
                totals[get_wuxing_by_tiangan(canggan)] += float(w)

        max_wx = max(totals, key=totals.get)
        min_wx = min(totals, key=totals.get)
        balance_gap = max(totals.values()) - min(totals.values())

        # ✅ 通根透干分强弱等级
        tongen_strength, tongen_details = self._calculate_tongen_strength(day_master, pillars)
        tougan_strength, tougan_details = self._calculate_tougan_strength(day_master, pillars)

        # 通根透干等级
        tongen_level = self._get_strength_level(tongen_strength)
        tougan_level = self._get_strength_level(tougan_strength)

        # ✅ 计算各项分数
        balance_score = self._calculate_balance_score(totals, dm_wx)
        tongen_score = min(tongen_strength * 5, 25)  # 通根分数，最高25分
        tougan_score = min(tougan_strength * 5, 25)  # 透干分数，最高25分

        # ✅ 修复：不打分，只判断阴阳平衡
        # 根据五行平衡和通根透干判断吉凶
        if balance_gap < 2.0 and tongen_level in ['强', '极强'] and tougan_level in ['强', '极强']:
            level = '大吉'
        elif balance_gap < 3.0 and tongen_level in ['中', '强', '极强']:
            level = '吉'
        elif balance_gap < 4.0:
            level = '中平'
        elif balance_gap < 5.0:
            level = '凶'
        else:
            level = '大凶'

        score = 0  # 不打分

        # 生成描述
        description = f"五行偏{max_wx}（{totals[max_wx]:.1f}），弱{min_wx}（{totals[min_wx]:.1f}）；"
        description += f"通根{tongen_level}（{tongen_strength:.1f}），透干{tougan_level}（{tougan_strength:.1f}）"

        advice = self._generate_advice(max_wx, min_wx, tongen_level, tougan_level, totals, dm_wx)

        return create_analysis_result(
            analyzer_name=self.name,
            book_name=self.book_name,
            analysis_type="五行平衡分析",
            level=level,
            score=score,
            description=description,
            details={
                'totals': totals,
                'max': max_wx,
                'min': min_wx,
                'balance_gap': balance_gap,
                'tongen_strength': tongen_strength,
                'tongen_level': tongen_level,
                'tongen_details': tongen_details,
                'tougan_strength': tougan_strength,
                'tougan_level': tougan_level,
                'tougan_details': tougan_details,
                'balance_score': balance_score,
                'tongen_score': tongen_score,
                'tougan_score': tougan_score
            },
            advice=advice
        )

    def _calculate_tongen_strength(self, day_master: str, pillars: Dict) -> Tuple[float, List[str]]:
        """
        计算通根强度
        ✅ 本气1.0，中气0.5，余气0.2
        ✅ 位置权重：日支1.5，月支1.2，年支时支1.0
        """
        dm_wx = get_wuxing_by_tiangan(day_master)
        strength = 0.0
        details = []

        position_weights = {
            'year': 1.0,
            'month': 1.2,
            'day': 1.5,
            'hour': 1.0
        }

        for pos, (gan, zhi) in pillars.items():
            pos_weight = position_weights.get(pos, 1.0)
            canggan_list = DIZHI_CANGGAN.get(zhi, [])

            for idx, (canggan, cg_weight) in enumerate(canggan_list):
                if get_wuxing_by_tiangan(canggan) == dm_wx:
                    # 判断本气、中气、余气
                    if idx == 0:  # 本气
                        root_strength = 1.0
                        root_type = '本气'
                    elif idx == 1:  # 中气
                        root_strength = 0.5
                        root_type = '中气'
                    else:  # 余气
                        root_strength = 0.2
                        root_type = '余气'

                    final_strength = root_strength * pos_weight
                    strength += final_strength
                    details.append(f"{pos}支{zhi}藏{canggan}（{root_type}，强度{final_strength:.1f}）")

        return strength, details

    def _calculate_tougan_strength(self, day_master: str, pillars: Dict) -> Tuple[float, List[str]]:
        """
        计算透干强度
        ✅ 位置权重：月干1.5，年干时干1.0
        """
        dm_wx = get_wuxing_by_tiangan(day_master)
        strength = 0.0
        details = []

        position_weights = {
            'year': 1.0,
            'month': 1.5,
            'hour': 1.0
        }

        for pos, (gan, zhi) in pillars.items():
            if pos == 'day':  # 不计日干本身
                continue

            if get_wuxing_by_tiangan(gan) == dm_wx:
                pos_weight = position_weights.get(pos, 1.0)
                strength += pos_weight
                details.append(f"{pos}干{gan}（强度{pos_weight:.1f}）")

        return strength, details

    def _get_strength_level(self, strength: float) -> str:
        """根据强度值返回等级"""
        if strength >= 3.0:
            return '极强'
        elif strength >= 2.0:
            return '强'
        elif strength >= 1.0:
            return '中等'
        elif strength >= 0.5:
            return '弱'
        elif strength > 0:
            return '极弱'
        else:
            return '无'

    def _calculate_balance_score(self, totals: Dict[str, float], dm_wx: str) -> float:
        """
        计算五行平衡分数
        ✅ 优化的评分公式（限制在0-25分）
        """
        # 1. 五行分布均衡度（标准差越小越好）
        values = list(totals.values())
        avg = sum(values) / len(values)
        variance = sum((v - avg) ** 2 for v in values) / len(values)
        std_dev = variance ** 0.5

        # 标准差越小，平衡度越高（0-10分）
        balance_bonus = max(0, 10 - std_dev * 3)

        # 2. 日主五行强度（不能太强也不能太弱）（0-8分）
        dm_strength = totals.get(dm_wx, 0)
        ideal_strength = avg  # 理想强度是平均值
        dm_deviation = abs(dm_strength - ideal_strength)
        dm_bonus = max(0, 8 - dm_deviation * 2)

        # 3. 五行相生链（连续相生加分）（0-7分）
        sheng_chain_bonus = min(7, self._calculate_sheng_chain_bonus(totals))

        total = balance_bonus + dm_bonus + sheng_chain_bonus
        return min(25.0, total)  # 限制在25分以内

    def _calculate_sheng_chain_bonus(self, totals: Dict[str, float]) -> float:
        """计算五行相生链加分"""
        # 五行相生顺序：木生火，火生土，土生金，金生水，水生木
        sheng_order = ['木', '火', '土', '金', '水']

        bonus = 0.0
        for i in range(5):
            current = sheng_order[i]
            next_wx = sheng_order[(i + 1) % 5]

            # 如果当前五行和下一个五行都存在，说明有相生链
            if totals.get(current, 0) > 0 and totals.get(next_wx, 0) > 0:
                bonus += 2.0

        return bonus

    def _generate_advice(self, max_wx: str, min_wx: str, tongen_level: str,
                        tougan_level: str, totals: Dict, dm_wx: str) -> str:
        """
        生成建议
        ✅ 根据五行平衡和通根透干给出建议
        """
        advice = []

        # 五行平衡建议
        if totals[max_wx] > totals[min_wx] * 2:
            advice.append(f"五行失衡，宜补{min_wx}、制{max_wx}以求中和")
        else:
            advice.append("五行较为平衡，宜维持现状")

        # 通根透干建议
        if tongen_level in ('极强', '强'):
            if tougan_level in ('极强', '强'):
                advice.append("通根透干俱强，根基稳固，力量外显，可大展宏图")
            else:
                advice.append("通根强而透干弱，根基稳固但力量内敛，宜厚积薄发")
        elif tongen_level in ('弱', '极弱', '无'):
            if tougan_level in ('强', '极强'):
                advice.append("透干强而通根弱，力量外显但根基不稳，宜谨慎行事")
            else:
                advice.append("通根透干俱弱，根基不稳力量不足，需外力扶持")
        else:
            advice.append("通根透干中等，根基尚可，宜稳健发展")

        # 日主强弱建议
        dm_strength = totals.get(dm_wx, 0)
        avg_strength = sum(totals.values()) / 5
        if dm_strength > avg_strength * 1.5:
            advice.append("日主过旺，宜泄耗（食伤财官）")
        elif dm_strength < avg_strength * 0.5:
            advice.append("日主过弱，宜扶抑（印比）")

        return "；".join(advice) + "。"
