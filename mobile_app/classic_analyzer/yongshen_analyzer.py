#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用神分析模块 - 基于《子平真诠》理论
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


class YongshenAnalyzer:
    """用神分析器 - 基于《子平真诠》理论"""
    
    # 用神类型表（基于《子平真诠》）
    YONGSHEN_TYPES = {
        '正用神': {'description': '月令透出者，为真用神', 'level': '贵'},
        '假用神': {'description': '月令不透出者，为假用神', 'level': '平'},
        '用神变化': {'description': '用神有变化，不可执一', 'level': '变'},
        '用神混杂': {'description': '用神混杂，需要清纯', 'level': '杂'},
        '用神缺失': {'description': '用神缺失，需要补救', 'level': '缺'},
    }
    
    # 用神喜忌表（基于《子平真诠》）
    YONGSHEN_XIJI = {
        '正官': {'xi': ['印星', '比劫'], 'ji': ['食伤', '财星']},
        '偏官': {'xi': ['印星', '比劫'], 'ji': ['食伤', '财星']},
        '正财': {'xi': ['食伤', '官杀'], 'ji': ['比劫', '印星']},
        '偏财': {'xi': ['食伤', '官杀'], 'ji': ['比劫', '印星']},
        '正印': {'xi': ['官杀', '比劫'], 'ji': ['财星', '食伤']},
        '偏印': {'xi': ['官杀', '比劫'], 'ji': ['财星', '食伤']},
        '食神': {'xi': ['财星', '比劫'], 'ji': ['印星', '官杀']},
        '伤官': {'xi': ['财星', '比劫'], 'ji': ['印星', '官杀']},
        '比肩': {'xi': ['印星', '食伤'], 'ji': ['官杀', '财星']},
        '劫财': {'xi': ['印星', '食伤'], 'ji': ['官杀', '财星']},
    }
    
    @classmethod
    def analyze_yongshen(cls, pillars: Dict[str, Tuple[str, str]], day_master: Optional[str] = None) -> Dict[str, Any]:
        """
        用神分析 - 基于《子平真诠》理论
        
        参数:
            pillars: 四柱信息 {'year': ('甲','子'), 'month': ('乙','丑'), 'day': ('丙','寅'), 'hour': ('丁','卯')}
            day_master: 日主，如果为None则从日柱提取
        
        返回:
            用神分析结果
        """
        if not pillars or 'day' not in pillars:
            raise ValueError('分析用神需要完整的四柱信息')
        
        day_master = day_master or pillars['day'][0]
        month_branch = pillars['month'][1]
        month_gan = pillars['month'][0]
        
        # 1. 分析月令用神（基于《子平真诠》理论）
        month_yongshen = cls._analyze_month_yongshen(day_master, month_gan, month_branch, pillars)
        
        # 2. 分析用神类型
        yongshen_type = cls._determine_yongshen_type(month_yongshen, pillars)
        
        # 3. 分析用神强弱
        yongshen_strength = cls._analyze_yongshen_strength(month_yongshen, pillars)
        
        # 4. 分析用神喜忌
        yongshen_xiji = cls._analyze_yongshen_xiji(day_master, month_yongshen, pillars)
        
        # 5. 分析用神流通
        yongshen_liutong = cls._analyze_yongshen_liutong(day_master, month_yongshen, pillars)

        # ✅ 修复：添加忌神分析
        jishen_list = cls._analyze_jishen(day_master, month_yongshen, pillars)

        return {
            'yongshen_type': yongshen_type,
            'month_yongshen': month_yongshen,
            'yongshen_strength': yongshen_strength,
            'yongshen_xiji': yongshen_xiji,
            'yongshen_liutong': yongshen_liutong,
            'description': cls._get_yongshen_description(yongshen_type, yongshen_strength),
            'advice': cls._get_yongshen_advice(yongshen_type, yongshen_strength, yongshen_xiji),
            'jishen': jishen_list,
            'classic_basis': '《子平真诠》：八字用神，专求月令；伤用神甚于伤身。',
        }
    
    @classmethod
    def _analyze_month_yongshen(cls, day_master: str, month_gan: str, month_branch: str, pillars: Dict[str, Tuple[str, str]]) -> Dict[str, Any]:
        """分析月令用神 - 基于《子平真诠》理论"""
        # 月令用神分析
        month_ten_god = get_ten_god(day_master, month_gan)
        
        # 分析月令藏干
        month_canggan = DIZHI_CANGGAN_WEIGHTS.get(month_branch, [])
        
        # 分析月令透出情况
        month_touchu = cls._analyze_month_touchu(month_gan, month_canggan, pillars)
        
        # 分析月令旺衰
        month_wangshuai = cls._analyze_month_wangshuai(day_master, month_branch)
        
        return {
            'month_gan': month_gan,
            'month_ten_god': month_ten_god,
            'month_canggan': month_canggan,
            'month_touchu': month_touchu,
            'month_wangshuai': month_wangshuai,
            'yongshen_quality': cls._evaluate_yongshen_quality(month_ten_god, month_touchu, month_wangshuai),
        }
    
    @classmethod
    def _analyze_month_touchu(cls, month_gan: str, month_canggan: List[Tuple[str, float]], pillars: Dict[str, Tuple[str, str]]) -> Dict[str, Any]:
        """分析月令透出情况"""
        # 检查月干是否透出
        gan_touchu = month_gan in [pillars[p][0] for p in pillars.keys()]
        
        # 检查月令藏干是否透出
        canggan_touchu = []
        for gan, weight in month_canggan:
            if gan in [pillars[p][0] for p in pillars.keys()]:
                canggan_touchu.append((gan, weight))
        
        return {
            'gan_touchu': gan_touchu,
            'canggan_touchu': canggan_touchu,
            'touchu_count': len(canggan_touchu),
            'touchu_quality': cls._evaluate_touchu_quality(gan_touchu, canggan_touchu),
        }
    
    @classmethod
    def _analyze_month_wangshuai(cls, day_master: str, month_branch: str) -> str:
        """分析月令旺衰"""
        day_master_wuxing = TIANGAN_WUXING.get(day_master, '')
        month_branch_wuxing = DIZHI_WUXING.get(month_branch, '')
        
        if day_master_wuxing == month_branch_wuxing:
            return '旺'
        elif month_branch_wuxing in ['木', '火', '土', '金', '水']:
            # 根据五行生克关系判断
            if month_branch_wuxing in ['木', '火'] and day_master_wuxing in ['木', '火']:
                return '旺'
            elif month_branch_wuxing in ['金', '水'] and day_master_wuxing in ['金', '水']:
                return '旺'
            else:
                return '衰'
        else:
            return '平'
    
    @classmethod
    def _evaluate_yongshen_quality(cls, month_ten_god: str, month_touchu: Dict[str, Any], month_wangshuai: str) -> str:
        """评估用神质量"""
        if month_touchu.get('gan_touchu') and month_wangshuai == '旺':
            return '上等'
        elif month_touchu.get('gan_touchu') or month_wangshuai == '旺':
            return '中等'
        else:
            return '下等'
    
    @classmethod
    def _evaluate_touchu_quality(cls, gan_touchu: bool, canggan_touchu: List[Tuple[str, float]]) -> str:
        """评估透出质量"""
        if gan_touchu and len(canggan_touchu) > 0:
            return '上等'
        elif gan_touchu or len(canggan_touchu) > 0:
            return '中等'
        else:
            return '下等'
    
    @classmethod
    def _determine_yongshen_type(cls, month_yongshen: Dict[str, Any], pillars: Dict[str, Tuple[str, str]]) -> str:
        """确定用神类型"""
        month_ten_god = month_yongshen.get('month_ten_god', '')
        month_touchu = month_yongshen.get('month_touchu', {})
        
        if month_touchu.get('gan_touchu'):
            return '正用神'
        elif month_touchu.get('canggan_touchu'):
            return '假用神'
        else:
            return '用神缺失'
    
    @classmethod
    def _analyze_yongshen_strength(cls, month_yongshen: Dict[str, Any], pillars: Dict[str, Tuple[str, str]]) -> Dict[str, Any]:
        """分析用神强弱"""
        month_wangshuai = month_yongshen.get('month_wangshuai', '平')
        yongshen_quality = month_yongshen.get('yongshen_quality', '下等')
        
        # ✅ 修复：直接判断强度等级，不计算评分
        if month_wangshuai == '旺' and yongshen_quality == '上等':
            strength_level = '强'
        elif month_wangshuai == '旺' or yongshen_quality == '上等':
            strength_level = '中'
        elif yongshen_quality == '中等':
            strength_level = '中'
        else:
            strength_level = '弱'

        return {
            'strength_level': strength_level,
            'month_wangshuai': month_wangshuai,
            'yongshen_quality': yongshen_quality,
        }
    
    @classmethod
    def _analyze_yongshen_xiji(cls, day_master: str, month_yongshen: Dict[str, Any], pillars: Dict[str, Tuple[str, str]]) -> Dict[str, Any]:
        """分析用神喜忌"""
        month_ten_god = month_yongshen.get('month_ten_god', '')
        
        # 获取用神喜忌
        xiji_info = cls.YONGSHEN_XIJI.get(month_ten_god, {'xi': [], 'ji': []})
        
        # 分析四柱中的喜忌神
        xishen_count = 0
        jishen_count = 0
        
        for pillar, (gan, zhi) in pillars.items():
            ten_god = get_ten_god(day_master, gan)
            if ten_god in xiji_info['xi']:
                xishen_count += 1
            elif ten_god in xiji_info['ji']:
                jishen_count += 1
        
        return {
            'xishen': xiji_info['xi'],
            'jishen': xiji_info['ji'],
            'xishen_count': xishen_count,
            'jishen_count': jishen_count,
            'xiji_balance': cls._calculate_xiji_balance(xishen_count, jishen_count),
        }
    
    @classmethod
    def _calculate_xiji_balance(cls, xishen_count: int, jishen_count: int) -> str:
        """计算喜忌平衡"""
        if xishen_count > jishen_count:
            return '喜神多'
        elif jishen_count > xishen_count:
            return '忌神多'
        else:
            return '平衡'
    
    @classmethod
    def _analyze_yongshen_liutong(cls, day_master: str, month_yongshen: Dict[str, Any], pillars: Dict[str, Tuple[str, str]]) -> Dict[str, Any]:
        """
        分析用神流通
        🔥 修复：正确匹配十神名称，不使用类别缩写
        """
        # 简化版用神流通分析
        month_ten_god = month_yongshen.get('month_ten_god', '')
        
        # ✅ 修复：直接判断流通等级，不计算评分
        # 检查用神是否被克破（使用具体十神名称）
        ke_po_shishen = ['食神', '伤官', '正财', '偏财']
        ke_po_count = 0
        for pillar, (gan, zhi) in pillars.items():
            ten_god = get_ten_god(day_master, gan)
            if ten_god in ke_po_shishen:
                ke_po_count += 1

        # 直接判断流通等级
        if ke_po_count == 0:
            liutong_level = '流通'
        elif ke_po_count <= 2:
            liutong_level = '一般'
        else:
            liutong_level = '阻塞'

        return {
            'liutong_level': liutong_level,
            'ke_po_count': ke_po_count,
        }

    @classmethod
    def _get_yongshen_description(cls, yongshen_type: str, yongshen_strength: Dict[str, Any]) -> str:
        """
        获取用神描述
        ✅ 修复：不再依赖评分，只使用强度等级
        """
        base_desc = cls.YONGSHEN_TYPES.get(yongshen_type, {}).get('description', '特殊用神')

        # 使用strength_level判断
        strength_level = yongshen_strength.get('strength_level', '中')

        if strength_level == '强':
            strength_desc = "，用神强旺"
        elif strength_level == '中':
            strength_desc = "，用神中等"
        else:  # '弱'
            strength_desc = "，用神偏弱"

        return base_desc + strength_desc
    
    @classmethod
    def _get_yongshen_advice(cls, yongshen_type: str, yongshen_strength: Dict[str, Any], yongshen_xiji: Dict[str, Any]) -> str:
        """获取用神建议"""
        if yongshen_type == '正用神':
            return '用神得力，宜顺势而为，可考虑扩张发展'
        elif yongshen_type == '假用神':
            return '用神不真，宜谨慎行事，注重积累与提升'
        elif yongshen_type == '用神缺失':
            return '用神缺失，宜保守稳健，寻找补救方法'
        else:
            return '用神特殊，宜具体情况具体分析'

    # ✅ 修复3：添加忌神分析方法
    # 十神类别映射表
    SHISHEN_CATEGORY_MAP = {
        '印星': ['正印', '偏印'],
        '比劫': ['比肩', '劫财'],
        '食伤': ['食神', '伤官'],
        '财星': ['正财', '偏财'],
        '官杀': ['正官', '偏官'],
    }

    @classmethod
    def _analyze_jishen(cls, day_master: str, month_yongshen: Dict[str, Any], pillars: Dict[str, Tuple[str, str]]) -> List[str]:
        """
        分析忌神 - 基于《子平真诠》理论
        忌神：对用神不利的五行或十神
        🔥 修复：使用类别映射而不是子串匹配
        """
        jishen_list = []

        # 获取月令用神的十神类型
        month_ten_god = month_yongshen.get('month_ten_god', '')

        # 根据用神类型确定忌神
        if month_ten_god in cls.YONGSHEN_XIJI:
            ji_categories = cls.YONGSHEN_XIJI[month_ten_god].get('ji', [])

            # 检查四柱中是否有忌神
            all_gans = [pillars['year'][0], pillars['month'][0], pillars['hour'][0]]
            for gan in all_gans:
                ten_god = get_ten_god(day_master, gan)
                
                # 检查该十神是否属于忌神类别
                for ji_category in ji_categories:
                    if ji_category in cls.SHISHEN_CATEGORY_MAP:
                        # 使用类别映射判断
                        if ten_god in cls.SHISHEN_CATEGORY_MAP[ji_category]:
                            wuxing = TIANGAN_WUXING.get(gan, '')
                            if wuxing and wuxing not in jishen_list:
                                jishen_list.append(wuxing)
                                break

        return jishen_list if jishen_list else ['无明显忌神']
