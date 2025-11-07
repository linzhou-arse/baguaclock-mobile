#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《三命通会》模块 - San Ming Tong Hui Module
==========================================

基于《三命通会》经典著作的命理分析模块
包含神煞分析、格局判断、大运流年等核心功能

主要功能：
- 神煞分析：天德贵人、月德贵人、天乙贵人等
- 格局判断：正官格、七杀格、财格等
- 大运分析：起运年龄、大运排列、吉凶判断
- 流年分析：流年吉凶、冲克关系、运势变化
"""

from .shensha_analyzer import ShenshaAnalyzer
from .geju_analyzer import GejuAnalyzer
from .dayun_analyzer import DayunAnalyzer
from .liunian_analyzer import LiunianAnalyzer
from .unified_analyzer import SantonghuiAnalyzer

__all__ = [
    'ShenshaAnalyzer',
    'GejuAnalyzer', 
    'DayunAnalyzer',
    'LiunianAnalyzer',
    'SantonghuiAnalyzer'
]

# 模块信息
MODULE_INFO = {
    'name': '三命通会',
    'author': '万民英',
    'dynasty': '明',
    'description': '明代万民英所著命理学经典，集历代命理精华',
    'features': [
        '神煞分析：天德、月德、天乙等吉神凶煞',
        '格局判断：正格、变格、外格分类',
        '大运分析：起运年龄、顺逆推运',
        '流年分析：流年吉凶、冲克关系'
    ]
}
