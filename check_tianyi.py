#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 代码中的天乙贵人表
TIANYI_TABLE_CODE = {
    '甲': ['丑', '未'], '乙': ['子', '申'],
    '丙': ['亥', '酉'], '丁': ['亥', '酉'],
    '戊': ['丑', '未'], '己': ['子', '申'],
    '庚': ['丑', '午'], '辛': ['寅', '午'],
    '壬': ['卯', '巳'], '癸': ['卯', '巳'],
}

# 正确的天乙贵人表（根据口诀）
TIANYI_TABLE_CORRECT = {
    '甲': ['丑', '未'],  # 甲戊庚牛羊
    '戊': ['丑', '未'],  # 甲戊庚牛羊
    '庚': ['丑', '未'],  # 甲戊庚牛羊
    '乙': ['子', '申'],  # 乙己鼠猴乡
    '己': ['子', '申'],  # 乙己鼠猴乡
    '丙': ['亥', '酉'],  # 丙丁猪鸡位
    '丁': ['亥', '酉'],  # 丙丁猪鸡位
    '壬': ['卯', '巳'],  # 壬癸兔蛇藏
    '癸': ['卯', '巳'],  # 壬癸兔蛇藏
    '辛': ['寅', '午'],  # 六辛逢虎马
}

print('=' * 60)
print('天乙贵人口诀验证')
print('=' * 60)

print('\n口诀：')
print('甲戊庚牛羊，乙己鼠猴乡，丙丁猪鸡位，壬癸兔蛇藏，六辛逢虎马')

print('\n代码中的天乙贵人表：')
for gan in ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']:
    print(f'{gan}: {TIANYI_TABLE_CODE[gan]}')

print('\n正确的天乙贵人表：')
for gan in ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']:
    print(f'{gan}: {TIANYI_TABLE_CORRECT[gan]}')

print('\n' + '=' * 60)
print('错误检查：')
print('=' * 60)

errors = []
for gan in ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']:
    if TIANYI_TABLE_CODE[gan] != TIANYI_TABLE_CORRECT[gan]:
        errors.append(f'❌ {gan}: 代码是{TIANYI_TABLE_CODE[gan]}，应该是{TIANYI_TABLE_CORRECT[gan]}')

if errors:
    for error in errors:
        print(error)
else:
    print('✅ 所有天干的天乙贵人都正确！')

print('\n' + '=' * 60)

