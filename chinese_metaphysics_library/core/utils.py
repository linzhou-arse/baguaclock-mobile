#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具函数 - Utility Functions
===========================

提供中国命理学知识库的通用工具函数
"""

from __future__ import annotations
import time
import json
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

from .data_structures import BaziData, AnalysisResult, AnalysisConfig
from .constants import TIANGAN_LIST, DIZHI_LIST, WUXING_LIST


def validate_bazi_data(bazi_data: BaziData) -> bool:
    """
    验证八字数据有效性
    
    Args:
        bazi_data: 八字数据
        
    Returns:
        bool: 验证是否通过
        
    Raises:
        ValidationError: 数据验证失败
    """
    try:
        # 验证天干地支
        for pillar_name, pillar_data in [('年', bazi_data.year), ('月', bazi_data.month), 
                                       ('日', bazi_data.day), ('时', bazi_data.hour)]:
            if len(pillar_data) != 2:
                raise ValidationError(f"{pillar_name}柱数据格式错误")
            
            gan, zhi = pillar_data
            if gan not in TIANGAN_LIST:
                raise ValidationError(f"{pillar_name}柱天干无效: {gan}")
            if zhi not in DIZHI_LIST:
                raise ValidationError(f"{pillar_name}柱地支无效: {zhi}")
        
        # 验证性别
        if bazi_data.gender not in ['男', '女']:
            raise ValidationError(f"性别无效: {bazi_data.gender}")
        
        return True
        
    except Exception as e:
        raise ValidationError(f"八字数据验证失败: {e}")


def format_analysis_result(result: AnalysisResult, config: Optional[AnalysisConfig] = None) -> Any:
    """
    格式化分析结果
    
    Args:
        result: 分析结果
        config: 输出配置
        
    Returns:
        格式化后的结果
    """
    config = config or AnalysisConfig()
    
    if config.output_format == 'dict':
        return result.to_dict()
    elif config.output_format == 'json':
        return result.to_json()
    elif config.output_format == 'summary':
        return result.get_summary()
    else:
        return result


def calculate_performance_metrics(results: List[AnalysisResult]) -> Dict[str, Any]:
    """
    计算性能指标
    
    Args:
        results: 分析结果列表
        
    Returns:
        性能指标字典
    """
    if not results:
        return {}
    
    total_time = sum(r.analysis_time for r in results)
    avg_time = total_time / len(results)
    max_time = max(r.analysis_time for r in results)
    min_time = min(r.analysis_time for r in results)
    
    cache_hits = sum(1 for r in results if r.cache_hit)
    cache_hit_rate = cache_hits / len(results)
    
    return {
        'total_analyses': len(results),
        'total_time_ms': total_time,
        'average_time_ms': avg_time,
        'max_time_ms': max_time,
        'min_time_ms': min_time,
        'cache_hits': cache_hits,
        'cache_hit_rate': cache_hit_rate
    }


def optimize_analysis_cache(analyzer, max_size: int = 1000, ttl: int = 3600):
    """
    优化分析缓存
    
    Args:
        analyzer: 分析器实例
        max_size: 最大缓存大小
        ttl: 缓存生存时间（秒）
    """
    if not analyzer.cache:
        return
    
    # 简单的LRU缓存清理
    if len(analyzer.cache) > max_size:
        # 按时间戳排序，删除最旧的条目
        sorted_items = sorted(
            analyzer.cache.items(),
            key=lambda x: x[1].timestamp
        )
        
        # 删除最旧的50%条目
        items_to_remove = len(sorted_items) // 2
        for key, _ in sorted_items[:items_to_remove]:
            del analyzer.cache[key]


def get_wuxing_by_tiangan(tiangan: str) -> str:
    """
    根据天干获取五行
    
    Args:
        tiangan: 天干
        
    Returns:
        五行
    """
    from .constants import TIANGAN_WUXING
    return TIANGAN_WUXING.get(tiangan, '')


def get_wuxing_by_dizhi(dizhi: str) -> str:
    """
    根据地支获取五行
    
    Args:
        dizhi: 地支
        
    Returns:
        五行
    """
    from .constants import DIZHI_WUXING
    return DIZHI_WUXING.get(dizhi, '')


def get_ten_god(day_master: str, other_gan: str) -> str:
    """
    计算十神

    根据《渊海子平》理论：
    1. 同五行 = 比肩/劫财（阴阳相同为比肩，不同为劫财）
    2. 我克的 = 正财/偏财（阴阳不同为正财，相同为偏财）
    3. 克我的 = 正官/七杀（阴阳相同为正官，不同为七杀）
    4. 生我的 = 正印/偏印（阴阳不同为正印，相同为偏印）
    5. 我生的 = 食神/伤官（阴阳相同为食神，不同为伤官）

    Args:
        day_master: 日主天干
        other_gan: 其他天干

    Returns:
        十神名称
    """
    from .constants import TIANGAN_WUXING, TIANGAN_YINYANG, WUXING_SHENG_MAP, WUXING_KE_MAP

    # 获取五行和阴阳
    day_wuxing = TIANGAN_WUXING.get(day_master, '')
    other_wuxing = TIANGAN_WUXING.get(other_gan, '')
    day_yinyang = TIANGAN_YINYANG.get(day_master, 0)
    other_yinyang = TIANGAN_YINYANG.get(other_gan, 0)

    # 判断阴阳是否相同
    same_yinyang = (day_yinyang == other_yinyang)

    # 1. 同五行
    if day_wuxing == other_wuxing:
        return '比肩' if same_yinyang else '劫财'

    # 2. 我克的（我克者为财）
    if WUXING_KE_MAP.get(day_wuxing) == other_wuxing:
        return '正财' if not same_yinyang else '偏财'

    # 3. 克我的（克我者为官杀）
    # 正官：克我者，与我阴阳不同（异性相克）
    # 七杀：克我者，与我阴阳相同（同性相克）
    if WUXING_KE_MAP.get(other_wuxing) == day_wuxing:
        return '正官' if not same_yinyang else '七杀'

    # 4. 生我的（生我者为印）
    if WUXING_SHENG_MAP.get(other_wuxing) == day_wuxing:
        return '正印' if not same_yinyang else '偏印'

    # 5. 我生的（我生者为食伤）
    if WUXING_SHENG_MAP.get(day_wuxing) == other_wuxing:
        return '食神' if same_yinyang else '伤官'

    return '未知'


def get_wealth_tomb_zhi(day_master: str) -> Optional[str]:
    """
    通用财库计算函数 - 基于《渊海子平·论财库》
    
    理论依据：
    - 财库 = 财星的墓库（十二长生的墓位），不是日主的墓库
    - 财星 = 日主五行所克之五行（我克者为财）
    
    计算公式：
    1. 根据日主五行，使用五行相克关系确定财星五行
    2. 根据财星五行，使用十二长生墓位确定财库地支
    
    十二长生墓位：
    - 木的墓库：未
    - 火的墓库：戌
    - 金的墓库：丑
    - 水的墓库：辰
    - 土的墓库：戌（土寄于火）
    
    Args:
        day_master: 日主天干
        
    Returns:
        财库地支，如果无法确定则返回None
        
    Examples:
        >>> get_wealth_tomb_zhi('辛')  # 辛金 → 财是木 → 木的墓库是未
        '未'
        >>> get_wealth_tomb_zhi('甲')  # 甲木 → 财是土 → 土的墓库是戌
        '戌'
    """
    from .constants import WUXING_KE_MAP
    
    # 1. 获取日主五行（使用已有的工具函数）
    day_master_wx = get_wuxing_by_tiangan(day_master)
    if not day_master_wx:
        return None
    
    # 2. 根据五行相克关系，确定财星五行（我克者为财）
    wealth_star_wx = WUXING_KE_MAP.get(day_master_wx)
    if not wealth_star_wx:
        return None
    
    # 3. 根据财星五行，确定财星的墓库地支（十二长生墓位）
    # 十二长生墓位映射
    tomb_zhi_map = {
        '木': '未',  # 木的墓库：未
        '火': '戌',  # 火的墓库：戌
        '金': '丑',  # 金的墓库：丑
        '水': '辰',  # 水的墓库：辰
        '土': '戌'   # 土的墓库：戌（土寄于火）
    }
    
    return tomb_zhi_map.get(wealth_star_wx)


def get_season_by_month_branch(month_branch: str) -> str:
    """
    根据月支获取季节
    
    Args:
        month_branch: 月支
        
    Returns:
        季节
    """
    from .constants import SEASON_MONTHS
    
    for season, months in SEASON_MONTHS.items():
        if month_branch in months:
            return season
    
    return '未知'


def clamp_score(score: float, min_score: float = 0.0, max_score: float = 100.0) -> float:
    """
    限制评分范围
    
    Args:
        score: 原始评分
        min_score: 最小评分
        max_score: 最大评分
        
    Returns:
        限制后的评分
    """
    return max(min_score, min(max_score, score))


def create_analysis_result(
    analyzer_name: str,
    book_name: str,
    analysis_type: str,
    level: str = "",
    score: float = 0.0,
    description: str = "",
    details: Optional[Dict[str, Any]] = None,
    advice: str = "",
    explanation: str = "",
    analysis_time: float = 0.0,
    cache_hit: bool = False,
    metadata: Optional[Dict[str, Any]] = None
) -> AnalysisResult:
    """
    创建分析结果
    
    Args:
        analyzer_name: 分析器名称
        book_name: 经典著作名称
        analysis_type: 分析类型
        level: 等级
        score: 评分
        description: 描述
        details: 详细信息
        advice: 建议
        explanation: 解释
        analysis_time: 分析时间
        cache_hit: 是否命中缓存
        metadata: 元数据
        
    Returns:
        分析结果
    """
    return AnalysisResult(
        analyzer_name=analyzer_name,
        book_name=book_name,
        analysis_type=analysis_type,
        level=level,
        score=score,
        description=description,
        details=details or {},
        advice=advice,
        explanation=explanation,
        analysis_time=analysis_time,
        cache_hit=cache_hit,
        metadata=metadata or {}
    )
