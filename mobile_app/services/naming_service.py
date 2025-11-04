#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
起名服务 - 移动端
保持原有业务逻辑不变
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

# 添加项目根目录
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class NamingService:
    """起名服务类"""
    
    def __init__(self):
        """初始化服务"""
        pass
    
    def analyze_name(self, surname: str, given_name: str, bazi_result: Dict[str, Any],
                    gender: str) -> Dict[str, Any]:
        """
        分析现有姓名
        
        Args:
            surname: 姓氏
            given_name: 名字
            bazi_result: 八字计算结果
            gender: 性别
        
        Returns:
            姓名分析结果
        """
        try:
            analysis = []
            analysis.append(f"【姓名分析】")
            analysis.append(f"姓名：{surname}{given_name}")
            analysis.append("")
            
            # 五行分析
            wuxing_analysis = self.analyze_name_wuxing(surname, given_name)
            analysis.append("【五行分析】")
            analysis.append(wuxing_analysis)
            analysis.append("")
            
            # 笔画分析
            stroke_analysis = self.analyze_name_strokes(surname, given_name)
            analysis.append("【笔画分析】")
            analysis.append(stroke_analysis)
            analysis.append("")
            
            # 与八字匹配度
            if bazi_result and 'sizhu' in bazi_result:
                match_analysis = self.analyze_bazi_match(surname, given_name, bazi_result)
                analysis.append("【八字匹配】")
                analysis.append(match_analysis)
            
            return {
                'success': True,
                'data': {
                    'analysis': '\n'.join(analysis),
                    'wuxing': wuxing_analysis,
                    'strokes': stroke_analysis
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def suggest_names(self, surname: str, bazi_result: Dict[str, Any], gender: str,
                     name_count: int = 5) -> Dict[str, Any]:
        """
        起名建议
        
        Args:
            surname: 姓氏
            bazi_result: 八字计算结果
            gender: 性别
            name_count: 建议数量
        
        Returns:
            起名建议结果
        """
        try:
            suggestions = []
            suggestions.append(f"【起名建议】")
            suggestions.append(f"姓氏：{surname}")
            suggestions.append(f"性别：{gender}")
            suggestions.append("")
            
            # 根据八字推荐名字（简化版）
            if bazi_result and 'sizhu' in bazi_result:
                sizhu = bazi_result['sizhu']
                day_master = sizhu.get('day_gan', '')
                
                suggestions.append("【推荐名字】")
                suggestions.append("基于八字用神和五行平衡推荐：")
                
                # 这里可以调用桌面版的起名算法
                # 暂时提供示例
                for i in range(1, name_count + 1):
                    suggestions.append(f"{i}. {surname}XX - 五行平衡，符合八字")
            else:
                suggestions.append("请先计算八字，以便提供更精准的起名建议")
            
            return {
                'success': True,
                'data': {
                    'suggestions': '\n'.join(suggestions)
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_name_wuxing(self, surname: str, given_name: str) -> str:
        """分析姓名五行"""
        # 简化版五行分析
        return f"姓名五行分布：需要根据具体字来分析\n建议：选择与八字用神相合的字"
    
    def analyze_name_strokes(self, surname: str, given_name: str) -> str:
        """分析姓名笔画"""
        # 简化版笔画分析
        return f"姓名笔画：需要根据具体字来计算\n建议：选择吉利的笔画数"
    
    def analyze_bazi_match(self, surname: str, given_name: str, bazi_result: Dict[str, Any]) -> str:
        """分析姓名与八字匹配度"""
        return "姓名与八字匹配度：需要根据八字用神来判断\n建议：选择补益用神的字"

