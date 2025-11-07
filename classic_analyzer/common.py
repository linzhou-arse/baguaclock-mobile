#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经典命理公共工具

提供：
1. 天干地支五行、阴阳、藏干权重等基础对照
2. 通用的五行权重计算（含藏干权重）
3. 日主强弱判定
4. 十神关系推断

所有数据以《渊海子平》《三命通会》《子平真诠》《滴天髓》《穷通宝鉴》为依据，
藏干权重采用常用的本气 / 中气 / 余气比例（1.0 / 0.6 / 0.3）。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 天干五行
TIANGAN_WUXING: Dict[str, str] = {
    '甲': '木', '乙': '木',
    '丙': '火', '丁': '火',
    '戊': '土', '己': '土',
    '庚': '金', '辛': '金',
    '壬': '水', '癸': '水',
}

# 天干阴阳（阳：+1，阴：-1）
TIANGAN_YINYANG: Dict[str, int] = {
    '甲': 1, '乙': -1,
    '丙': 1, '丁': -1,
    '戊': 1, '己': -1,
    '庚': 1, '辛': -1,
    '壬': 1, '癸': -1,
}

# 地支对应的本气/中气/余气藏干及权重
# ✅ 已统一：使用与 chinese_metaphysics_library/core/constants.py 相同的定义
# 权重说明：本气0.6-0.7，中气0.2-0.3，余气0.1，总和为1.0
DIZHI_CANGGAN_WEIGHTS: Dict[str, List[Tuple[str, float]]] = {
    '子': [('癸', 1.0)],                          # 子水：纯癸水
    '丑': [('己', 0.6), ('癸', 0.3), ('辛', 0.1)],  # 丑土：己土本气，癸水中气，辛金余气
    '寅': [('甲', 0.7), ('丙', 0.2), ('戊', 0.1)],  # 寅木：甲木本气，丙火中气，戊土余气
    '卯': [('乙', 1.0)],                          # 卯木：纯乙木
    '辰': [('戊', 0.6), ('乙', 0.3), ('癸', 0.1)],  # 辰土：戊土本气，乙木中气，癸水余气
    '巳': [('丙', 0.7), ('戊', 0.2), ('庚', 0.1)],  # 巳火：丙火本气，戊土中气，庚金余气
    '午': [('丁', 0.7), ('己', 0.3)],              # 午火：丁火本气，己土中气
    '未': [('己', 0.6), ('丁', 0.3), ('乙', 0.1)],  # 未土：己土本气，丁火中气，乙木余气
    '申': [('庚', 0.7), ('壬', 0.2), ('戊', 0.1)],  # 申金：庚金本气，壬水中气，戊土余气
    '酉': [('辛', 1.0)],                          # 酉金：纯辛金
    '戌': [('戊', 0.6), ('辛', 0.3), ('丁', 0.1)],  # 戌土：戊土本气，辛金中气，丁火余气
    '亥': [('壬', 0.7), ('甲', 0.3)]               # 亥水：壬水本气，甲木中气
}

# 地支主五行（供快速判断）
DIZHI_WUXING: Dict[str, str] = {
    '子': '水', '丑': '土', '寅': '木', '卯': '木',
    '辰': '土', '巳': '火', '午': '火', '未': '土',
    '申': '金', '酉': '金', '戌': '土', '亥': '水',
}

SHENG_MAP: Dict[str, str] = {
    '木': '火',
    '火': '土',
    '土': '金',
    '金': '水',
    '水': '木',
}
SHENG_REVERSE: Dict[str, str] = {v: k for k, v in SHENG_MAP.items()}

KE_MAP: Dict[str, str] = {
    '木': '土',
    '土': '水',
    '水': '火',
    '火': '金',
    '金': '木',
}
KE_REVERSE: Dict[str, str] = {v: k for k, v in KE_MAP.items()}


def compute_wuxing_distribution(pillars: Dict[str, Tuple[str, str]]) -> Dict[str, float]:
    """
    计算五行分布（含藏干权重）
    Args:
        pillars: {'year': ('甲','子'), ...}
    Returns:
        dict: {'木': 3.2, '火': ...}
    """
    totals = {'木': 0.0, '火': 0.0, '土': 0.0, '金': 0.0, '水': 0.0}
    for gan, zhi in pillars.values():
        totals[TIANGAN_WUXING[gan]] += 1.0
        for hidden_gan, weight in DIZHI_CANGGAN_WEIGHTS[zhi]:
            totals[TIANGAN_WUXING[hidden_gan]] += weight
    return totals


