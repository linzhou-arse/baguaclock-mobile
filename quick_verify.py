#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速验证工具：一键验证大运分析是否正确
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chinese_metaphysics_library.core.data_structures import BaziData
from chinese_metaphysics_library.santonghui.dayun_analyzer import DayunAnalyzer

# 测试用例：1978年11月5日丑时 男命
bazi_data = BaziData(
    year=('戊', '午'),
    month=('壬', '戌'),
    day=('辛', '未'),
    hour=('己', '丑'),
    birth_year=1978,
    birth_month=11,
    birth_day=5,
    birth_hour=1,
    gender='男'
)

analyzer = DayunAnalyzer()
result = analyzer.analyze(bazi_data)

print("=" * 80)
print("大运分析快速验证")
print("=" * 80)
print()

# 验证1：起运年龄
qiyun_age = result.details.get('qiyun_age')
print(f"✅ 起运年龄：{qiyun_age}岁（预期：1.0岁）" if qiyun_age == 1.0 else f"❌ 起运年龄：{qiyun_age}岁（预期：1.0岁）")

# 验证2：大运方向
direction = result.details.get('direction')
print(f"✅ 大运方向：{direction}（预期：顺行）" if direction == '顺行' else f"❌ 大运方向：{direction}（预期：顺行）")

# 验证3：首步大运
dayun_pillars = result.details.get('dayun_pillars', [])
if len(dayun_pillars) > 0:
    gan, zhi = dayun_pillars[0]
    start_age = int(qiyun_age)
    end_age = int(qiyun_age + 9)
    start_year = 1978 + start_age
    end_year = 1978 + end_age
    
    expected = "癸亥 1~10岁 (1979-1988年)"
    actual = f"{gan}{zhi} {start_age}~{end_age}岁 ({start_year}-{end_year}年)"
    
    if actual == expected:
        print(f"✅ 首步大运：{actual}")
    else:
        print(f"❌ 首步大运：{actual}（预期：{expected}）")

# 验证4：吉凶判断
print()
print("大运吉凶判断（前5步）：")
for i, pillar in enumerate(dayun_pillars[:5], start=1):
    gan, zhi = pillar
    start_age = qiyun_age + (i - 1) * 10
    end_age = start_age + 9
    
    day_master = bazi_data.day[0]
    jixiong_info = analyzer._judge_single_dayun_xiji(
        gan, zhi, day_master,
        xishen_wuxing=None,
        jishen_wuxing=None,
        pillars=None,
        yongshen_method=None
    )
    
    xiji = jixiong_info.get('xiji', '平')
    level = jixiong_info.get('level', '平运')
    
    print(f"  {i}. {gan}{zhi} {int(start_age)}~{int(end_age)}岁 → {xiji}({level})")

print()
print("=" * 80)
print("验证完成！")
print("=" * 80)

