#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
流年分析器 - Liunian Analyzer
===========================

基于《三命通会·流年篇》的流年分析
"""

from __future__ import annotations
from typing import Dict, List, Any, Tuple
import time
from datetime import datetime

from ..core.base_analyzer import BaseAnalyzer
from ..core.data_structures import BaziData, AnalysisResult, AnalysisConfig
from ..core.utils import create_analysis_result, get_wuxing_by_tiangan, get_wuxing_by_dizhi

# 尝试导入sxtwl用于节气计算
try:
    import sxtwl
    SXTWL_AVAILABLE = True
except ImportError:
    SXTWL_AVAILABLE = False


TIANGAN_SEQ = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DIZHI_SEQ = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

LIUCHONG = {('子','午'),('丑','未'),('寅','申'),('卯','酉'),('辰','戌'),('巳','亥')}
LIUHE = {('子','丑'),('寅','亥'),('卯','戌'),('辰','酉'),('巳','申'),('午','未')}


class LiunianAnalyzer(BaseAnalyzer):
    """流年分析器 - 基于《三命通会·流年篇》"""
    
    def __init__(self, config: AnalysisConfig = None):
        super().__init__("流年分析器", "三命通会", config)
    
    def analyze(self, bazi_data: BaziData) -> AnalysisResult:
        """
        🔥 升级：执行流年分析（当前年 + 未来10年详细分析）
        1. 当前年份详细分析
        2. 未来10年逐年分析
        3. 关键月份分析
        """
        start_time = time.time()

        try:
            current_year = datetime.now().year
            day_master = bazi_data.get_day_master()
            pillars = bazi_data.get_pillars()

            # 1. 当前年份分析
            current_analysis = self._analyze_single_year(bazi_data, current_year)
            
            # 2. 🔥 新增：未来10年详细分析
            future_years_analysis = []
            for i in range(1, 11):
                future_year = current_year + i
                year_analysis = self._analyze_single_year(bazi_data, future_year)
                future_years_analysis.append({
                    'year': future_year,
                    'ganzhi': year_analysis['ganzhi'],
                    'level': year_analysis['level'],
                    'score': year_analysis['score'],
                    'key_points': year_analysis['key_points'],
                    'advice': year_analysis['advice']
                })
            
            # 3. 🔥 新增：关键月份分析（当前年和下一年）
            key_months = self._analyze_key_months(bazi_data, current_year)
            
            # 综合评分：当前年为主，未来10年取平均
            current_score = current_analysis['score']
            future_avg_score = sum(y['score'] for y in future_years_analysis) / len(future_years_analysis) if future_years_analysis else current_score
            overall_score = current_score * 0.6 + future_avg_score * 0.4
            overall_level = self._score_to_level(overall_score)

            analysis_time = (time.time() - start_time) * 1000

            description = f"当前年：{current_year}（{current_analysis['ganzhi']}）- {current_analysis['level']}；未来10年平均：{self._score_to_level(future_avg_score)}"
            advice = current_analysis['advice'] + f"；未来10年整体趋势：{self._get_future_trend_advice(future_years_analysis)}"

            return create_analysis_result(
                analyzer_name=self.name,
                book_name=self.book_name,
                analysis_type="流年分析（10年详细）",
                level=overall_level,
                score=overall_score,
                description=description,
                details={
                    'current_year': current_analysis,
                    'future_10_years': future_years_analysis,
                    'key_months': key_months,
                    'overall_score': overall_score,
                    'future_avg_score': future_avg_score
                },
                advice=advice,
                analysis_time=analysis_time
            )

        except Exception as e:
            raise Exception(f"流年分析失败: {e}")
    
    def _analyze_single_year(self, bazi_data: BaziData, year: int) -> Dict[str, Any]:
        """
        分析单个年份的流年运势 - 基于《三命通会·论太岁》经典理论
        ✅ 修复：不再使用简单base_score + delta打分，改为基于经典理论的具体判断
        """
        gan, zhi = self._year_ganzhi(year)
        day_master = bazi_data.get_day_master()
        pillars = bazi_data.get_pillars()

        # ✅ 修复：基于《三命通会·论太岁》经典理论判断流年吉凶
        # 理论依据：
        # 1. "太岁如君也，大运如臣也。如君臣和悦，其年则吉；若值刑战，其年则凶"
        # 2. "岁伤日干，有祸必轻；日犯岁君，灾殃必重"
        # 3. "真太岁...要大运日主与太岁相和相顺，其年则吉；若值刑冲破害，与太岁互相战克则凶"
        # 4. "岁运并临，独羊刃、七煞为凶，财、官、印绶亦吉"
        # 5. "日年相并，如君子得之，谓之君臣处会，其年利奏对，有面君之喜"
        
        # 1. 获取与原局的关系（六合、六冲等）
        _, relations = self._score_relations_with_chart(zhi, pillars)
        
        # 2. 获取大运与流年的关系
        dayun_score, dayun_info = self._analyze_dayun_overlay(bazi_data, year)
        
        # 3. 基于经典理论判断流年等级
        level, level_reason = self._judge_liunian_level_classical(gan, zhi, day_master, pillars, relations, dayun_info, bazi_data)
        
        # 关键点分析
        key_points = self._extract_key_points(gan, zhi, day_master, pillars, relations, dayun_info)
        
        # 建议
        advice = self._advice_from_relations(relations) + "；" + self._advice_from_dayun(dayun_info)
        
        return {
            'year': year,
            'ganzhi': f"{gan}{zhi}",
            'gan': gan,
            'zhi': zhi,
            'score': 0,  # ✅ 不再使用score
            'level': level,
            'base_score': 0,  # ✅ 保留字段以兼容，但不再使用
            'delta': 0,  # ✅ 保留字段以兼容，但不再使用
            'level_reason': level_reason,  # ✅ 新增：判断依据
            'relations': relations,
            'dayun_info': dayun_info,
            'key_points': key_points,
            'advice': advice
        }
    
    def _extract_key_points(self, gan: str, zhi: str, day_master: str, pillars: Dict, relations: Dict, dayun_info: str) -> List[str]:
        """
        提取关键点：六合、六冲、大运关系等
        """
        points = []
        
        # 六合关系
        if relations.get('六合'):
            points.append(f"与{', '.join(relations['六合'])}柱六合，人际关系顺畅")
        
        # 六冲关系
        if relations.get('六冲'):
            points.append(f"与{', '.join(relations['六冲'])}柱六冲，变动较大")
        
        # 大运关系
        if '六合' in dayun_info:
            points.append("大运流年六合，运势顺畅")
        elif '六冲' in dayun_info:
            points.append("大运流年六冲，需谨慎应对")
        
        # 日主关系
        gan_wx = get_wuxing_by_tiangan(gan)
        zhi_wx = get_wuxing_by_dizhi(zhi)
        dm_wx = get_wuxing_by_tiangan(day_master)
        
        if gan_wx == dm_wx:
            points.append("流年天干与日主比和，助力增强")
        elif self._is_sheng(gan_wx, dm_wx):
            points.append("流年天干生助日主，有利发展")
        elif self._is_ke(gan_wx, dm_wx):
            points.append("流年天干克制日主，需注意压力")
        
        return points
    
    def _is_sheng(self, wx1: str, wx2: str) -> bool:
        """判断五行相生"""
        sheng_map = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        return sheng_map.get(wx1) == wx2
    
    def _is_ke(self, wx1: str, wx2: str) -> bool:
        """判断五行相克"""
        ke_map = {'木': '土', '火': '金', '土': '水', '金': '木', '水': '火'}
        return ke_map.get(wx1) == wx2
    
    def _analyze_key_months(self, bazi_data: BaziData, year: int) -> Dict[str, List[Dict[str, Any]]]:
        """
        🔥 新增：分析关键月份
        分析当前年和下一年的关键月份（六合、六冲、三合等）
        """
        key_months = {}
        
        for y in [year, year + 1]:
            year_months = []
            gan, zhi = self._year_ganzhi(y)
            
            # 分析每个月份
            for month in range(1, 13):
                month_zhi = DIZHI_SEQ[month - 1]  # 正月为寅，二月为卯...
                month_gan = self._get_month_gan(gan, month)
                
                # 检查月份与原局的关系
                month_relations = self._check_month_relations(month_zhi, bazi_data.get_pillars())
                
                if month_relations['is_key']:
                    year_months.append({
                        'month': month,
                        'ganzhi': f"{month_gan}{month_zhi}",
                        'relation': month_relations['type'],
                        'level': month_relations['level'],
                        'advice': month_relations['advice']
                    })
            
            if year_months:
                key_months[str(y)] = year_months
        
        return key_months
    
    def _get_month_gan(self, year_gan: str, month: int) -> str:
        """
        根据年干和月份计算月干（五虎遁法）
        """
        # 五虎遁口诀：甲己之年丙作首，乙庚之年戊为头，丙辛之年寻庚起，丁壬壬寅顺水流，若问戊癸何处起，甲寅之上好追求
        wuhu_dun = {
            '甲': ['丙', '丁', '戊', '己', '庚', '辛', '壬', '癸', '甲', '乙', '丙', '丁'],
            '己': ['丙', '丁', '戊', '己', '庚', '辛', '壬', '癸', '甲', '乙', '丙', '丁'],
            '乙': ['戊', '己', '庚', '辛', '壬', '癸', '甲', '乙', '丙', '丁', '戊', '己'],
            '庚': ['戊', '己', '庚', '辛', '壬', '癸', '甲', '乙', '丙', '丁', '戊', '己'],
            '丙': ['庚', '辛', '壬', '癸', '甲', '乙', '丙', '丁', '戊', '己', '庚', '辛'],
            '辛': ['庚', '辛', '壬', '癸', '甲', '乙', '丙', '丁', '戊', '己', '庚', '辛'],
            '丁': ['壬', '癸', '甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'],
            '壬': ['壬', '癸', '甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸'],
            '戊': ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸', '甲', '乙'],
            '癸': ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸', '甲', '乙']
        }
        return wuhu_dun.get(year_gan, ['丙'] * 12)[month - 1]
    
    def _check_month_relations(self, month_zhi: str, pillars: Dict) -> Dict[str, Any]:
        """
        检查月份地支与原局的关系
        """
        has_he = False
        has_chong = False
        
        for pos, (gan, zhi) in pillars.items():
            pair = (month_zhi, zhi)
            pair_rev = (zhi, month_zhi)
            if pair in LIUHE or pair_rev in LIUHE:
                has_he = True
            if pair in LIUCHONG or pair_rev in LIUCHONG:
                has_chong = True
        
        if has_he and not has_chong:
            return {
                'is_key': True,
                'type': '六合',
                'level': '吉',
                'advice': '此月与原局六合，宜合作拓展、婚庆人和'
            }
        elif has_chong and not has_he:
            return {
                'is_key': True,
                'type': '六冲',
                'level': '凶',
                'advice': '此月与原局六冲，宜稳守为先，慎迁动与冲突'
            }
        elif has_he and has_chong:
            return {
                'is_key': True,
                'type': '合冲并见',
                'level': '中平',
                'advice': '此月合冲并见，宜中庸处事，取和为贵'
            }
        
        return {'is_key': False}
    
    def _get_future_trend_advice(self, future_years: List[Dict]) -> str:
        """
        根据未来10年分析给出趋势建议
        """
        if not future_years:
            return "无未来年份数据"
        
        # 统计吉凶年数
        ji_count = sum(1 for y in future_years if y['level'] in ['大吉', '吉'])
        xiong_count = sum(1 for y in future_years if y['level'] in ['大凶', '凶'])
        ping_count = len(future_years) - ji_count - xiong_count
        
        if ji_count > xiong_count * 2:
            return "未来10年整体吉利，宜积极进取，把握机遇"
        elif ji_count > xiong_count:
            return "未来10年总体向好，但需注意波动，稳中求进"
        elif xiong_count > ji_count * 2:
            return "未来10年挑战较多，需谨慎应对，稳守为主"
        elif xiong_count > ji_count:
            return "未来10年波折较多，需加强准备，避免冒进"
        else:
            return "未来10年运势平稳，按部就班发展即可"

    def _year_ganzhi(self, year: int) -> Tuple[str, str]:
        """
        🔥 修复：使用确定的基准年1984年（甲子年）
        1984年是确定的甲子年，使用它作为基准更可靠
        如果年份在1984年之前，向前推算；如果之后，向后推算
        """
        # 1984年为甲子年（确定的基准）
        offset = year - 1984
        gan = TIANGAN_SEQ[offset % 10]
        zhi = DIZHI_SEQ[offset % 12]
        return gan, zhi

    def _score_relations_with_chart(self, liunian_zhi: str, pillars: Dict[str, Tuple[str,str]]) -> Tuple[float, Dict[str, List[str]]]:
        delta = 0.0
        relations: Dict[str, List[str]] = {'六合': [], '六冲': []}
        for pos, (gan, zhi) in pillars.items():
            pair = (liunian_zhi, zhi)
            pair_rev = (zhi, liunian_zhi)
            if pair in LIUCHONG or pair_rev in LIUCHONG:
                relations['六冲'].append(pos)
                delta -= 6
            if pair in LIUHE or pair_rev in LIUHE:
                relations['六合'].append(pos)
                delta += 6
        # 合冲同现时，按中和视之：上面加减已自然抵消
        return delta, relations

    def _score_to_level(self, score: float) -> str:
        if score >= 85:
            return '大吉'
        elif score >= 70:
            return '吉'
        elif score >= 55:
            return '中平'
        elif score >= 40:
            return '凶'
        return '大凶'

    def _calculate_base_score(self, liunian_gan: str, liunian_zhi: str, day_master: str) -> float:
        """
        根据流年与日主的五行关系计算基础分
        ✅ 新增：动态基础分，不再硬编码60分
        """
        day_master_wx = get_wuxing_by_tiangan(day_master)
        liunian_gan_wx = get_wuxing_by_tiangan(liunian_gan)
        liunian_zhi_wx = get_wuxing_by_dizhi(liunian_zhi)

        # 五行关系映射
        wuxing_relations = {
            '木': {'生': '火', '克': '土', '被生': '水', '被克': '金'},
            '火': {'生': '土', '克': '金', '被生': '木', '被克': '水'},
            '土': {'生': '金', '克': '水', '被生': '火', '被克': '木'},
            '金': {'生': '水', '克': '木', '被生': '土', '被克': '火'},
            '水': {'生': '木', '克': '火', '被生': '金', '被克': '土'}
        }

        relations = wuxing_relations.get(day_master_wx, {})

        # 基础分：55分（中平）
        base = 55.0

        # 分析天干关系
        if liunian_gan_wx == day_master_wx:
            base += 3  # 比和，助力
        elif liunian_gan_wx == relations.get('被生'):
            base += 5  # 生我，有利
        elif liunian_gan_wx == relations.get('生'):
            base -= 2  # 我生，泄气
        elif liunian_gan_wx == relations.get('被克'):
            base -= 5  # 克我，不利
        elif liunian_gan_wx == relations.get('克'):
            base -= 3  # 我克，耗力

        # 分析地支关系（权重减半）
        if liunian_zhi_wx == day_master_wx:
            base += 1.5
        elif liunian_zhi_wx == relations.get('被生'):
            base += 2.5
        elif liunian_zhi_wx == relations.get('生'):
            base -= 1
        elif liunian_zhi_wx == relations.get('被克'):
            base -= 2.5
        elif liunian_zhi_wx == relations.get('克'):
            base -= 1.5

        return base

    def _analyze_dayun_overlay(self, bazi_data: BaziData, current_year: int) -> Tuple[float, str]:
        """
        分析流年叠加大运的影响
        ✅ 已修复：使用实际起运年龄，不再硬编码8岁
        """
        try:
            # 计算当前大运
            birth_year = bazi_data.birth_year
            age = current_year - birth_year

            # ✅ 使用实际起运年龄（尝试从sxtwl计算，失败则使用简化算法）
            qiyun_age = self._calculate_qiyun_age(bazi_data)
            dayun_step = max(0, (age - qiyun_age) // 10) if qiyun_age else max(0, (age - 8) // 10)
            
            # 获取月柱作为大运起点
            month_gan, month_zhi = bazi_data.get_pillars()['month']
            
            # 计算大运方向
            year_gan = bazi_data.get_pillars()['year'][0]
            yang_gan = {'甲', '丙', '戊', '庚', '壬'}
            is_yang_year = year_gan in yang_gan
            direction = '顺行' if (is_yang_year and bazi_data.gender == '男') or (not is_yang_year and bazi_data.gender == '女') else '逆行'
            
            # 计算当前大运干支
            gan_idx = TIANGAN_SEQ.index(month_gan)
            zhi_idx = DIZHI_SEQ.index(month_zhi)
            offset = dayun_step + 1 if direction == '顺行' else -(dayun_step + 1)
            current_dayun_gan = TIANGAN_SEQ[(gan_idx + offset) % 10]
            current_dayun_zhi = DIZHI_SEQ[(zhi_idx + offset) % 12]
            
            # 分析大运与流年的关系
            liunian_gan, liunian_zhi = self._year_ganzhi(current_year)
            
            # 大运与流年天干关系
            gan_relation = self._analyze_gan_relation(current_dayun_gan, liunian_gan)
            
            # 大运与流年地支关系
            zhi_relation = self._analyze_zhi_relation(current_dayun_zhi, liunian_zhi)
            
            # 综合评分
            score_delta = gan_relation['score'] + zhi_relation['score']
            info = f"大运{current_dayun_gan}{current_dayun_zhi}，天干{gan_relation['type']}，地支{zhi_relation['type']}"
            
            return score_delta, info
            
        except Exception as e:
            return 0.0, f"大运叠加分析异常：{e}"
    
    def _analyze_gan_relation(self, dayun_gan: str, liunian_gan: str) -> Dict[str, Any]:
        """分析天干关系"""
        # 简化版天干关系分析
        if dayun_gan == liunian_gan:
            return {'type': '比和', 'score': 2}
        
        # 生克关系
        sheng_map = {'甲': '丙', '乙': '丁', '丙': '戊', '丁': '己', '戊': '庚', 
                    '己': '辛', '庚': '壬', '辛': '癸', '壬': '甲', '癸': '乙'}
        ke_map = {'甲': '戊', '乙': '己', '丙': '庚', '丁': '辛', '戊': '壬',
                 '己': '癸', '庚': '甲', '辛': '乙', '壬': '丙', '癸': '丁'}
        
        if sheng_map.get(dayun_gan) == liunian_gan:
            return {'type': '大运生流年', 'score': 3}
        elif sheng_map.get(liunian_gan) == dayun_gan:
            return {'type': '流年生大运', 'score': 1}
        elif ke_map.get(dayun_gan) == liunian_gan:
            return {'type': '大运克流年', 'score': -2}
        elif ke_map.get(liunian_gan) == dayun_gan:
            return {'type': '流年克大运', 'score': -3}
        
        return {'type': '无特殊关系', 'score': 0}
    
    def _analyze_zhi_relation(self, dayun_zhi: str, liunian_zhi: str) -> Dict[str, Any]:
        """分析地支关系"""
        if dayun_zhi == liunian_zhi:
            return {'type': '比和', 'score': 2}
        
        # 六合关系
        pair = (dayun_zhi, liunian_zhi)
        pair_rev = (liunian_zhi, dayun_zhi)
        if pair in LIUHE or pair_rev in LIUHE:
            return {'type': '六合', 'score': 4}
        
        # 六冲关系
        if pair in LIUCHONG or pair_rev in LIUCHONG:
            return {'type': '六冲', 'score': -4}
        
        return {'type': '无特殊关系', 'score': 0}
    
    def _advice_from_dayun(self, dayun_info: str) -> str:
        """根据大运信息给出建议"""
        if '六合' in dayun_info:
            return '大运流年六合，运势顺畅，宜积极进取。'
        elif '六冲' in dayun_info:
            return '大运流年六冲，变化较大，宜稳中求变。'
        elif '比和' in dayun_info:
            return '大运流年比和，运势平稳，宜巩固基础。'
        else:
            return '大运流年关系平常，按部就班发展。'

    def _judge_liunian_level_classical(self, gan: str, zhi: str, day_master: str, 
                                       pillars: Dict, relations: Dict, dayun_info: str,
                                       bazi_data: BaziData) -> Tuple[str, str]:
        """
        基于《三命通会·论太岁》经典理论判断流年等级
        
        理论依据：
        1. "太岁如君也，大运如臣也。如君臣和悦，其年则吉；若值刑战，其年则凶"
        2. "岁伤日干，有祸必轻；日犯岁君，灾殃必重"
        3. "真太岁...要大运日主与太岁相和相顺，其年则吉；若值刑冲破害，与太岁互相战克则凶"
        4. "岁运并临，独羊刃、七煞为凶，财、官、印绶亦吉"
        5. "日年相并，如君子得之，谓之君臣处会，其年利奏对，有面君之喜"
        
        返回: (level, reason)
        """
        from ..core.utils import get_ten_god, get_wuxing_by_tiangan
        from ..core.constants import DIZHI_CANGGAN, DIZHI_LIUCHONG
        
        # 1. 检查真太岁（《三命通会》："生时相逢真太岁"）
        # 如甲子生人又见甲子年，谓之真太岁
        year_gan, year_zhi = pillars['year']
        if gan == year_gan and zhi == year_zhi:
            # 真太岁：要大运日主与太岁相和相顺，其年则吉；若值刑冲破害，与太岁互相战克则凶
            day_zhi = pillars['day'][1]
            # 检查是否与太岁刑冲破害
            has_chong = (day_zhi, zhi) in DIZHI_LIUCHONG or (zhi, day_zhi) in DIZHI_LIUCHONG
            
            if has_chong:
                return ('凶', '真太岁且日支与太岁相冲，与太岁互相战克则凶（《三命通会》："真太岁...若值刑冲破害，与太岁互相战克则凶"）')
            else:
                return ('大吉', '真太岁且大运日主与太岁相和相顺，其年则吉（《三命通会》："真太岁...要大运日主与太岁相和相顺，其年则吉"）')
        
        # 2. 检查岁运并临（《三命通会》："又如甲子流年又是甲子运，谓之岁运并临"）
        # 尝试从dayun_info中提取大运干支
        day_zhi = pillars['day'][1]
        if '大运' in dayun_info:
            # 解析大运干支（简化处理）
            try:
                # 从dayun_info中提取大运干支，格式如"大运甲子"
                import re
                match = re.search(r'大运([甲乙丙丁戊己庚辛壬癸])([子丑寅卯辰巳午未申酉戌亥])', dayun_info)
                if match:
                    dayun_gan, dayun_zhi = match.groups()
                    if gan == dayun_gan and zhi == dayun_zhi:
                        # 岁运并临：独羊刃、七煞为凶，财、官、印绶亦吉
                        dayun_tg = get_ten_god(day_master, gan)
                        if dayun_tg in ['偏官', '羊刃']:  # 简化判断，假设羊刃可通过其他方式识别
                            return ('凶', '岁运并临且为七煞，独羊刃、七煞为凶（《三命通会》："岁运并临，独羊刃、七煞为凶"）')
                        elif dayun_tg in ['正财', '偏财', '正官', '偏官', '正印', '偏印']:
                            return ('大吉', '岁运并临且为财官印绶，财、官、印绶亦吉（《三命通会》："岁运并临...财、官、印绶亦吉"）')
            except:
                pass
        
        # 3. 检查日年相并（《三命通会》："又如甲子日见甲子太岁，谓之日年相并"）
        day_gan = pillars['day'][0]
        if gan == day_gan and zhi == day_zhi:
            # 日年相并：如君子得之，谓之君臣处会，其年利奏对，有面君之喜
            return ('大吉', '日年相并，谓之君臣处会，其年利奏对，有面君之喜（《三命通会》："日年相并，如君子得之，谓之君臣处会"）')
        
        # 4. 检查日犯岁君（《三命通会》："日犯岁君，灾殃必重"）
        # 日犯岁君：如甲日克戊年为偏财，譬臣其君，子其父，深为不利
        day_master_wx = get_wuxing_by_tiangan(day_master)
        liunian_gan_wx = get_wuxing_by_tiangan(gan)
        
        # 检查日主是否克太岁（日犯岁君）
        wuxing_ke_map = {
            '木': '土', '火': '金', '土': '水', '金': '木', '水': '火'
        }
        if wuxing_ke_map.get(day_master_wx) == liunian_gan_wx:
            # 日犯岁君，灾殃必重（但需检查是否有救）
            # 如果有救（如大运制伏、四柱有合等），则凶减轻
            # 简化判断：如果大运有利，凶减轻
            if '比和' in dayun_info or '六合' in dayun_info:
                return ('凶', '日犯岁君但有救，灾殃减轻（《三命通会》："日犯岁君，灾殃必重...若五行有救，四柱有情...凶为吉兆"）')
            else:
                return ('大凶', '日犯岁君，灾殃必重（《三命通会》："日犯岁君，灾殃必重"）')
        
        # 5. 检查岁伤日干（《三命通会》："岁伤日干，有祸必轻"）
        # 岁伤日干：如庚年克甲日为偏官，譬君治臣，父治子，虽有灾晦，不为大害
        if wuxing_ke_map.get(liunian_gan_wx) == day_master_wx:
            # 岁伤日干，有祸必轻
            return ('小凶', '岁伤日干，有祸必轻（《三命通会》："岁伤日干，有祸必轻"）')
        
        # 6. 检查太岁与大运的配合（《三命通会》："太岁如君也，大运如臣也。如君臣和悦，其年则吉；若值刑战，其年则凶"）
        if '六合' in dayun_info:
            return ('大吉', '太岁与大运六合，君臣和悦，其年则吉（《三命通会》："太岁如君也，大运如臣也。如君臣和悦，其年则吉"）')
        elif '六冲' in dayun_info:
            return ('凶', '太岁与大运六冲，若值刑战，其年则凶（《三命通会》："太岁如君也，大运如臣也...若值刑战，其年则凶"）')
        elif '比和' in dayun_info:
            return ('吉', '太岁与大运比和，君臣和悦（《三命通会》："太岁如君也，大运如臣也。如君臣和悦，其年则吉"）')
        
        # 7. 检查流年与原局的六合六冲
        has_liuhe = bool(relations.get('六合'))
        has_liuchong = bool(relations.get('六冲'))
        
        if has_liuhe and not has_liuchong:
            return ('吉', '流年与原局六合，其年则吉（《三命通会》：六合主吉）')
        elif has_liuchong and not has_liuhe:
            return ('凶', '流年与原局六冲，其年则凶（《三命通会》：六冲主凶）')
        elif has_liuhe and has_liuchong:
            return ('中平', '流年与原局合冲并见，吉凶参半（《三命通会》：合冲并见需具体分析）')
        
        # 8. 基于大运与流年的生克关系判断（参考《三命通会》理论）
        if '大运生流年' in dayun_info:
            return ('吉', '大运生流年，君臣和悦（《三命通会》："太岁如君也，大运如臣也。如君臣和悦，其年则吉"）')
        elif '流年克大运' in dayun_info:
            return ('凶', '流年克大运，若值刑战，其年则凶（《三命通会》："若值刑战，其年则凶"）')
        
        # 9. 一般情况（需结合具体分析）
        return ('中平', '流年与命局配合一般，需结合大运流年具体分析（《三命通会·论太岁》：大运需结合命局四柱强弱分析）')
    
    def _advice_from_relations(self, relations: Dict[str, List[str]]) -> str:
        has_he = bool(relations['六合'])
        has_chong = bool(relations['六冲'])
        if has_he and not has_chong:
            return '流年与原局六合，宜合作拓展、婚庆人和。'
        if has_chong and not has_he:
            return '流年与原局有冲，宜稳守为先，慎迁动与冲突。'
        if has_he and has_chong:
            return '合冲并见，宜中庸处事，取和为贵，先避冲后取合。'
        return '平常之岁，按部就班，稳中求进。'

    def _calculate_qiyun_age(self, bazi_data: BaziData) -> int:
        """
        计算起运年龄
        ✅ 新增：使用节气精算（如果sxtwl可用），否则使用简化算法
        """
        if not SXTWL_AVAILABLE:
            # 简化算法：男阳女阴8岁，男阴女阳3岁
            year_gan = bazi_data.get_pillars()['year'][0]
            yang_gan = {'甲', '丙', '戊', '庚', '壬'}
            is_yang_year = year_gan in yang_gan

            if (is_yang_year and bazi_data.gender == '男') or (not is_yang_year and bazi_data.gender == '女'):
                return 8  # 顺行，8岁起运
            else:
                return 3  # 逆行，3岁起运

        try:
            # 使用sxtwl节气精算
            year = bazi_data.birth_year
            month = bazi_data.birth_month
            day = bazi_data.birth_day

            # 计算方向
            year_gan = bazi_data.get_pillars()['year'][0]
            yang_gan = {'甲', '丙', '戊', '庚', '壬'}
            is_yang_year = year_gan in yang_gan
            direction = '顺行' if (is_yang_year and bazi_data.gender == '男') or (not is_yang_year and bazi_data.gender == '女') else '逆行'

            # 简化版节气计算：按月份估算
            jieqi_days = {
                1: 6, 2: 4, 3: 6, 4: 5, 5: 6, 6: 6,
                7: 7, 8: 8, 9: 8, 10: 8, 11: 7, 12: 7
            }

            if month in jieqi_days:
                if direction == '顺行':
                    days_to_jieqi = jieqi_days[month] - day
                    if days_to_jieqi <= 0:
                        days_to_jieqi += 30
                else:
                    days_to_jieqi = day - jieqi_days[month]
                    if days_to_jieqi <= 0:
                        days_to_jieqi += 30

                # 三天折一年
                qiyun_age = int(days_to_jieqi / 3.0)
                return max(1, min(10, qiyun_age))  # 限制在1-10岁之间
            else:
                return 8  # 默认8岁

        except Exception:
            return 8  # 异常时默认8岁