@dataclass
class DayMasterProfile:
    element: str
    yin_yang: int
    strength: str
    support_power: float
    pressure_power: float
    distribution: Dict[str, float]


def evaluate_day_master_strength(pillars: Dict[str, Tuple[str, str]]) -> DayMasterProfile:
    """
    综合五行权重，评估日主强弱
    """
    distribution = compute_wuxing_distribution(pillars)
    day_gan = pillars['day'][0]
    day_element = TIANGAN_WUXING[day_gan]
    day_yin_yang = TIANGAN_YINYANG[day_gan]

    resource_element = SHENG_REVERSE[day_element]
    drain_element = SHENG_MAP[day_element]
    wealth_element = KE_MAP[day_element]
    officer_element = KE_REVERSE[day_element]

    support = distribution[day_element] + distribution[resource_element]
    pressure = distribution[drain_element] + distribution[wealth_element] + distribution[officer_element]

    # 🔥 修复：以支持力与制约力对比判定强弱，增加"中和"状态
    # 根据《子平真诠》理论：支持力与制约力相差不超过20%为中和
    ratio = support / pressure if pressure > 0 else 10.0  # 避免除零
    if ratio >= 1.5:
        strength = '旺'  # 偏强
    elif ratio >= 1.2:
        strength = '中旺'  # 中和偏强
    elif ratio >= 0.8:
        strength = '中和'  # 平衡
    elif ratio >= 0.67:
        strength = '中弱'  # 中和偏弱
    else:
        strength = '弱'  # 偏弱

    return DayMasterProfile(
        element=day_element,
        yin_yang=day_yin_yang,
        strength=strength,
        support_power=support,
        pressure_power=pressure,
        distribution=distribution,
    )


def summarize_branch_elements(zhi: str) -> Dict[str, float]:
    """
    汇总某地支藏干转换后的五行权重
    """
    totals = {'木': 0.0, '火': 0.0, '土': 0.0, '金': 0.0, '水': 0.0}
    for hidden_gan, weight in DIZHI_CANGGAN_WEIGHTS[zhi]:
        totals[TIANGAN_WUXING[hidden_gan]] += weight
    return totals


def summarize_ganzhi_elements(gan: str, zhi: str) -> Dict[str, float]:
    """
    汇总某天干地支组合的五行权重
    """
    totals = summarize_branch_elements(zhi)
    totals[TIANGAN_WUXING[gan]] += 1.0
    return totals


def get_ten_god(day_gan: str, other_gan: str) -> str:
    """
    推断日干与其它天干的十神关系
    根据《渊海子平》，程序顺序深报：
    1. 同五行 = 比肩/劫财
    2. 我克的 = 正财/偏财
    3. 克我的 = 正官/七杀
    4. 生我的 = 正印/偏印
    5. 我生的 = 食神/伤官
    """
    day_element = TIANGAN_WUXING[day_gan]
    target_element = TIANGAN_WUXING[other_gan]
    same_yang = TIANGAN_YINYANG[day_gan] == TIANGAN_YINYANG[other_gan]

    # 1. 同五行
    if day_element == target_element:
        return '比肩' if same_yang else '劫财'

    # 2. 我克的（优先级）
    if KE_MAP[day_element] == target_element:
        return '正财' if not same_yang else '偏财'

    # 3. 克我的
    if KE_MAP[target_element] == day_element:
        return '正官' if same_yang else '七杀'

    # 4. 生我的
    if SHENG_MAP[target_element] == day_element:
        # 🔥 修复：正印是生我者与我阴阳不同，偏印是生我者与我阴阳相同
        return '正印' if not same_yang else '偏印'

    # 5. 我生的
    if SHENG_MAP[day_element] == target_element:
        # 🔥 修复：食神是我生者与我阴阳相同，伤官是我生者与我阴阳不同
        return '食神' if same_yang else '伤官'

    return '未知'


def clamp_score(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    """
    辅助：限制分值区间
    """
    return max(lower, min(upper, value))
