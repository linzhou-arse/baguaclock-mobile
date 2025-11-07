#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
人品交友分析器 - Renpin Analyzer
================================

基于《渊海子平·论性情》的人品交友分析器

功能：
1. 人品综合评估
2. 性格与品德关系
3. 交友建议

理论依据：
- 《渊海子平·论性情》性格分析
- 《三命通会·论性情》品德关系
"""

from typing import Dict, List, Tuple, Any, Optional
from ..core.base_analyzer import BaseAnalyzer
from ..core.data_structures import BaziData, AnalysisResult, AnalysisConfig
from ..core.utils import create_analysis_result, get_wuxing_by_tiangan
from ..core.utils import get_ten_god
from ..core.constants import DIZHI_CANGGAN


class RenpinAnalyzer(BaseAnalyzer):
    """
    人品交友分析器 - 基于《渊海子平·论性情》理论
    """
    
    def __init__(self, config: AnalysisConfig = None):
        super().__init__("人品交友分析器", "渊海子平", config)
    
    def analyze(self, bazi_data: BaziData) -> AnalysisResult:
        """
        分析人品和交友建议
        """
        pillars = bazi_data.get_pillars()
        day_master = bazi_data.get_day_master()
        
        # 1. 统计十神
        ten_god_count = self._count_ten_gods(pillars, day_master)
        
        # 2. 分析人品基础（基于十神）
        renpin_base = self._analyze_renpin_base(ten_god_count)
        
        # 3. 分析性格特征（基于日主和十神）
        character_analysis = self._analyze_character(pillars, day_master, ten_god_count)
        
        # 4. 人品综合评分
        renpin_score = self._calculate_renpin_score(renpin_base, character_analysis)
        
        # 5. 交友建议
        friendship_advice = self._generate_friendship_advice(renpin_score, ten_god_count)
        
        # 判断吉凶等级
        level = self._determine_level(renpin_score)
        
        # 生成描述
        description = self._generate_description(renpin_base, character_analysis, renpin_score)
        
        # 生成建议
        advice = self._generate_advice(renpin_score, friendship_advice)
        
        return create_analysis_result(
            analyzer_name=self.name,
            book_name=self.book_name,
            analysis_type="人品交友分析",
            level=level,
            score=0,
            description=description,
            details={
                'ten_god_count': ten_god_count,
                'renpin_base': renpin_base,
                'character_analysis': character_analysis,
                'renpin_score': renpin_score,
                'friendship_advice': friendship_advice
            },
            advice=advice
        )
    
    def _count_ten_gods(self, pillars: Dict, day_master: str) -> Dict[str, float]:
        """
        统计十神数量
        """
        ten_god_count = {
            '比肩': 0.0, '劫财': 0.0,
            '食神': 0.0, '伤官': 0.0,
            '正财': 0.0, '偏财': 0.0,
            '正官': 0.0, '偏官': 0.0,
            '正印': 0.0, '偏印': 0.0
        }
        
        for pos, (gan, zhi) in pillars.items():
            # 天干十神
            ten_god = get_ten_god(day_master, gan)
            if ten_god in ten_god_count:
                ten_god_count[ten_god] += 1.0
            
            # 地支藏干十神（加权）
            canggan_list = DIZHI_CANGGAN.get(zhi, [])
            for cg, weight in canggan_list:
                tg = get_ten_god(day_master, cg)
                if tg in ten_god_count:
                    ten_god_count[tg] += weight
        
        return ten_god_count
    
    def _analyze_renpin_base(self, ten_god_count: Dict[str, float]) -> Dict[str, Any]:
        """
        分析人品基础（基于十神组合）
        """
        # 正面的十神（加分）
        positive_tg = ['正印', '正官', '正财', '食神']
        positive_score = sum(ten_god_count.get(tg, 0) for tg in positive_tg)
        
        # 负面的十神（减分）
        negative_tg = ['偏官', '伤官', '偏印']
        negative_score = sum(ten_god_count.get(tg, 0) for tg in negative_tg)
        
        # 中性十神
        neutral_tg = ['比肩', '劫财', '偏财']
        neutral_score = sum(ten_god_count.get(tg, 0) for tg in neutral_tg)
        
        # ✅ 修复：评估人品基础，更客观
        net_score = positive_score - negative_score * 0.8

        if net_score >= 3.0:
            level = '十神配置极好'
            desc = '正面十神多，性格正面特征明显'
        elif net_score >= 2.0:
            level = '十神配置很好'
            desc = '正面十神较多，性格特征较为正面'
        elif net_score >= 1.0:
            level = '十神配置较好'
            desc = '正面十神略多，性格特征偏正面'
        elif net_score >= 0:
            level = '十神配置平衡'
            desc = '十神平衡，性格特征正负参半'
        elif net_score >= -1.0:
            level = '十神配置略有偏颇'
            desc = '负面十神略多，性格特征需观察'
        else:
            level = '十神配置偏负面'
            desc = '负面十神较多，性格特征需深入了解'
        
        return {
            'positive_score': positive_score,
            'negative_score': negative_score,
            'neutral_score': neutral_score,
            'net_score': net_score,
            'level': level,
            'description': desc
        }
    
    def _analyze_character(self, pillars: Dict, day_master: str,
                          ten_god_count: Dict[str, float]) -> Dict[str, Any]:
        """
        分析性格特征
        """
        # 日主性格特征
        day_wx = get_wuxing_by_tiangan(day_master)
        day_character = {
            '木': '仁慈正直，积极进取',
            '火': '热情开朗，积极乐观',
            '土': '诚实守信，稳重踏实',
            '金': '果断坚毅，重视原则',
            '水': '聪明灵活，善于变通'
        }.get(day_wx, '性格特点需具体分析')
        
        # 十神性格影响
        character_traits = []
        
        if ten_god_count.get('正印', 0) >= 1.0:
            character_traits.append('善良仁慈')
        if ten_god_count.get('正官', 0) >= 1.0:
            character_traits.append('正直负责')
        if ten_god_count.get('正财', 0) >= 1.0:
            character_traits.append('务实理性')
        if ten_god_count.get('偏官', 0) >= 1.0:
            character_traits.append('果断但可能急躁')
        if ten_god_count.get('伤官', 0) >= 1.0:
            character_traits.append('聪明但可能叛逆')
        if ten_god_count.get('偏印', 0) >= 1.0:
            character_traits.append('敏感但可能多疑')
        
        return {
            'day_character': day_character,
            'character_traits': character_traits,
            'summary': f"日主{day_wx}：{day_character}；十神性格：{', '.join(character_traits) if character_traits else '较为平衡'}"
        }
    
    def _calculate_renpin_score(self, renpin_base: Dict, character: Dict) -> Dict[str, Any]:
        """
        计算人品综合评分
        """
        base_score = renpin_base['net_score'] * 10
        
        # 性格加分（基于正面特征）
        character_bonus = 0
        positive_traits = ['善良仁慈', '正直负责', '务实理性']
        for trait in character['character_traits']:
            if any(pt in trait for pt in positive_traits):
                character_bonus += 5
        
        total_score = base_score + character_bonus
        
        # ✅ 修复：判断人品等级，更客观，不武断
        # 理论依据：《渊海子平·论性情》："性情之善恶，非一端可定"
        if total_score >= 40:
            renpin_level = '人品极好'
            renpin_desc = '十神配置良好，性格正面特征明显，为人正直善良'
        elif total_score >= 25:
            renpin_level = '人品很好'
            renpin_desc = '十神配置较好，性格特征偏正面，为人较为可靠'
        elif total_score >= 10:
            renpin_level = '人品较好'
            renpin_desc = '十神配置尚可，性格特征有正有负，整体偏正面'
        elif total_score >= 0:
            renpin_level = '人品中等'
            renpin_desc = '十神配置平衡，性格特征正负参半，需具体观察'
        elif total_score >= -10:
            renpin_level = '人品一般'
            renpin_desc = '十神配置略有偏颇，性格特征有待观察，建议谨慎了解'
        else:
            renpin_level = '人品有待观察'
            renpin_desc = '十神配置偏负面，性格特征需要深入了解，建议多方观察'
        
        return {
            'total_score': total_score,
            'base_score': base_score,
            'character_bonus': character_bonus,
            'level': renpin_level,
            'description': renpin_desc
        }
    
    def _generate_friendship_advice(self, renpin_score: Dict,
                                   ten_god_count: Dict[str, float]) -> List[str]:
        """
        生成交友建议
        ✅ 修复：更客观的交友建议，不武断
        """
        advice_list = []
        score = renpin_score['total_score']

        if score >= 40:
            advice_list.append("性格正面特征明显，可以建立深厚友谊")
            advice_list.append("适合长期交往，相互扶持")
        elif score >= 25:
            advice_list.append("性格特征较好，可以建立良好友谊")
            advice_list.append("适合正常交往，共同进步")
        elif score >= 10:
            advice_list.append("性格特征尚可，可以正常交往")
            advice_list.append("建议多观察了解，逐步建立友谊")
        elif score >= 0:
            advice_list.append("性格特征正负参半，建议保持正常交往")
            advice_list.append("在交往中多观察，根据实际情况调整")
        elif score >= -10:
            advice_list.append("性格特征略有偏颇，建议谨慎了解")
            advice_list.append("可以正常交往，但需要多方观察验证")
        else:
            advice_list.append("性格特征需要深入了解，建议多方观察")
            advice_list.append("在交往中注意观察实际表现，不可仅凭八字判断")
        
        # 特殊建议
        if ten_god_count.get('偏官', 0) >= 2.0:
            advice_list.append("偏官多，性格可能较为急躁，交往时需注意沟通方式")
        
        if ten_god_count.get('伤官', 0) >= 2.0:
            advice_list.append("伤官多，可能较为叛逆，交往时需包容理解")
        
        if ten_god_count.get('正印', 0) >= 2.0:
            advice_list.append("正印多，性格善良，可放心交往")
        
        return advice_list
    
    def _determine_level(self, renpin_score: Dict) -> str:
        """
        判断吉凶等级
        """
        score = renpin_score['total_score']
        
        if score >= 40:
            return '大吉'
        elif score >= 25:
            return '吉'
        elif score >= 10:
            return '中平'
        elif score >= 0:
            return '中平'
        else:
            return '凶'
    
    def _generate_description(self, renpin_base: Dict, character: Dict,
                             renpin_score: Dict) -> str:
        """
        生成描述
        """
        desc_parts = []
        
        desc_parts.append(f"人品基础：{renpin_base['description']}")
        desc_parts.append(f"性格特征：{character['summary']}")
        desc_parts.append(f"综合评估：{renpin_score['description']}（得分{renpin_score['total_score']:.0f}）")
        
        return "；".join(desc_parts)
    
    def _generate_advice(self, renpin_score: Dict, friendship_advice: List[str]) -> str:
        """
        生成建议
        """
        return "建议：" + "；".join(friendship_advice) + "。"

