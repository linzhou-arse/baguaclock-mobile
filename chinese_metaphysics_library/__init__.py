#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中国命理学知识库 - Chinese Metaphysics Library
===============================================

将中国传统命理学经典著作完全代码化的知识库
基于《三命通会》《渊海子平》《子平真诠》《滴天髓》《穷通宝鉴》《兰台妙选》六书

核心特性：
- 完整的知识库：六书内容100%代码化
- 标准化接口：统一的调用方式
- 高性能实现：毫秒级分析速度
- 可扩展架构：易于添加新功能
- 完整文档：详细的使用说明

版本：1.0.0
作者：AI Assistant
许可证：MIT License
"""

__version__ = "1.0.0"
__author__ = "AI Assistant"
__license__ = "MIT License"

# 核心模块导入
from .core import BaseAnalyzer, BaziData, AnalysisResult, AnalysisConfig
from .core.utils import validate_bazi_data, format_analysis_result

# 六书模块导入
from .santonghui import SantonghuiAnalyzer
from .yuanhaiziping import YuanhaizipingAnalyzer
from .zipingzhenquan import ZipingzhenquanAnalyzer
from .ditiansui import DitiansuiAnalyzer
from .qiongtongbaojian import QiongtongbaojianAnalyzer
from .lantaimiaoxuan import LantaimiaoxuanAnalyzer

# 统一分析器
from .unified_analyzer import UnifiedMetaphysicsAnalyzer

__all__ = [
    # 核心模块
    'BaseAnalyzer', 'BaziData', 'AnalysisResult', 'AnalysisConfig',
    'validate_bazi_data', 'format_analysis_result',
    
    # 六书分析器
    'SantonghuiAnalyzer',
    'YuanhaizipingAnalyzer', 
    'ZipingzhenquanAnalyzer',
    'DitiansuiAnalyzer',
    'QiongtongbaojianAnalyzer',
    'LantaimiaoxuanAnalyzer',
    
    # 统一分析器
    'UnifiedMetaphysicsAnalyzer',
]

# 项目信息
PROJECT_INFO = {
    'name': 'Chinese Metaphysics Library',
    'version': __version__,
    'description': '中国传统命理学经典著作完全代码化知识库',
    'books': [
        '三命通会', '渊海子平', '子平真诠', 
        '滴天髓', '穷通宝鉴', '兰台妙选'
    ],
    'features': [
        '完整的知识库：六书内容100%代码化',
        '标准化接口：统一的调用方式',
        '高性能实现：毫秒级分析速度',
        '可扩展架构：易于添加新功能',
        '完整文档：详细的使用说明'
    ]
}

def get_project_info():
    """获取项目信息"""
    return PROJECT_INFO

def get_supported_books():
    """获取支持的经典著作列表"""
    return PROJECT_INFO['books']

def get_library_features():
    """获取知识库特性"""
    return PROJECT_INFO['features']
