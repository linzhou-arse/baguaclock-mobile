#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
八字分析全面测试脚本 v2.0
测试内容：
1. 各年龄段（0-20, 21-40, 41-60, 61-80, 81+）
2. 男女各20人，共40个测试用例
3. 含各种命格（财格、官格、印格、食伤格、比劫格等）
4. 各种不同的时运（顺行、逆行、不同起运年龄）
5. 五行全的、五行各种缺的（缺木、缺火、缺土、缺金、缺水）
6. 含闰月情况
7. 检查硬编码、内容差异、准确性
"""

import sys
import io
import json
import os
from datetime import datetime
from collections import defaultdict

# 设置输出编码为UTF-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

# 导入必要的模块
ANALYZER_AVAILABLE = False
try:
    from local_mingli_analyzer import LocalMingliAnalyzer
    print("✅ LocalMingliAnalyzer 导入成功")
    ANALYZER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ LocalMingliAnalyzer 导入失败: {e}")
    import traceback
    traceback.print_exc()

# 测试用例配置 - 精心设计覆盖各种情况
TEST_CASES = [
    # ========== 年龄段0-20（2004-2024年出生）==========
    # 男性10个
    {'name': '测试01男_财格', 'gender': '男', 'year': 2010, 'month': 3, 'day': 15, 'hour': 7, 'is_leap': False, 'target': '财格'},
    {'name': '测试02男_官格', 'gender': '男', 'year': 2012, 'month': 6, 'day': 20, 'hour': 14, 'is_leap': False, 'target': '官格'},
    {'name': '测试03男_印格', 'gender': '男', 'year': 2015, 'month': 9, 'day': 10, 'hour': 21, 'is_leap': False, 'target': '印格'},
    {'name': '测试04男_食伤格', 'gender': '男', 'year': 2017, 'month': 12, 'day': 25, 'hour': 3, 'is_leap': False, 'target': '食伤格'},
    {'name': '测试05男_比劫格', 'gender': '男', 'year': 2020, 'month': 2, 'day': 5, 'hour': 9, 'is_leap': False, 'target': '比劫格'},
    {'name': '测试06男_五行全', 'gender': '男', 'year': 2011, 'month': 4, 'day': 18, 'hour': 11, 'is_leap': False, 'target': '五行全'},
    {'name': '测试07男_缺木', 'gender': '男', 'year': 2013, 'month': 7, 'day': 22, 'hour': 17, 'is_leap': False, 'target': '缺木'},
    {'name': '测试08男_缺火', 'gender': '男', 'year': 2016, 'month': 10, 'day': 8, 'hour': 1, 'is_leap': False, 'target': '缺火'},
    {'name': '测试09男_缺金', 'gender': '男', 'year': 2018, 'month': 1, 'day': 12, 'hour': 13, 'is_leap': False, 'target': '缺金'},
    {'name': '测试10男_闰月', 'gender': '男', 'year': 2020, 'month': 4, 'day': 15, 'hour': 19, 'is_leap': True, 'target': '闰月'},  # 2020年闰4月
    
    # 女性10个
    {'name': '测试11女_财格', 'gender': '女', 'year': 2009, 'month': 5, 'day': 14, 'hour': 7, 'is_leap': False, 'target': '财格'},
    {'name': '测试12女_官格', 'gender': '女', 'year': 2011, 'month': 8, 'day': 19, 'hour': 14, 'is_leap': False, 'target': '官格'},
    {'name': '测试13女_印格', 'gender': '女', 'year': 2014, 'month': 11, 'day': 9, 'hour': 21, 'is_leap': False, 'target': '印格'},
    {'name': '测试14女_食伤格', 'gender': '女', 'year': 2016, 'month': 2, 'day': 24, 'hour': 3, 'is_leap': False, 'target': '食伤格'},
    {'name': '测试15女_比劫格', 'gender': '女', 'year': 2019, 'month': 5, 'day': 4, 'hour': 9, 'is_leap': False, 'target': '比劫格'},
    {'name': '测试16女_五行全', 'gender': '女', 'year': 2010, 'month': 6, 'day': 17, 'hour': 11, 'is_leap': False, 'target': '五行全'},
    {'name': '测试17女_缺土', 'gender': '女', 'year': 2012, 'month': 9, 'day': 21, 'hour': 17, 'is_leap': False, 'target': '缺土'},
    {'name': '测试18女_缺水', 'gender': '女', 'year': 2015, 'month': 12, 'day': 7, 'hour': 1, 'is_leap': False, 'target': '缺水'},
    {'name': '测试19女_缺多行', 'gender': '女', 'year': 2017, 'month': 3, 'day': 11, 'hour': 13, 'is_leap': False, 'target': '缺多行'},
    {'name': '测试20女_闰月', 'gender': '女', 'year': 1976, 'month': 8, 'day': 25, 'hour': 19, 'is_leap': True, 'target': '闰月'},  # 1976年闰8月
    
    # ========== 年龄段21-40（1984-2003年出生）==========
    # 男性10个
    {'name': '测试21男_财官格', 'gender': '男', 'year': 1990, 'month': 5, 'day': 12, 'hour': 7, 'is_leap': False, 'target': '财官格'},
    {'name': '测试22男_官印格', 'gender': '男', 'year': 1992, 'month': 8, 'day': 16, 'hour': 14, 'is_leap': False, 'target': '官印格'},
    {'name': '测试23男_食伤生财', 'gender': '男', 'year': 1995, 'month': 11, 'day': 6, 'hour': 21, 'is_leap': False, 'target': '食伤生财'},
    {'name': '测试24男_从财格', 'gender': '男', 'year': 1997, 'month': 2, 'day': 20, 'hour': 3, 'is_leap': False, 'target': '从财格'},
    {'name': '测试25男_从官格', 'gender': '男', 'year': 2000, 'month': 6, 'day': 3, 'hour': 9, 'is_leap': False, 'target': '从官格'},
    {'name': '测试26男_五行全', 'gender': '男', 'year': 1991, 'month': 4, 'day': 15, 'hour': 11, 'is_leap': False, 'target': '五行全'},
    {'name': '测试27男_缺木', 'gender': '男', 'year': 1993, 'month': 7, 'day': 19, 'hour': 17, 'is_leap': False, 'target': '缺木'},
    {'name': '测试28男_缺火', 'gender': '男', 'year': 1996, 'month': 10, 'day': 5, 'hour': 1, 'is_leap': False, 'target': '缺火'},
    {'name': '测试29男_缺金', 'gender': '男', 'year': 1998, 'month': 1, 'day': 9, 'hour': 13, 'is_leap': False, 'target': '缺金'},
    {'name': '测试30男_闰月', 'gender': '男', 'year': 2000, 'month': 4, 'day': 22, 'hour': 19, 'is_leap': True, 'target': '闰月'},  # 2000年闰4月
    
    # 女性10个
    {'name': '测试31女_财官格', 'gender': '女', 'year': 1989, 'month': 5, 'day': 11, 'hour': 7, 'is_leap': False, 'target': '财官格'},
    {'name': '测试32女_官印格', 'gender': '女', 'year': 1991, 'month': 8, 'day': 15, 'hour': 14, 'is_leap': False, 'target': '官印格'},
    {'name': '测试33女_食伤生财', 'gender': '女', 'year': 1994, 'month': 11, 'day': 5, 'hour': 21, 'is_leap': False, 'target': '食伤生财'},
    {'name': '测试34女_从财格', 'gender': '女', 'year': 1996, 'month': 2, 'day': 19, 'hour': 3, 'is_leap': False, 'target': '从财格'},
    {'name': '测试35女_从官格', 'gender': '女', 'year': 1999, 'month': 6, 'day': 2, 'hour': 9, 'is_leap': False, 'target': '从官格'},
    {'name': '测试36女_五行全', 'gender': '女', 'year': 1990, 'month': 4, 'day': 14, 'hour': 11, 'is_leap': False, 'target': '五行全'},
    {'name': '测试37女_缺土', 'gender': '女', 'year': 1992, 'month': 7, 'day': 18, 'hour': 17, 'is_leap': False, 'target': '缺土'},
    {'name': '测试38女_缺水', 'gender': '女', 'year': 1995, 'month': 10, 'day': 4, 'hour': 1, 'is_leap': False, 'target': '缺水'},
    {'name': '测试39女_缺多行', 'gender': '女', 'year': 1997, 'month': 1, 'day': 8, 'hour': 13, 'is_leap': False, 'target': '缺多行'},
    {'name': '测试40女_闰月', 'gender': '女', 'year': 1979, 'month': 6, 'day': 10, 'hour': 19, 'is_leap': True, 'target': '闰月'},  # 1979年闰6月
    
    # ========== 年龄段41-60（1964-1983年出生）==========
    # 男性10个
    {'name': '测试41男_特殊格局', 'gender': '男', 'year': 1970, 'month': 1, 'day': 15, 'hour': 7, 'is_leap': False, 'target': '特殊格局'},
    {'name': '测试42男_身强', 'gender': '男', 'year': 1972, 'month': 4, 'day': 19, 'hour': 14, 'is_leap': False, 'target': '身强'},
    {'name': '测试43男_身弱', 'gender': '男', 'year': 1975, 'month': 7, 'day': 9, 'hour': 21, 'is_leap': False, 'target': '身弱'},
    {'name': '测试44男_中和', 'gender': '男', 'year': 1977, 'month': 10, 'day': 23, 'hour': 3, 'is_leap': False, 'target': '中和'},
    {'name': '测试45男_太旺', 'gender': '男', 'year': 1980, 'month': 2, 'day': 6, 'hour': 9, 'is_leap': False, 'target': '太旺'},
    {'name': '测试46男_五行全', 'gender': '男', 'year': 1971, 'month': 5, 'day': 13, 'hour': 11, 'is_leap': False, 'target': '五行全'},
    {'name': '测试47男_缺木', 'gender': '男', 'year': 1973, 'month': 8, 'day': 17, 'hour': 17, 'is_leap': False, 'target': '缺木'},
    {'name': '测试48男_缺火', 'gender': '男', 'year': 1976, 'month': 11, 'day': 3, 'hour': 1, 'is_leap': False, 'target': '缺火'},
    {'name': '测试49男_缺金', 'gender': '男', 'year': 1978, 'month': 2, 'day': 7, 'hour': 13, 'is_leap': False, 'target': '缺金'},
    {'name': '测试50男_闰月', 'gender': '男', 'year': 1960, 'month': 6, 'day': 5, 'hour': 19, 'is_leap': True, 'target': '闰月'},  # 1960年闰6月
    
    # 女性10个
    {'name': '测试51女_特殊格局', 'gender': '女', 'year': 1969, 'month': 1, 'day': 14, 'hour': 7, 'is_leap': False, 'target': '特殊格局'},
    {'name': '测试52女_身强', 'gender': '女', 'year': 1971, 'month': 4, 'day': 18, 'hour': 14, 'is_leap': False, 'target': '身强'},
    {'name': '测试53女_身弱', 'gender': '女', 'year': 1974, 'month': 7, 'day': 8, 'hour': 21, 'is_leap': False, 'target': '身弱'},
    {'name': '测试54女_中和', 'gender': '女', 'year': 1976, 'month': 10, 'day': 22, 'hour': 3, 'is_leap': False, 'target': '中和'},
    {'name': '测试55女_太旺', 'gender': '女', 'year': 1979, 'month': 2, 'day': 5, 'hour': 9, 'is_leap': False, 'target': '太旺'},
    {'name': '测试56女_五行全', 'gender': '女', 'year': 1970, 'month': 5, 'day': 12, 'hour': 11, 'is_leap': False, 'target': '五行全'},
    {'name': '测试57女_缺土', 'gender': '女', 'year': 1972, 'month': 8, 'day': 16, 'hour': 17, 'is_leap': False, 'target': '缺土'},
    {'name': '测试58女_缺水', 'gender': '女', 'year': 1975, 'month': 11, 'day': 2, 'hour': 1, 'is_leap': False, 'target': '缺水'},
    {'name': '测试59女_缺多行', 'gender': '女', 'year': 1977, 'month': 2, 'day': 6, 'hour': 13, 'is_leap': False, 'target': '缺多行'},
    {'name': '测试60女_闰月', 'gender': '女', 'year': 1976, 'month': 8, 'day': 9, 'hour': 19, 'is_leap': True, 'target': '闰月'},  # 1976年闰8月
    
]

def calculate_bazi_pillars(year, month, day, hour, is_leap=False):
    """直接计算八字四柱（不使用GUI）"""
    try:
        from lunar_python import Lunar, Solar
        
        # 转换时辰到具体时间
        hour_map = {
            1: (23, 30), 3: (1, 30), 5: (3, 30), 7: (5, 30), 9: (7, 30), 11: (9, 30),
            13: (11, 30), 15: (13, 30), 17: (15, 30), 19: (17, 30), 21: (19, 30), 23: (21, 30)
        }
        input_hour, input_minute = hour_map.get(hour, (1, 30))
        
        # ✅ 修复：处理闰月（先检查年份是否有该闰月）
        lunar_month = month
        if is_leap:
            # 检查该年份是否有这个闰月
            try:
                # 尝试创建闰月，如果失败说明该年份没有这个闰月
                test_lunar = Lunar.fromYmdHms(year, -month, 1, 0, 0, 0)
                lunar_month = -month  # 有闰月，使用负数
            except Exception:
                # 该年份没有这个闰月，使用正常月份
                print(f"  ⚠️ {year}年没有闰{month}月，使用正常{month}月")
                lunar_month = month
                is_leap = False  # 修正is_leap标志
        
        lunar = Lunar.fromYmdHms(year, lunar_month, day, input_hour, input_minute, 0)
        
        solar = lunar.getSolar()
        
        # 获取四柱
        year_gan_zhi = lunar.getYearInGanZhi()
        month_gan_zhi = lunar.getMonthInGanZhi()
        day_gan_zhi = lunar.getDayInGanZhi()
        hour_gan_zhi = lunar.getTimeInGanZhi()
        
        pillars = {
            'year': year_gan_zhi,
            'month': month_gan_zhi,
            'day': day_gan_zhi,
            'hour': hour_gan_zhi
        }
        
        # ✅ 修复：提取月柱干支信息
        month_gan = month_gan_zhi[0] if len(month_gan_zhi) >= 1 else ''
        month_zhi = month_gan_zhi[1] if len(month_gan_zhi) >= 2 else ''
        year_gan = year_gan_zhi[0] if len(year_gan_zhi) >= 1 else ''
        
        birth_info = {
            'year': year,
            'month': month,
            'day': day,
            'hour': hour,
            'gender': None,  # 稍后设置
            'solar_year': solar.getYear(),
            'solar_month': solar.getMonth(),
            'solar_day': solar.getDay(),
            'lunar_month': month,
            'lunar_day': day,
            'is_leap': is_leap,
            # ✅ 修复：添加月柱和年干信息，用于大运计算
            'month_gan': month_gan,
            'month_zhi': month_zhi,
            'year_gan': year_gan,
            'pillars': {
                'year': [year_gan_zhi[0], year_gan_zhi[1]] if len(year_gan_zhi) >= 2 else ['', ''],
                'month': [month_gan, month_zhi],
                'day': [day_gan_zhi[0], day_gan_zhi[1]] if len(day_gan_zhi) >= 2 else ['', ''],
                'hour': [hour_gan_zhi[0], hour_gan_zhi[1]] if len(hour_gan_zhi) >= 2 else ['', '']
            }
        }
        
        return pillars, birth_info
        
    except Exception as e:
        print(f"  ⚠️ 计算四柱失败: {e}")
        return None, None

def analyze_bazi_case(analyzer, case):
    """分析单个八字案例"""
    try:
        # 直接计算四柱
        pillars, birth_info = calculate_bazi_pillars(
            year=case['year'],
            month=case['month'],
            day=case['day'],
            hour=case['hour'],
            is_leap=case.get('is_leap', False)
        )
        
        if not pillars:
            return None
        
        # 设置性别
        if birth_info:
            birth_info['gender'] = case['gender']
        
        # 转换四柱格式（从字符串转为列表）
        pillars_dict = {
            'year': [pillars['year'][0], pillars['year'][1]],
            'month': [pillars['month'][0], pillars['month'][1]],
            'day': [pillars['day'][0], pillars['day'][1]],
            'hour': [pillars['hour'][0], pillars['hour'][1]]
        }
        
        # 进行完整分析
        analysis_result = analyzer.analyze_bazi(
            pillars=pillars_dict,
            gender=case['gender'],
            birth_info=birth_info
        )
        
        return {
            'case': case,
            'pillars': {
                'year': pillars['year'],
                'month': pillars['month'],
                'day': pillars['day'],
                'hour': pillars['hour']
            },
            'analysis': analysis_result,
            'bazi_result': {'birth_info': birth_info}
        }
        
    except Exception as e:
        print(f"❌ 分析失败 {case['name']}: {e}")
        import traceback
        traceback.print_exc()
        return None

def extract_key_info(analysis_result):
    """提取关键信息用于对比"""
    if not isinstance(analysis_result, dict):
        return {}
    
    key_info = {}
    
    # 提取五行分布（注意：local_mingli_analyzer返回的是count和percent）
    if 'wuxing_analysis' in analysis_result:
        wuxing = analysis_result['wuxing_analysis']
        if isinstance(wuxing, dict):
            # 提取五行计数和百分比
            wuxing_count = wuxing.get('count', {})
            wuxing_percent = wuxing.get('percent', {})
            key_info['wuxing_count'] = str(sorted(wuxing_count.items())) if wuxing_count else '{}'
            key_info['wuxing_percent'] = str(sorted(wuxing_percent.items())) if wuxing_percent else '{}'
            key_info['wuxing_missing'] = str(sorted(wuxing.get('missing', [])))
            key_info['wuxing_strong'] = str(sorted(wuxing.get('strong', [])))
    
    # 提取十神分布（✅ 修复：使用count字段，不是distribution）
    if 'shishen_analysis' in analysis_result:
        shishen = analysis_result['shishen_analysis']
        if isinstance(shishen, dict):
            # ✅ 修复：analyze_shishen返回的是count字段，不是distribution
            distribution = shishen.get('count', shishen.get('distribution', {}))
            if distribution:
                key_info['shishen_distribution'] = str(sorted(distribution.items()))
            else:
                key_info['shishen_distribution'] = '{}'
    
    # 提取格局
    if 'geju_analysis' in analysis_result:
        geju = analysis_result['geju_analysis']
        if isinstance(geju, dict):
            key_info['geju_type'] = geju.get('pattern_type', '') or geju.get('pattern', '') or geju.get('type', '')
            key_info['geju_description'] = geju.get('description', '') or geju.get('summary', '')
    
    # 提取旺衰
    if 'wangshuai_analysis' in analysis_result:
        wangshuai = analysis_result['wangshuai_analysis']
        if isinstance(wangshuai, dict):
            key_info['strength_level'] = wangshuai.get('strength_level', '') or wangshuai.get('level', '')
            key_info['strength_ratio'] = wangshuai.get('strength_ratio', 0) or wangshuai.get('ratio', 0)
    
    # 提取财运
    if 'career_wealth' in analysis_result:
        career = analysis_result['career_wealth']
        if isinstance(career, dict):
            key_info['wealth_level'] = career.get('wealth_level', '')
            key_info['wealth_score'] = career.get('wealth_score', 0)
    
    # 提取婚姻
    if 'marriage' in analysis_result:
        marriage = analysis_result['marriage']
        if isinstance(marriage, dict):
            key_info['marriage_quality'] = marriage.get('quality', '')
    
    # 提取健康
    if 'health' in analysis_result:
        health = analysis_result['health']
        if isinstance(health, dict):
            key_info['health_risk'] = health.get('risk_level', '') or health.get('level', '')
    
    # 检查大运硬编码（检查是否使用固定模式）
    if 'dayun' in analysis_result:
        dayun = analysis_result['dayun']
        if isinstance(dayun, dict):
            dayun_info = dayun.get('info', '')
            # 检查是否包含固定的干支组合
            key_info['dayun_has_fixed'] = '甲子' in dayun_info and '乙丑' in dayun_info and '丙寅' in dayun_info
    
    # 提取报告文本的关键片段
    if 'local_analysis_text' in analysis_result:
        text = analysis_result['local_analysis_text']
        if isinstance(text, str):
            # 提取关键段落
            key_info['has_wuxing'] = '五行' in text
            key_info['has_shishen'] = '十神' in text
            key_info['has_geju'] = '格局' in text
            key_info['has_marriage'] = '婚姻' in text
            key_info['has_health'] = '健康' in text
            key_info['text_length'] = len(text)
            # 提取前200字符作为标识（增加长度以便更准确对比）
            key_info['text_preview'] = text[:200] if len(text) > 200 else text
            # 提取关键数值（如财运评分、格局评分等）
            import re
            wealth_score_match = re.search(r'财富评分[：:]\s*(\d+\.?\d*)', text)
            if wealth_score_match:
                key_info['text_wealth_score'] = wealth_score_match.group(1)
    
    return key_info

def check_hardcoded_values(results):
    """检查是否有硬编码值"""
    print("\n" + "="*80)
    print("🔍 检查硬编码值")
    print("="*80)
    
    # 检查所有结果中的关键字段是否相同
    identical_items = defaultdict(list)
    
    for result in results:
        if not result:
            continue
        
        key_info = extract_key_info(result['analysis'])
        
        # 检查各项是否完全相同
        for key, value in key_info.items():
            if key in ['text_preview', 'text_length']:
                continue  # 文本长度和预览可能不同
            value_str = str(value)
            identical_items[value_str].append((result['case']['name'], key))
    
    # 找出完全相同的结果
    hardcoded_suspicious = []
    for value_str, items in identical_items.items():
        if len(items) > 1:
            # 有多个案例使用相同的值
            unique_cases = set([item[0] for item in items])
            if len(unique_cases) > 1:
                hardcoded_suspicious.append({
                    'value': value_str,
                    'field': items[0][1],
                    'cases': list(unique_cases),
                    'count': len(items)
                })
    
    if hardcoded_suspicious:
        print("\n⚠️ 发现可能的硬编码值（多个案例使用相同值）：")
        # 按数量排序，显示最多的
        hardcoded_suspicious.sort(key=lambda x: x['count'], reverse=True)
        for item in hardcoded_suspicious[:15]:  # 显示前15个
            print(f"  - 字段 '{item['field']}' = '{item['value']}'")
            print(f"    出现在 {item['count']} 个案例中: {', '.join(item['cases'][:5])}")
            if len(item['cases']) > 5:
                print(f"    ... 还有 {len(item['cases'])-5} 个案例")
    else:
        print("✅ 未发现明显的硬编码值（所有案例的关键字段都有差异）")
    
    return hardcoded_suspicious

def check_content_differences(results):
    """检查内容是否不同"""
    print("\n" + "="*80)
    print("🔍 检查内容差异")
    print("="*80)
    
    identical_reports = []
    
    for i, result1 in enumerate(results):
        if not result1:
            continue
        
        for j, result2 in enumerate(results[i+1:], start=i+1):
            if not result2:
                continue
            
            key_info1 = extract_key_info(result1['analysis'])
            key_info2 = extract_key_info(result2['analysis'])
            
            # 比较关键字段
            differences = []
            for key in key_info1:
                if key in ['text_preview', 'text_length']:
                    continue
                if key_info1.get(key) != key_info2.get(key):
                    differences.append(key)
            
            # 如果完全相同（除了文本长度）
            if len(differences) == 0:
                identical_reports.append({
                    'case1': result1['case']['name'],
                    'case2': result2['case']['name'],
                    'pillars1': result1['pillars'],
                    'pillars2': result2['pillars']
                })
    
    if identical_reports:
        print(f"\n⚠️ 发现 {len(identical_reports)} 对完全相同的分析报告：")
        for item in identical_reports[:10]:  # 显示前10对
            print(f"  - {item['case1']} vs {item['case2']}")
            print(f"    四柱1: {item['pillars1']}")
            print(f"    四柱2: {item['pillars2']}")
    else:
        print("✅ 所有分析报告都有差异（这是正常的）")
    
    return identical_reports

def check_coverage(results):
    """检查测试覆盖率"""
    print("\n" + "="*80)
    print("📊 测试覆盖率检查")
    print("="*80)
    
    # 统计各种类型
    geju_types = defaultdict(int)
    strength_levels = defaultdict(int)
    wealth_levels = defaultdict(int)
    marriage_qualities = defaultdict(int)
    health_risks = defaultdict(int)
    wuxing_missing_count = defaultdict(int)
    
    for result in results:
        if not result:
            continue
        
        key_info = extract_key_info(result['analysis'])
        
        geju_types[key_info.get('geju_type', '')] += 1
        strength_levels[key_info.get('strength_level', '')] += 1
        wealth_levels[key_info.get('wealth_level', '')] += 1
        marriage_qualities[key_info.get('marriage_quality', '')] += 1
        health_risks[key_info.get('health_risk', '')] += 1
        
        # 统计五行缺失情况
        missing = key_info.get('wuxing_missing', '[]')
        if missing == '[]':
            wuxing_missing_count['五行全'] += 1
        else:
            wuxing_missing_count[f'缺{missing}'] += 1
    
    print("\n📈 格局类型分布：")
    for geju, count in sorted(geju_types.items(), key=lambda x: x[1], reverse=True):
        if geju:
            print(f"  - {geju}: {count} 个")
    
    print("\n📈 身强身弱分布：")
    for strength, count in sorted(strength_levels.items(), key=lambda x: x[1], reverse=True):
        if strength:
            print(f"  - {strength}: {count} 个")
    
    print("\n📈 财运等级分布：")
    for wealth, count in sorted(wealth_levels.items(), key=lambda x: x[1], reverse=True):
        if wealth:
            print(f"  - {wealth}: {count} 个")
    
    print("\n📈 婚姻质量分布：")
    for marriage, count in sorted(marriage_qualities.items(), key=lambda x: x[1], reverse=True):
        if marriage:
            print(f"  - {marriage}: {count} 个")
    
    print("\n📈 健康风险分布：")
    for health, count in sorted(health_risks.items(), key=lambda x: x[1], reverse=True):
        if health:
            print(f"  - {health}: {count} 个")
    
    print("\n📈 五行缺失分布：")
    for missing, count in sorted(wuxing_missing_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {missing}: {count} 个")

def generate_test_report(results):
    """生成测试报告"""
    print("\n" + "="*80)
    print("📊 测试报告汇总")
    print("="*80)
    
    successful = [r for r in results if r is not None]
    failed = [r for r in results if r is None]
    
    print(f"\n✅ 成功分析: {len(successful)} 个")
    print(f"❌ 失败分析: {len(failed)} 个")
    
    # 统计关键信息
    if successful:
        print("\n📈 关键信息统计：")
        
        # 五行分布统计
        wuxing_types = defaultdict(int)
        geju_types = defaultdict(int)
        strength_levels = defaultdict(int)
        wealth_levels = defaultdict(int)
        
        for result in successful:
            key_info = extract_key_info(result['analysis'])
            
            if 'geju_type' in key_info:
                geju_types[key_info['geju_type']] += 1
            if 'strength_level' in key_info:
                strength_levels[key_info['strength_level']] += 1
            if 'wealth_level' in key_info:
                wealth_levels[key_info['wealth_level']] += 1
        
        print(f"\n  格局类型分布：")
        for geju, count in sorted(geju_types.items(), key=lambda x: x[1], reverse=True):
            if geju:
                print(f"    - {geju}: {count} 个")
        
        print(f"\n  身强身弱分布：")
        for strength, count in sorted(strength_levels.items(), key=lambda x: x[1], reverse=True):
            if strength:
                print(f"    - {strength}: {count} 个")
        
        print(f"\n  财运等级分布：")
        for wealth, count in sorted(wealth_levels.items(), key=lambda x: x[1], reverse=True):
            if wealth:
                print(f"    - {wealth}: {count} 个")
    
    # 保存详细报告
    report_file = f"bazi_test_report_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            # 只保存关键信息，避免文件过大
            report_data = {
                'test_time': datetime.now().isoformat(),
                'total_cases': len(results),
                'successful': len(successful),
                'failed': len(failed),
                'results': []
            }
            
            for result in successful[:20]:  # 只保存前20个详细结果
                report_data['results'].append({
                    'name': result['case']['name'],
                    'gender': result['case']['gender'],
                    'target': result['case'].get('target', ''),
                    'birth_date': f"{result['case']['year']}-{result['case']['month']}-{result['case']['day']}",
                    'pillars': result['pillars'],
                    'key_info': extract_key_info(result['analysis'])
                })
            
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        print(f"\n💾 详细报告已保存到: {report_file}")
    except Exception as e:
        print(f"⚠️ 保存报告失败: {e}")

def main():
    """主测试函数"""
    print("="*80)
    print("八字分析全面测试 v2.0")
    print("="*80)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试用例数: {len(TEST_CASES)} 个（男女各20个）")
    print(f"测试目标: 各种命格、时运、五行情况、闰月")
    
    if not ANALYZER_AVAILABLE:
        print("❌ 无法导入分析器，测试终止")
        print("请检查 local_mingli_analyzer.py 是否存在")
        return
    
    # 初始化分析器
    try:
        analyzer = LocalMingliAnalyzer()
        print("✅ 分析器初始化成功")
    except Exception as e:
        print(f"❌ 分析器初始化失败: {e}")
        return
    
    # 执行测试
    all_results = []
    
    print("\n" + "="*80)
    print("开始测试...")
    print("="*80)
    
    for i, case in enumerate(TEST_CASES, 1):
        target_info = case.get('target', '')
        print(f"\n[{i}/{len(TEST_CASES)}] 测试 {case['name']} ({target_info})...")
        result = analyze_bazi_case(analyzer, case)
        all_results.append(result)
        if result:
            pillars = result['pillars']
            print(f"  ✅ 成功: 四柱 = {pillars['year']} {pillars['month']} {pillars['day']} {pillars['hour']}")
        else:
            print(f"  ❌ 失败")
    
    # 检查硬编码
    hardcoded_items = check_hardcoded_values(all_results)
    
    # 检查内容差异
    identical_items = check_content_differences(all_results)
    
    # 检查覆盖率
    check_coverage(all_results)
    
    # 生成报告
    generate_test_report(all_results)
    
    # 总结
    print("\n" + "="*80)
    print("📋 测试总结")
    print("="*80)
    print(f"✅ 成功分析: {sum(1 for r in all_results if r)} 个")
    print(f"❌ 失败分析: {sum(1 for r in all_results if r is None)} 个")
    print(f"⚠️ 硬编码可疑项: {len(hardcoded_items)} 个")
    print(f"⚠️ 完全相同报告: {len(identical_items)} 对")
    
    if len(hardcoded_items) == 0 and len(identical_items) == 0:
        print("\n🎉 测试通过！未发现明显的硬编码问题，所有分析结果都有差异。")
    else:
        print("\n⚠️ 发现潜在问题，请检查上述报告。")

if __name__ == '__main__':
    main()

