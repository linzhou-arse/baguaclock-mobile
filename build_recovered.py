#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八卦时钟编译脚本
使用PyInstaller将Python项目打包为可执行文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def check_dependencies():
    """检查必要的依赖"""
    try:
        import PyQt5
        print("✓ PyQt5 已安装")
    except ImportError:
        print("✗ PyQt5 未安装，请运行: pip install PyQt5")
        return False
    
    try:
        import requests
        print("✓ requests 已安装")
    except ImportError:
        print("✗ requests 未安装，请运行: pip install requests")
        return False
    
    try:
        import pygame
        print("✓ pygame 已安装")
    except ImportError:
        print("⚠ pygame 未安装，音效功能将不可用")
    
    try:
        import lunar_python
        print("✓ lunar_python 已安装")
    except ImportError:
        print("⚠ lunar_python 未安装，农历转换功能可能受限")
    
    try:
        import sxtwl
        print("✓ sxtwl 已安装")
    except ImportError:
        print("⚠ sxtwl 未安装，本地八字计算功能将不可用")
    
    try:
        import PyInstaller
        print("✓ PyInstaller 已安装")
    except ImportError:
        print("✗ PyInstaller 未安装，请运行: pip install pyinstaller")
        return False
    
    return True

def clean_build():
    """清理之前的构建文件"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"清理目录: {dir_name}")
            shutil.rmtree(dir_name)

def build_executable():
    """使用PyInstaller构建可执行文件"""
    print("开始构建可执行文件...")
    
    # PyInstaller命令参数
    cmd = [
        sys.executable, '-m', 'PyInstaller',  # 使用当前Python解释器调用PyInstaller
        '--onefile',                    # 打包成单个文件
        '--windowed',                   # Windows下不显示控制台
        '--name=八卦时钟V2.0.1',         # 可执行文件名称
        '--icon=icon.ico',              # 图标文件（如果存在）
        '--add-data=deepseek_config.json:.',  # 包含配置文件
        '--add-data=alarms.json:.',     # 包含闹钟文件
        '--add-data=saved_persons:saved_persons',  # 包含保存的人员数据
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=PyQt5.QtWidgets',
        '--hidden-import=requests',
        '--hidden-import=pygame',
        '--hidden-import=lunar_python',
        '--hidden-import=sxtwl',
        '--hidden-import=sxtwl_adapter',
        'bagua_clock.py'                # 主程序文件
    ]
    
    # 如果没有图标文件，移除图标参数
    if not os.path.exists('icon.ico'):
        cmd = [arg for arg in cmd if not arg.startswith('--icon')]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("构建成功！")
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def copy_resources():
    """复制必要的资源文件到dist目录"""
    if not os.path.exists('dist'):
        return
    
    resources = [
        'deepseek_config.json',
        'alarms.json',
        'saved_persons'
    ]
    
    for resource in resources:
        if os.path.exists(resource):
            dest = os.path.join('dist', resource)
            if os.path.isdir(resource):
                if os.path.exists(dest):
                    shutil.rmtree(dest)
                shutil.copytree(resource, dest)
                print(f"复制目录: {resource} -> dist/{resource}")
            else:
                shutil.copy2(resource, dest)
                print(f"复制文件: {resource} -> dist/{resource}")

def main():
    """主函数"""
    print("=" * 50)
    print("八卦时钟 V2.0.1 编译脚本")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        print("\n请先安装缺失的依赖，然后重新运行此脚本")
        return False
    
    # 清理构建目录
    clean_build()
    
    # 构建可执行文件
    if not build_executable():
        return False
    
    # 复制资源文件
    copy_resources()
    
    print("\n" + "=" * 50)
    print("编译完成！")
    print("可执行文件位置: dist/八卦时钟V2.0.1.exe")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
