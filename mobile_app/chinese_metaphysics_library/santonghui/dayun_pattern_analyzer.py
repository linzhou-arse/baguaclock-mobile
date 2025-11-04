#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大运格局分析器 - Dayun Pattern Analyzer
=====================================

基于《三命通会》《子平真诠》理论的大运判断
核心逻辑：格局 + 十神 + 五行平衡 三维判断
"""

from typing import Dict, List, Tuple, Any
from ..core.utils import get_wuxing_by_tiangan, get_wuxing_by_dizhi, get_ten_god
from ..core.constants import TIANGAN_WUXING, DIZHI_CANGGAN


class DayunPatternAnalyzer:
    """大运格局分析器 - 基于格局+十神的综合判断"""
    
    def __init__(self):
        """初始化分析器"""
        pass
    
    def judge_dayun_step(self, 
                        gan: str, 
                        zhi: str, 
                        day_master: str,
                        pillars: Dict[str, Tuple[str, str]],
                        pattern_info: Dict[str, Any],
                        yongshen_info: Dict[str, Any]) -> Dict[str, str]:
        """
        判断单步大运的吉凶
        
        参数:
            gan: 大运天干
            zhi: 大运地支
            day_master: 日主
            pillars: 四柱信息
            pattern_info: 格局信息 {'pattern': '伤官配印格', 'status': '成格', 'issue': '印重'}
            yongshen_info: 用神信息 {'yongshen': '壬甲', 'xishen': '水木', 'jishen': '土金', 'method': '调候'}
        
        返回:
            {
                'description': '食伤运，聪明初显',  # 具体描述
                'level': '吉',  # 吉凶等级
                'reason': '食伤泄秀，淘金有力'  # 判断理由
            }
        """
        # 1. 计算大运天干的十神
        dayun_ten_god = get_ten_god(day_master, gan)
        
        # 2. 获取格局信息
        pattern = pattern_info.get('pattern', '')
        pattern_issue = pattern_info.get('issue', '')  # 格局的病症（如"印重"）
        
        # 3. 获取用神信息
        yongshen_method = yongshen_info.get('method', '')
        xishen_wuxing = yongshen_info.get('xishen_wuxing', [])  # 喜神五行列表
        jishen_wuxing = yongshen_info.get('jishen_wuxing', [])  # 忌神五行列表
        
        # 4. 基于格局+十神+五行的综合判断
        result = self._judge_by_pattern_and_shishen(
            gan, zhi, dayun_ten_god, day_master, pillars,
            pattern, pattern_issue, 
            xishen_wuxing, jishen_wuxing, yongshen_method
        )
        
        return result
    
    def _judge_by_pattern_and_shishen(self,
                                      gan: str,
                                      zhi: str,
                                      dayun_ten_god: str,
                                      day_master: str,
                                      pillars: Dict[str, Tuple[str, str]],
                                      pattern: str,
                                      pattern_issue: str,
                                      xishen_wuxing: List[str],
                                      jishen_wuxing: List[str],
                                      yongshen_method: str) -> Dict[str, str]:
        """
        基于格局+十神的综合判断
        
        核心逻辑：
        1. 先看格局类型（如"伤官配印格"）
        2. 再看格局病症（如"印重"）
        3. 结合大运十神判断吉凶
        """
        # 获取大运天干和地支的五行
        gan_wx = TIANGAN_WUXING.get(gan, '')
        zhi_wx = get_wuxing_by_dizhi(zhi)
        
        # 判断大运五行是否为喜/忌
        gan_is_xishen = gan_wx in xishen_wuxing
        gan_is_jishen = gan_wx in jishen_wuxing
        zhi_is_xishen = zhi_wx in xishen_wuxing
        zhi_is_jishen = zhi_wx in jishen_wuxing
        
        # 特殊格局判断
        # 伤官格或伤官配印格
        if '伤官' in pattern:
            return self._judge_shangguan_peiyin(
                gan, zhi, dayun_ten_god, pattern_issue,
                gan_wx, zhi_wx, gan_is_xishen, gan_is_jishen,
                zhi_is_xishen, zhi_is_jishen, xishen_wuxing, jishen_wuxing,
                pillars  # 🔥 传入四柱信息，用于判断"伤官见官"
            )
        
        # 其他格局的判断逻辑（待扩展）
        # TODO: 添加其他格局的判断
        
        # 默认：基于五行喜忌的简单判断
        return self._judge_by_wuxing_xiji(
            gan, zhi, dayun_ten_god,
            gan_wx, zhi_wx, gan_is_xishen, gan_is_jishen,
            zhi_is_xishen, zhi_is_jishen
        )
    
    def _judge_shangguan_peiyin(self,
                                gan: str,
                                zhi: str,
                                dayun_ten_god: str,
                                pattern_issue: str,
                                gan_wx: str,
                                zhi_wx: str,
                                gan_is_xishen: bool,
                                gan_is_jishen: bool,
                                zhi_is_xishen: bool,
                                zhi_is_jishen: bool,
                                xishen_wuxing: List[str],
                                jishen_wuxing: List[str],
                                pillars: Dict = None) -> Dict[str, str]:
        """
        伤官配印格的大运判断
        
        理论依据：
        - 伤官配印格，印重为病时：
          - 食伤运：泄秀淘金 → 吉
          - 财运：财破印 → 吉（因为印重，破印反而好）
          - 官杀运：官印相生 → 中性偏忌（因为印已重，再生印不利）
          - 印运：土重埋金 → 忌
          - 比劫运：帮身 → 中性
        """
        # 判断是否"印重为病"
        yin_zhong = '印重' in pattern_issue or '印星过重' in pattern_issue or '土重' in pattern_issue
        
        # 1. 食伤运
        if dayun_ten_god in ['食神', '伤官']:
            # 🔥 检查是否"伤官见官"（原局有官杀）
            has_guan_sha = False
            if pillars:
                from ..core.utils import get_ten_god
                # 🔥 修复：从参数中获取日主，而不是从pillars中提取
                # day_master 已经在调用时传入了
                for pos, (gan_p, zhi_p) in pillars.items():
                    if pos == 'day':
                        continue
                    ten_god_p = get_ten_god(day_master, gan_p)
                    print(f"🔍 检查原局{pos}柱天干{gan_p}的十神: {ten_god_p}")
                    if ten_god_p in ['正官', '七杀', '偏官']:
                        has_guan_sha = True
                        print(f"✅ 发现官杀: {pos}柱{gan_p}={ten_god_p}")
                        break

            # 伤官见官，慎言
            print(f"🔍 壬申大运判断: dayun_ten_god={dayun_ten_god}, has_guan_sha={has_guan_sha}")
            if dayun_ten_god == '伤官' and has_guan_sha:
                return {
                    'description': '伤官见官，慎言',
                    'level': '中平',
                    'reason': '伤官见官，需谨慎言行'
                }

            if yin_zhong:
                # 印重时，食伤泄秀淘金，大吉
                if gan_is_xishen or zhi_is_xishen:
                    # 食神运，聪明初显
                    if '食神' in dayun_ten_god:
                        return {
                            'description': '食神运，聪明初显',
                            'level': '吉',
                            'reason': '食伤泄秀，淘金有力'
                        }
                    else:
                        return {
                            'description': f'{dayun_ten_god}运，才华展现',
                            'level': '吉',
                            'reason': '食伤泄秀，淘金有力'
                        }
                else:
                    return {
                        'description': f'{dayun_ten_god}运，平稳发展',
                        'level': '中平',
                        'reason': '食伤泄秀，但力量不足'
                    }
            else:
                # 印不重时，食伤可能克印，需谨慎
                return {
                    'description': f'{dayun_ten_god}运，需谨慎',
                    'level': '中平',
                    'reason': '食伤克印，需注意平衡'
                }
        
        # 2. 财运
        elif dayun_ten_god in ['正财', '偏财']:
            if yin_zhong:
                # 印重时，财破印，反而好
                if '正财' in dayun_ten_god:
                    # 正财透出，学业关键期
                    if gan_is_xishen:
                        return {
                            'description': '财星透出，学业关键期',
                            'level': '吉',
                            'reason': '财破印，印重得解'
                        }
                    else:
                        # 财星坐库或受制
                        return {
                            'description': '财星坐库，机遇与压力并存',
                            'level': '中平',
                            'reason': '财有根但受制'
                        }
                else:
                    # 偏财
                    # 🔥 检查是否"财星坐库"（地支为丑、辰、未、戌）
                    if zhi in ['丑', '辰', '未', '戌']:
                        return {
                            'description': '财星坐库，机遇与压力并存',
                            'level': '中平',
                            'reason': '财有根但受制'
                        }
                    else:
                        return {
                            'description': f'{dayun_ten_god}运，财运有机遇',
                            'level': '吉',
                            'reason': '财破印，印重得解'
                        }
            else:
                # 印不重时，财运正常判断
                if gan_is_xishen or zhi_is_xishen:
                    return {
                        'description': f'{dayun_ten_god}运，财运亨通',
                        'level': '吉',
                        'reason': '财星得用'
                    }
                else:
                    return {
                        'description': f'{dayun_ten_god}运，平稳',
                        'level': '中平',
                        'reason': '财星力量一般'
                    }
        
        # 3. 官杀运
        elif dayun_ten_god in ['正官', '偏官', '七杀']:
            if yin_zhong:
                # 印重时，官印相生，再生印不利
                if '正官' in dayun_ten_god:
                    return {
                        'description': '官印相生，事业进阶期',
                        'level': '中平',
                        'reason': '官印相生，但印已重，需注意平衡'
                    }
                else:
                    # 七杀/偏官
                    # 检查地支是否有财星（木）
                    if zhi_wx in xishen_wuxing and '木' in xishen_wuxing:
                        # 七杀坐财
                        return {
                            'description': '七杀坐财，当前大运，事业拼搏期',
                            'level': '中平',
                            'reason': '七杀有制，可用'
                        }
                    elif gan_is_xishen or zhi_is_xishen:
                        return {
                            'description': f'{dayun_ten_god}运，有机遇',
                            'level': '中平',
                            'reason': '七杀有制'
                        }
                    else:
                        return {
                            'description': f'{dayun_ten_god}运，压力较大',
                            'level': '小凶',
                            'reason': '七杀无制，压力大'
                        }
            else:
                # 印不重时，官印相生，吉
                return {
                    'description': f'{dayun_ten_god}运，事业有成',
                    'level': '吉',
                    'reason': '官印相生'
                }
        
        # 4. 印运
        elif dayun_ten_god in ['正印', '偏印']:
            if yin_zhong:
                # 印重时，再行印运，土重埋金，大忌
                if '正印' in dayun_ten_god:
                    return {
                        'description': '正印大运，土重埋金，宜守成',
                        'level': '凶',
                        'reason': '印星再重，土重埋金'
                    }
                else:
                    # 偏印
                    return {
                        'description': '偏印透干，修身养性',
                        'level': '凶',
                        'reason': '偏印透干，土火并旺'
                    }
            else:
                # 印不重时，印运可能吉
                return {
                    'description': f'{dayun_ten_god}运，学业有成',
                    'level': '吉',
                    'reason': '印星生身'
                }
        
        # 5. 比劫运
        elif dayun_ten_god in ['比肩', '劫财']:
            # 比劫帮身，中性
            if '比肩' in dayun_ten_god:
                return {
                    'description': '比肩运，平和',
                    'level': '中平',
                    'reason': '比肩帮身，平稳'
                }
            else:
                # 劫财
                # 检查是否有火旺（不利）
                if gan_is_jishen or zhi_is_jishen:
                    return {
                        'description': '劫财帮身，晚景平顺',
                        'level': '中平',
                        'reason': '比劫帮身，但有火旺'
                    }
                else:
                    return {
                        'description': f'{dayun_ten_god}运，平稳',
                        'level': '中平',
                        'reason': '比劫帮身'
                    }
        
        # 默认
        return {
            'description': f'{dayun_ten_god}运',
            'level': '中平',
            'reason': '平稳运势'
        }
    
    def _judge_by_wuxing_xiji(self,
                              gan: str,
                              zhi: str,
                              dayun_ten_god: str,
                              gan_wx: str,
                              zhi_wx: str,
                              gan_is_xishen: bool,
                              gan_is_jishen: bool,
                              zhi_is_xishen: bool,
                              zhi_is_jishen: bool) -> Dict[str, str]:
        """
        基于五行喜忌的简单判断（兜底逻辑）
        """
        # 天干透出喜神
        if gan_is_xishen and not gan_is_jishen:
            if zhi_is_xishen:
                return {
                    'description': f'{dayun_ten_god}运，运势大吉',
                    'level': '大吉',
                    'reason': '天干地支皆喜神'
                }
            else:
                return {
                    'description': f'{dayun_ten_god}运，运势较好',
                    'level': '吉',
                    'reason': '天干透出喜神'
                }
        
        # 天干透出忌神
        elif gan_is_jishen and not gan_is_xishen:
            if zhi_is_jishen:
                return {
                    'description': f'{dayun_ten_god}运，需谨慎',
                    'level': '凶',
                    'reason': '天干地支皆忌神'
                }
            else:
                return {
                    'description': f'{dayun_ten_god}运，压力较大',
                    'level': '小凶',
                    'reason': '天干透出忌神'
                }
        
        # 喜忌参半
        else:
            return {
                'description': f'{dayun_ten_god}运，平稳',
                'level': '中平',
                'reason': '喜忌参半'
            }

