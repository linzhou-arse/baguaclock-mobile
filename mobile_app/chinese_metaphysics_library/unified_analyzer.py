#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一命理分析器 - Unified Metaphysics Analyzer
==========================================

整合六书分析功能的统一分析器
"""

from __future__ import annotations
from typing import Dict, List, Any
import time

from .core.base_analyzer import BaseAnalyzer
from .core.data_structures import BaziData, AnalysisResult, AnalysisConfig
from .core.utils import create_analysis_result
from .santonghui import SantonghuiAnalyzer
from .yuanhaiziping import YuanhaizipingAnalyzer
from .zipingzhenquan import ZipingzhenquanAnalyzer
from .ditiansui import DitiansuiAnalyzer
from .qiongtongbaojian import QiongtongbaojianAnalyzer
from .lantaimiaoxuan import LantaimiaoxuanAnalyzer


class UnifiedMetaphysicsAnalyzer(BaseAnalyzer):
    """统一命理分析器 - 整合六书分析功能"""
    
    def __init__(self, config: AnalysisConfig = None):
        super().__init__("统一命理分析器", "六书综合", config)
        
        # 初始化六书分析器
        self.analyzers = {
            '三命通会': SantonghuiAnalyzer(config),
            '渊海子平': YuanhaizipingAnalyzer(config),
            '子平真诠': ZipingzhenquanAnalyzer(config),
            '滴天髓': DitiansuiAnalyzer(config),
            '穷通宝鉴': QiongtongbaojianAnalyzer(config),
            '兰台妙选': LantaimiaoxuanAnalyzer(config)
        }
    
    def analyze(self, bazi_data: BaziData) -> AnalysisResult:
        """
        执行六书综合分析
        
        🔥 优化：增强错误处理，确保每本书都能正确分析或记录错误
        """
        start_time = time.time()
        
        try:
            # 执行所有分析器
            results = {}
            successful_count = 0
            errors = []
            level_counts = {'大吉': 0, '吉': 0, '中平': 0, '凶': 0, '大凶': 0}

            for book_name, analyzer in self.analyzers.items():
                try:
                    result = analyzer.analyze_with_performance(bazi_data)
                    results[book_name] = result
                    successful_count += 1

                    # ✅ 统计吉凶等级（不打分）
                    result_level = result.level if hasattr(result, 'level') else '中平'
                    if result_level in level_counts:
                        level_counts[result_level] += 1

                    print(f"✅ 《{book_name}》分析成功：{result_level}")
                except Exception as e:
                    error_msg = f"《{book_name}》分析失败: {str(e)}"
                    print(f"❌ {error_msg}")
                    errors.append(error_msg)
                    # 创建一个默认结果以保持结构完整
                    from .core.utils import create_analysis_result
                    results[book_name] = create_analysis_result(
                        analyzer_name=analyzer.name,
                        book_name=book_name,
                        analysis_type="分析失败",
                        level="未知",
                        score=0,  # 不打分
                        description=f"《{book_name}》分析遇到错误",
                        details={'error': str(e)},
                        advice="",
                        explanation=error_msg
                    )

            # ✅ 综合判断吉凶（不打分，不平均）
            # 以多数派为准
            if level_counts['大吉'] >= 2:
                level = "大吉"
            elif level_counts['吉'] + level_counts['大吉'] >= 3:
                level = "吉"
            elif level_counts['凶'] + level_counts['大凶'] >= 3:
                level = "凶"
            elif level_counts['大凶'] >= 2:
                level = "大凶"
            else:
                level = "中平"
            
            analysis_time = (time.time() - start_time) * 1000

            # 构建说明信息
            explanation = f"整合《三命通会》《渊海子平》《子平真诠》《滴天髓》《穷通宝鉴》《兰台妙选》六大经典，不打分，只论吉凶。"
            if errors:
                explanation += f"\n注意：{len(errors)}本书分析遇到错误"

            # 构建详细说明
            level_summary = f"大吉{level_counts['大吉']}项，吉{level_counts['吉']}项，中平{level_counts['中平']}项，凶{level_counts['凶']}项，大凶{level_counts['大凶']}项"

            print(f"📊 六书综合分析完成：{successful_count}/{len(self.analyzers)} 成功，综合等级：{level}（{level_summary}）")

            return create_analysis_result(
                analyzer_name=self.name,
                book_name=self.book_name,
                analysis_type="六书综合分析",
                level=level,
                score=0,  # 不打分
                description=f"六书综合分析：{level}（{level_summary}）",
                details=results,
                advice="基于六书经典的综合建议：格局成败为本，大运流年为用。" if successful_count > 0 else "部分分析失败，建议检查日志",
                explanation=explanation,
                analysis_time=analysis_time
            )
            
        except Exception as e:
            error_msg = f"六书综合分析失败: {e}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
    
    def analyze_by_book(self, bazi_data: BaziData, book_name: str) -> AnalysisResult:
        """按指定经典分析"""
        if book_name not in self.analyzers:
            raise ValueError(f"不支持的经典著作: {book_name}")
        
        return self.analyzers[book_name].analyze_with_performance(bazi_data)
    
    def get_supported_books(self) -> List[str]:
        """获取支持的经典著作列表"""
        return list(self.analyzers.keys())
    
    def get_analyzer_stats(self) -> Dict[str, Any]:
        """获取所有分析器统计信息"""
        stats = {}
        for book_name, analyzer in self.analyzers.items():
            stats[book_name] = analyzer.get_performance_stats()
        return stats
