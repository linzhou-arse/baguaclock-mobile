#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五行分析模块 - 基于《滴天髓》理论
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


class WuxingAnalyzer:
    """五行分析器 - 基于《滴天髓》理论"""
    
    # 五行生克关系表（基于《滴天髓》）
    WUXING_SHENGKE = {
        '木': {'生': '火', '克': '土', '被生': '水', '被克': '金'},
        '火': {'生': '土', '克': '金', '被生': '木', '被克': '水'},
        '土': {'生': '金', '克': '水', '被生': '火', '被克': '木'},
        '金': {'生': '水', '克': '木', '被生': '土', '被克': '火'},
        '水': {'生': '木', '克': '火', '被生': '金', '被克': '土'},
    }
    
    # 五行调候表（基于《滴天髓》）
    WUXING_TIAOHOU = {
        '木': {'寒': '火', '热': '水', '湿': '土', '燥': '水'},
        '火': {'寒': '木', '热': '水', '湿': '土', '燥': '水'},
        '土': {'寒': '火', '热': '水', '湿': '木', '燥': '水'},
        '金': {'寒': '火', '热': '水', '湿': '土', '燥': '水'},
        '水': {'寒': '火', '热': '土', '湿': '木', '燥': '金'},
    }
    
    # 五行旺衰表（基于《滴天髓》）
    WUXING_WANGSHUAI = {
        '春': {'旺': '木', '相': '火', '休': '水', '囚': '金', '死': '土'},
        '夏': {'旺': '火', '相': '土', '休': '木', '囚': '水', '死': '金'},
        '秋': {'旺': '金', '相': '水', '休': '土', '囚': '火', '死': '木'},
        '冬': {'旺': '水', '相': '木', '休': '金', '囚': '土', '死': '火'},
        '四季': {'旺': '土', '相': '金', '休': '火', '囚': '木', '死': '水'},
    }
    
    @classmethod
    def analyze_wuxing(cls, pillars: Dict[str, Tuple[str, str]], day_master: Optional[str] = None) -> Dict[str, Any]:
        """
        五行分析 - 基于《滴天髓》理论
        
        参数:
            pillars: 四柱信息 {'year': ('甲','子'), 'month': ('乙','丑'), 'day': ('丙','寅'), 'hour': ('丁','卯')}
            day_master: 日主，如果为None则从日柱提取
        
        返回:
            五行分析结果
        """
        if not pillars or 'day' not in pillars:
            raise ValueError('分析五行需要完整的四柱信息')
        
        day_master = day_master or pillars['day'][0]
        month_branch = pillars['month'][1]
        
        # 1. 分析五行分布
        wuxing_distribution = cls._analyze_wuxing_distribution(pillars)
        
        # 2. 分析五行旺衰
        wuxing_wangshuai = cls._analyze_wuxing_wangshuai(day_master, month_branch, pillars)
        
        # 3. 分析五行生克
        wuxing_shengke = cls._analyze_wuxing_shengke(wuxing_distribution, pillars)
        
        # 4. 分析五行调候
        wuxing_tiaohou = cls._analyze_wuxing_tiaohou(day_master, month_branch, pillars)
        
        # 5. 分析五行平衡
        wuxing_balance = cls._analyze_wuxing_balance(wuxing_distribution, wuxing_wangshuai, wuxing_shengke)
        
        # 6. 综合评分
        total_score = cls._calculate_wuxing_score(wuxing_distribution, wuxing_wangshuai, wuxing_shengke, wuxing_tiaohou, wuxing_balance)
        
        return {
            'wuxing_distribution': wuxing_distribution,
            'wuxing_wangshuai': wuxing_wangshuai,
            'wuxing_shengke': wuxing_shengke,
            'wuxing_tiaohou': wuxing_tiaohou,
            'wuxing_balance': wuxing_balance,
            'total_score': total_score,
            'description': cls._get_wuxing_description(wuxing_distribution, wuxing_balance),
            'advice': cls._get_wuxing_advice(wuxing_distribution, wuxing_balance, wuxing_tiaohou),
        }
    
    @classmethod
    def _analyze_wuxing_distribution(cls, pillars: Dict[str, Tuple[str, str]]) -> Dict[str, Any]:
        """分析五行分布 - 基于《滴天髓》理论"""
        wuxing_count = {'木': 0, '火': 0, '土': 0, '金': 0, '水': 0}
        wuxing_weight = {'木': 0.0, '火': 0.0, '土': 0.0, '金': 0.0, '水': 0.0}
        
        # 分析天干五行
        for pillar, (gan, zhi) in pillars.items():
            gan_wuxing = TIANGAN_WUXING.get(gan, '')
            if gan_wuxing:
                wuxing_count[gan_wuxing] += 1
                wuxing_weight[gan_wuxing] += 1.0
        
        # 分析地支五行（包括藏干）
        for pillar, (gan, zhi) in pillars.items():
            zhi_wuxing = DIZHI_WUXING.get(zhi, '')
            if zhi_wuxing:
                wuxing_count[zhi_wuxing] += 1
                wuxing_weight[zhi_wuxing] += 1.0
            
            # 分析地支藏干
            canggan_list = DIZHI_CANGGAN_WEIGHTS.get(zhi, [])
            for canggan, weight in canggan_list:
                canggan_wuxing = TIANGAN_WUXING.get(canggan, '')
                if canggan_wuxing:
                    wuxing_weight[canggan_wuxing] += weight
        
        # 计算五行百分比
        total_weight = sum(wuxing_weight.values())
        wuxing_percentage = {k: v / total_weight * 100 if total_weight > 0 else 0 for k, v in wuxing_weight.items()}
        
        # 分析五行强弱
        wuxing_strength = cls._analyze_wuxing_strength(wuxing_weight)
        
        # 分析缺失五行
        missing_wuxing = [k for k, v in wuxing_count.items() if v == 0]
        
        return {
            'wuxing_count': wuxing_count,
            'wuxing_weight': wuxing_weight,
            'wuxing_percentage': wuxing_percentage,
            'wuxing_strength': wuxing_strength,
            'missing_wuxing': missing_wuxing,
            'total_weight': total_weight,
        }
    
    @classmethod
    def _analyze_wuxing_strength(cls, wuxing_weight: Dict[str, float]) -> Dict[str, str]:
        """分析五行强弱"""
        max_weight = max(wuxing_weight.values()) if wuxing_weight.values() else 0
        min_weight = min(wuxing_weight.values()) if wuxing_weight.values() else 0
        
        wuxing_strength = {}
        for wuxing, weight in wuxing_weight.items():
            if weight >= max_weight * 0.8:
                wuxing_strength[wuxing] = '旺'
            elif weight >= max_weight * 0.6:
                wuxing_strength[wuxing] = '相'
            elif weight >= max_weight * 0.4:
                wuxing_strength[wuxing] = '休'
            elif weight >= max_weight * 0.2:
                wuxing_strength[wuxing] = '囚'
            else:
                wuxing_strength[wuxing] = '死'
        
        return wuxing_strength
    
    @classmethod
    def _analyze_wuxing_wangshuai(cls, day_master: str, month_branch: str, pillars: Dict[str, Tuple[str, str]]) -> Dict[str, Any]:
        """分析五行旺衰 - 基于《滴天髓》理论"""
        # 确定季节
        season = cls._determine_season(month_branch)
        
        # 获取季节旺衰表
        season_wangshuai = cls.WUXING_WANGSHUAI.get(season, {})
        
        # 分析日主旺衰
        day_master_wuxing = TIANGAN_WUXING.get(day_master, '')
        day_master_wangshuai = season_wangshuai.get(day_master_wuxing, '平')
        
        # 分析各五行旺衰
        wuxing_wangshuai = {}
        for wuxing in ['木', '火', '土', '金', '水']:
            wuxing_wangshuai[wuxing] = season_wangshuai.get(wuxing, '平')
        
        return {
            'season': season,
            'day_master_wuxing': day_master_wuxing,
            'day_master_wangshuai': day_master_wangshuai,
            'wuxing_wangshuai': wuxing_wangshuai,
        }
    
    @classmethod
    def _determine_season(cls, month_branch: str) -> str:
        """确定季节"""
        spring_branches = ['寅', '卯', '辰']
        summer_branches = ['巳', '午', '未']
        autumn_branches = ['申', '酉', '戌']
        winter_branches = ['亥', '子', '丑']
        
        if month_branch in spring_branches:
            return '春'
        elif month_branch in summer_branches:
            return '夏'
        elif month_branch in autumn_branches:
            return '秋'
        elif month_branch in winter_branches:
            return '冬'
        else:
            return '四季'
    
    @classmethod
    def _analyze_wuxing_shengke(cls, wuxing_distribution: Dict[str, Any], pillars: Dict[str, Tuple[str, str]]) -> Dict[str, Any]:
        """分析五行生克 - 基于《滴天髓》理论"""
        wuxing_weight = wuxing_distribution.get('wuxing_weight', {})
        
        # 分析生克关系
        shengke_analysis = {}
        for wuxing in ['木', '火', '土', '金', '水']:
            shengke_info = cls.WUXING_SHENGKE.get(wuxing, {})
            shengke_analysis[wuxing] = {
                '生': shengke_info.get('生', ''),
                '克': shengke_info.get('克', ''),
                '被生': shengke_info.get('被生', ''),
                '被克': shengke_info.get('被克', ''),
                '生力': wuxing_weight.get(shengke_info.get('生', ''), 0),
                '克力': wuxing_weight.get(shengke_info.get('克', ''), 0),
                '被生力': wuxing_weight.get(shengke_info.get('被生', ''), 0),
                '被克力': wuxing_weight.get(shengke_info.get('被克', ''), 0),
            }
        
        # 分析生克平衡
        shengke_balance = cls._calculate_shengke_balance(shengke_analysis)
        
        return {
            'shengke_analysis': shengke_analysis,
            'shengke_balance': shengke_balance,
        }
    
    @classmethod
    def _calculate_shengke_balance(cls, shengke_analysis: Dict[str, Any]) -> str:
        """计算生克平衡"""
        total_sheng = sum(info.get('生力', 0) for info in shengke_analysis.values())
        total_ke = sum(info.get('克力', 0) for info in shengke_analysis.values())
        
        if total_sheng > total_ke * 1.2:
            return '生多克少'
        elif total_ke > total_sheng * 1.2:
            return '克多生少'
        else:
            return '生克平衡'
    
    @classmethod
    def _analyze_wuxing_tiaohou(cls, day_master: str, month_branch: str, pillars: Dict[str, Tuple[str, str]]) -> Dict[str, Any]:
        """分析五行调候 - 基于《滴天髓》理论"""
        day_master_wuxing = TIANGAN_WUXING.get(day_master, '')
        month_branch_wuxing = DIZHI_WUXING.get(month_branch, '')
        
        # 分析调候需求
        tiaohou_needs = cls._analyze_tiaohou_needs(day_master_wuxing, month_branch_wuxing)
        
        # 分析调候用神
        tiaohou_yongshen = cls._analyze_tiaohou_yongshen(tiaohou_needs, pillars)
        
        return {
            'tiaohou_needs': tiaohou_needs,
            'tiaohou_yongshen': tiaohou_yongshen,
        }
    
    @classmethod
    def _analyze_tiaohou_needs(cls, day_master_wuxing: str, month_branch_wuxing: str) -> List[str]:
        """分析调候需求"""
        needs = []
        
        # 基于日主和月支分析调候需求
        if day_master_wuxing == '木' and month_branch_wuxing in ['亥', '子', '丑']:
            needs.append('火')  # 寒木需要火调候
        elif day_master_wuxing == '火' and month_branch_wuxing in ['亥', '子', '丑']:
            needs.append('木')  # 寒火需要木调候
        elif day_master_wuxing == '土' and month_branch_wuxing in ['亥', '子', '丑']:
            needs.append('火')  # 寒土需要火调候
        elif day_master_wuxing == '金' and month_branch_wuxing in ['亥', '子', '丑']:
            needs.append('火')  # 寒金需要火调候
        elif day_master_wuxing == '水' and month_branch_wuxing in ['亥', '子', '丑']:
            needs.append('火')  # 寒水需要火调候
        
        return needs
    
    @classmethod
    def _analyze_tiaohou_yongshen(cls, tiaohou_needs: List[str], pillars: Dict[str, Tuple[str, str]]) -> List[str]:
        """分析调候用神"""
        yongshen = []
        
        # 检查四柱中是否有调候用神
        for pillar, (gan, zhi) in pillars.items():
            gan_wuxing = TIANGAN_WUXING.get(gan, '')
            zhi_wuxing = DIZHI_WUXING.get(zhi, '')
            
            if gan_wuxing in tiaohou_needs:
                yongshen.append(gan)
            if zhi_wuxing in tiaohou_needs:
                yongshen.append(zhi)
        
        return yongshen
    
    @classmethod
    def _analyze_wuxing_balance(cls, wuxing_distribution: Dict[str, Any], wuxing_wangshuai: Dict[str, Any], wuxing_shengke: Dict[str, Any]) -> Dict[str, Any]:
        """分析五行平衡 - 基于《滴天髓》理论"""
        wuxing_weight = wuxing_distribution.get('wuxing_weight', {})
        wuxing_strength = wuxing_distribution.get('wuxing_strength', {})
        
        # 计算五行平衡度
        balance_score = cls._calculate_balance_score(wuxing_weight, wuxing_strength)
        
        # 分析五行缺失
        missing_wuxing = wuxing_distribution.get('missing_wuxing', [])
        
        # 分析五行过旺
        over_wang_wuxing = [k for k, v in wuxing_strength.items() if v == '旺']
        
        return {
            'balance_score': balance_score,
            'balance_level': cls._get_balance_level(balance_score),
            'missing_wuxing': missing_wuxing,
            'over_wang_wuxing': over_wang_wuxing,
        }
    
    @classmethod
    def _calculate_balance_score(cls, wuxing_weight: Dict[str, float], wuxing_strength: Dict[str, str]) -> float:
        """计算平衡度"""
        if not wuxing_weight:
            return 0.0
        
        # 计算权重方差
        weights = list(wuxing_weight.values())
        mean_weight = sum(weights) / len(weights)
        variance = sum((w - mean_weight) ** 2 for w in weights) / len(weights)
        
        # 计算平衡度（方差越小越平衡）
        max_variance = mean_weight ** 2
        balance_score = 1.0 - (variance / max_variance) if max_variance > 0 else 1.0
        
        return max(0.0, min(1.0, balance_score))
    
    @classmethod
    def _get_balance_level(cls, balance_score: float) -> str:
        """获取平衡等级"""
        if balance_score >= 0.8:
            return '平衡'
        elif balance_score >= 0.6:
            return '较平衡'
        elif balance_score >= 0.4:
            return '不平衡'
        else:
            return '严重不平衡'
    
    @classmethod
    def _calculate_wuxing_score(cls, wuxing_distribution: Dict[str, Any], wuxing_wangshuai: Dict[str, Any], wuxing_shengke: Dict[str, Any], wuxing_tiaohou: Dict[str, Any], wuxing_balance: Dict[str, Any]) -> int:
        """计算五行评分"""
        base_score = 60
        
        # 根据五行平衡调整
        balance_score = wuxing_balance.get('balance_score', 0.5)
        base_score += int((balance_score - 0.5) * 40)
        
        # 根据缺失五行调整
        missing_count = len(wuxing_balance.get('missing_wuxing', []))
        base_score -= missing_count * 5
        
        # 根据过旺五行调整
        over_wang_count = len(wuxing_balance.get('over_wang_wuxing', []))
        base_score -= over_wang_count * 3
        
        # 根据调候用神调整
        tiaohou_yongshen = wuxing_tiaohou.get('tiaohou_yongshen', [])
        if tiaohou_yongshen:
            base_score += 5
        
        return clamp_score(base_score)
    
    @classmethod
    def _get_wuxing_description(cls, wuxing_distribution: Dict[str, Any], wuxing_balance: Dict[str, Any]) -> str:
        """获取五行描述"""
        balance_level = wuxing_balance.get('balance_level', '不平衡')
        missing_wuxing = wuxing_balance.get('missing_wuxing', [])
        
        desc = f"五行{balance_level}"
        if missing_wuxing:
            desc += f"，缺失{''.join(missing_wuxing)}"
        
        return desc
    
    @classmethod
    def _get_wuxing_advice(cls, wuxing_distribution: Dict[str, Any], wuxing_balance: Dict[str, Any], wuxing_tiaohou: Dict[str, Any]) -> str:
        """获取五行建议"""
        balance_level = wuxing_balance.get('balance_level', '不平衡')
        missing_wuxing = wuxing_balance.get('missing_wuxing', [])
        tiaohou_yongshen = wuxing_tiaohou.get('tiaohou_yongshen', [])
        
        if balance_level == '平衡':
            return '五行平衡，宜保持现状，注重协调发展'
        elif missing_wuxing:
            return f'五行缺失{"".join(missing_wuxing)}，宜补充相应元素，注重平衡发展'
        elif tiaohou_yongshen:
            return '需要调候用神，宜注重环境调节，保持身心平衡'
        else:
            return '五行不平衡，宜注重整体协调，避免偏颇发展'
