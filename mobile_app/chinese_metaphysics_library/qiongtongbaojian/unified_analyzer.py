from typing import Dict, List
from ..core.base_analyzer import BaseAnalyzer
from ..core.data_structures import BaziData, AnalysisResult, AnalysisConfig
from ..core.utils import create_analysis_result, get_wuxing_by_tiangan
from ..core.constants import DIZHI_CANGGAN
from .qiongtong_table import get_qiongtong_info, check_yongshen_presence

class QiongtongbaojianAnalyzer(BaseAnalyzer):
    """
    《穷通宝鉴》统一分析器
    基于120种日主月令组合的用神喜忌查表系统
    ✅ 已修复：消除硬编码，实现完整的120种组合查表
    """
    def __init__(self, config: AnalysisConfig = None):
        super().__init__("穷通宝鉴统一分析器", "穷通宝鉴", config)

    def analyze(self, bazi_data: BaziData) -> AnalysisResult:
        """
        四季调候与用神分析
        ✅ 已修复：使用120种组合查表，动态评分
        """
        month_branch = bazi_data.get_month_branch()
        day_master = bazi_data.get_day_master()
        pillars = bazi_data.get_pillars()

        # 从120种组合表中获取用神信息
        qiongtong_info = get_qiongtong_info(day_master, month_branch)

        # 提取信息
        yongshen_list = qiongtong_info['yongshen']
        xishen_list = qiongtong_info['xishen']
        jishen_list = qiongtong_info['jishen']
        season = qiongtong_info['season']
        temperature = qiongtong_info['temperature']
        base_score = qiongtong_info['base_score']
        description_base = qiongtong_info['description']
        advice_base = qiongtong_info['advice']

        # 检查用神是否出现
        yongshen_check = check_yongshen_presence(yongshen_list, pillars)
        xishen_check = check_yongshen_presence(xishen_list, pillars)
        jishen_check = check_yongshen_presence(jishen_list, pillars)

        # 动态计算评分
        score = base_score

        # 用神出现加分（最重要）
        if yongshen_check['present']:
            strength = yongshen_check['strength']
            score += 15 * strength  # 最多加15分
        else:
            score -= 15  # 用神不现扣15分

        # 喜神出现加分
        if xishen_check['present']:
            strength = xishen_check['strength']
            score += 8 * strength  # 最多加8分

        # 忌神出现扣分
        if jishen_check['present']:
            strength = jishen_check['strength']
            score -= 12 * strength  # 最多扣12分

        # 检查用神在地支藏干中的情况
        canggan_bonus = self._check_yongshen_in_canggan(yongshen_list, pillars)
        score += canggan_bonus

        # 限制在0-100范围内
        score = max(0.0, min(100.0, score))

        # 确定等级
        level = self._score_to_level(score)

        # 生成详细描述
        description = self._generate_description(
            description_base, season, temperature,
            yongshen_list, yongshen_check,
            xishen_list, xishen_check,
            jishen_list, jishen_check
        )

        # 生成建议
        advice = self._generate_advice(
            advice_base, yongshen_check, xishen_check, jishen_check
        )

        return create_analysis_result(
            analyzer_name=self.name,
            book_name=self.book_name,
            analysis_type="调候用神分析",
            level=level,
            score=score,
            description=description,
            details={
                'season': season,
                'temperature': temperature,
                'yongshen': yongshen_list,
                'xishen': xishen_list,
                'jishen': jishen_list,
                'yongshen_present': yongshen_check['present'],
                'yongshen_positions': yongshen_check['positions'],
                'xishen_present': xishen_check['present'],
                'jishen_present': jishen_check['present']
            },
            advice=advice
        )

    def _check_yongshen_in_canggan(self, yongshen_list: List[str], pillars: Dict) -> float:
        """
        检查用神是否在地支藏干中
        藏干中的用神力量较弱，但也有一定作用
        """
        bonus = 0.0

        for pillar_name, (gan, zhi) in pillars.items():
            canggan_list = DIZHI_CANGGAN.get(zhi, [])
            for canggan, weight in canggan_list:
                if canggan in yongshen_list:
                    # 藏干中的用神，根据权重和位置加分
                    position_weight = {'month': 1.0, 'year': 0.8, 'day': 0.6, 'hour': 0.4}.get(pillar_name, 0.5)
                    bonus += 5 * weight * position_weight

        return min(bonus, 10.0)  # 最多加10分

    def _score_to_level(self, score: float) -> str:
        """评分转等级"""
        if score >= 85:
            return '大吉'
        elif score >= 70:
            return '吉'
        elif score >= 55:
            return '中平'
        elif score >= 40:
            return '凶'
        else:
            return '大凶'

    def _generate_description(
        self, base_desc: str, season: str, temperature: str,
        yongshen_list: List[str], yongshen_check: Dict,
        xishen_list: List[str], xishen_check: Dict,
        jishen_list: List[str], jishen_check: Dict
    ) -> str:
        """生成详细描述"""
        parts = [base_desc]

        # ✅ 修复：用神情况 - 只显示实际出现的用神，使用"透于"而非"出现于"
        if yongshen_check['present']:
            positions_str = '、'.join(yongshen_check['positions'])
            # 使用check结果中返回的实际出现的用神列表
            present_yongshen = yongshen_check.get('present_list', [])

            if present_yongshen:
                # ✅ 修复：使用"透于"而非"出现于"，更符合命理术语
                parts.append(f"用神{'、'.join(present_yongshen)}透于{positions_str}，调候得宜")
            else:
                parts.append(f"用神{'、'.join(yongshen_list)}未现，调候不足")
        else:
            parts.append(f"用神{'、'.join(yongshen_list)}未现，调候不足")

        # 🔥 修复：喜神情况 - 只显示实际出现的喜神
        if xishen_check['present']:
            present_xishen = xishen_check.get('present_list', [])
            if present_xishen:
                parts.append(f"喜神{'、'.join(present_xishen)}助力")

        # ✅ 修复：忌神情况 - 只显示实际出现的忌神，使用"透出"而非"出现"
        if jishen_check['present']:
            present_jishen = jishen_check.get('present_list', [])
            if present_jishen:
                # ✅ 修复：使用"透出"而非"出现"，更符合命理术语
                parts.append(f"忌神{'、'.join(present_jishen)}透出，需要化解")

        return "；".join(parts)

    def _generate_advice(
        self, base_advice: str,
        yongshen_check: Dict,
        xishen_check: Dict,
        jishen_check: Dict
    ) -> str:
        """生成建议"""
        parts = [base_advice]

        if yongshen_check['present']:
            parts.append("调候得宜，宜顺势而为，把握机遇")
        else:
            parts.append("调候不足，需要外力补助，可通过方位、颜色、职业等方式调整")

        if jishen_check['present']:
            parts.append("注意化解忌神影响，避免相关不利因素")

        return"；".join(parts)
