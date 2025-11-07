#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
八卦时钟打包脚本 - 生成独立可执行文件
使用PyInstaller将项目打包成EXE，不依赖Python环境
"""

import sys
import os
import shutil
import subprocess
from pathlib import Path

def check_dependencies():
    """检查必要的依赖是否已安装"""
    print("="*80)
    print("检查依赖...")
    print("="*80)
    
    required_modules = [
        'PyQt5',
        'PyInstaller',
        'requests',
        'pygame',
        'lunar_python',
        'sxtwl'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            if module == 'PyQt5':
                __import__('PyQt5.QtWidgets')
            elif module == 'lunar_python':
                __import__('lunar_python')
            elif module == 'sxtwl':
                __import__('sxtwl')
            else:
                __import__(module)
            print(f"✅ {module} 已安装")
        except ImportError:
            print(f"❌ {module} 未安装")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n⚠️ 缺少以下模块: {', '.join(missing_modules)}")
        print("请运行: pip install " + " ".join(missing_modules))
        return False
    
    print("\n✅ 所有依赖已安装")
    return True

def clean_build_dirs():
    """清理构建目录"""
    print("\n" + "="*80)
    print("清理构建目录...")
    print("="*80)
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"✅ 已清理: {dir_name}")
            except Exception as e:
                print(f"⚠️ 清理 {dir_name} 失败: {e}")
    
    # 清理.spec文件
    spec_files = list(Path('.').glob('*.spec'))
    for spec_file in spec_files:
        try:
            spec_file.unlink()
            print(f"✅ 已删除: {spec_file}")
        except Exception as e:
            print(f"⚠️ 删除 {spec_file} 失败: {e}")

def collect_data_files():
    """收集需要打包的数据文件"""
    data_files = []
    
    # 配置文件
    config_files = ['alarms.json', 'custom_locations.json']
    for config_file in config_files:
        if os.path.exists(config_file):
            data_files.append(f"{config_file};.")
            print(f"✅ 包含配置文件: {config_file}")
    
    # saved_persons目录
    if os.path.exists('saved_persons'):
        data_files.append(f"saved_persons;saved_persons")
        print(f"✅ 包含目录: saved_persons")
    
    # 中国命学六书目录（可选）
    if os.path.exists('中国命学六书'):
        data_files.append(f"中国命学六书;中国命学六书")
        print(f"✅ 包含目录: 中国命学六书")
    
    return data_files

def build_executable():
    """使用PyInstaller构建可执行文件"""
    print("\n" + "="*80)
    print("开始构建可执行文件...")
    print("="*80)
    
    # 收集数据文件
    data_files = collect_data_files()
    
    # PyInstaller命令参数
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--onefile',                          # 打包成单个文件
        '--windowed',                         # Windows下不显示控制台（GUI应用）
        '--name=传统八字命理分析系统',         # 可执行文件名称
        '--clean',                            # 清理临时文件
        '--noconfirm',                        # 覆盖输出目录而不询问
        
        # 隐藏导入（确保所有模块都被包含）
        '--hidden-import=PyQt5',
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=PyQt5.QtWidgets',
        '--hidden-import=PyQt5.QtWebEngineWidgets',
        '--hidden-import=requests',
        '--hidden-import=pygame',
        '--hidden-import=lunar_python',
        '--hidden-import=lunar_python.Lunar',
        '--hidden-import=sxtwl',
        '--hidden-import=sxtwl_adapter',
        '--hidden-import=local_mingli_analyzer',
        '--hidden-import=local_mingli_analyzer_unified',
        '--hidden-import=classic_analyzer',
        '--hidden-import=classic_analyzer.common',
        '--hidden-import=classic_analyzer.caiyun',
        '--hidden-import=classic_analyzer.geju_analyzer',
        '--hidden-import=classic_analyzer.dayun',
        '--hidden-import=classic_analyzer.shensha',
        '--hidden-import=classic_analyzer.wuxing_analyzer',
        '--hidden-import=chinese_metaphysics_library',
        '--hidden-import=chinese_metaphysics_library.core',
        '--hidden-import=chinese_metaphysics_library.yuanhaiziping',
        '--hidden-import=chinese_metaphysics_library.santonghui',
        '--hidden-import=chinese_metaphysics_library.zipingzhenquan',
        '--hidden-import=chinese_metaphysics_library.ditiansui',
        '--hidden-import=chinese_metaphysics_library.qiongtongbaojian',
        '--hidden-import=chinese_metaphysics_library.lantaimiaoxuan',
        '--hidden-import=classic_lookup_tables',
        
        # 添加数据文件
    ]
    
    # 添加数据文件
    for data_file in data_files:
        cmd.append(f'--add-data={data_file}')
    
    # 添加主程序文件
    cmd.append('bagua_clock.py')
    
    print(f"\n执行命令: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        print("✅ 构建成功！")
        if result.stdout:
            # 只显示关键信息
            lines = result.stdout.split('\n')
            for line in lines:
                if any(keyword in line for keyword in ['Building', 'INFO:', 'WARNING:', 'ERROR:', 'Successfully']):
                    print(line)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败!")
        print(f"错误代码: {e.returncode}")
        if e.stdout:
            print(f"标准输出:\n{e.stdout}")
        if e.stderr:
            print(f"错误输出:\n{e.stderr}")
        return False

def verify_executable():
    """验证生成的可执行文件"""
    print("\n" + "="*80)
    print("验证可执行文件...")
    print("="*80)
    
    exe_path = os.path.join('dist', '传统八字命理分析系统.exe')
    
    if os.path.exists(exe_path):
        file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
        print(f"✅ 可执行文件已生成: {exe_path}")
        print(f"   文件大小: {file_size:.2f} MB")
        return True
    else:
        print(f"❌ 可执行文件未找到: {exe_path}")
        return False

def main():
    """主函数"""
    print("="*80)
    print("传统八字命理分析系统 - EXE打包脚本")
    print("="*80)
    print(f"Python版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    
    # 检查依赖
    if not check_dependencies():
        print("\n❌ 依赖检查失败，请先安装缺失的依赖")
        print("运行: pip install PyQt5 PyInstaller requests pygame lunar-python sxtwl")
        return False
    
    # 清理构建目录
    clean_build_dirs()
    
    # 构建可执行文件
    if not build_executable():
        print("\n❌ 构建失败")
        return False
    
    # 验证可执行文件
    if not verify_executable():
        print("\n❌ 验证失败")
        return False
    
    print("\n" + "="*80)
    print("✅ 打包完成！")
    print("="*80)
    print(f"可执行文件位置: dist/传统八字命理分析系统.exe")
    print(f"\n使用说明:")
    print(f"  1. 可执行文件位于 dist 目录")
    print(f"  2. 可以直接运行，不需要Python环境")
    print(f"  3. 首次运行可能需要几秒钟启动时间")
    print(f"  4. 如果遇到问题，请检查是否缺少必要的系统库")
    print("="*80)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


