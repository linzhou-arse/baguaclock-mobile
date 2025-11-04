#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一命理分析器 - Unified Mingli Analyzer
========================================

整合 LocalMingliAnalyzer 和 chinese_metaphysics_library 的统一分析器
提供完整的八字命理分析功能
"""

from typing import Dict, Any, Optional
from local_mingli_analyzer import LocalMingliAnalyzer

# 尝试导入六书知识库
try:
    from chinese_metaphysics_library import UnifiedMetaphysicsAnalyzer
    from chinese_metaphysics_library.core.data_structures import BaziData, AnalysisConfig
    CML_AVAILABLE = True
except ImportError:
    CML_AVAILABLE = False
    print("[WARNING] 六书知识库未加载，将使用基础分析器")


class UnifiedMingliAnalyzer:
    """统一命理分析器 - 整合本地分析器和六书知识库"""
    
    def __init__(self):
        """初始化统一分析器"""
        # 初始化本地分析器（基础分析）
        self.local_analyzer = LocalMingliAnalyzer()
        
        # 初始化六书分析器（高级分析）
        if CML_AVAILABLE:
            config = AnalysisConfig(
                enable_cache=True,
                include_details=True,
                include_advice=True,
                include_explanation=True
            )
            self.cml_analyzer = UnifiedMetaphysicsAnalyzer(config)
        else:
            self.cml_analyzer = None
    
    def analyze_bazi(self, pillars: Dict[str, str], gender: str = '男', 
                     birth_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        完整的八字分析
        
        Args:
            pillars: 四柱数据 {'year': '甲子', 'month': '丙寅', 'day': '戊辰', 'hour': '庚申'}
            gender: 性别 '男' 或 '女'
            birth_info: 出生信息（可选）
        
        Returns:
            完整的分析报告字典
        """
        # 使用本地分析器进行基础分析
        local_result = self.local_analyzer.analyze_bazi(pillars, gender, birth_info)
        
        # 如果六书知识库可用，进行高级分析
        if self.cml_analyzer and birth_info:
            try:
                # 构建 BaziData 对象
                bazi_data = self._build_bazi_data(pillars, gender, birth_info)
                
                # 执行六书综合分析
                cml_result = self.cml_analyzer.analyze(bazi_data)
                
                # 整合分析结果
                local_result['六书分析'] = {
                    '综合评分': cml_result.score,
                    '综合等级': cml_result.level,
                    '分析说明': cml_result.description,
                    '详细结果': cml_result.details,
                    '建议': cml_result.advice,
                    '解释': cml_result.explanation
                }
            except Exception as e:
                print(f"[WARNING] 六书分析失败: {e}")
                local_result['六书分析'] = {'错误': str(e)}
        
        return local_result
    
    def _build_bazi_data(self, pillars: Dict[str, str], gender: str, 
                        birth_info: Dict[str, Any]) -> 'BaziData':
        """构建 BaziData 对象"""
        # 解析四柱
        year_gan, year_zhi = pillars['year'][0], pillars['year'][1]
        month_gan, month_zhi = pillars['month'][0], pillars['month'][1]
        day_gan, day_zhi = pillars['day'][0], pillars['day'][1]
        hour_gan, hour_zhi = pillars['hour'][0], pillars['hour'][1]
        
        # 构建 BaziData
        bazi_data = BaziData(
            year=(year_gan, year_zhi),
            month=(month_gan, month_zhi),
            day=(day_gan, day_zhi),
            hour=(hour_gan, hour_zhi),
            birth_year=birth_info.get('year', 1990),
            birth_month=birth_info.get('month', 1),
            birth_day=birth_info.get('day', 1),
            birth_hour=birth_info.get('hour', 12),
            gender=gender,
            name=birth_info.get('name'),
            lunar_calendar=birth_info.get('lunar_calendar', True),
            location=birth_info.get('location')
        )
        
        return bazi_data
    
    def get_analyzer_info(self) -> Dict[str, Any]:
        """获取分析器信息"""
        info = {
            '本地分析器': '可用',
            '六书知识库': '可用' if CML_AVAILABLE else '不可用'
        }
        
        if CML_AVAILABLE and self.cml_analyzer:
            info['支持的经典'] = self.cml_analyzer.get_supported_books()
        
        return info
    
    def analyze_by_book(self, pillars: Dict[str, str], gender: str, 
                       birth_info: Dict[str, Any], book_name: str) -> Dict[str, Any]:
        """
        按指定经典分析
        
        Args:
            pillars: 四柱数据
            gender: 性别
            birth_info: 出生信息
            book_name: 经典名称（如'三命通会'）
        
        Returns:
            指定经典的分析结果
        """
        if not CML_AVAILABLE or not self.cml_analyzer:
            return {'错误': '六书知识库不可用'}
        
        try:
            bazi_data = self._build_bazi_data(pillars, gender, birth_info)
            result = self.cml_analyzer.analyze_by_book(bazi_data, book_name)
            
            return {
                '经典': book_name,
                '评分': result.score,
                '等级': result.level,
                '描述': result.description,
                '详情': result.details,
                '建议': result.advice,
                '解释': result.explanation
            }
        except Exception as e:
            return {'错误': f'分析失败: {e}'}


# 为了向后兼容，提供别名
UnifiedAnalyzer = UnifiedMingliAnalyzer


# 测试代码
if __name__ == '__main__':
    print("=" * 60)
    print("统一命理分析器测试")
    print("=" * 60)
    
    # 创建分析器
    analyzer = UnifiedMingliAnalyzer()
    
    # 显示分析器信息
    print("\n分析器信息:")
    info = analyzer.get_analyzer_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # 测试八字
    test_pillars = {
        'year': '庚午',
        'month': '戊寅',
        'day': '丙午',
        'hour': '癸巳'
    }
    
    test_birth_info = {
        'year': 1990,
        'month': 1,
        'day': 15,
        'hour': 10,
        'name': '测试',
        'lunar_calendar': True,
        'location': '北京'
    }
    
    print("\n" + "=" * 60)
    print("测试八字分析")
    print("=" * 60)
    print(f"四柱: {test_pillars}")
    print(f"性别: 男")
    
    # 执行分析
    result = analyzer.analyze_bazi(test_pillars, '男', test_birth_info)
    
    # 显示结果摘要
    print("\n分析结果摘要:")
    print(f"  格局: {result.get('格局判断', {}).get('格局类型', '未知')}")
    print(f"  旺衰: {result.get('旺衰分析', {}).get('旺衰等级', '未知')}")
    print(f"  用神: {result.get('用神分析', {}).get('用神', '未知')}")
    
    if '六书分析' in result:
        print(f"\n六书综合分析:")
        print(f"  评分: {result['六书分析'].get('综合评分', 0):.1f}")
        print(f"  等级: {result['六书分析'].get('综合等级', '未知')}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

