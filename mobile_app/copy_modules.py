#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
复制项目根目录的Python模块到mobile_app目录
用于Buildozer构建APK
"""

import os
import shutil
from pathlib import Path

# 项目根目录
project_root = Path(__file__).parent.parent
mobile_app_dir = Path(__file__).parent

# 需要复制的模块和目录
modules_to_copy = [
    'sxtwl_adapter.py',
    'local_mingli_analyzer.py',
    'local_mingli_analyzer_unified.py',
    'classic_analyzer',
    'chinese_metaphysics_library',
    'classic_lookup_tables.py',
]

# 需要复制的数据文件
data_files_to_copy = [
    'custom_locations.json',
    'alarms.json',
    'saved_persons',
]

print("=" * 60)
print("复制项目模块到mobile_app目录")
print("=" * 60)

# 复制Python模块
copied_modules = []
for module in modules_to_copy:
    src = project_root / module
    dst = mobile_app_dir / module
    
    if src.exists():
        if src.is_file():
            # 复制文件
            shutil.copy2(src, dst)
            print(f"✅ 已复制文件: {module}")
            copied_modules.append(module)
        elif src.is_dir():
            # 复制目录
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"✅ 已复制目录: {module}")
            copied_modules.append(module)
    else:
        print(f"⚠️  未找到: {module}")

# 复制数据文件
print("\n复制数据文件...")
for data_file in data_files_to_copy:
    src = project_root / data_file
    dst = mobile_app_dir / data_file
    
    if src.exists():
        if src.is_file():
            shutil.copy2(src, dst)
            print(f"✅ 已复制数据文件: {data_file}")
        elif src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print(f"✅ 已复制数据目录: {data_file}")
    else:
        print(f"⚠️  未找到数据文件: {data_file}")

print("\n" + "=" * 60)
print(f"复制完成！共复制 {len(copied_modules)} 个模块")
print("=" * 60)
print("\n现在可以运行 buildozer android debug 构建APK")

