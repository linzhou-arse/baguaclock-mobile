#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
祖上庇护分析器 - Zushang Analyzer
================================

基于《渊海子平·六亲章》《三命通会·六亲论》的祖上庇护分析器

功能：
1. 年柱父母宫分析
2. 正印偏财与祖上关系
3. 祖上庇护能力评估

理论依据：
- 《渊海子平·六亲章》：年柱为父母宫，代表祖上
- 《三命通会·六亲论》：年柱干支代表祖辈、父母
- 正印代表祖上德泽，偏财代表祖上财富
"""

from typing import Dict, List, Tuple, Any, Optional
from ..core.base_analyzer import BaseAnalyzer
from ..core.data_structures import BaziData, AnalysisResult, AnalysisConfig
from ..core.utils import create_analysis_result, get_wuxing_by_tiangan, get_wuxing_by_dizhi
from ..core.constants import DIZHI_CANGGAN
from ..core.utils import get_ten_god


class ZushangAnalyzer(BaseAnalyzer):
    """
    祖上庇护分析器 - 基于《渊海子平·六亲章》《三命通会·六亲论》
    """
    
    def __init__(self, config: AnalysisConfig = None):
        super().__init__("祖上庇护分析器", "渊海子平", config)
    
    def analyze(self, bazi_data: BaziData) -> AnalysisResult:
        """
        分析祖上庇护能力
        """
        pillars = bazi_data.get_pillars()
        day_master = bazi_data.get_day_master()
        gender = bazi_data.gender
        
        # 1. 年柱分析（父母宫）
        nianzhu_analysis = self._analyze_nianzhu(pillars, day_master, gender)
        
        # 2. 正印分析（祖上德泽）
        zhengyin_analysis = self._analyze_zhengyin(pillars, day_master)
        
        # 3. 偏财分析（祖上财富）
        piancai_analysis = self._analyze_piancai(pillars, day_master, gender)
        
        # 4. 综合评估祖上庇护能力
        comprehensive_assessment = self._comprehensive_assessment(
            nianzhu_analysis, zhengyin_analysis, piancai_analysis
        )
        
        # 判断吉凶等级
        level = self._determine_level(comprehensive_assessment)
        
        # 生成描述
        description = self._generate_description(
            nianzhu_analysis, zhengyin_analysis, piancai_analysis, comprehensive_assessment
        )
        
        # 生成建议
        advice = self._generate_advice(comprehensive_assessment)
        
        return create_analysis_result(
            analyzer_name=self.name,
            book_name=self.book_name,
            analysis_type="祖上庇护分析",
            level=level,
            score=0,
            description=description,
            details={
                'nianzhu_analysis': nianzhu_analysis,
                'zhengyin_analysis': zhengyin_analysis,
                'piancai_analysis': piancai_analysis,
                'comprehensive_assessment': comprehensive_assessment
            },
            advice=advice
        )
    
    def _analyze_nianzhu(self, pillars: Dict, day_master: str, gender: str) -> Dict[str, Any]:
        """
        分析年柱（父母宫）
        """
        year_gan, year_zhi = pillars.get('year', ('', ''))
        
        # 年干十神
        year_gan_tg = get_ten_god(day_master, year_gan) if year_gan else None
        
        # 年支藏干分析
        year_zhi_canggan = []
        year_zhi_tg = []
        if year_zhi:
            canggan_list = DIZHI_CANGGAN.get(year_zhi, [])
            for cg, weight in canggan_list:
                tg = get_ten_god(day_master, cg)
                year_zhi_canggan.append({
                    'canggan': cg,
                    'weight': weight,
                    'ten_god': tg
                })
                year_zhi_tg.append(tg)
        
        # 判断年柱强弱（是否有根气）
        year_strong = False
        if year_zhi:
            # 检查年支藏干是否有本气（权重>=0.6）
            for item in year_zhi_canggan:
                if item['weight'] >= 0.6:
                    year_strong = True
                    break
        
        # 评估年柱父母宫
        if year_gan_tg in ['正印', '偏印']:
            assessment = '年柱有印，祖上德泽深厚'
        elif year_gan_tg in ['正财', '偏财']:
            assessment = '年柱有财，祖上财富较好'
        elif year_gan_tg in ['正官', '偏官']:
            assessment = '年柱有官，祖上有官运'
        else:
            assessment = '年柱父母宫一般'
        
        return {
            'year_gan': year_gan,
            'year_zhi': year_zhi,
            'year_gan_ten_god': year_gan_tg,
            'year_zhi_canggan': year_zhi_canggan,
            'year_strong': year_strong,
            'assessment': assessment
        }
    
    def _analyze_zhengyin(self, pillars: Dict, day_master: str) -> Dict[str, Any]:
        """
        分析正印（代表祖上德泽）
        """
        zhengyin_count = 0.0
        zhengyin_positions = []
        
        # 统计正印（天干+地支藏干）
        for pos, (gan, zhi) in pillars.items():
            # 天干正印
            ten_god = get_ten_god(day_master, gan)
            if ten_god == '正印':
                zhengyin_count += 1.0
                zhengyin_positions.append({
                    'position': pos,
                    'type': '天干',
                    'gan': gan,
                    'weight': 1.0
                })
            
            # 地支藏干正印
            canggan_list = DIZHI_CANGGAN.get(zhi, [])
            for cg, weight in canggan_list:
                tg = get_ten_god(day_master, cg)
                if tg == '正印':
                    zhengyin_count += weight
                    zhengyin_positions.append({
                        'position': pos,
                        'type': '地支藏干',
                        'zhi': zhi,
                        'canggan': cg,
                        'weight': weight
                    })
        
        # 评估正印强弱
        if zhengyin_count >= 2.0:
            strength = '强'
            desc = '正印强，祖上德泽深厚，有良好家风传承'
        elif zhengyin_count >= 1.0:
            strength = '中等'
            desc = '正印中等，祖上有一定德泽'
        elif zhengyin_count >= 0.5:
            strength = '弱'
            desc = '正印弱，祖上德泽一般'
        else:
            strength = '无'
            desc = '正印不显，祖上德泽较少'
        
        return {
            'count': zhengyin_count,
            'positions': zhengyin_positions,
            'strength': strength,
            'description': desc
        }
    
    def _analyze_piancai(self, pillars: Dict, day_master: str, gender: str) -> Dict[str, Any]:
        """
        分析偏财（代表祖上财富，男命偏财为父，女命正官为父）
        """
        is_male = gender == '男'
        
        # 根据性别判断父星
        if is_male:
            father_star_name = '偏财'
        else:
            father_star_name = '正官'  # 女命正官为父
        
        father_star_count = 0.0
        father_star_positions = []
        
        # 统计父星（天干+地支藏干）
        for pos, (gan, zhi) in pillars.items():
            ten_god = get_ten_god(day_master, gan)
            if ten_god == father_star_name:
                father_star_count += 1.0
                father_star_positions.append({
                    'position': pos,
                    'type': '天干',
                    'gan': gan,
                    'weight': 1.0
                })
            
            # 地支藏干
            canggan_list = DIZHI_CANGGAN.get(zhi, [])
            for cg, weight in canggan_list:
                tg = get_ten_god(day_master, cg)
                if tg == father_star_name:
                    father_star_count += weight
                    father_star_positions.append({
                        'position': pos,
                        'type': '地支藏干',
                        'zhi': zhi,
                        'canggan': cg,
                        'weight': weight
                    })
        
        # 评估父星强弱（代表祖上财富）
        if father_star_count >= 1.5:
            strength = '强'
            desc = f'{father_star_name}强，祖上财富较好，有经济基础'
        elif father_star_count >= 1.0:
            strength = '中等'
            desc = f'{father_star_name}中等，祖上有一定财富'
        elif father_star_count >= 0.5:
            strength = '弱'
            desc = f'{father_star_name}弱，祖上财富一般'
        else:
            strength = '无'
            desc = f'{father_star_name}不显，祖上财富较少'
        
        return {
            'count': father_star_count,
            'positions': father_star_positions,
            'strength': strength,
            'description': desc,
            'star_name': father_star_name
        }
    
    def _comprehensive_assessment(self, nianzhu: Dict, zhengyin: Dict, 
                                 piancai: Dict) -> Dict[str, Any]:
        """
        综合评估祖上庇护能力
        """
        # 评分系统
        score = 0.0
        
        # 年柱评分（0-30分）
        if nianzhu['year_strong']:
            score += 15
        if nianzhu['year_gan_ten_god'] in ['正印', '偏印', '正财', '偏财', '正官', '偏官']:
            score += 15
        
        # 正印评分（0-35分）
        zhengyin_scores = {'强': 35, '中等': 20, '弱': 10, '无': 0}
        score += zhengyin_scores.get(zhengyin['strength'], 0)
        
        # 偏财评分（0-35分）
        piancai_scores = {'强': 35, '中等': 20, '弱': 10, '无': 0}
        score += piancai_scores.get(piancai['strength'], 0)
        
        # 判断庇护等级
        if score >= 80:
            level = '庇护极强'
            desc = '祖上庇护能力极强，德泽深厚，有良好家世背景'
        elif score >= 60:
            level = '庇护较强'
            desc = '祖上庇护能力较强，有一定德泽和财富基础'
        elif score >= 40:
            level = '庇护中等'
            desc = '祖上庇护能力中等，有一定基础但不够深厚'
        elif score >= 20:
            level = '庇护较弱'
            desc = '祖上庇护能力较弱，需要自身努力'
        else:
            level = '庇护很弱'
            desc = '祖上庇护能力很弱，主要靠自身奋斗'
        
        return {
            'score': score,
            'level': level,
            'description': desc,
            'details': {
                'nianzhu_score': 15 if nianzhu['year_strong'] else 0,
                'zhengyin_score': zhengyin_scores.get(zhengyin['strength'], 0),
                'piancai_score': piancai_scores.get(piancai['strength'], 0)
            }
        }
    
    def _determine_level(self, assessment: Dict) -> str:
        """
        判断吉凶等级
        """
        score = assessment['score']
        
        if score >= 80:
            return '大吉'
        elif score >= 60:
            return '吉'
        elif score >= 40:
            return '中平'
        elif score >= 20:
            return '凶'
        else:
            return '大凶'
    
    def _generate_description(self, nianzhu: Dict, zhengyin: Dict,
                             piancai: Dict, assessment: Dict) -> str:
        """
        生成描述
        """
        desc_parts = []
        
        desc_parts.append(f"年柱：{nianzhu['year_gan']}{nianzhu['year_zhi']}（{nianzhu['assessment']}）")
        desc_parts.append(f"正印：{zhengyin['description']}（{zhengyin['count']:.1f}）")
        desc_parts.append(f"偏财：{piancai['description']}（{piancai['count']:.1f}）")
        desc_parts.append(f"综合：{assessment['description']}（得分{assessment['score']:.0f}）")
        
        return "；".join(desc_parts)
    
    def _generate_advice(self, assessment: Dict) -> str:
        """
        生成建议
        """
        score = assessment['score']
        level = assessment['level']
        
        advice_list = []
        
        if score >= 80:
            advice_list.append("祖上庇护极强，应珍惜家世背景，传承良好家风")
            advice_list.append("可依靠祖上德泽和财富，但要保持谦逊和努力")
        elif score >= 60:
            advice_list.append("祖上庇护较强，有良好基础，宜继续发扬光大")
            advice_list.append("可适当依靠祖上资源，但要培养自身能力")
        elif score >= 40:
            advice_list.append("祖上庇护中等，有一定基础，主要靠自身努力")
            advice_list.append("可通过后天努力和善行积累，改善家族运势")
        elif score >= 20:
            advice_list.append("祖上庇护较弱，需更多依靠自身奋斗")
            advice_list.append("可通过教育、修行、善行等方式，为后代积累福德")
        else:
            advice_list.append("祖上庇护很弱，完全依靠自身奋斗")
            advice_list.append("可通过自身努力和善行，开创家族新气象")
            advice_list.append("注意教育后代，为家族积累福德")
        
        return "建议：" + "；".join(advice_list) + "。"

