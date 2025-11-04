#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
杀气分析器 - Qisha Analyzer
===========================

基于《三命通会·论七杀》的杀气轻重量化分析器

功能：
1. 杀气轻重量化分析
2. 七杀制化情况
3. 杀气影响评估

理论依据：
- 《三命通会·论七杀》七杀理论
- 食伤制杀、印化杀理论
"""

from typing import Dict, List, Tuple, Any, Optional
from ..core.base_analyzer import BaseAnalyzer
from ..core.data_structures import BaziData, AnalysisResult, AnalysisConfig
from ..core.utils import create_analysis_result, get_wuxing_by_tiangan
from ..core.constants import DIZHI_CANGGAN
from ..core.utils import get_ten_god


class QishaAnalyzer(BaseAnalyzer):
    """
    杀气分析器 - 基于《三命通会·论七杀》理论
    量化分析杀气的轻重程度
    """
    
    def __init__(self, config: AnalysisConfig = None):
        super().__init__("杀气分析器", "三命通会", config)
    
    def analyze(self, bazi_data: BaziData) -> AnalysisResult:
        """
        分析杀气轻重
        """
        pillars = bazi_data.get_pillars()
        day_master = bazi_data.get_day_master()
        
        # 1. 统计七杀数量（天干+地支藏干）
        qisha_count, qisha_details = self._count_qisha(day_master, pillars)
        
        # 2. 分析七杀位置
        qisha_positions = self._analyze_qisha_positions(day_master, pillars)
        
        # 3. 分析制化情况
        zhihua_analysis = self._analyze_zhihua(day_master, pillars)
        
        # 4. 量化杀气轻重
        qisha_level = self._calculate_qisha_level(qisha_count, qisha_positions, zhihua_analysis)
        
        # 5. 评估杀气影响
        impact_assessment = self._assess_impact(qisha_level, zhihua_analysis)
        
        # 判断吉凶等级
        level = self._determine_level(qisha_level, zhihua_analysis)
        
        # 生成描述
        description = self._generate_description(qisha_count, qisha_level, zhihua_analysis)
        
        # 生成建议
        advice = self._generate_advice(qisha_level, zhihua_analysis, impact_assessment)
        
        return create_analysis_result(
            analyzer_name=self.name,
            book_name=self.book_name,
            analysis_type="杀气分析",
            level=level,
            score=0,
            description=description,
            details={
                'qisha_count': qisha_count,
                'qisha_details': qisha_details,
                'qisha_positions': qisha_positions,
                'zhihua_analysis': zhihua_analysis,
                'qisha_level': qisha_level,
                'impact_assessment': impact_assessment
            },
            advice=advice
        )
    
    def _count_qisha(self, day_master: str, pillars: Dict) -> Tuple[float, List[Dict]]:
        """
        统计七杀数量（包括天干和地支藏干）
        """
        # ✅ 修复：position英文转中文
        position_cn_map = {
            'year': '年柱',
            'month': '月柱',
            'day': '日柱',
            'hour': '时柱'
        }

        count = 0.0
        details = []

        # 统计天干七杀
        for pos, (gan, zhi) in pillars.items():
            ten_god = get_ten_god(day_master, gan)
            if ten_god == '七杀':
                count += 1.0
                pos_cn = position_cn_map.get(pos, pos)
                details.append({
                    'type': '天干',
                    'position': pos,
                    'gan': gan,
                    'weight': 1.0,
                    'description': f"{pos_cn}干{gan}为七杀"
                })

        # 统计地支藏干七杀（加权）
        for pos, (gan, zhi) in pillars.items():
            canggan_list = DIZHI_CANGGAN.get(zhi, [])
            for cg, weight in canggan_list:
                ten_god = get_ten_god(day_master, cg)
                if ten_god == '七杀':
                    count += weight
                    pos_cn = position_cn_map.get(pos, pos)
                    details.append({
                        'type': '地支藏干',
                        'position': pos,
                        'zhi': zhi,
                        'canggan': cg,
                        'weight': weight,
                        'description': f"{pos_cn}支{zhi}藏{cg}（七杀，权重{weight:.1f}）"
                    })

        return count, details
    
    def _analyze_qisha_positions(self, day_master: str, pillars: Dict) -> Dict[str, Any]:
        """
        分析七杀位置
        """
        positions = {
            'year': False,
            'month': False,
            'day': False,
            'hour': False
        }
        
        position_weights = {
            'year': 0.8,   # 年柱七杀，影响较小
            'month': 1.5,  # 月柱七杀，影响最大（月令）
            'day': 1.2,    # 日柱七杀，影响较大（日支）
            'hour': 0.6    # 时柱七杀，影响较小
        }
        
        total_weight = 0.0
        
        for pos, (gan, zhi) in pillars.items():
            # 天干七杀
            if get_ten_god(day_master, gan) == '七杀':
                positions[pos] = True
                total_weight += position_weights.get(pos, 1.0)
            
            # 地支藏干七杀
            canggan_list = DIZHI_CANGGAN.get(zhi, [])
            for cg, weight in canggan_list:
                if get_ten_god(day_master, cg) == '七杀':
                    positions[pos] = True
                    total_weight += position_weights.get(pos, 1.0) * weight
        
        return {
            'positions': positions,
            'total_weight': total_weight,
            'most_important': max(positions.items(), key=lambda x: x[1])[0] if any(positions.values()) else None
        }
    
    def _analyze_zhihua(self, day_master: str, pillars: Dict) -> Dict[str, Any]:
        """
        分析七杀制化情况
        """
        # ✅ 修复：position英文转中文
        position_cn_map = {
            'year': '年柱',
            'month': '月柱',
            'day': '日柱',
            'hour': '时柱'
        }

        # 统计食伤（制杀）
        shishang_count = 0.0
        shishang_details = []

        # 统计印星（化杀）
        yinxing_count = 0.0
        yinxing_details = []

        for pos, (gan, zhi) in pillars.items():
            ten_god = get_ten_god(day_master, gan)
            pos_cn = position_cn_map.get(pos, pos)

            # 食伤制杀
            if ten_god in ['食神', '伤官']:
                shishang_count += 1.0
                shishang_details.append(f"{pos_cn}干{gan}为{ten_god}，可制杀")

            # 印星化杀
            if ten_god in ['正印', '偏印']:
                yinxing_count += 1.0
                yinxing_details.append(f"{pos_cn}干{gan}为{ten_god}，可化杀")

        # 检查地支藏干
        for pos, (gan, zhi) in pillars.items():
            canggan_list = DIZHI_CANGGAN.get(zhi, [])
            pos_cn = position_cn_map.get(pos, pos)
            for cg, weight in canggan_list:
                ten_god = get_ten_god(day_master, cg)

                if ten_god in ['食神', '伤官']:
                    shishang_count += weight
                    shishang_details.append(f"{pos_cn}支{zhi}藏{cg}（{ten_god}，权重{weight:.1f}），可制杀")

                if ten_god in ['正印', '偏印']:
                    yinxing_count += weight
                    yinxing_details.append(f"{pos_cn}支{zhi}藏{cg}（{ten_god}，权重{weight:.1f}），可化杀")
        
        # 判断制化情况
        if shishang_count >= 1.0:
            zhihua_status = '食伤制杀'
            zhihua_strength = '强' if shishang_count >= 2.0 else '中'
        elif yinxing_count >= 1.0:
            zhihua_status = '印星化杀'
            zhihua_strength = '强' if yinxing_count >= 2.0 else '中'
        else:
            zhihua_status = '无制化'
            zhihua_strength = '无'
        
        return {
            'status': zhihua_status,
            'strength': zhihua_strength,
            'shishang_count': shishang_count,
            'yinxing_count': yinxing_count,
            'shishang_details': shishang_details,
            'yinxing_details': yinxing_details
        }
    
    def _calculate_qisha_level(self, qisha_count: float, qisha_positions: Dict,
                              zhihua_analysis: Dict) -> Dict[str, Any]:
        """
        量化杀气轻重
        """
        # 基础杀气分数（七杀数量）
        base_score = qisha_count * 10
        
        # 位置加权（月柱七杀最重要）
        position_score = qisha_positions['total_weight'] * 5
        
        # 制化减分（有制化则减分）
        zhihua_deduction = 0
        if zhihua_analysis['status'] == '食伤制杀':
            zhihua_deduction = zhihua_analysis['shishang_count'] * 8
        elif zhihua_analysis['status'] == '印星化杀':
            zhihua_deduction = zhihua_analysis['yinxing_count'] * 6
        
        # 总杀气分数
        total_score = base_score + position_score - zhihua_deduction
        
        # 判断杀气等级
        if total_score >= 30:
            level = '杀气极重'
            level_desc = '七杀无制化，杀气极重，压力大，需注意'
        elif total_score >= 20:
            level = '杀气重'
            level_desc = '七杀较多，杀气重，有一定压力'
        elif total_score >= 10:
            level = '杀气中等'
            level_desc = '有七杀，杀气中等，影响一般'
        elif total_score >= 0:
            level = '杀气轻'
            level_desc = '七杀有制化，杀气轻，影响较小'
        else:
            level = '杀气很轻'
            level_desc = '七杀被有效制化，杀气很轻，影响很小'
        
        return {
            'total_score': total_score,
            'base_score': base_score,
            'position_score': position_score,
            'zhihua_deduction': zhihua_deduction,
            'level': level,
            'level_desc': level_desc
        }
    
    def _assess_impact(self, qisha_level: Dict, zhihua_analysis: Dict) -> Dict[str, Any]:
        """
        评估杀气影响
        """
        total_score = qisha_level['total_score']
        
        # 影响领域
        impact_areas = []
        if total_score >= 20:
            impact_areas.extend(['事业压力', '健康隐患', '人际关系'])
        elif total_score >= 10:
            impact_areas.extend(['事业压力', '情绪波动'])
        else:
            impact_areas.append('轻微影响')
        
        # 影响程度
        if total_score >= 30:
            impact_level = '严重影响'
        elif total_score >= 20:
            impact_level = '较大影响'
        elif total_score >= 10:
            impact_level = '中等影响'
        else:
            impact_level = '轻微影响'
        
        # 建议
        if zhihua_analysis['status'] == '无制化' and total_score >= 20:
            suggestions = ['建议寻找食伤或印星来制化七杀', '注意调节情绪', '避免过度压力']
        elif zhihua_analysis['status'] != '无制化':
            suggestions = ['七杀有制化，格局较好', '注意保持制化力量', '适当发挥七杀的积极作用']
        else:
            suggestions = ['杀气较轻，影响不大', '保持现状即可']
        
        return {
            'impact_level': impact_level,
            'impact_areas': impact_areas,
            'suggestions': suggestions
        }
    
    def _determine_level(self, qisha_level: Dict, zhihua_analysis: Dict) -> str:
        """
        判断吉凶等级
        """
        total_score = qisha_level['total_score']
        
        if total_score < 0:
            return '大吉'  # 七杀被有效制化
        elif total_score < 10:
            return '吉'  # 七杀有制化
        elif total_score < 20:
            return '中平'  # 七杀中等
        elif total_score < 30:
            return '凶'  # 七杀重，无制化
        else:
            return '大凶'  # 七杀极重，无制化
    
    def _generate_description(self, qisha_count: float, qisha_level: Dict,
                            zhihua_analysis: Dict) -> str:
        """
        生成描述
        """
        desc_parts = []
        
        desc_parts.append(f"七杀数量：{qisha_count:.1f}")
        desc_parts.append(f"杀气等级：{qisha_level['level']}（得分{qisha_level['total_score']:.1f}）")
        desc_parts.append(f"制化情况：{zhihua_analysis['status']}（{zhihua_analysis['strength']}）")
        
        return "；".join(desc_parts)
    
    def _generate_advice(self, qisha_level: Dict, zhihua_analysis: Dict,
                        impact_assessment: Dict) -> str:
        """
        生成建议
        """
        advice_list = []
        
        # 基于影响评估的建议
        advice_list.extend(impact_assessment['suggestions'])
        
        # 具体制化建议
        if zhihua_analysis['status'] == '无制化':
            if qisha_level['total_score'] >= 20:
                advice_list.append("七杀无制化，建议通过大运流年寻找食伤或印星来制化")
        
        if not advice_list:
            return "杀气分析正常，无需特别建议。"
        
        return "建议：" + "；".join(advice_list) + "。"

