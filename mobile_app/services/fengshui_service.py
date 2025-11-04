#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风水服务 - 移动端
保持原有业务逻辑不变
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

# 添加项目根目录
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class FengshuiService:
    """风水服务类"""
    
    def __init__(self):
        """初始化服务"""
        pass
    
    def analyze_fengshui(self, fengshui_type: str, direction: str, total_floors: int,
                        current_floor: int, area: float, main_resident: str = "",
                        special_need: str = "", birth_year: Optional[int] = None,
                        gender: Optional[str] = None) -> Dict[str, Any]:
        """
        风水分析
        
        Args:
            fengshui_type: 风水类型（阳宅、阴宅、办公室）
            direction: 房屋朝向
            total_floors: 总层数
            current_floor: 当前楼层
            area: 面积
            main_resident: 主要居住者
            special_need: 特殊需求
            birth_year: 出生年份（用于命卦计算）
            gender: 性别（用于命卦计算）
        
        Returns:
            风水分析结果
        """
        try:
            # 调用桌面版的风水分析逻辑
            # 这里需要从桌面版提取核心算法
            
            # 八卦方位分析
            direction_info = self.get_direction_analysis(direction)
            
            # 玄空飞星分析
            flying_star = self.analyze_xuankong_feixing(direction, current_floor)
            
            # 楼层分析
            floor_analysis = self.analyze_floor(current_floor, total_floors, direction_info['element'])
            
            # 面积分析
            area_analysis = self.analyze_area(area, direction_info['element'])
            
            # 八宅分析（如果有个人信息）
            bazhai_analysis = None
            if birth_year and gender:
                bazhai_analysis = self.analyze_bazhai(direction, birth_year, gender)
            
            return {
                'success': True,
                'data': {
                    'direction_info': direction_info,
                    'flying_star': flying_star,
                    'floor_analysis': floor_analysis,
                    'area_analysis': area_analysis,
                    'bazhai_analysis': bazhai_analysis,
                    'overall_score': direction_info.get('score', 60)
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_direction_analysis(self, direction: str) -> Dict[str, Any]:
        """获取朝向分析"""
        bagua_directions = {
            "坐北朝南": {
                "gua": "坎宅离门", "element": "水", "score": 95, "level": "大吉",
                "desc": "坎水得位，离火照明，阴阳调和，是最理想的朝向",
                "family_benefit": "利中男，主智慧聪明",
                "career": "适合从事智慧型、流动性工作",
                "health": "利于肾脏、泌尿系统健康",
                "wealth": "财运稳定，细水长流",
                "layout": "客厅宜在南方，卧室宜在北方"
            },
            "坐东朝西": {
                "gua": "震宅兑门", "element": "木", "score": 75, "level": "中吉",
                "desc": "震木生发，兑金收敛，动静相宜",
                "family_benefit": "利长子，主事业发展",
                "career": "适合开创性、竞争性工作",
                "health": "利于肝胆、神经系统",
                "wealth": "财运波动，需要积极进取",
                "layout": "书房宜在东方，客厅宜在西方"
            },
            "坐南朝北": {
                "gua": "离宅坎门", "element": "火", "score": 45, "level": "大凶",
                "desc": "离火被坎水冲克，阴气过重，需要特别调理",
                "family_benefit": "不利中女，影响心脏健康",
                "career": "事业发展受阻，需要额外努力",
                "health": "注意心脏、血液循环问题",
                "wealth": "财运不稳，容易破财",
                "layout": "需要增加阳气，多用红色、橙色装饰"
            },
            "坐西朝东": {
                "gua": "兑宅震门", "element": "金", "score": 70, "level": "中平",
                "desc": "兑金克震木，需要调和五行",
                "family_benefit": "利少女，主口才艺术",
                "career": "适合艺术、娱乐、金融工作",
                "health": "利于肺部、呼吸系统",
                "wealth": "财运中等，需要理性投资",
                "layout": "卧室宜在西方，活动区宜在东方"
            },
            "坐东北朝西南": {
                "gua": "艮宅坤门", "element": "土", "score": 80, "level": "中吉",
                "desc": "艮土得坤土相助，厚德载物，利于积累",
                "family_benefit": "利少男和母亲，家庭和睦",
                "career": "适合稳定性、积累性工作",
                "health": "利于脾胃、消化系统",
                "wealth": "财运稳健，善于储蓄",
                "layout": "财位宜在东北，厨房宜在西南"
            },
            "坐西南朝东北": {
                "gua": "坤宅艮门", "element": "土", "score": 65, "level": "中平",
                "desc": "坤土包容，艮土稳固，利于家庭和谐",
                "family_benefit": "利母亲和少男，女性当家",
                "career": "适合服务性、照顾性工作",
                "health": "注意腹部、脾胃健康",
                "wealth": "财运平稳，适合保守投资",
                "layout": "主卧宜在西南，书房宜在东北"
            },
            "坐东南朝西北": {
                "gua": "巽宅乾门", "element": "木", "score": 85, "level": "大吉",
                "desc": "巽木得乾金修剪，文昌大利，财运亨通",
                "family_benefit": "利长女和父亲，文武双全",
                "career": "适合文化、教育、贸易工作",
                "health": "利于胆囊、神经系统",
                "wealth": "财运极佳，多方来财",
                "layout": "书房宜在东南，客厅宜在西北"
            },
            "坐西北朝东南": {
                "gua": "乾宅巽门", "element": "金", "score": 90, "level": "大吉",
                "desc": "乾金得巽木生财，权威显达，事业有成",
                "family_benefit": "利父亲和长女，权威与智慧并重",
                "career": "适合管理、领导、决策工作",
                "health": "利于头部、肺部健康",
                "wealth": "财运旺盛，权财双收",
                "layout": "主卧宜在西北，财位宜在东南"
            }
        }
        
        return bagua_directions.get(direction, {
            "gua": "未知卦位", "element": "未知", "score": 60, "level": "中平",
            "desc": "需要具体勘察分析",
            "family_benefit": "需要详细分析",
            "career": "根据具体情况调整",
            "health": "保持良好生活习惯",
            "wealth": "需要合理规划",
            "layout": "请咨询专业风水师"
        })
    
    def analyze_xuankong_feixing(self, direction: str, current_floor: int) -> Dict[str, Any]:
        """玄空飞星分析"""
        # 基础星盘（简化版）
        base_stars = {
            "坐北朝南": {"center": 8, "south": 3, "north": 4},
            "坐东朝西": {"center": 6, "south": 1, "north": 2},
            "坐南朝北": {"center": 2, "south": 6, "north": 7},
            "坐西朝东": {"center": 4, "south": 8, "north": 9},
        }
        
        stars = base_stars.get(direction, base_stars["坐北朝南"])
        
        # 楼层调整
        floor_star = (current_floor - 1) % 9 + 1
        
        return {
            "star_distribution": stars,
            "floor_star": floor_star,
            "analysis": f"当前楼层飞星：{floor_star}，影响整体运势"
        }
    
    def analyze_floor(self, current_floor: int, total_floors: int, element: str) -> Dict[str, Any]:
        """楼层分析"""
        return {
            "current_floor": current_floor,
            "total_floors": total_floors,
            "element": element,
            "analysis": f"楼层{current_floor}，五行属{element}，适合{element}属性的人居住"
        }
    
    def analyze_area(self, area: float, element: str) -> Dict[str, Any]:
        """面积分析"""
        if area < 50:
            size_desc = "小户型"
        elif area < 100:
            size_desc = "中户型"
        else:
            size_desc = "大户型"
        
        return {
            "area": area,
            "size_desc": size_desc,
            "analysis": f"面积{area}平方米，{size_desc}，适合{element}属性的布局"
        }
    
    def analyze_bazhai(self, direction: str, birth_year: int, gender: str) -> Dict[str, Any]:
        """八宅分析"""
        # 计算命卦
        year_last_two = birth_year % 100
        if gender == '男':
            mingua_num = (100 - year_last_two) % 9
            if mingua_num == 0:
                mingua_num = 9
        else:
            mingua_num = (year_last_two + 5) % 9
            if mingua_num == 0:
                mingua_num = 9
        
        mingua_map = {
            1: '坎', 2: '坤', 3: '震', 4: '巽',
            5: '坤', 6: '乾', 7: '兑', 8: '艮', 9: '离'
        }
        mingua = mingua_map.get(mingua_num, '未知')
        
        return {
            "mingua": mingua,
            "mingua_num": mingua_num,
            "description": f"{gender}命，{birth_year}年生，命卦为{mingua}（{mingua_num}）"
        }

