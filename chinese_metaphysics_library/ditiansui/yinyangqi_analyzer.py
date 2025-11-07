#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
阴阳气分析器 - Yinyangqi Analyzer
================================

基于《渊海子平》《三命通会》《滴天髓》阴阳理论的阴阳气分析器

功能：
1. 天干阴阳分析 - ✅ 有充分经典依据
2. 地支藏干阴阳分析 - ✅ 有经典依据
3. 阴阳平衡判断 - ⚠️ 基于经典理论推导

理论依据：
✅ 《渊海子平·论日为主》："分之阴阳，曰官、曰杀，甲乙见庚辛也"
✅ 《子平真诠·论阴阳生克》："甲者，阳木也；乙者，阴木也"
✅ 《三命通会·论天干阴阳生死》："甲丙戊庚壬为阳，乙丁己辛癸为阴"
✅ 《滴天髓·天干章》："五阳皆阳丙为最，五阴皆阴癸为至"

重要说明：
- 天干阴阳有充分经典依据 ✅
- 地支藏干阴阳有经典依据 ✅
- 地支本身阴阳缺乏明确经典依据，已删除 ❌
- 权重分配（天干0.6、地支0.4）没有经典依据，已删除 ❌
- 等级划分（>=70%很大等）没有经典依据，已删除 ❌
- 改为简单的阴阳平衡判断 ⚠️
"""

from typing import Dict, List, Tuple, Any, Optional
from ..core.base_analyzer import BaseAnalyzer
from ..core.data_structures import BaziData, AnalysisResult, AnalysisConfig
from ..core.utils import create_analysis_result, get_wuxing_by_tiangan, get_wuxing_by_dizhi
from ..core.constants import TIANGAN_YINYANG, DIZHI_CANGGAN, DIZHI_WUXING, TIANGAN_WUXING


class YinyangqiAnalyzer(BaseAnalyzer):
    """
    阴阳气分析器 - 基于《渊海子平》《三命通会》阴阳理论
    """
    
    def __init__(self, config: AnalysisConfig = None):
        super().__init__("阴阳气分析器", "渊海子平", config)
    
    def analyze(self, bazi_data: BaziData) -> AnalysisResult:
        """
        分析阴阳气强弱
        """
        pillars = bazi_data.get_pillars()
        day_master = bazi_data.get_day_master()
        
        # 1. 统计天干阴阳
        gan_yinyang = self._analyze_gan_yinyang(pillars)
        
        # 2. 统计地支阴阳（包括藏干）
        zhi_yinyang = self._analyze_zhi_yinyang(pillars, day_master)
        
        # 3. 综合阴阳分析
        comprehensive_yinyang = self._comprehensive_yinyang(gan_yinyang, zhi_yinyang)
        
        # 4. 判断阴阳平衡
        balance_assessment = self._assess_balance(comprehensive_yinyang)
        
        # 判断吉凶等级
        level = self._determine_level(balance_assessment)
        
        # 生成描述
        description = self._generate_description(
            gan_yinyang, zhi_yinyang, comprehensive_yinyang, balance_assessment
        )
        
        # 生成建议
        advice = self._generate_advice(comprehensive_yinyang, balance_assessment)
        
        return create_analysis_result(
            analyzer_name=self.name,
            book_name=self.book_name,
            analysis_type="阴阳气分析",
            level=level,
            score=0,
            description=description,
            details={
                'gan_yinyang': gan_yinyang,
                'zhi_yinyang': zhi_yinyang,
                'comprehensive_yinyang': comprehensive_yinyang,
                'balance_assessment': balance_assessment
            },
            advice=advice
        )
    
    def _analyze_gan_yinyang(self, pillars: Dict) -> Dict[str, Any]:
        """
        分析天干阴阳分布

        ✅ 有充分经典依据

        理论依据：
        《三命通会·论天干阴阳生死》："甲丙戊庚壬为阳，乙丁己辛癸为阴"
        《滴天髓·天干章》："五阳皆阳丙为最，五阴皆阴癸为至"
        """
        yang_count = 0
        yin_count = 0
        yang_gans = []
        yin_gans = []

        for pos, (gan, zhi) in pillars.items():
            yinyang = TIANGAN_YINYANG.get(gan, 0)
            if yinyang > 0:  # 阳干
                yang_count += 1
                yang_gans.append({
                    'position': pos,
                    'gan': gan,
                    'wuxing': get_wuxing_by_tiangan(gan)
                })
            elif yinyang < 0:  # 阴干
                yin_count += 1
                yin_gans.append({
                    'position': pos,
                    'gan': gan,
                    'wuxing': get_wuxing_by_tiangan(gan)
                })

        total = yang_count + yin_count
        yang_ratio = yang_count / total if total > 0 else 0
        yin_ratio = yin_count / total if total > 0 else 0

        return {
            'yang_count': yang_count,
            'yin_count': yin_count,
            'yang_ratio': yang_ratio,
            'yin_ratio': yin_ratio,
            'yang_gans': yang_gans,
            'yin_gans': yin_gans,
            'description': f"天干阳{yang_count}阴{yin_count}，阳气占比{yang_ratio*100:.0f}%"
        }
    
    def _analyze_zhi_yinyang(self, pillars: Dict, day_master: str) -> Dict[str, Any]:
        """
        分析地支藏干阴阳分布

        ✅ 有经典依据（仅统计藏干，不统计地支本身）

        理论依据：
        《三命通会·论地支藏干》：地支藏干理论

        重要说明：
        - ❌ 删除了地支本身阴阳（子寅辰午申戌为阳，丑卯巳未酉亥为阴）
          原因：《滴天髓》虽提到，但缺乏明确理论依据
        - ✅ 保留地支藏干阴阳（基于天干阴阳理论）
        - ✅ 使用藏干权重（本气/中气/余气）
          理论依据：《三命通会·论地支藏干》："藏干有本气、中气、余气，各有权重"
          权重说明：本气0.6-0.7，中气0.2-0.3，余气0.1
        """
        yang_count = 0.0
        yin_count = 0.0
        yang_details = []
        yin_details = []

        # 只统计地支藏干的阴阳（不统计地支本身）
        # ✅ 修复：使用真实的藏干权重进行计算（本气/中气/余气）
        for pos, (gan, zhi) in pillars.items():
            # 地支藏干
            canggan_list = DIZHI_CANGGAN.get(zhi, [])
            for cg, weight in canggan_list:
                cg_yinyang = TIANGAN_YINYANG.get(cg, 0)
                if cg_yinyang > 0:
                    yang_count += weight  # ✅ 使用真实权重，而不是简单计数
                    yang_details.append({
                        'position': pos,
                        'zhi': zhi,
                        'canggan': cg,
                        'weight': weight  # 保存权重信息
                    })
                elif cg_yinyang < 0:
                    yin_count += weight  # ✅ 使用真实权重，而不是简单计数
                    yin_details.append({
                        'position': pos,
                        'zhi': zhi,
                        'canggan': cg,
                        'weight': weight  # 保存权重信息
                    })

        total = yang_count + yin_count
        yang_ratio = yang_count / total if total > 0 else 0
        yin_ratio = yin_count / total if total > 0 else 0

        return {
            'yang_count': yang_count,
            'yin_count': yin_count,
            'yang_ratio': yang_ratio,
            'yin_ratio': yin_ratio,
            'yang_details': yang_details,
            'yin_details': yin_details,
            'description': f"地支藏干阳{yang_count:.1f}阴{yin_count:.1f}，阳气占比{yang_ratio*100:.0f}%"
        }
    
    def _comprehensive_yinyang(self, gan_yinyang: Dict, zhi_yinyang: Dict) -> Dict[str, Any]:
        """
        综合阴阳分析

        ⚠️ 基于经典理论推导

        重要说明：
        - ❌ 删除了权重分配（天干0.6、地支0.4）- 没有经典依据
        - ❌ 删除了等级划分（>=70%很大等）- 没有经典依据
        - ✅ 改为简单平均和阴阳平衡判断

        理论依据：
        《滴天髓·性情章》："五气不戾，性情中和；浊乱偏枯，性情乖逆"
        - 强调阴阳平衡的重要性
        """
        # ✅ 修复：天干计数为整数，地支藏干为加权和（已有权重）
        # 理论依据：《三命通会》天干直接计数，地支藏干按权重计算
        total_yang = float(gan_yinyang['yang_count']) + zhi_yinyang['yang_count']
        total_yin = float(gan_yinyang['yin_count']) + zhi_yinyang['yin_count']

        total = total_yang + total_yin
        yang_ratio = total_yang / total if total > 0 else 0.5
        yin_ratio = total_yin / total if total > 0 else 0.5

        # 简单的阴阳平衡判断（不使用等级划分）
        balance_gap = abs(yang_ratio - yin_ratio)

        if balance_gap <= 0.1:
            balance_status = '阴阳平衡'
            balance_desc = '阴阳平衡，命局和谐（基于《滴天髓》"五气不戾，性情中和"）'
        elif yang_ratio > yin_ratio:
            balance_status = '阳气偏重'
            balance_desc = f'阳气偏重（阳{yang_ratio*100:.0f}%，阴{yin_ratio*100:.0f}%），性格较为刚强主动'
        else:
            balance_status = '阴气偏重'
            balance_desc = f'阴气偏重（阴{yin_ratio*100:.0f}%，阳{yang_ratio*100:.0f}%），性格较为柔和内敛'

        return {
            'yang_count': total_yang,
            'yin_count': total_yin,
            'yang_ratio': yang_ratio,
            'yin_ratio': yin_ratio,
            'balance_status': balance_status,
            'balance_description': balance_desc
        }
    
    def _assess_balance(self, comprehensive: Dict) -> Dict[str, Any]:
        """
        评估阴阳平衡

        ⚠️ 基于经典理论推导

        理论依据：
        《滴天髓·性情章》："五气不戾，性情中和；浊乱偏枯，性情乖逆"
        """
        # 直接使用 comprehensive 中的 balance_status 和 balance_description
        return {
            'balance_status': comprehensive.get('balance_status', '未知'),
            'balance_description': comprehensive.get('balance_description', '需要进一步分析')
        }
    
    def _determine_level(self, balance: Dict) -> str:
        """
        判断吉凶等级

        ⚠️ 基于经典理论推导

        理论依据：
        《滴天髓·性情章》："五气不戾，性情中和；浊乱偏枯，性情乖逆"
        - 阴阳平衡为吉，偏颇为凶
        """
        balance_status = balance.get('balance_status', '未知')

        if balance_status == '阴阳平衡':
            return '吉'
        elif balance_status in ['阳气偏重', '阴气偏重']:
            return '中平'
        else:
            return '需进一步分析'
    
    def _generate_description(self, gan_yinyang: Dict, zhi_yinyang: Dict,
                             comprehensive: Dict, balance: Dict) -> str:
        """
        生成描述
        """
        desc_parts = []

        desc_parts.append(gan_yinyang['description'])
        desc_parts.append(zhi_yinyang['description'])
        desc_parts.append(f"综合：阳{comprehensive['yang_count']:.1f}阴{comprehensive['yin_count']:.1f}，阳气占比{comprehensive['yang_ratio']*100:.0f}%")
        desc_parts.append(f"平衡：{balance['balance_description']}")

        return "；".join(desc_parts)
    
    def _generate_advice(self, comprehensive: Dict, balance: Dict) -> str:
        """
        生成建议

        ⚠️ 基于经典理论推导

        理论依据：
        《滴天髓·性情章》："五气不戾，性情中和；浊乱偏枯，性情乖逆"
        """
        advice_list = []

        balance_status = balance.get('balance_status', '未知')
        yang_ratio = comprehensive['yang_ratio']

        if balance_status == '阴阳平衡':
            advice_list.append("阴阳平衡良好，保持现状即可")
        elif balance_status == '阳气偏重':
            advice_list.append("阳气偏重，建议多静心养性，避免过于急躁")
            advice_list.append("可通过接触阴柔事物来平衡（基于五行调候理论）")
        elif balance_status == '阴气偏重':
            advice_list.append("阴气偏重，建议多运动锻炼，增强活力")
            advice_list.append("可通过接触阳刚事物来补充（基于五行调候理论）")

        if not advice_list:
            return "阴阳气分析正常，保持现状即可。"

        return "建议：" + "；".join(advice_list) + "。"

