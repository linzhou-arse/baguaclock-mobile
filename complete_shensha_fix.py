#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整修复神煞分析器
一次性替换所有 classic_source='' 为正确的经典出处
"""

import re

# 读取文件
with open('classic_analyzer/shensha.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 定义所有需要替换的模式和对应的经典出处
replacements = [
    # 华盖
    (r"(name='华盖'.*?classic_source=)''",
     r"\1'《三命通会》'"),
    
    # 驿马
    (r"(name='驿马'.*?classic_source=)''",
     r"\1'《三命通会》'"),
    
    # 红艳
    (r"(name='红艳'.*?classic_source=)''",
     r"\1'《兰台妙选》'"),
    
    # 孤辰
    (r"(name='孤辰'.*?classic_source=)''",
     r"\1'《三命通会·总论诸神煞》'"),
    
    # 寡宿（可能是Unicode编码）
    (r"(name='.*?寡.*?'.*?classic_source=)''",
     r"\1'《三命通会·总论诸神煞》'"),
    
    # 天德贵人
    (r"(name='天德贵人'.*?classic_source=)''",
     r"\1'《渊海子平》《三命通会》'"),
    
    # 月德贵人
    (r"(name='月德贵人'.*?classic_source=)''",
     r"\1'《渊海子平》《三命通会》'"),
    
    # 劫煞
    (r"(name='劫.*?'.*?classic_source=)''",
     r"\1'《三命通会·总论诸神煞》'"),
    
    # 亡神煞
    (r"(name='亡神.*?'.*?classic_source=)''",
     r"\1'《三命通会·总论诸神煞》'"),
    
    # 勾绞煞
    (r"(name='.*?勾.*?'.*?classic_source=)''",
     r"\1'《三命通会·总论诸神煞》'"),
    
    # 十恶大败煞
    (r"(name='十恶大败.*?'.*?classic_source=)''",
     r"\1'《渊海子平》'"),
    
    # 剑锋煞
    (r"(name='.*?剑锋.*?'.*?classic_source=)''",
     r"\1'《三命通会·总论诸神煞》'"),
    
    # 病符煞
    (r"(name='.*?病符.*?'.*?classic_source=)''",
     r"\1'《三命通会·总论诸神煞》'"),
    
    # 死符煞
    (r"(name='.*?死符.*?'.*?classic_source=)''",
     r"\1'《三命通会·总论诸神煞》'"),
]

# 执行替换
for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# 保存文件
with open('classic_analyzer/shensha.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ 完整修复完成！")
print("已为所有神煞添加经典出处")

