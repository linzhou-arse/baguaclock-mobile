#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心基础模块 - Core Foundation Module
====================================

提供中国命理学知识库的核心基础功能：
- 基础数据结构定义
- 通用分析器基类
- 工具函数和验证器
- 性能优化组件
"""

from .base_analyzer import BaseAnalyzer
from .data_structures import BaziData, AnalysisResult, AnalysisConfig
from .utils import (
    validate_bazi_data, 
    format_analysis_result,
    calculate_performance_metrics,
    optimize_analysis_cache
)
from .constants import (
    TIANGAN_LIST, DIZHI_LIST, WUXING_LIST,
    SHISEN_LIST, SHENGSHA_LIST, GEJU_LIST
)

__all__ = [
    'BaseAnalyzer',
    'BaziData', 
    'AnalysisResult',
    'AnalysisConfig',
    'validate_bazi_data',
    'format_analysis_result', 
    'calculate_performance_metrics',
    'optimize_analysis_cache',
    'TIANGAN_LIST',
    'DIZHI_LIST', 
    'WUXING_LIST',
    'SHISEN_LIST',
    'SHENGSHA_LIST',
    'GEJU_LIST'
]
