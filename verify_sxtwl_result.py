#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lunar_python import Lunar, Solar
import sxtwl

print("="*80)
print("【权威验证：农历1978年10月5日丑时的精确四柱】")
print("="*80)

year = 1978
month = 10
day = 5
hour_index = 1

print(f"\n用户输入：农历 {year}年{month}月{day}日 丑时(1:00-3:00)")
print(f"用户声称的四柱：戊午 壬戌 辛未 己丑")

# 步骤1：农历转公历
print(f"\n【步骤1】农历转公历转换")
print("="*80)

hour_map = {0: (23, 30), 1: (1, 30), 2: (3, 30), 3: (5, 30), 4: (7, 30), 5: (9, 30),
           6: (11, 30), 7: (13, 30), 8: (15, 30), 9: (17, 30), 10: (19, 30), 11: (21, 30)}

input_hour, input_minute = hour_map.get(hour_index, (1, 30))

lunar = Lunar.fromYmdHms(year, month, day, input_hour, input_minute, 0)
solar = lunar.getSolar()

solar_year = solar.getYear()
solar_month = solar.getMonth()
solar_day = solar.getDay()

print(f"农历 {year}年{month}月{day}日 {input_hour}:{input_minute:02d}")
print(f"  ↓ (使用lunar_python库转换)")
print(f"公历 {solar_year}年{solar_month}月{solar_day}日 {input_hour}:{input_minute:02d}")

# 步骤2：使用sxtwl计算四柱
print(f"\n【步骤2】使用sxtwl库精确计算四柱")
print("="*80)

day_obj = sxtwl.fromSolar(solar_year, solar_month, solar_day)

year_gz = day_obj.getYearGZ()
month_gz = day_obj.getMonthGZ()
day_gz = day_obj.getDayGZ()
hour_gz = day_obj.getHourGZ(input_hour)

TIANGAN = "甲乙丙丁戊己庚辛壬癸"
DIZHI = "子丑寅卯辰巳午未申酉戌亥"

year_pillar = f"{TIANGAN[year_gz.tg]}{DIZHI[year_gz.dz]}"
month_pillar = f"{TIANGAN[month_gz.tg]}{DIZHI[month_gz.dz]}"
day_pillar = f"{TIANGAN[day_gz.tg]}{DIZHI[day_gz.dz]}"
hour_pillar = f"{TIANGAN[hour_gz.tg]}{DIZHI[hour_gz.dz]}"

print(f"sxtwl计算结果：")
print(f"  年柱：{year_pillar}")
print(f"  月柱：{month_pillar}")
print(f"  日柱：{day_pillar}")
print(f"  时柱：{hour_pillar}")

# 步骤3：对比
print(f"\n【步骤3】与用户声称的四柱对比")
print("="*80)

user_pillars = ['戊午', '壬戌', '辛未', '己丑']
computed_pillars = [year_pillar, month_pillar, day_pillar, hour_pillar]
pillar_names = ['年柱', '月柱', '日柱', '时柱']

print(f"\n{'柱次':<6} {'用户声称':<10} {'sxtwl计算':<10} {'一致?':<8}")
print("-" * 40)

matches = 0
for i, name in enumerate(pillar_names):
    is_match = user_pillars[i] == computed_pillars[i]
    matches += 1 if is_match else 0
    symbol = "✅" if is_match else "❌"
    print(f"{name:<6} {user_pillars[i]:<10} {computed_pillars[i]:<10} {symbol:<8}")

print(f"\n总体匹配度：{matches}/4 = {matches*25}%")

# 步骤4
print(f"\n【步骤4】sxtwl库的权威性说明")
print("="*80)
print("""
sxtwl库是业界标准的八字计算库，采用的规则：
  • 年柱：以立春为岁首（节气定年）
  • 月柱：以节气中气为月首（定气月）
  • 日柱：以午夜子时为日首
  • 时柱：根据小时精确推算

如果其他软件得到不同结果，可能原因：
  1. 使用了孟春正月（比sxtwl晚）
  2. 使用了朔气月而非定气月
  3. 手工排盘有计算错误
  4. 使用了不同的历法校正标准

【结论】
sxtwl是公认的权威标准库。建议使用sxtwl的结果。
""")

print(f"\n【建议】")
print("="*80)
print(f"使用sxtwl计算的四柱进行分析：{year_pillar} {month_pillar} {day_pillar} {hour_pillar}")
print(f"这样得到的财运、大运、格局分析才会准确。")
print()
