#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据结构定义 - Data Structures
=============================

定义中国命理学知识库的核心数据结构
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class BaziData:
    """八字数据结构"""
    year: Tuple[str, str]  # (天干, 地支)
    month: Tuple[str, str]  # (天干, 地支)
    day: Tuple[str, str]   # (天干, 地支)
    hour: Tuple[str, str]  # (天干, 地支)
    
    # 基本信息
    birth_year: int
    birth_month: int
    birth_day: int
    birth_hour: int
    gender: str  # '男' or '女'
    name: Optional[str] = None
    
    # 扩展信息
    lunar_calendar: bool = False
    timezone: str = 'Asia/Shanghai'
    location: Optional[str] = None
    
    def __post_init__(self):
        """数据验证"""
        self._validate_data()
    
    def _validate_data(self):
        """验证八字数据有效性"""
        # 验证天干地支
        valid_tiangan = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        valid_dizhi = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        
        for pillar_name, pillar_data in [('年', self.year), ('月', self.month), 
                                       ('日', self.day), ('时', self.hour)]:
            if len(pillar_data) != 2:
                raise ValueError(f"{pillar_name}柱数据格式错误")
            
            gan, zhi = pillar_data
            if gan not in valid_tiangan:
                raise ValueError(f"{pillar_name}柱天干无效: {gan}")
            if zhi not in valid_dizhi:
                raise ValueError(f"{pillar_name}柱地支无效: {zhi}")
        
        # 验证性别
        if self.gender not in ['男', '女']:
            raise ValueError(f"性别无效: {self.gender}")
    
    def get_pillars(self) -> Dict[str, Tuple[str, str]]:
        """获取四柱数据"""
        return {
            'year': self.year,
            'month': self.month,
            'day': self.day,
            'hour': self.hour
        }
    
    def get_day_master(self) -> str:
        """获取日主"""
        return self.day[0]
    
    def get_month_branch(self) -> str:
        """获取月支"""
        return self.month[1]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'year': self.year,
            'month': self.month,
            'day': self.day,
            'hour': self.hour,
            'birth_year': self.birth_year,
            'birth_month': self.birth_month,
            'birth_day': self.birth_day,
            'birth_hour': self.birth_hour,
            'gender': self.gender,
            'name': self.name,
            'lunar_calendar': self.lunar_calendar,
            'timezone': self.timezone,
            'location': self.location
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BaziData:
        """从字典创建实例"""
        return cls(
            year=data['year'],
            month=data['month'],
            day=data['day'],
            hour=data['hour'],
            birth_year=data['birth_year'],
            birth_month=data['birth_month'],
            birth_day=data['birth_day'],
            birth_hour=data['birth_hour'],
            gender=data['gender'],
            name=data.get('name'),
            lunar_calendar=data.get('lunar_calendar', False),
            timezone=data.get('timezone', 'Asia/Shanghai'),
            location=data.get('location')
        )


@dataclass
class AnalysisResult:
    """分析结果数据结构"""
    # 基本信息
    analyzer_name: str
    book_name: str
    analysis_type: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    # 分析结果
    level: str = ""  # 等级
    score: float = 0.0  # 评分
    description: str = ""  # 描述
    details: Dict[str, Any] = field(default_factory=dict)  # 详细信息
    
    # 建议和解释
    advice: str = ""  # 建议
    explanation: str = ""  # 解释
    
    # 性能信息
    analysis_time: float = 0.0  # 分析耗时（毫秒）
    cache_hit: bool = False  # 是否命中缓存
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'analyzer_name': self.analyzer_name,
            'book_name': self.book_name,
            'analysis_type': self.analysis_type,
            'timestamp': self.timestamp.isoformat(),
            'level': self.level,
            'score': self.score,
            'description': self.description,
            'details': self.details,
            'advice': self.advice,
            'explanation': self.explanation,
            'analysis_time': self.analysis_time,
            'cache_hit': self.cache_hit,
            'metadata': self.metadata
        }
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    def get_summary(self) -> str:
        """获取结果摘要"""
        return f"{self.book_name} - {self.analysis_type}: {self.level} ({self.score}分)"


@dataclass
class AnalysisConfig:
    """分析配置"""
    # 性能配置
    enable_cache: bool = True
    cache_ttl: int = 3600  # 缓存生存时间（秒）
    max_analysis_time: float = 1000.0  # 最大分析时间（毫秒）
    
    # 分析配置
    include_details: bool = True
    include_advice: bool = True
    include_explanation: bool = True
    
    # 输出配置
    output_format: str = 'dict'  # 'dict', 'json', 'summary'
    language: str = 'zh'  # 'zh', 'en'
    
    # 调试配置
    debug_mode: bool = False
    verbose: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'enable_cache': self.enable_cache,
            'cache_ttl': self.cache_ttl,
            'max_analysis_time': self.max_analysis_time,
            'include_details': self.include_details,
            'include_advice': self.include_advice,
            'include_explanation': self.include_explanation,
            'output_format': self.output_format,
            'language': self.language,
            'debug_mode': self.debug_mode,
            'verbose': self.verbose
        }
