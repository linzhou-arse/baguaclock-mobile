#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
三才分析器 - Sancai Analyzer
===========================

基于《滴天髓》天道、地道、人道理论的三才分析器

理论依据：
- 《滴天髓》第一章：天道、地道、人道
- "天道"：阴阳本乎太极，五行播于四时
- "地道"：五行相生相克，地支藏干
- "人道"：人事吉凶，命运兴衰
"""

from typing import Dict, List, Tuple, Any
from ..core.base_analyzer import BaseAnalyzer
from ..core.data_structures import BaziData, AnalysisResult, AnalysisConfig
from ..core.utils import create_analysis_result, get_wuxing_by_tiangan, get_wuxing_by_dizhi
from ..core.constants import DIZHI_CANGGAN, TIANGAN_YINYANG, TIANGAN_WUXING, DIZHI_WUXING


class SancaiAnalyzer(BaseAnalyzer):
    """
    三才分析器 - 基于《滴天髓》天道、地道、人道理论
    """
    
    def __init__(self, config: AnalysisConfig = None):
        super().__init__("三才分析器", "滴天髓", config)
    
    def analyze(self, bazi_data: BaziData) -> AnalysisResult:
        """
        三才综合分析：天道、地道、人道
        """
        pillars = bazi_data.get_pillars()
        day_master = bazi_data.get_day_master()
        
        # 1. 天道分析
        tiandao_analysis = self._analyze_tiandao(pillars, day_master)
        
        # 2. 地道分析
        didao_analysis = self._analyze_didao(pillars, day_master)
        
        # 3. 人道分析
        rendao_analysis = self._analyze_rendao(pillars, day_master, tiandao_analysis, didao_analysis)
        
        # 4. 综合评估
        comprehensive_assessment = self._comprehensive_assessment(
            tiandao_analysis, didao_analysis, rendao_analysis
        )
        
        # 5. 判断吉凶等级
        level = self._determine_level(comprehensive_assessment)
        
        # 生成描述
        description = f"天道：{tiandao_analysis['summary']}；"
        description += f"地道：{didao_analysis['summary']}；"
        description += f"人道：{rendao_analysis['summary']}"
        
        # 生成建议
        advice = self._generate_advice(tiandao_analysis, didao_analysis, rendao_analysis)
        
        return create_analysis_result(
            analyzer_name=self.name,
            book_name=self.book_name,
            analysis_type="三才分析",
            level=level,
            score=0,  # 不打分
            description=description,
            details={
                'tiandao': tiandao_analysis,
                'didao': didao_analysis,
                'rendao': rendao_analysis,
                'comprehensive': comprehensive_assessment
            },
            advice=advice
        )
    
    def _analyze_tiandao(self, pillars: Dict, day_master: str) -> Dict[str, Any]:
        """
        天道分析 - 基于《滴天髓》："天道：阴阳本乎太极，五行播于四时"
        
        分析内容：
        1. 天干五行分布
        2. 天干阴阳分布
        3. 五行当令情况
        4. 天干透出情况
        """
        # 统计天干五行
        gan_wuxing_count = {'木': 0, '火': 0, '土': 0, '金': 0, '水': 0}
        gan_yinyang_count = {'阳': 0, '阴': 0}
        
        for pos, (gan, zhi) in pillars.items():
            wx = get_wuxing_by_tiangan(gan)
            gan_wuxing_count[wx] += 1
            
            yinyang = TIANGAN_YINYANG.get(gan, 0)
            if yinyang > 0:
                gan_yinyang_count['阳'] += 1
            elif yinyang < 0:
                gan_yinyang_count['阴'] += 1
        
        # 找出最多的五行和阴阳
        max_wx = max(gan_wuxing_count, key=gan_wuxing_count.get)
        max_yinyang = max(gan_yinyang_count, key=gan_yinyang_count.get)
        
        # 判断天道强弱
        wx_diversity = len([v for v in gan_wuxing_count.values() if v > 0])
        yinyang_balance = abs(gan_yinyang_count['阳'] - gan_yinyang_count['阴'])

        # ✅ 修复：判断是否五行俱全（必须5种都有）
        wuxing_complete = wx_diversity == 5

        # ✅ 修复：找出缺少的五行
        missing_wuxing = [wx for wx, count in gan_wuxing_count.items() if count == 0]
        missing_wuxing_str = '、'.join(missing_wuxing) if missing_wuxing else ''

        if wx_diversity >= 3 and yinyang_balance <= 1:
            tiandao_strength = '中和'
            if wuxing_complete:
                tiandao_desc = '天道中和，阴阳平衡，五行俱全'
            else:
                tiandao_desc = f'天道中和，阴阳平衡，五行不全（缺{missing_wuxing_str}）'
        elif wx_diversity >= 2:
            tiandao_strength = '中等'
            if missing_wuxing:
                tiandao_desc = f'天道中等，五行偏{max_wx}，{max_yinyang}气较旺，缺{missing_wuxing_str}'
            else:
                tiandao_desc = f'天道中等，五行偏{max_wx}，{max_yinyang}气较旺'
        else:
            tiandao_strength = '偏颇'
            tiandao_desc = f'天道偏颇，五行单一（{max_wx}），{max_yinyang}气过旺，缺{missing_wuxing_str}'
        
        return {
            'wuxing_count': gan_wuxing_count,
            'yinyang_count': gan_yinyang_count,
            'max_wuxing': max_wx,
            'max_yinyang': max_yinyang,
            'wuxing_diversity': wx_diversity,
            'yinyang_balance': yinyang_balance,
            'strength': tiandao_strength,
            'summary': tiandao_desc,
            'details': {
                'wuxing_distribution': f"五行分布：木{gan_wuxing_count['木']}、火{gan_wuxing_count['火']}、土{gan_wuxing_count['土']}、金{gan_wuxing_count['金']}、水{gan_wuxing_count['水']}",
                'yinyang_distribution': f"阴阳分布：阳{gan_yinyang_count['阳']}、阴{gan_yinyang_count['阴']}"
            }
        }
    
    def _analyze_didao(self, pillars: Dict, day_master: str) -> Dict[str, Any]:
        """
        地道分析 - 基于《滴天髓》："地道：五行相生相克，地支藏干"
        
        分析内容：
        1. 地支五行分布
        2. 地支藏干情况
        3. 根气强弱
        4. 地支相生相克关系
        """
        # 统计地支五行（包括藏干）
        zhi_wuxing_count = {'木': 0.0, '火': 0.0, '土': 0.0, '金': 0.0, '水': 0.0}
        
        # 统计根气（日主在地支的根气）
        genqi_strength = 0.0
        genqi_positions = []
        
        dm_wx = get_wuxing_by_tiangan(day_master)
        
        for pos, (gan, zhi) in pillars.items():
            # ✅ 修复：只统计藏干五行，不要重复计算地支本身五行
            # 理论依据：《滴天髓》："地支藏干，各有权重"
            # 地支的五行已经包含在藏干中（本气、中气、余气），不需要单独加1.0

            # 藏干五行（加权统计）
            canggan_list = DIZHI_CANGGAN.get(zhi, [])
            for cg, weight in canggan_list:
                cg_wx = get_wuxing_by_tiangan(cg)
                zhi_wuxing_count[cg_wx] += weight

                # 如果是日主的根气
                if cg_wx == dm_wx:
                    genqi_strength += weight
                    pos_name = {'year': '年', 'month': '月', 'day': '日', 'hour': '时'}.get(pos, pos)
                    genqi_positions.append(f"{pos_name}支({zhi})，权重{weight:.1f}")
        
        # 找出最多的五行
        max_zhi_wx = max(zhi_wuxing_count, key=zhi_wuxing_count.get)
        
        # 判断地道强弱
        if genqi_strength >= 2.0:
            didao_strength = '深厚'
            didao_desc = f'地道深厚，根气强（{genqi_strength:.1f}），五行偏{max_zhi_wx}'
        elif genqi_strength >= 1.0:
            didao_strength = '中等'
            didao_desc = f'地道中等，根气尚可（{genqi_strength:.1f}），五行偏{max_zhi_wx}'
        else:
            didao_strength = '薄弱'
            didao_desc = f'地道薄弱，根气弱（{genqi_strength:.1f}），五行偏{max_zhi_wx}'
        
        return {
            'wuxing_count': zhi_wuxing_count,
            'max_wuxing': max_zhi_wx,
            'genqi_strength': genqi_strength,
            'genqi_positions': genqi_positions,
            'strength': didao_strength,
            'summary': didao_desc,
            'details': {
                'wuxing_distribution': f"地支五行：木{zhi_wuxing_count['木']:.1f}、火{zhi_wuxing_count['火']:.1f}、土{zhi_wuxing_count['土']:.1f}、金{zhi_wuxing_count['金']:.1f}、水{zhi_wuxing_count['水']:.1f}",
                'genqi_detail': f"根气分布：{', '.join(genqi_positions) if genqi_positions else '无根气'}"
            }
        }
    
    def _analyze_rendao(self, pillars: Dict, day_master: str, 
                       tiandao: Dict, didao: Dict) -> Dict[str, Any]:
        """
        人道分析 - 基于《滴天髓》："人道：人事吉凶，命运兴衰"
        
        分析内容：
        1. 天道与地道的配合
        2. 五行流通情况
        3. 格局配合
        4. 人事吉凶判断
        """
        # 判断天道与地道的配合
        tiandao_wx = tiandao['max_wuxing']
        didao_wx = didao['max_wuxing']
        
        # 五行相生关系
        sheng_map = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        
        if tiandao_wx == didao_wx:
            coordination = '统一'
            coordination_desc = f'天道地道统一，都偏{tiandao_wx}，力量集中'
        elif sheng_map.get(tiandao_wx) == didao_wx:
            coordination = '相生'
            coordination_desc = f'天道生地道（{tiandao_wx}生{didao_wx}），流通有情'
        elif sheng_map.get(didao_wx) == tiandao_wx:
            coordination = '相生'
            coordination_desc = f'地道生天道（{didao_wx}生{tiandao_wx}），根基深厚'
        else:
            coordination = '不同'
            coordination_desc = f'天道地道不同（天道偏{tiandao_wx}，地道偏{didao_wx}），需要调和'
        
        # 根气与天道的配合
        genqi_strong = didao['genqi_strength'] >= 1.0
        tiandao_balanced = tiandao['strength'] == '中和'
        
        if genqi_strong and tiandao_balanced:
            rendao_strength = '上等'
            rendao_desc = '人道上等，天道中和，地道深厚，格局配合良好'
        elif genqi_strong or tiandao_balanced:
            rendao_strength = '中等'
            rendao_desc = '人道中等，天道地道配合尚可'
        else:
            rendao_strength = '下等'
            rendao_desc = '人道下等，天道地道配合不佳，需要调和'
        
        return {
            'coordination': coordination,
            'coordination_desc': coordination_desc,
            'strength': rendao_strength,
            'summary': rendao_desc,
            'details': {
                'tiandao_didao': f"天道地道配合：{coordination_desc}",
                'genqi_status': f"根气情况：{'深厚' if genqi_strong else '薄弱'}",
                'tiandao_status': f"天道情况：{tiandao['strength']}"
            }
        }
    
    def _comprehensive_assessment(self, tiandao: Dict, didao: Dict, rendao: Dict) -> Dict[str, Any]:
        """
        综合评估三才配合情况
        """
        scores = {
            '上等': 3,
            '中和': 2,
            '深厚': 2,
            '中等': 1,
            '下等': 0,
            '薄弱': 0,
            '偏颇': 0
        }
        
        tiandao_score = scores.get(tiandao['strength'], 1)
        didao_score = scores.get(didao['strength'], 1)
        rendao_score = scores.get(rendao['strength'], 1)
        
        total_score = tiandao_score + didao_score + rendao_score
        
        if total_score >= 6:
            assessment = '三才配合极佳'
        elif total_score >= 4:
            assessment = '三才配合良好'
        elif total_score >= 2:
            assessment = '三才配合一般'
        else:
            assessment = '三才配合不佳'
        
        return {
            'total_score': total_score,
            'tiandao_score': tiandao_score,
            'didao_score': didao_score,
            'rendao_score': rendao_score,
            'assessment': assessment
        }
    
    def _determine_level(self, assessment: Dict) -> str:
        """
        根据综合评估判断吉凶等级
        """
        total_score = assessment['total_score']
        
        if total_score >= 6:
            return '大吉'
        elif total_score >= 4:
            return '吉'
        elif total_score >= 2:
            return '中平'
        else:
            return '凶'
    
    def _generate_advice(self, tiandao: Dict, didao: Dict, rendao: Dict) -> str:
        """
        生成三才分析建议
        """
        advice_list = []
        
        # 天道建议
        if tiandao['strength'] == '偏颇':
            advice_list.append(f"天道偏颇，建议调和五行，使{tiandao['max_wuxing']}不过旺")
        
        if tiandao['yinyang_balance'] > 1:
            advice_list.append(f"阴阳不平衡，建议调和阴阳，使阴阳趋于平衡")
        
        # 地道建议
        if didao['strength'] == '薄弱':
            advice_list.append(f"地道薄弱，根气不足，建议在{', '.join(didao['genqi_positions']) if didao['genqi_positions'] else '相关地支'}方面加强")
        
        # 人道建议
        if rendao['coordination'] == '不同':
            advice_list.append(f"天道地道不同，需要调和，使天道地道相互配合")
        
        if rendao['strength'] == '下等':
            advice_list.append("人道配合不佳，建议从五行流通、格局配合等方面改善")
        
        if not advice_list:
            return "三才配合良好，保持现状即可。"
        
        return "建议：" + "；".join(advice_list) + "。"

