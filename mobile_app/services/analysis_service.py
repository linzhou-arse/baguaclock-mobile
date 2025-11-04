#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
综合分析服务 - 移动端
整合神煞、财运、婚姻、职业等分析功能
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

# 添加项目根目录
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class AnalysisService:
    """综合分析服务类"""
    
    def __init__(self):
        """初始化服务"""
        self._init_modules()
    
    def _init_modules(self):
        """初始化分析模块"""
        # 神煞分析器
        try:
            from classic_analyzer.shensha import ShenShaAnalyzer
            self.shensha_analyzer = ShenShaAnalyzer
            self.shensha_available = True
        except ImportError:
            self.shensha_available = False
        
        # 财运分析器
        try:
            from classic_analyzer.caiyun import CaiyunAnalyzer
            self.caiyun_analyzer = CaiyunAnalyzer
            self.caiyun_available = True
        except ImportError:
            self.caiyun_available = False
        
        # 本地命理分析器（包含婚姻、职业等）
        try:
            from local_mingli_analyzer_unified import UnifiedMingliAnalyzer
            self.mingli_analyzer = UnifiedMingliAnalyzer()
            self.mingli_available = True
        except ImportError:
            self.mingli_available = False
    
    def analyze_shensha(self, pillars: Dict[str, tuple], birth_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        神煞分析
        
        Args:
            pillars: {'year': ('甲','子'), 'month': ('丙','寅'), ...}
            birth_info: {'gender': '男/女', ...}
        
        Returns:
            神煞分析结果
        """
        if not self.shensha_available:
            return {'error': '神煞分析器未安装'}
        
        try:
            result = self.shensha_analyzer.analyze_shensha(pillars, birth_info)
            return {
                'success': True,
                'data': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_caiyun(self, pillars: Dict[str, tuple], day_master: str) -> Dict[str, Any]:
        """
        财运分析
        
        Args:
            pillars: 四柱信息
            day_master: 日主
        
        Returns:
            财运分析结果
        """
        if not self.caiyun_available:
            return {'error': '财运分析器未安装'}
        
        try:
            result = self.caiyun_analyzer.analyze_caiyun(pillars, day_master)
            return {
                'success': True,
                'data': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_marriage(self, pillars: Dict[str, tuple], day_master: str, gender: str, 
                        birth_info: Optional[Dict] = None) -> Dict[str, Any]:
        """
        婚姻分析
        
        Args:
            pillars: 四柱信息
            day_master: 日主
            gender: 性别
            birth_info: 出生信息
        
        Returns:
            婚姻分析结果
        """
        if not self.mingli_available:
            return {'error': '命理分析器未安装'}
        
        try:
            # 使用本地分析器的婚姻分析功能
            result = self.mingli_analyzer.analyze_bazi(pillars, gender, birth_info)
            
            # 提取婚姻相关信息
            if isinstance(result, dict):
                marriage_info = result.get('marriage', {})
                return {
                    'success': True,
                    'data': marriage_info
                }
            else:
                # 如果返回的是字符串，尝试解析
                return {
                    'success': True,
                    'data': {'summary': str(result)}
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_career(self, pillars: Dict[str, tuple], day_master: str, gender: str,
                      birth_info: Optional[Dict] = None) -> Dict[str, Any]:
        """
        职业分析
        
        Args:
            pillars: 四柱信息
            day_master: 日主
            gender: 性别
            birth_info: 出生信息
        
        Returns:
            职业分析结果
        """
        if not self.mingli_available:
            return {'error': '命理分析器未安装'}
        
        try:
            result = self.mingli_analyzer.analyze_bazi(pillars, gender, birth_info)
            
            # 提取职业相关信息
            if isinstance(result, dict):
                career_info = result.get('career_wealth', {})
                return {
                    'success': True,
                    'data': career_info
                }
            else:
                return {
                    'success': True,
                    'data': {'summary': str(result)}
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

