#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修复神煞分析器
将所有 weight= 参数替换为 classic_source= 参数
"""

import re

# 读取文件
with open('classic_analyzer/shensha.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 定义所有神煞的经典出处
shensha_sources = {
    '天乙贵人': '《渊海子平》《三命通会》',
    '文昌贵人': '《渊海子平》',
    '禄神': '《三命通会》《渊海子平》',
    '福禄': '《三命通会》《渊海子平》',  # 禄神的另一个名称
    '羊刃': '《三命通会·总论诸神煞》',
    '桃花': '《三命通会·总论诸神煞》',
    '咸池': '《三命通会·总论诸神煞》',
    '华盖': '《三命通会》',
    '驿马': '《三命通会》',
    '红艳': '《兰台妙选》',
    '孤辰': '《三命通会·总论诸神煞》',
    '寡宿': '《三命通会·总论诸神煞》',
    '空亡': '《三命通会·总论诸神煞》',
    '旬空': '《三命通会·总论诸神煞》',
    '劫煞': '《三命通会·总论诸神煞》',
    '亡神煞': '《三命通会·总论诸神煞》',
    '勾绞煞': '《三命通会·总论诸神煞》',
    '十恶大败煞': '《渊海子平》',
    '雷霆煞': '《三命通会·总论诸神煞》',
    '剑锋煞': '《三命通会·总论诸神煞》',
    '病符煞': '《三命通会·总论诸神煞》',
    '死符煞': '《三命通会·总论诸神煞》',
    '官符煞': '《三命通会·总论诸神煞》',
    '天德贵人': '《渊海子平》《三命通会》',
    '月德贵人': '《渊海子平》《三命通会》',
}

# 替换所有 weight= 为 classic_source=''
# 使用正则表达式查找所有 weight= 行
pattern = r"(\s+)weight=(-?\d+)\s*#.*"

def replace_weight(match):
    indent = match.group(1)
    return f"{indent}classic_source=''"

content = re.sub(pattern, replace_weight, content)

# 保存文件
with open('classic_analyzer/shensha.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 批量替换完成！")
print("已将所有 weight= 参数替换为 classic_source=''")
print("\n下一步：需要手动为每个神煞填写正确的经典出处")

