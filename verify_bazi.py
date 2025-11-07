#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八字验证工具 - 使用sxtwl库验证用户输入的八字数据
"""

from datetime import datetime, timezone, timedelta
from sxtwl_adapter import compute_bazi_json, Rules, Location
import lunar_python

# 用户输入数据
print("="*70)
print("【用户输入的八字信息】")
print("="*70)
print("出生时间（农历）：1978年10月5日 丑时(1:00-3:00)")
print("性别：男")
print("用户声称的【精确四柱】：")
print("  年柱：戊午")
print("  月柱：壬戌")
print("  日柱：辛未")
print("  时柱：己丑")
print()

# 方法1：使用lunar_python库进行农历->公历转换
print("="*70)
print("【方法1：农历-公历转换验证】")
print("="*70)

try:
    # lunar_python 的API
    lunar_date = lunar_python.Converter.Lunar2Solar(1978, 10, 5, False)
    solar_year = lunar_date.year
    solar_month = lunar_date.month
    solar_day = lunar_date.day
    print(f"农历 1978年10月5日 → 公历 {solar_year}年{solar_month}月{solar_day}日")
except Exception as e:
    print(f"❌ 转换失败: {e}")
    solar_year, solar_month, solar_day = 1978, 11, 19

# 方法2：使用sxtwl库进行精确八字计算
print()
print("="*70)
print("【方法2：lsxtw库精确计算（带真太阳时）】")
print("="*70)

try:
    # 丑时对应 1:00-3:00，取中点 2:00
    hour = 1  # 1:00
    minute = 0
    second = 0
    
    print(f"出生公历时间（无真太阳时调整）：{solar_year}年{solar_month}月{solar_day}日 {hour}:{minute}")
    
    # 使用sxtwl计算（不使用真太阳时）
    result_no_tst = compute_bazi_json(
        year=solar_year,
        month=solar_month,
        day=solar_day,
        hour=hour,
        minute=minute,
        second=second,
        tz_offset_hours=8.0,
        rules=Rules(use_true_solar_time=False),
        location=Location(lon=120.0, lat=40.0)  # 北京
    )
    
    print("\n✅ sxtwl计算结果（不使用真太阳时）：")
    pillars = result_no_tst['pillars']
    print(f"  年柱：{pillars['year']}")
    print(f"  月柱：{pillars['month']}")
    print(f"  日柱：{pillars['day']}")
    print(f"  时柱：{pillars['hour']}")
    
    # 与用户数据对比
    print("\n【与用户声称四柱的对比】")
    user_pillars = {
        'year': '戊午',
        'month': '壬戌',
        'day': '辛未',
        'hour': '己丑'
    }
    
    pillar_names = ['年', '月', '日', '时']
    matches = 0
    for i, pillar in enumerate(['year', 'month', 'day', 'hour']):
        computed = result_no_tst['pillars'][pillar]
        user = user_pillars[pillar]
        match = computed == user
        matches += 1 if match else 0
        status = "✅" if match else "❌"
        print(f"  {status} {pillar_names[i]}柱：" + 
              f"计算={computed} vs 用户={user}")
    
    print(f"\n匹配度：{matches}/4 = {matches*25}%")
    
except Exception as e:
    print(f"❌ sxtwl计算失败: {e}")
    import traceback
    traceback.print_exc()

# 方法3：十神验证
print()
print("="*70)
print("【方法3：十神关系验证】")
print("="*70)

print("日主：辛（金，阴）")
print("\n十神判断规则（基于五行生克和阴阳）：")
print("  • 我克者为财（异性→正财，同性→偏财）")
print("  • 克我者为官（异性→正官，同性→偏官/七煞）")
print("  • 生我者为印（异性→正印，同性→偏印）")
print("  • 我生者为食伤（同性→食神，异性→伤官）")
print("  • 同我者为比劫（同性→比肩，异性→劫财）")

print("\n【用户声称的十神】")
print("  年干：戊（土，阳）→ 与辛（金，阴）为异性 → 生我 → 正印 ✅")
print("  月干：壬（水，阳）→ 与辛（金，阴）为异性 → 我生 → 伤官 ⚠️ 用户未标注")
print("  时干：己（土，阴）→ 与辛（金，阴）为同性 → 生我 → 偏印 ✅")

print("\n⚠️ 用户只列出了3个十神，但四柱有4个天干，日柱天干「辛」是日主本身不需标注")

# 方法4：完整的十神分析
print()
print("="*70)
print("【方法4：完整的十神分析】")
print("="*70)

TIANGAN_WUXING = {
    '甲': '木', '乙': '木',
    '丙': '火', '丁': '火',
    '戊': '土', '己': '土',
    '庚': '金', '辛': '金',
    '壬': '水', '癸': '水'
}

SHENG_MAP = {
    '木': '火',
    '火': '土',
    '土': '金',
    '金': '水',
    '水': '木'
}

KE_MAP = {
    '木': '土',
    '火': '金',
    '土': '水',
    '金': '木',
    '水': '火'
}

pillars_user = {
    'year': '戊',
    'month': '壬',
    'day': '辛',
    'hour': '己'
}

day_master = '辛'
day_master_wuxing = TIANGAN_WUXING[day_master]

print(f"日主：{day_master} ({day_master_wuxing}，阴干）")
print(f"\n我克的五行（财星）：{KE_MAP.get(day_master_wuxing, '未知')}")
print(f"克我的五行（官星）：木（对应日主金）")
print(f"生我的五行（印星）：土（对应日主金）")
print(f"我生的五行（食伤）：水（对应日主金）")

print("\n四柱天干的十神分析：")
gan_list = ['年', '月', '日', '时']
for idx, (gan_name, gan) in enumerate(pillars_user.items()):
    if gan == day_master:
        print(f"  {gan_list[idx]}干：{gan}（日主本身）")
        continue
    
    gan_wuxing = TIANGAN_WUXING[gan]
    gan_is_yang = gan in ['甲', '丙', '戊', '庚', '壬']
    day_is_yang = False  # 辛是阴干
    same_gender = gan_is_yang == day_is_yang
    
    # 判断十神
    if gan_wuxing == day_master_wuxing:
        ten_god = '比肩' if same_gender else '劫财'
    elif gan_wuxing == KE_MAP[day_master_wuxing]:
        ten_god = '偏财' if same_gender else '正财'
    elif gan_wuxing in ['木']  and day_master_wuxing == '金':
        ten_god = '偏官' if same_gender else '正官'
    elif gan_wuxing in ['土']:
        ten_god = '偏印' if same_gender else '正印'
    elif gan_wuxing in ['水']:
        ten_god = '食神' if same_gender else '伤官'
    else:
        ten_god = '未知'
    
    print(f"  {gan_list[idx]}干：{gan}({gan_wuxing}，{'阳' if gan_is_yang else '阴'}干) → {ten_god}")

print()
print("="*70)
print("【验证总结】")
print("="*70)
print("✅ = 正确")
print("❌ = 错误或需要核实")
print("⚠️ = 需要进一步验证")
