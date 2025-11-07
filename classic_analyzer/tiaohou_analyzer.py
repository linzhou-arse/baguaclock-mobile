#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调候分析模块 - 基于《穷通宝鉴》理论
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from classic_analyzer.common import (
    DIZHI_CANGGAN_WEIGHTS,
    TIANGAN_WUXING,
    DIZHI_WUXING,
    get_ten_god,
    clamp_score,
)
from classic_analyzer.classic_texts import find_qiongtong_tiaohou_snippet



class TiaohouAnalyzer:
    """调候分析器 - 基于《穷通宝鉴》理论"""

    # 调候用神表（基于《穷通宝鉴》120种日主月令组合）
    # 格式：{日干: {月支: {'主用神': [], '辅用神': [], '说明': ''}}}
    # 经典依据：《穷通宝鉴》原文，按10天干×12月支=120种组合
    TIAOHOU_YONGSHEN = {
        '甲': {
            '寅': {'主': ['丙', '癸'], '辅': ['庚'], '说明': '正月甲木，初春尚有余寒，得丙癸逢，富贵双全'},
            '卯': {'主': ['庚'], '辅': ['丙', '丁'], '说明': '二月甲木，阳刃驾杀，庚金得所'},
            '辰': {'主': ['庚'], '辅': ['丁', '壬'], '说明': '三月甲木，先取庚金，次用壬水'},
            '巳': {'主': ['癸'], '辅': ['庚', '丁'], '说明': '四月甲木，先癸后丁，庚金次之'},
            '午': {'主': ['癸'], '辅': ['庚'], '说明': '五月甲木，木性虚焦，癸为第一'},
            '未': {'主': ['癸'], '辅': ['庚'], '说明': '六月甲木，同午月'},
            '申': {'主': ['庚'], '辅': ['丁', '壬'], '说明': '七月甲木，伐木宜庚，暖木宜丁'},
            '酉': {'主': ['庚'], '辅': ['丁'], '说明': '八月甲木，庚金坐禄，专用丁火制之'},
            '戌': {'主': ['庚'], '辅': ['甲', '丁'], '说明': '九月甲木，土旺宜疏'},
            '亥': {'主': ['庚'], '辅': ['丁', '丙'], '说明': '十月甲木，水冷木寒，丙火为尊'},
            '子': {'主': ['丁'], '辅': ['庚', '丙'], '说明': '十一月甲木，木寒宜丁，甲强用庚'},
            '丑': {'主': ['丁'], '辅': ['庚', '丙'], '说明': '十二月甲木，同子月'},
        },
        '乙': {
            '寅': {'主': ['丙'], '辅': ['癸'], '说明': '正月乙木，寒木向阳'},
            '卯': {'主': ['癸'], '辅': ['丙'], '说明': '二月乙木，旺木宜癸水滋润'},
            '辰': {'主': ['癸'], '辅': ['丙'], '说明': '三月乙木，湿土晦木，先用癸水'},
            '巳': {'主': ['癸'], '辅': [], '说明': '四月乙木，木性虚焦，专用癸水'},
            '午': {'主': ['癸'], '辅': ['丙'], '说明': '五月乙木，木枯宜癸'},
            '未': {'主': ['癸'], '辅': ['丙'], '说明': '六月乙木，同午月'},
            '申': {'主': ['丙'], '辅': ['癸'], '说明': '七月乙木，寒气渐生，丙火为先'},
            '酉': {'主': ['丙'], '辅': ['癸'], '说明': '八月乙木，同申月'},
            '戌': {'主': ['癸'], '辅': ['丙'], '说明': '九月乙木，土旺晦木，癸水为先'},
            '亥': {'主': ['丙'], '辅': [], '说明': '十月乙木，水旺木寒，专用丙火'},
            '子': {'主': ['丙'], '辅': [], '说明': '十一月乙木，同亥月'},
            '丑': {'主': ['丙'], '辅': [], '说明': '十二月乙木，同亥月'},
        },
        '丙': {
            '寅': {'主': ['壬'], '辅': ['庚'], '说明': '正月丙火，壬水为主，庚金发水源'},
            '卯': {'主': ['壬'], '辅': [], '说明': '二月丙火，专用壬水'},
            '辰': {'主': ['壬'], '辅': ['甲'], '说明': '三月丙火，土旺火晦，壬水为主'},
            '巳': {'主': ['壬'], '辅': [], '说明': '四月丙火，火旺宜壬'},
            '午': {'主': ['壬'], '辅': ['庚'], '说明': '五月丙火，专用壬水，庚金发源'},
            '未': {'主': ['壬'], '辅': ['庚'], '说明': '六月丙火，同午月'},
            '申': {'主': ['壬'], '辅': ['戊'], '说明': '七月丙火，壬水为用，戊土为佐'},
            '酉': {'主': ['壬'], '辅': [], '说明': '八月丙火，专用壬水'},
            '戌': {'主': ['壬'], '辅': ['甲'], '说明': '九月丙火，火土燥烈，壬甲为用'},
            '亥': {'主': ['戊'], '辅': ['甲'], '说明': '十月丙火，水旺宜戊土制之'},
            '子': {'主': ['戊'], '辅': ['壬'], '说明': '十一月丙火，水旺用戊，寒用壬'},
            '丑': {'主': ['戊'], '辅': ['壬'], '说明': '十二月丙火，同子月'},
        },
        '丁': {
            '寅': {'主': ['甲'], '辅': ['庚'], '说明': '正月丁火，甲木引丁，庚金劈甲'},
            '卯': {'主': ['甲'], '辅': ['庚'], '说明': '二月丁火，同寅月'},
            '辰': {'主': ['甲'], '辅': ['庚'], '说明': '三月丁火，土旺晦火，甲木为先'},
            '巳': {'主': ['甲'], '辅': ['庚'], '说明': '四月丁火，专用甲木'},
            '午': {'主': ['壬'], '辅': ['甲', '庚'], '说明': '五月丁火，火旺宜壬水'},
            '未': {'主': ['甲'], '辅': ['壬'], '说明': '六月丁火，甲木为主，壬水次之'},
            '申': {'主': ['甲'], '辅': ['庚', '丙'], '说明': '七月丁火，甲木引丁，庚金劈甲'},
            '酉': {'主': ['甲'], '辅': ['庚'], '说明': '八月丁火，同申月'},
            '戌': {'主': ['甲'], '辅': ['庚'], '说明': '九月丁火，土旺晦火，甲木为先'},
            '亥': {'主': ['甲'], '辅': ['庚'], '说明': '十月丁火，水旺木寒，甲木为先'},
            '子': {'主': ['甲'], '辅': ['庚'], '说明': '十一月丁火，同亥月'},
            '丑': {'主': ['甲'], '辅': ['庚'], '说明': '十二月丁火，同亥月'},
        },
        '戊': {
            '寅': {'主': ['丙', '甲'], '辅': ['癸'], '说明': '正月戊土，先丙后甲，癸水次之'},
            '卯': {'主': ['丙', '甲'], '辅': ['癸'], '说明': '二月戊土，同寅月'},
            '辰': {'主': ['甲', '丙'], '辅': ['癸'], '说明': '三月戊土，先甲后丙'},
            '巳': {'主': ['甲', '丙'], '辅': ['癸'], '说明': '四月戊土，先甲后丙癸'},
            '午': {'主': ['癸', '甲'], '辅': ['丙'], '说明': '五月戊土，先癸后甲'},
            '未': {'主': ['癸', '甲'], '辅': ['丙'], '说明': '六月戊土，同午月'},
            '申': {'主': ['丙', '癸'], '辅': ['甲'], '说明': '七月戊土，先丙后癸'},
            '酉': {'主': ['丙', '癸'], '辅': [], '说明': '八月戊土，同申月'},
            '戌': {'主': ['甲', '丙'], '辅': ['癸'], '说明': '九月戊土，先甲后丙'},
            '亥': {'主': ['甲', '丙'], '辅': [], '说明': '十月戊土，先甲后丙'},
            '子': {'主': ['丙', '甲'], '辅': [], '说明': '十一月戊土，先丙后甲'},
            '丑': {'主': ['丙', '甲'], '辅': [], '说明': '十二月戊土，同子月'},
        },
        '己': {
            '寅': {'主': ['丙'], '辅': ['癸'], '说明': '正月己土，先丙后癸'},
            '卯': {'主': ['甲'], '辅': ['癸'], '说明': '二月己土，先甲后癸'},
            '辰': {'主': ['丙'], '辅': ['癸'], '说明': '三月己土，先丙后癸'},
            '巳': {'主': ['癸'], '辅': ['丙'], '说明': '四月己土，先癸后丙'},
            '午': {'主': ['癸'], '辅': ['丙'], '说明': '五月己土，专用癸水'},
            '未': {'主': ['癸'], '辅': ['丙'], '说明': '六月己土，同午月'},
            '申': {'主': ['丙'], '辅': ['癸'], '说明': '七月己土，先丙后癸'},
            '酉': {'主': ['丙'], '辅': ['癸'], '说明': '八月己土，同申月'},
            '戌': {'主': ['甲'], '辅': ['丙'], '说明': '九月己土，先甲后丙'},
            '亥': {'主': ['丙'], '辅': ['甲'], '说明': '十月己土，先丙后甲'},
            '子': {'主': ['丙'], '辅': ['甲'], '说明': '十一月己土，同亥月'},
            '丑': {'主': ['丙'], '辅': ['甲'], '说明': '十二月己土，同亥月'},
        },
        '庚': {
            '寅': {'主': ['丁', '甲'], '辅': ['丙'], '说明': '正月庚金，丁甲并用'},
            '卯': {'主': ['丁', '甲'], '辅': ['庚'], '说明': '二月庚金，同寅月'},
            '辰': {'主': ['甲', '丁'], '辅': ['壬'], '说明': '三月庚金，先甲后丁'},
            '巳': {'主': ['壬', '癸'], '辅': ['丁'], '说明': '四月庚金，先壬后癸'},
            '午': {'主': ['壬'], '辅': ['癸'], '说明': '五月庚金，专用壬水'},
            '未': {'主': ['丁', '甲'], '辅': ['壬'], '说明': '六月庚金，先丁后甲'},
            '申': {'主': ['丁', '甲'], '辅': [], '说明': '七月庚金，丁甲并用'},
            '酉': {'主': ['丁', '甲'], '辅': [], '说明': '八月庚金，同申月'},
            '戌': {'主': ['甲', '壬'], '辅': [], '说明': '九月庚金，先甲后壬'},
            '亥': {'主': ['丁', '丙'], '辅': [], '说明': '十月庚金，先丁后丙'},
            '子': {'主': ['丁', '甲'], '辅': [], '说明': '十一月庚金，同亥月'},
            '丑': {'主': ['丁', '丙'], '辅': [], '说明': '十二月庚金，同亥月'},
        },
        '辛': {
            '寅': {'主': ['己', '壬'], '辅': [], '说明': '正月辛金，先己后壬'},
            '卯': {'主': ['壬'], '辅': ['甲'], '说明': '二月辛金，先壬后甲'},
            '辰': {'主': ['壬'], '辅': ['甲'], '说明': '三月辛金，同卯月'},
            '巳': {'主': ['壬'], '辅': ['甲'], '说明': '四月辛金，专用壬水'},
            '午': {'主': ['壬'], '辅': ['己'], '说明': '五月辛金，同巳月'},
            '未': {'主': ['壬'], '辅': ['己'], '说明': '六月辛金，同巳月'},
            '申': {'主': ['壬'], '辅': ['甲'], '说明': '七月辛金，专用壬水'},
            '酉': {'主': ['壬'], '辅': ['甲'], '说明': '八月辛金，同申月'},
            '戌': {'主': ['壬'], '辅': ['甲'], '说明': '九月辛金，火土为病，水木为药'},
            '亥': {'主': ['丙'], '辅': ['戊'], '说明': '十月辛金，先丙后戊'},
            '子': {'主': ['丙'], '辅': ['戊'], '说明': '十一月辛金，同亥月'},
            '丑': {'主': ['丙'], '辅': ['壬'], '说明': '十二月辛金，先丙后壬'},
        },
        '壬': {
            '寅': {'主': ['戊', '丙'], '辅': ['庚'], '说明': '正月壬水，先戊后丙'},
            '卯': {'主': ['庚'], '辅': ['戊', '丁'], '说明': '二月壬水，先庚后戊丁'},
            '辰': {'主': ['甲'], '辅': ['庚'], '说明': '三月壬水，先甲后庚'},
            '巳': {'主': ['壬', '辛'], '辅': ['庚'], '说明': '四月壬水，先壬后辛'},
            '午': {'主': ['壬', '辛'], '辅': ['庚'], '说明': '五月壬水，同巳月'},
            '未': {'主': ['辛', '甲'], '辅': [], '说明': '六月壬水，先辛后甲'},
            '申': {'主': ['戊', '丁'], '辅': [], '说明': '七月壬水，先戊后丁'},
            '酉': {'主': ['甲', '庚'], '辅': [], '说明': '八月壬水，先甲后庚'},
            '戌': {'主': ['甲', '丙'], '辅': [], '说明': '九月壬水，先甲后丙'},
            '亥': {'主': ['戊', '丙'], '辅': [], '说明': '十月壬水，先戊后丙'},
            '子': {'主': ['戊', '丙'], '辅': [], '说明': '十一月壬水，同亥月'},
            '丑': {'主': ['丙', '丁'], '辅': [], '说明': '十二月壬水，先丙后丁'},
        },
        '癸': {
            '寅': {'主': ['辛', '丙'], '辅': [], '说明': '正月癸水，先辛后丙'},
            '卯': {'主': ['庚'], '辅': ['辛'], '说明': '二月癸水，先庚后辛'},
            '辰': {'主': ['甲'], '辅': ['庚'], '说明': '三月癸水，先甲后庚'},
            '巳': {'主': ['辛'], '辅': ['庚'], '说明': '四月癸水，先辛后庚'},
            '午': {'主': ['庚', '辛'], '辅': [], '说明': '五月癸水，庚辛并用'},
            '未': {'主': ['辛'], '辅': ['庚'], '说明': '六月癸水，先辛后庚'},
            '申': {'主': ['丁'], '辅': ['甲'], '说明': '七月癸水，先丁后甲'},
            '酉': {'主': ['辛'], '辅': ['丙'], '说明': '八月癸水，先辛后丙'},
            '戌': {'主': ['辛', '甲'], '辅': [], '说明': '九月癸水，先辛后甲'},
            '亥': {'主': ['庚', '辛'], '辅': ['戊'], '说明': '十月癸水，先庚辛后戊'},
            '子': {'主': ['丙', '辛'], '辅': [], '说明': '十一月癸水，先丙后辛'},
            '丑': {'主': ['丙', '辛'], '辅': [], '说明': '十二月癸水，同子月'},
        },
    }

    # 季节表
    SEASON_TABLE = {
        '寅': '春', '卯': '春', '辰': '春',
        '巳': '夏', '午': '夏', '未': '夏',
        '申': '秋', '酉': '秋', '戌': '秋',
        '亥': '冬', '子': '冬', '丑': '冬',
    }

    @classmethod
    def analyze_tiaohou(cls, pillars: Dict[str, Tuple[str, str]], day_master: Optional[str] = None) -> Dict[str, Any]:
        """
        调候分析 - 基于《穷通宝鉴》理论

        参数:
            pillars: 四柱信息 {'year': ('甲','子'), 'month': ('乙','丑'), 'day': ('丙','寅'), 'hour': ('丁','卯')}
            day_master: 日主，如果为None则从日柱提取

        返回:
            调候分析结果
        """
        if not pillars or 'day' not in pillars:
            raise ValueError('分析调候需要完整的四柱信息')

        day_master = day_master or pillars['day'][0]
        month_branch = pillars['month'][1]

        # 1. 分析调候需求
        tiaohou_needs = cls._analyze_tiaohou_needs(day_master, month_branch, pillars)

        # 2. 分析调候用神
        tiaohou_yongshen = cls._analyze_tiaohou_yongshen(day_master, month_branch, pillars)

        # 3. 分析调候效果
        tiaohou_effect = cls._analyze_tiaohou_effect(tiaohou_needs, tiaohou_yongshen, pillars)

        # 4. 分析调候平衡
        tiaohou_balance = cls._analyze_tiaohou_balance(tiaohou_needs, tiaohou_yongshen, tiaohou_effect)

        return {
            'tiaohou_needs': tiaohou_needs,
            'tiaohou_yongshen': tiaohou_yongshen,
            'tiaohou_effect': tiaohou_effect,
            'tiaohou_balance': tiaohou_balance,
            'description': cls._get_tiaohou_description(tiaohou_needs, tiaohou_balance),
            'advice': cls._get_tiaohou_advice(tiaohou_needs, tiaohou_yongshen, tiaohou_balance),
            'classic_basis': cls._build_classic_basis(day_master, month_branch),
        }

    @classmethod
    def _analyze_tiaohou_needs(cls, day_master: str, month_branch: str, pillars: Dict[str, Tuple[str, str]]) -> Dict[str, Any]:
        """分析调候需求 - 基于《穷通宝鉴》120种组合"""
        # 确定季节
        season = cls.SEASON_TABLE.get(month_branch, '春')

        # ✅ 修复：使用120种组合表（日干×月支）
        tiaohou_table = cls.TIAOHOU_YONGSHEN.get(day_master, {})
        month_tiaohou = tiaohou_table.get(month_branch, {})  # 直接用月支，不用季节

        # 获取主用神和辅用神
        main_yongshen = month_tiaohou.get('主', [])
        aux_yongshen = month_tiaohou.get('辅', [])
        explanation = month_tiaohou.get('说明', '')

        # 分析寒暖燥湿（保留原有逻辑）
        han_nuan_zao_shi = cls._analyze_han_nuan_zao_shi(day_master, month_branch, pillars)

        # ✅ 修复：调候需求直接来自《穷通宝鉴》原文
        tiaohou_needs = main_yongshen + aux_yongshen

        return {
            'season': season,
            'han_nuan_zao_shi': han_nuan_zao_shi,
            'tiaohou_needs': tiaohou_needs,
            'main_yongshen': main_yongshen,
            'aux_yongshen': aux_yongshen,
            'explanation': explanation,
            'tiaohou_priority': cls._determine_tiaohou_priority(tiaohou_needs, han_nuan_zao_shi),
        }

    @classmethod
    def _analyze_han_nuan_zao_shi(cls, day_master: str, month_branch: str, pillars: Dict[str, Tuple[str, str]]) -> Dict[str, bool]:
        """分析寒暖燥湿"""
        # 简化版寒暖燥湿分析
        han_nuan_zao_shi = {
            '寒': False,
            '热': False,
            '湿': False,
            '燥': False,
        }

        # 基于月支判断寒暖
        if month_branch in ['亥', '子', '丑']:
            han_nuan_zao_shi['寒'] = True
        elif month_branch in ['巳', '午', '未']:
            han_nuan_zao_shi['热'] = True

        # 基于日主判断燥湿
        day_master_wuxing = TIANGAN_WUXING.get(day_master, '')
        if day_master_wuxing in ['木', '火']:
            han_nuan_zao_shi['燥'] = True
        elif day_master_wuxing in ['金', '水']:
            han_nuan_zao_shi['湿'] = True

        return han_nuan_zao_shi

    @classmethod
    def _determine_tiaohou_priority(cls, tiaohou_needs: List[str], han_nuan_zao_shi: Dict[str, bool]) -> List[str]:
        """确定调候优先级"""
        priority = []

        # 根据寒暖燥湿的严重程度确定优先级
        if han_nuan_zao_shi.get('寒', False):
            priority.append('火')
        if han_nuan_zao_shi.get('热', False):
            priority.append('水')
        if han_nuan_zao_shi.get('湿', False):
            priority.append('土')
        if han_nuan_zao_shi.get('燥', False):
            priority.append('水')

        return priority

    @classmethod
    def _analyze_tiaohou_yongshen(cls, day_master: str, month_branch: str, pillars: Dict[str, Tuple[str, str]]) -> Dict[str, Any]:
        """分析调候用神 - 基于《穷通宝鉴》120种组合"""
        # 获取调候需求
        tiaohou_needs = cls._analyze_tiaohou_needs(day_master, month_branch, pillars)
        main_yongshen = tiaohou_needs.get('main_yongshen', [])
        aux_yongshen = tiaohou_needs.get('aux_yongshen', [])

        # ✅ 修复：分析四柱中的调候用神（按天干查找，不按五行）
        main_found = []
        main_missing = []
        aux_found = []
        aux_missing = []

        # 检查主用神
        for yongshen in main_yongshen:
            found = False
            for pillar, pair in pillars.items():
                if isinstance(pair, (list, tuple)) and len(pair) >= 2:
                    gan, zhi = pair[0], pair[1]
                else:
                    continue

                # ✅ 修复：直接按天干查找，不转换五行
                if gan == yongshen:
                    main_found.append({
                        'yongshen': yongshen,
                        'position': pillar,
                        'gan': gan,
                        'type': '主用神',
                    })
                    found = True
                    break

            if not found:
                main_missing.append(yongshen)

        # 检查辅用神
        for yongshen in aux_yongshen:
            found = False
            for pillar, pair in pillars.items():
                if isinstance(pair, (list, tuple)) and len(pair) >= 2:
                    gan, zhi = pair[0], pair[1]
                else:
                    continue

                if gan == yongshen:
                    aux_found.append({
                        'yongshen': yongshen,
                        'position': pillar,
                        'gan': gan,
                        'type': '辅用神',
                    })
                    found = True
                    break

            if not found:
                aux_missing.append(yongshen)

        return {
            'main_yongshen': main_yongshen,
            'aux_yongshen': aux_yongshen,
            'main_found': main_found,
            'main_missing': main_missing,
            'aux_found': aux_found,
            'aux_missing': aux_missing,
            'yongshen_found': main_found + aux_found,
            'yongshen_missing': main_missing + aux_missing,
            'yongshen_count': len(main_found) + len(aux_found),
            'yongshen_quality': cls._evaluate_yongshen_quality(yongshen_found, needs),
        }

    @classmethod
    def _evaluate_yongshen_quality(cls, yongshen_found: List[Dict[str, Any]], needs: List[str]) -> str:
        """评估用神质量"""
        if len(yongshen_found) == len(needs):
            return '上等'
        elif len(yongshen_found) > 0:
            return '中等'
        else:
            return '下等'

    @classmethod
    def _analyze_tiaohou_effect(cls, tiaohou_needs: Dict[str, Any], tiaohou_yongshen: Dict[str, Any], pillars: Dict[str, Tuple[str, str]]) -> Dict[str, Any]:
        """分析调候效果 - 基于《穷通宝鉴》理论"""
        needs = tiaohou_needs.get('tiaohou_needs', [])
        yongshen_found = tiaohou_yongshen.get('yongshen_found', [])

        # ✅ 修复：直接判断效果等级，不计算评分
        found_count = len(yongshen_found)
        needs_count = len(needs)

        if needs_count == 0:
            effect_level = '无需调候'
        elif found_count >= needs_count:
            effect_level = '上等'
        elif found_count >= needs_count * 0.6:
            effect_level = '中等'
        elif found_count >= needs_count * 0.4:
            effect_level = '下等'
        else:
            effect_level = '很差'

        # 分析调候平衡
        balance = cls._analyze_tiaohou_balance_detail(needs, yongshen_found)

        return {
            'effect_level': effect_level,
            'balance': balance,
        }

    @classmethod
    def _analyze_tiaohou_balance_detail(cls, needs: List[str], yongshen_found: List[Dict[str, Any]]) -> str:
        """分析调候平衡详情"""
        if not needs:
            return '无需调候'

        found_count = len(yongshen_found)
        needs_count = len(needs)

        if found_count == needs_count:
            return '调候平衡'
        elif found_count > needs_count:
            return '调候过旺'
        else:
            return '调候不足'

    @classmethod
    def _analyze_tiaohou_balance(cls, tiaohou_needs: Dict[str, Any], tiaohou_yongshen: Dict[str, Any], tiaohou_effect: Dict[str, Any]) -> Dict[str, Any]:
        """分析调候平衡 - 基于《穷通宝鉴》理论"""
        needs = tiaohou_needs.get('tiaohou_needs', [])
        yongshen_found = tiaohou_yongshen.get('yongshen_found', [])

        # ✅ 修复：直接判断平衡等级，不计算评分
        found_count = len(yongshen_found)
        needs_count = len(needs)

        if needs_count == 0:
            balance_level = '无需调候'
        elif found_count >= needs_count:
            balance_level = '平衡'
        elif found_count >= needs_count * 0.6:
            balance_level = '较平衡'
        elif found_count >= needs_count * 0.4:
            balance_level = '不平衡'
        else:
            balance_level = '严重不平衡'

        # 分析调候缺失
        missing_yongshen = tiaohou_yongshen.get('yongshen_missing', [])

        # 分析调候过旺
        over_wang_yongshen = []
        if len(yongshen_found) > len(needs):
            over_wang_yongshen = [y['yongshen'] for y in yongshen_found[len(needs):]]

        return {
            'balance_level': balance_level,
            'missing_yongshen': missing_yongshen,
            'over_wang_yongshen': over_wang_yongshen,
        }

    @classmethod
    def _get_tiaohou_description(cls, tiaohou_needs: Dict[str, Any], tiaohou_balance: Dict[str, Any]) -> str:
        """获取调候描述"""
        needs = tiaohou_needs.get('tiaohou_needs', [])
        balance_level = tiaohou_balance.get('balance_level', '不平衡')

        if not needs:
            return '无需调候'

        desc = f"调候{balance_level}"
        if needs:
            desc += f"，需要{''.join(needs)}"

        return desc

    @classmethod
    def _get_tiaohou_advice(cls, tiaohou_needs: Dict[str, Any], tiaohou_yongshen: Dict[str, Any], tiaohou_balance: Dict[str, Any]) -> str:
        """获取调候建议"""
        needs = tiaohou_needs.get('tiaohou_needs', [])
        yongshen_found = tiaohou_yongshen.get('yongshen_found', [])
        balance_level = tiaohou_balance.get('balance_level', '不平衡')

        if not needs:
            return '无需调候，保持现状即可'

        if balance_level == '平衡':
            return '调候平衡，宜保持现状，注重协调发展'
        elif len(yongshen_found) < len(needs):
            missing = tiaohou_balance.get('missing_yongshen', [])
            return f'调候不足，需要补充{"".join(missing)}，注重环境调节'
        else:
            return '调候过旺，宜适度调节，避免过度'
    @classmethod
    def _build_classic_basis(cls, day_master: str, month_branch: str) -> str:
        """✅ 修复：给出调候分析的经典依据引用，直接从120种组合表中获取"""
        tiaohou_table = cls.TIAOHOU_YONGSHEN.get(day_master, {})
        month_tiaohou = tiaohou_table.get(month_branch, {})
        explanation = month_tiaohou.get('说明', '')

        if explanation:
            return f'《穷通宝鉴》：{explanation}'

        # 如果没有找到，尝试使用原文片段
        snippet = find_qiongtong_tiaohou_snippet(day_master, month_branch)
        if snippet:
            return snippet

        return '《子平真诠》：论命惟以月令用神为主，然亦须配气候而互参之。'
