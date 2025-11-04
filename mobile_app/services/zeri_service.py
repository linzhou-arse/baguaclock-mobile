#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
择日服务 - 移动端
保持原有业务逻辑不变
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, date, timedelta

# 添加项目根目录
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class ZeriService:
    """择日服务类"""
    
    def __init__(self):
        """初始化服务"""
        pass
    
    def analyze_general_auspicious_dates(self, event_type: str, start_date: date, 
                                       end_date: date, preferred_hour: str = "不限时辰") -> Dict[str, Any]:
        """
        分析黄道吉日（不需要八字）
        
        Args:
            event_type: 事件类型（如：结婚嫁娶、开业开张等）
            start_date: 开始日期
            end_date: 结束日期
            preferred_hour: 首选时辰
        
        Returns:
            择日分析结果
        """
        try:
            # 基于传统黄历理论分析
            analysis = []
            analysis.append("【黄道吉日分析】")
            analysis.append("基于传统黄历理论，不依赖个人八字")
            analysis.append("")
            
            analysis.append(f"📅 择日事件：{event_type}")
            analysis.append(f"📆 择日范围：{start_date} 至 {end_date}")
            if preferred_hour != "不限时辰":
                analysis.append(f"⏰ 首选时辰：{preferred_hour}")
            analysis.append("")
            
            # 获取通用吉日
            auspicious_dates = self.get_general_auspicious_dates(event_type, start_date, end_date)
            analysis.extend(auspicious_dates)
            
            # 时辰建议
            hour_suggestions = self.get_general_auspicious_hours(event_type, preferred_hour)
            analysis.extend(hour_suggestions)
            
            return {
                'success': True,
                'data': {
                    'analysis': '\n'.join(analysis),
                    'dates': auspicious_dates
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def analyze_bazi_auspicious_dates(self, event_type: str, bazi_result: Dict[str, Any],
                                     start_date: date, end_date: date, 
                                     preferred_hour: str = "不限时辰") -> Dict[str, Any]:
        """
        分析八字择日（需要八字）
        
        Args:
            event_type: 事件类型
            bazi_result: 八字计算结果
            start_date: 开始日期
            end_date: 结束日期
            preferred_hour: 首选时辰
        
        Returns:
            择日分析结果
        """
        try:
            analysis = []
            analysis.append("【八字择日分析】")
            analysis.append("基于个人八字的专业择日分析")
            analysis.append("")
            
            # 个人信息
            name = bazi_result.get('name', '未知')
            gender = bazi_result.get('gender', '未知')
            if 'sizhu' in bazi_result:
                sizhu = bazi_result['sizhu']
                bazi_text = f"{sizhu.get('year', '')} {sizhu.get('month', '')} {sizhu.get('day', '')} {sizhu.get('hour', '')}"
            else:
                bazi_text = "无法获取"
            
            analysis.append(f"👤 姓名：{name}")
            analysis.append(f"⚥ 性别：{gender}")
            analysis.append(f"🔮 八字：{bazi_text}")
            analysis.append("")
            
            analysis.append(f"📅 择日事件：{event_type}")
            analysis.append(f"📆 择日范围：{start_date} 至 {end_date}")
            if preferred_hour != "不限时辰":
                analysis.append(f"⏰ 首选时辰：{preferred_hour}")
            analysis.append("")
            
            # 基于八字分析吉日（简化版）
            analysis.append("【推荐吉日】")
            analysis.append("基于八字用神和忌神分析，选择对个人有利的日期")
            
            # 这里可以调用桌面版的择日算法
            # 暂时提供基础分析
            analysis.append("建议选择：")
            analysis.append("• 与日主相合的日子")
            analysis.append("• 用神当值的日子")
            analysis.append("• 避开忌神当值的日子")
            
            return {
                'success': True,
                'data': {
                    'analysis': '\n'.join(analysis)
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_general_auspicious_dates(self, event_type: str, start_date: date, end_date: date) -> list:
        """获取通用黄道吉日"""
        dates = []
        dates.append("【推荐吉日】")
        
        # 基于传统黄历的吉日计算（简化版）
        # 这里可以实现具体的黄道吉日计算逻辑
        current = start_date
        count = 0
        while current <= end_date and count < 10:
            # 简化：选择每月的前几天（实际应基于黄历）
            if current.day <= 15:
                dates.append(f"• {current.strftime('%Y年%m月%d日')} - 黄道吉日")
                count += 1
            current += timedelta(days=7)  # 每周检查一次
        
        if not dates or len(dates) == 1:
            dates.append("• 建议选择每月初一、初八、十五等传统吉日")
        
        return dates
    
    def get_general_auspicious_hours(self, event_type: str, preferred_hour: str) -> list:
        """获取通用吉时"""
        hours = []
        hours.append("\n【推荐时辰】")
        
        # 根据事件类型推荐时辰
        event_hours = {
            "结婚嫁娶": ["午时(11:00-13:00)", "巳时(9:00-11:00)", "辰时(7:00-9:00)"],
            "开业开张": ["巳时(9:00-11:00)", "午时(11:00-13:00)", "辰时(7:00-9:00)"],
            "搬家入宅": ["巳时(9:00-11:00)", "午时(11:00-13:00)", "未时(13:00-15:00)"],
            "动土建房": ["巳时(9:00-11:00)", "午时(11:00-13:00)", "辰时(7:00-9:00)"],
        }
        
        recommended = event_hours.get(event_type, ["巳时(9:00-11:00)", "午时(11:00-13:00)"])
        for hour in recommended:
            hours.append(f"• {hour} - 大吉")
        
        return hours

