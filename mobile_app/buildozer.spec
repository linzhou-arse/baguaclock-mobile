# Buildozer配置文件 - Android APK构建
# 用于将Python应用打包为Android APK

[app]

# 应用名称
title = 八卦时钟

# 包名（必须是唯一的，反向域名格式）
package.name = com.quanhang.baguaclock

# 包域名
package.domain = com.quanhang

# 源代码目录
source.dir = .

# 源代码主文件
source.include_exts = py,png,jpg,kv,atlas,json,txt,md

# 应用程序入口
main.py = main.py

# 应用版本
version = 2.0.0

# 应用版本代码（每次发布递增）
# 0 = 自动递增
version.code = 1

# 应用图标
icon.filename = %(source.dir)s/icon.png

# 应用权限
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# Android最低版本
android.minapi = 21

# Android目标版本
android.targetapi = 31

# Android架构
android.archs = arm64-v8a,armeabi-v7a

# Python依赖
requirements = python3,kivy==2.3.0,kivymd==1.1.1,plyer,pyjnius,requests

# 应用方向
orientation = portrait

# 全屏模式
fullscreen = 0

[buildozer]

# 日志级别
log_level = 2

# 构建目录
# build_dir = ./.buildozer

# 是否使用Cython
# cython = False

# 是否使用Cython优化
# cythonize = False

# 是否显示警告
# warn_on_root = 1

# 国内镜像源配置
p4a.bootstrap = sdl2
p4a.local_recipes = ./p4a-recipes

# 使用开发分支以获得最新修复
p4a.branch = develop

# NDK API版本
android.ndk_api = 21