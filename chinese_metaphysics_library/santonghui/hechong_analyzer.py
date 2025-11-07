#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合冲分析器 - Hechong Analyzer
=============================

基于《三命通会》《渊海子平》合冲理论的八字合婚分析器

理论依据：
- 《三命通会》地支六合、六冲理论
- 《渊海子平》天干合化理论
- 八字合婚：两个八字的相生相克关系分析
"""

from typing import Dict, List, Tuple, Any, Optional
from ..core.base_analyzer import BaseAnalyzer
from ..core.data_structures import BaziData, AnalysisResult, AnalysisConfig
from ..core.utils import create_analysis_result, get_wuxing_by_tiangan, get_wuxing_by_dizhi
from ..core.constants import (
    TIANGAN_HEHUA, DIZHI_LIUHE, DIZHI_LIUCHONG, 
    TIANGAN_WUXING, DIZHI_WUXING, DIZHI_CANGGAN,
    WUXING_SHENG_MAP, WUXING_KE_MAP
)


class HechongAnalyzer(BaseAnalyzer):
    """
    合冲分析器 - 基于《三命通会》《渊海子平》合冲理论
    分析两个八字之间的相生相克关系
    """
    
    def __init__(self, config: AnalysisConfig = None):
        super().__init__("合冲分析器", "三命通会", config)
    
    def analyze_two_bazi(self, bazi1: BaziData, bazi2: BaziData) -> AnalysisResult:
        """
        分析两个八字之间的合冲关系
        
        参数：
            bazi1: 第一个八字数据
            bazi2: 第二个八字数据
        
        返回：
            合冲分析结果
        """
        pillars1 = bazi1.get_pillars()
        pillars2 = bazi2.get_pillars()
        day_master1 = bazi1.get_day_master()
        day_master2 = bazi2.get_day_master()
        
        # 1. 天干合化分析
        gan_hehua = self._analyze_gan_hehua(pillars1, pillars2)
        
        # 2. 地支六合分析
        zhi_liuhe = self._analyze_zhi_liuhe(pillars1, pillars2)
        
        # 3. 地支六冲分析
        zhi_liuchong = self._analyze_zhi_liuchong(pillars1, pillars2)
        
        # 4. 五行相生相克分析
        wuxing_shengke = self._analyze_wuxing_shengke(pillars1, pillars2, day_master1, day_master2)
        
        # 5. 综合评分
        comprehensive_score = self._calculate_comprehensive_score(
            gan_hehua, zhi_liuhe, zhi_liuchong, wuxing_shengke
        )
        
        # 6. 判断吉凶等级
        level = self._determine_level(comprehensive_score)
        
        # 生成描述
        description = self._generate_description(
            gan_hehua, zhi_liuhe, zhi_liuchong, wuxing_shengke, comprehensive_score
        )
        
        # 生成建议
        advice = self._generate_advice(
            gan_hehua, zhi_liuhe, zhi_liuchong, wuxing_shengke, comprehensive_score
        )
        
        return create_analysis_result(
            analyzer_name=self.name,
            book_name=self.book_name,
            analysis_type="合冲分析",
            level=level,
            score=0,  # 不打分
            description=description,
            details={
                'gan_hehua': gan_hehua,
                'zhi_liuhe': zhi_liuhe,
                'zhi_liuchong': zhi_liuchong,
                'wuxing_shengke': wuxing_shengke,
                'comprehensive_score': comprehensive_score
            },
            advice=advice
        )
    
    def analyze_single_bazi(self, bazi_data: BaziData) -> AnalysisResult:
        """
        分析单个八字内部的合冲关系
        
        参数：
            bazi_data: 八字数据
        
        返回：
            内部合冲分析结果
        """
        pillars = bazi_data.get_pillars()
        
        # 1. 天干合化分析（内部）
        gan_hehua = self._analyze_gan_hehua_internal(pillars)
        
        # 2. 地支六合分析（内部）
        zhi_liuhe = self._analyze_zhi_liuhe_internal(pillars)
        
        # 3. 地支六冲分析（内部）
        zhi_liuchong = self._analyze_zhi_liuchong_internal(pillars)
        
        # 4. 综合评估
        comprehensive_score = self._calculate_internal_score(
            gan_hehua, zhi_liuhe, zhi_liuchong
        )
        
        level = self._determine_level(comprehensive_score)
        
        description = self._generate_internal_description(
            gan_hehua, zhi_liuhe, zhi_liuchong, comprehensive_score
        )
        
        advice = self._generate_internal_advice(
            gan_hehua, zhi_liuhe, zhi_liuchong
        )
        
        return create_analysis_result(
            analyzer_name=self.name,
            book_name=self.book_name,
            analysis_type="内部合冲分析",
            level=level,
            score=0,
            description=description,
            details={
                'gan_hehua': gan_hehua,
                'zhi_liuhe': zhi_liuhe,
                'zhi_liuchong': zhi_liuchong,
                'comprehensive_score': comprehensive_score
            },
            advice=advice
        )
    
    def analyze(self, bazi_data: BaziData) -> AnalysisResult:
        """
        默认分析：分析单个八字内部的合冲关系
        """
        return self.analyze_single_bazi(bazi_data)
    
    def _analyze_gan_hehua(self, pillars1: Dict, pillars2: Dict) -> Dict[str, Any]:
        """
        分析两个八字之间的天干合化
        """
        hehua_pairs = []
        hehua_count = 0
        
        # 遍历所有天干组合
        for pos1, (gan1, zhi1) in pillars1.items():
            for pos2, (gan2, zhi2) in pillars2.items():
                pair_key1 = gan1 + gan2
                pair_key2 = gan2 + gan1
                
                # 检查是否有合化
                if pair_key1 in TIANGAN_HEHUA:
                    hehua_result = TIANGAN_HEHUA[pair_key1]
                    hehua_pairs.append({
                        'gan1': gan1,
                        'gan2': gan2,
                        'pos1': pos1,
                        'pos2': pos2,
                        'result': hehua_result,
                        'description': f"{pos1}干{gan1}与{pos2}干{gan2}合化{hehua_result}"
                    })
                    hehua_count += 1
        
        return {
            'count': hehua_count,
            'pairs': hehua_pairs,
            'summary': f"共{hehua_count}组天干合化" if hehua_count > 0 else "无天干合化"
        }
    
    def _analyze_zhi_liuhe(self, pillars1: Dict, pillars2: Dict) -> Dict[str, Any]:
        """
        分析两个八字之间的地支六合
        """
        liuhe_pairs = []
        liuhe_count = 0
        
        for pos1, (gan1, zhi1) in pillars1.items():
            for pos2, (gan2, zhi2) in pillars2.items():
                pair_key1 = zhi1 + zhi2
                pair_key2 = zhi2 + zhi1
                
                # 检查是否有六合
                if pair_key1 in DIZHI_LIUHE:
                    liuhe_result = DIZHI_LIUHE[pair_key1]
                    liuhe_pairs.append({
                        'zhi1': zhi1,
                        'zhi2': zhi2,
                        'pos1': pos1,
                        'pos2': pos2,
                        'result': liuhe_result,
                        'description': f"{pos1}支{zhi1}与{pos2}支{zhi2}六合化{liuhe_result}"
                    })
                    liuhe_count += 1
        
        return {
            'count': liuhe_count,
            'pairs': liuhe_pairs,
            'summary': f"共{liuhe_count}组地支六合" if liuhe_count > 0 else "无地支六合"
        }
    
    def _analyze_zhi_liuchong(self, pillars1: Dict, pillars2: Dict) -> Dict[str, Any]:
        """
        分析两个八字之间的地支六冲
        """
        liuchong_pairs = []
        liuchong_count = 0
        
        for pos1, (gan1, zhi1) in pillars1.items():
            for pos2, (gan2, zhi2) in pillars2.items():
                pair_key1 = zhi1 + zhi2
                pair_key2 = zhi2 + zhi1
                
                # 检查是否有六冲
                if pair_key1 in DIZHI_LIUCHONG:
                    liuchong_pairs.append({
                        'zhi1': zhi1,
                        'zhi2': zhi2,
                        'pos1': pos1,
                        'pos2': pos2,
                        'description': f"{pos1}支{zhi1}与{pos2}支{zhi2}六冲"
                    })
                    liuchong_count += 1
        
        return {
            'count': liuchong_count,
            'pairs': liuchong_pairs,
            'summary': f"共{liuchong_count}组地支六冲" if liuchong_count > 0 else "无地支六冲"
        }
    
    def _analyze_wuxing_shengke(self, pillars1: Dict, pillars2: Dict, 
                               day_master1: str, day_master2: str) -> Dict[str, Any]:
        """
        分析两个八字之间的五行相生相克关系
        """
        # 统计两个八字的五行分布
        wuxing1 = {'木': 0.0, '火': 0.0, '土': 0.0, '金': 0.0, '水': 0.0}
        wuxing2 = {'木': 0.0, '火': 0.0, '土': 0.0, '金': 0.0, '水': 0.0}
        
        # 统计八字1的五行
        for pos, (gan, zhi) in pillars1.items():
            wuxing1[get_wuxing_by_tiangan(gan)] += 1.0
            wuxing1[get_wuxing_by_dizhi(zhi)] += 1.0
            for cg, weight in DIZHI_CANGGAN.get(zhi, []):
                wuxing1[get_wuxing_by_tiangan(cg)] += weight
        
        # 统计八字2的五行
        for pos, (gan, zhi) in pillars2.items():
            wuxing2[get_wuxing_by_tiangan(gan)] += 1.0
            wuxing2[get_wuxing_by_dizhi(zhi)] += 1.0
            for cg, weight in DIZHI_CANGGAN.get(zhi, []):
                wuxing2[get_wuxing_by_tiangan(cg)] += weight
        
        # 分析相生相克关系
        dm_wx1 = get_wuxing_by_tiangan(day_master1)
        dm_wx2 = get_wuxing_by_tiangan(day_master2)
        
        # 日主之间的相生相克
        shengke_relation = self._get_wuxing_relation(dm_wx1, dm_wx2)
        
        # 计算相生相克得分
        sheng_score = 0
        ke_score = 0
        details = []
        
        for wx in ['木', '火', '土', '金', '水']:
            count1 = wuxing1[wx]
            count2 = wuxing2[wx]
            
            # 如果两个八字都有这个五行，则为相生（同气相求）
            if count1 > 0 and count2 > 0:
                sheng_score += min(count1, count2)
                details.append(f"同有{wx}（八字1有{count1:.1f}，八字2有{count2:.1f}），相生")
            
            # 分析相克关系
            ke_target = WUXING_KE_MAP.get(wx)
            if ke_target and count1 > 0 and wuxing2[ke_target] > 0:
                ke_score += min(count1, wuxing2[ke_target])
                details.append(f"八字1的{wx}克八字2的{ke_target}，相克")
        
        total_score = sheng_score - ke_score * 0.5  # 相生加分，相克减分
        
        return {
            'relation': shengke_relation,
            'sheng_score': sheng_score,
            'ke_score': ke_score,
            'total_score': total_score,
            'details': details,
            'summary': f"日主关系：{shengke_relation}，相生得分{sheng_score:.1f}，相克得分{ke_score:.1f}"
        }
    
    def _get_wuxing_relation(self, wx1: str, wx2: str) -> str:
        """
        获取两个五行之间的关系
        """
        if wx1 == wx2:
            return '相同'
        elif WUXING_SHENG_MAP.get(wx1) == wx2:
            return '相生（我生他）'
        elif WUXING_SHENG_MAP.get(wx2) == wx1:
            return '相生（他生我）'
        elif WUXING_KE_MAP.get(wx1) == wx2:
            return '相克（我克他）'
        elif WUXING_KE_MAP.get(wx2) == wx1:
            return '相克（他克我）'
        else:
            return '无关'
    
    def _calculate_comprehensive_score(self, gan_hehua: Dict, zhi_liuhe: Dict,
                                      zhi_liuchong: Dict, wuxing_shengke: Dict) -> float:
        """
        计算综合合冲得分
        """
        score = 0.0
        
        # 天干合化加分（每组+5分）
        score += gan_hehua['count'] * 5
        
        # 地支六合加分（每组+3分）
        score += zhi_liuhe['count'] * 3
        
        # 地支六冲减分（每组-5分）
        score -= zhi_liuchong['count'] * 5
        
        # 五行相生相克得分（加权）
        score += wuxing_shengke['total_score'] * 2
        
        return score
    
    def _determine_level(self, score: float) -> str:
        """
        根据得分判断吉凶等级
        """
        if score >= 20:
            return '大吉'
        elif score >= 10:
            return '吉'
        elif score >= 0:
            return '中平'
        elif score >= -10:
            return '凶'
        else:
            return '大凶'
    
    def _generate_description(self, gan_hehua: Dict, zhi_liuhe: Dict,
                             zhi_liuchong: Dict, wuxing_shengke: Dict,
                             score: float) -> str:
        """
        生成合冲分析描述
        """
        desc_parts = []
        
        if gan_hehua['count'] > 0:
            desc_parts.append(gan_hehua['summary'])
        
        if zhi_liuhe['count'] > 0:
            desc_parts.append(zhi_liuhe['summary'])
        
        if zhi_liuchong['count'] > 0:
            desc_parts.append(zhi_liuchong['summary'])
        
        desc_parts.append(wuxing_shengke['summary'])
        desc_parts.append(f"综合得分：{score:.1f}")
        
        return "；".join(desc_parts)
    
    def _generate_advice(self, gan_hehua: Dict, zhi_liuhe: Dict,
                        zhi_liuchong: Dict, wuxing_shengke: Dict,
                        score: float) -> str:
        """
        生成合冲分析建议
        """
        advice_list = []
        
        if gan_hehua['count'] > 0:
            advice_list.append(f"天干有{gan_hehua['count']}组合化，缘分深厚，宜加强合作")
        
        if zhi_liuhe['count'] > 0:
            advice_list.append(f"地支有{zhi_liuhe['count']}组六合，关系和谐，宜相互配合")
        
        if zhi_liuchong['count'] > 0:
            advice_list.append(f"地支有{zhi_liuchong['count']}组六冲，关系紧张，宜注意调和矛盾")
        
        if wuxing_shengke['relation'] == '相克（我克他）':
            advice_list.append("日主相克，一方克制另一方，需要平衡关系")
        elif wuxing_shengke['relation'] == '相生（我生他）':
            advice_list.append("日主相生，一方生助另一方，关系融洽")
        
        if score < 0:
            advice_list.append("综合得分较低，关系需要改善，建议多沟通调和")
        
        if not advice_list:
            return "合冲关系平衡，保持现状即可。"
        
        return "建议：" + "；".join(advice_list) + "。"
    
    # 内部合冲分析方法（单个八字）
    def _analyze_gan_hehua_internal(self, pillars: Dict) -> Dict[str, Any]:
        """分析单个八字内部的天干合化"""
        # ✅ 修复：position英文转中文
        position_cn_map = {
            'year': '年柱',
            'month': '月柱',
            'day': '日柱',
            'hour': '时柱'
        }

        hehua_pairs = []
        gans = [(pos, gan) for pos, (gan, zhi) in pillars.items()]

        for i in range(len(gans)):
            for j in range(i + 1, len(gans)):
                pos1, gan1 = gans[i]
                pos2, gan2 = gans[j]
                pair_key = gan1 + gan2

                if pair_key in TIANGAN_HEHUA:
                    pos1_cn = position_cn_map.get(pos1, pos1)
                    pos2_cn = position_cn_map.get(pos2, pos2)
                    hehua_pairs.append({
                        'gan1': gan1,
                        'gan2': gan2,
                        'pos1': pos1,
                        'pos2': pos2,
                        'result': TIANGAN_HEHUA[pair_key],
                        'description': f"{pos1_cn}干{gan1}与{pos2_cn}干{gan2}合化{TIANGAN_HEHUA[pair_key]}"
                    })

        return {
            'count': len(hehua_pairs),
            'pairs': hehua_pairs,
            'summary': f"内部共{len(hehua_pairs)}组天干合化" if hehua_pairs else "内部无天干合化"
        }
    
    def _analyze_zhi_liuhe_internal(self, pillars: Dict) -> Dict[str, Any]:
        """分析单个八字内部的地支六合"""
        # ✅ 修复：position英文转中文
        position_cn_map = {
            'year': '年柱',
            'month': '月柱',
            'day': '日柱',
            'hour': '时柱'
        }

        liuhe_pairs = []
        zhis = [(pos, zhi) for pos, (gan, zhi) in pillars.items()]

        for i in range(len(zhis)):
            for j in range(i + 1, len(zhis)):
                pos1, zhi1 = zhis[i]
                pos2, zhi2 = zhis[j]
                pair_key = zhi1 + zhi2

                if pair_key in DIZHI_LIUHE:
                    pos1_cn = position_cn_map.get(pos1, pos1)
                    pos2_cn = position_cn_map.get(pos2, pos2)
                    liuhe_pairs.append({
                        'zhi1': zhi1,
                        'zhi2': zhi2,
                        'pos1': pos1,
                        'pos2': pos2,
                        'result': DIZHI_LIUHE[pair_key],
                        'description': f"{pos1_cn}支{zhi1}与{pos2_cn}支{zhi2}六合化{DIZHI_LIUHE[pair_key]}"
                    })

        return {
            'count': len(liuhe_pairs),
            'pairs': liuhe_pairs,
            'summary': f"内部共{len(liuhe_pairs)}组地支六合" if liuhe_pairs else "内部无地支六合"
        }
    
    def _analyze_zhi_liuchong_internal(self, pillars: Dict) -> Dict[str, Any]:
        """分析单个八字内部的地支六冲"""
        # ✅ 修复：position英文转中文
        position_cn_map = {
            'year': '年柱',
            'month': '月柱',
            'day': '日柱',
            'hour': '时柱'
        }

        liuchong_pairs = []
        zhis = [(pos, zhi) for pos, (gan, zhi) in pillars.items()]

        for i in range(len(zhis)):
            for j in range(i + 1, len(zhis)):
                pos1, zhi1 = zhis[i]
                pos2, zhi2 = zhis[j]
                pair_key = zhi1 + zhi2

                if pair_key in DIZHI_LIUCHONG:
                    pos1_cn = position_cn_map.get(pos1, pos1)
                    pos2_cn = position_cn_map.get(pos2, pos2)
                    liuchong_pairs.append({
                        'zhi1': zhi1,
                        'zhi2': zhi2,
                        'pos1': pos1,
                        'pos2': pos2,
                        'description': f"{pos1_cn}支{zhi1}与{pos2_cn}支{zhi2}六冲"
                    })

        return {
            'count': len(liuchong_pairs),
            'pairs': liuchong_pairs,
            'summary': f"内部共{len(liuchong_pairs)}组地支六冲" if liuchong_pairs else "内部无地支六冲"
        }
    
    def _calculate_internal_score(self, gan_hehua: Dict, zhi_liuhe: Dict,
                                 zhi_liuchong: Dict) -> float:
        """计算内部合冲得分"""
        score = 0.0
        score += gan_hehua['count'] * 3
        score += zhi_liuhe['count'] * 2
        score -= zhi_liuchong['count'] * 3
        return score
    
    def _generate_internal_description(self, gan_hehua: Dict, zhi_liuhe: Dict,
                                      zhi_liuchong: Dict, score: float) -> str:
        """生成内部合冲描述"""
        desc_parts = [
            gan_hehua['summary'],
            zhi_liuhe['summary'],
            zhi_liuchong['summary'],
            f"内部合冲得分：{score:.1f}"
        ]
        return "；".join(desc_parts)
    
    def _generate_internal_advice(self, gan_hehua: Dict, zhi_liuhe: Dict,
                                 zhi_liuchong: Dict) -> str:
        """生成内部合冲建议"""
        advice_list = []
        
        if zhi_liuchong['count'] > 0:
            advice_list.append(f"内部有{zhi_liuchong['count']}组六冲，命局有矛盾，需要调和")
        
        if gan_hehua['count'] > 0 or zhi_liuhe['count'] > 0:
            advice_list.append("内部有合化，命局和谐，但需注意合化后的五行变化")
        
        if not advice_list:
            return "内部合冲关系平衡，命局稳定。"
        
        return "建议：" + "；".join(advice_list) + "。"

