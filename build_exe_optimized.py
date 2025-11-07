#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
传统八字命理分析系统 - 优化打包脚本
使用spec文件进行打包，提供更好的控制和进度显示
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def check_pyinstaller():
    """检查PyInstaller是否安装"""
    try:
        import PyInstaller
        print(f"✅ PyInstaller版本: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("❌ PyInstaller未安装")
        print("请运行: pip install pyinstaller")
        return False

def build_with_spec():
    """使用spec文件打包"""
    print("="*80)
    print("开始使用spec文件打包...")
    print("="*80)
    
    spec_file = '传统八字命理分析系统.spec'
    
    if not os.path.exists(spec_file):
        print(f"❌ spec文件不存在: {spec_file}")
        return False
    
    print(f"使用spec文件: {spec_file}")
    print("\n⏳ 打包中，请耐心等待...")
    print("（这可能需要5-15分钟，取决于您的电脑性能）\n")
    
    start_time = time.time()
    
    try:
        # 使用spec文件打包
        cmd = [sys.executable, '-m', 'PyInstaller', '--clean', '--noconfirm', spec_file]
        
        print(f"执行命令: {' '.join(cmd)}\n")
        
        # 实时显示输出
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='ignore',
            bufsize=1,
            universal_newlines=True
        )
        
        # 显示关键进度信息
        for line in process.stdout:
            if any(keyword in line for keyword in ['Building', 'INFO:', 'checking', 'analyzing', 'Processing', 'copying', 'WARNING:', 'ERROR:']):
                print(line.rstrip())
        
        process.wait()
        
        elapsed_time = time.time() - start_time
        
        if process.returncode == 0:
            print(f"\n✅ 打包成功！耗时: {elapsed_time:.1f} 秒")
            return True
        else:
            print(f"\n❌ 打包失败！错误代码: {process.returncode}")
            return False
            
    except Exception as e:
        print(f"\n❌ 打包过程出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_exe():
    """验证生成的EXE文件"""
    print("\n" + "="*80)
    print("验证可执行文件...")
    print("="*80)
    
    exe_path = os.path.join('dist', '传统八字命理分析系统.exe')
    
    if os.path.exists(exe_path):
        file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
        print(f"✅ 可执行文件已生成")
        print(f"   路径: {os.path.abspath(exe_path)}")
        print(f"   大小: {file_size:.2f} MB")
        
        # 检查文件是否可执行
        if file_size > 10:  # 至少10MB，说明打包成功
            print(f"   状态: ✅ 文件大小正常")
            return True
        else:
            print(f"   状态: ⚠️ 文件可能不完整")
            return False
    else:
        print(f"❌ 可执行文件未找到: {exe_path}")
        return False

def main():
    """主函数"""
    print("="*80)
    print("传统八字命理分析系统 - EXE打包脚本（优化版）")
    print("="*80)
    print(f"Python版本: {sys.version.split()[0]}")
    print(f"工作目录: {os.getcwd()}\n")
    
    # 检查PyInstaller
    if not check_pyinstaller():
        return False
    
    # 使用spec文件打包
    if not build_with_spec():
        return False
    
    # 验证EXE
    if not verify_exe():
        return False
    
    print("\n" + "="*80)
    print("✅ 打包完成！")
    print("="*80)
    exe_path = os.path.abspath(os.path.join('dist', '传统八字命理分析系统.exe'))
    print(f"可执行文件: {exe_path}")
    print(f"\n使用说明:")
    print(f"  1. 可以直接双击运行，无需Python环境")
    print(f"  2. 首次启动可能需要几秒钟")
    print(f"  3. 如果遇到缺少DLL的错误，请安装Visual C++ Redistributable")
    print(f"  4. 可以将EXE文件复制到任何Windows电脑上运行")
    print("="*80)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            print("\n❌ 打包失败，请检查错误信息")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断打包")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


