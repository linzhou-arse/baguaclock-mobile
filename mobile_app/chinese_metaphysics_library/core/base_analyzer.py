#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础分析器 - Base Analyzer
========================

提供所有命理分析器的基类，实现通用功能：
- 性能监控
- 缓存管理
- 错误处理
- 结果格式化
"""

from __future__ import annotations
import time
import hashlib
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from functools import wraps
import logging

from .data_structures import BaziData, AnalysisResult, AnalysisConfig
from .utils import validate_bazi_data, format_analysis_result


class BaseAnalyzer(ABC):
    """基础分析器抽象类"""
    
    def __init__(self, name: str, book_name: str, config: Optional[AnalysisConfig] = None):
        """
        初始化分析器
        
        Args:
            name: 分析器名称
            book_name: 经典著作名称
            config: 分析配置
        """
        self.name = name
        self.book_name = book_name
        self.config = config or AnalysisConfig()
        self.cache = {} if self.config.enable_cache else None
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        
        # 性能统计
        self.analysis_count = 0
        self.total_time = 0.0
        self.cache_hits = 0
    
    @abstractmethod
    def analyze(self, bazi_data: BaziData) -> AnalysisResult:
        """
        执行分析（子类必须实现）
        
        Args:
            bazi_data: 八字数据
            
        Returns:
            AnalysisResult: 分析结果
        """
        pass
    
    def analyze_with_performance(self, bazi_data: BaziData) -> AnalysisResult:
        """
        带性能监控的分析
        
        Args:
            bazi_data: 八字数据
            
        Returns:
            AnalysisResult: 分析结果
        """
        # 验证输入数据
        validate_bazi_data(bazi_data)
        
        # 检查缓存
        cache_key = self._get_cache_key(bazi_data)
        if self.cache and cache_key in self.cache:
            self.cache_hits += 1
            cached_result = self.cache[cache_key]
            cached_result.cache_hit = True
            return cached_result
        
        # 执行分析
        start_time = time.time()
        try:
            result = self.analyze(bazi_data)
            
            # 计算分析时间
            analysis_time = (time.time() - start_time) * 1000  # 转换为毫秒
            
            # 更新性能统计
            self.analysis_count += 1
            self.total_time += analysis_time
            result.analysis_time = analysis_time
            
            # 缓存结果
            if self.cache:
                self.cache[cache_key] = result
                # 简单的TTL管理（实际项目中应使用更复杂的缓存策略）
                if len(self.cache) > 1000:  # 限制缓存大小
                    self.cache.clear()
            
            return result
            
        except Exception as e:
            self.logger.error(f"分析失败: {e}")
            raise
    
    def _get_cache_key(self, bazi_data: BaziData) -> str:
        """生成缓存键"""
        data_str = json.dumps(bazi_data.to_dict(), sort_keys=True)
        return hashlib.md5(f"{self.name}_{data_str}".encode()).hexdigest()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        avg_time = self.total_time / self.analysis_count if self.analysis_count > 0 else 0
        cache_hit_rate = self.cache_hits / self.analysis_count if self.analysis_count > 0 else 0
        
        return {
            'analyzer_name': self.name,
            'book_name': self.book_name,
            'analysis_count': self.analysis_count,
            'total_time_ms': self.total_time,
            'average_time_ms': avg_time,
            'cache_hits': self.cache_hits,
            'cache_hit_rate': cache_hit_rate
        }
    
    def clear_cache(self):
        """清空缓存"""
        if self.cache:
            self.cache.clear()
    
    def reset_stats(self):
        """重置统计信息"""
        self.analysis_count = 0
        self.total_time = 0.0
        self.cache_hits = 0


def performance_monitor(func):
    """性能监控装饰器"""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        result = func(self, *args, **kwargs)
        execution_time = (time.time() - start_time) * 1000
        
        if hasattr(self, 'logger'):
            self.logger.debug(f"{func.__name__} 执行时间: {execution_time:.2f}ms")
        
        return result
    return wrapper


class AnalysisError(Exception):
    """分析错误异常"""
    pass


class ValidationError(AnalysisError):
    """数据验证错误"""
    pass


class PerformanceError(AnalysisError):
    """性能错误"""
    pass
