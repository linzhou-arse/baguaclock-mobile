#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八字计算服务 - 移动端
保持原有业务逻辑不变，只做接口适配
"""

import sys
from pathlib import Path

# 添加项目根目录
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class BaziService:
    """八字计算服务类"""
    
    def __init__(self):
        """初始化服务"""
        self.sxtwl_available = False
        self.analyzer_available = False
        
        # 尝试导入sxtwl适配器
        try:
            from sxtwl_adapter import compute_bazi_json, Rules, Location
            self.compute_bazi_json = compute_bazi_json
            self.Rules = Rules
            self.Location = Location
            self.sxtwl_available = True
        except ImportError:
            pass
        
        # 尝试导入分析器
        try:
            from local_mingli_analyzer_unified import UnifiedMingliAnalyzer
            self.analyzer = UnifiedMingliAnalyzer()
            self.analyzer_available = True
        except ImportError:
            pass
    
    def calculate(self, year, month, day, hour, gender='male', location=None):
        """
        计算八字
        
        Args:
            year: 出生年份
            month: 出生月份（1-12）
            day: 出生日期
            hour: 出生时辰（0-23）
            gender: 性别（'male'或'female'）
            location: 出生地（可选）
        
        Returns:
            dict: 八字计算结果
        """
        if not self.sxtwl_available:
            return {
                'error': 'sxtwl模块未安装',
                'sizhu': None
            }
        
        try:
            # 构造输入参数
            rules = self.Rules()
            rules.use_solar_time = True  # 使用真太阳时
            
            # 如果有位置信息，设置位置
            if location:
                # 这里可以解析位置字符串，获取经纬度
                # 简化处理：使用默认位置
                loc = self.Location()
                loc.longitude = 116.3974  # 北京经度（默认）
                loc.latitude = 39.9093    # 北京纬度（默认）
                rules.location = loc
            
            # 计算八字
            result_json = self.compute_bazi_json(
                year=year,
                month=month,
                day=day,
                hour=hour,
                rules=rules
            )
            
            # 解析结果
            if isinstance(result_json, str):
                import json
                result = json.loads(result_json)
            else:
                result = result_json
            
            # 如果有分析器，进行详细分析
            if self.analyzer_available and result:
                analysis = self.analyzer.analyze(result)
                result['analysis'] = analysis
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'sizhu': None
            }
    
    def analyze_detail(self, bazi_result):
        """
        详细分析八字
        
        Args:
            bazi_result: 八字计算结果
        
        Returns:
            dict: 详细分析结果
        """
        if not self.analyzer_available:
            return {'error': '分析器未安装'}
        
        try:
            return self.analyzer.analyze(bazi_result)
        except Exception as e:
            return {'error': str(e)}

