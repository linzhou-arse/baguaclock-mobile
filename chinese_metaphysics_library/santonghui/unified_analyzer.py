#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《三命通会》统一分析器 - Santonghui Unified Analyzer
=================================================

整合《三命通会》所有分析功能的统一分析器
"""

from __future__ import annotations
from typing import Dict, List, Any
import time

from ..core.base_analyzer import BaseAnalyzer
from ..core.data_structures import BaziData, AnalysisResult, AnalysisConfig
from ..core.utils import create_analysis_result
from .shensha_analyzer import ShenshaAnalyzer
from .geju_analyzer import GejuAnalyzer
from .dayun_analyzer import DayunAnalyzer
from .liunian_analyzer import LiunianAnalyzer


class SantonghuiAnalyzer(BaseAnalyzer):
    """《三命通会》统一分析器"""
    
    def __init__(self, config: AnalysisConfig = None):
        super().__init__("三命通会统一分析器", "三命通会", config)
        
        # 初始化子分析器
        self.shensha_analyzer = ShenshaAnalyzer(config)
        self.geju_analyzer = GejuAnalyzer(config)
        self.dayun_analyzer = DayunAnalyzer(config)
        self.liunian_analyzer = LiunianAnalyzer(config)
    
    def analyze(self, bazi_data: BaziData) -> AnalysisResult:
        """
        执行综合分析 - 基于《三命通会》理论
        ✅ 修复：移除打分系统，改为吉凶判断
        """
        start_time = time.time()

        try:
            # 执行各项分析
            shensha_result = self.shensha_analyzer.analyze(bazi_data)
            geju_result = self.geju_analyzer.analyze(bazi_data)
            dayun_result = self.dayun_analyzer.analyze(bazi_data)
            liunian_result = self.liunian_analyzer.analyze(bazi_data)

            # ✅ 综合判断吉凶（不打分，不平均）
            # 1. 格局成败最重要
            geju_level = geju_result.level if hasattr(geju_result, 'level') else '未知'

            # 2. 大运喜忌次重要
            dayun_level = dayun_result.level if hasattr(dayun_result, 'level') else '未知'

            # 3. 神煞吉凶
            shensha_level = shensha_result.level if hasattr(shensha_result, 'level') else '未知'

            # 综合判断
            if '大成' in geju_level and '大吉' in dayun_level:
                level = "大吉"
                description = "格局大成，大运得地，神煞吉多，命格极佳。"
            elif '成立' in geju_level and ('吉' in dayun_level or '喜' in dayun_level):
                level = "吉"
                description = "格局成立，大运得力，命局平衡。"
            elif '勉强' in geju_level or '平' in dayun_level:
                level = "中平"
                description = "格局勉强或大运平平，需稳步前行。"
            elif '破败' in geju_level or '凶' in dayun_level:
                level = "凶"
                description = "格局破败或大运不佳，需防波折。"
            else:
                level = "中平"
                description = "命局平平，需稳步前行。"

            analysis_time = (time.time() - start_time) * 1000

            return create_analysis_result(
                analyzer_name=self.name,
                book_name=self.book_name,
                analysis_type="综合分析",
                level=level,
                score=0,  # 不打分
                description=f"《三命通会》综合分析：{description}",
                details={
                    'shensha': shensha_result.to_dict(),
                    'geju': geju_result.to_dict(),
                    'dayun': dayun_result.to_dict(),
                    'liunian': liunian_result.to_dict()
                },
                advice="基于《三命通会》的综合建议：格局成败为本，大运流年为用。",
                explanation="整合神煞、格局、大运、流年四大分析维度，不打分，只论吉凶。",
                analysis_time=analysis_time
            )
            
        except Exception as e:
            raise Exception(f"《三命通会》分析失败: {e}")
    
    def analyze_shensha(self, bazi_data: BaziData) -> AnalysisResult:
        """神煞分析"""
        return self.shensha_analyzer.analyze_with_performance(bazi_data)
    
    def analyze_geju(self, bazi_data: BaziData) -> AnalysisResult:
        """格局分析"""
        return self.geju_analyzer.analyze_with_performance(bazi_data)
    
    def analyze_dayun(self, bazi_data: BaziData) -> AnalysisResult:
        """大运分析"""
        return self.dayun_analyzer.analyze_with_performance(bazi_data)
    
    def analyze_liunian(self, bazi_data: BaziData) -> AnalysisResult:
        """流年分析"""
        return self.liunian_analyzer.analyze_with_performance(bazi_data)
