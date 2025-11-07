#!/usr/bin/env python3

# 修改buildozer源代码以解决PEP 668问题
import sys

# 文件路径
file_path = '/home/builduser/.local/lib/python3.12/site-packages/buildozer/targets/android.py'

# 读取文件内容
with open(file_path, 'r') as f:
    content = f.read()

# 替换内容
content = content.replace('options = ["--user"]', 'options = ["--user", "--break-system-packages"]')

# 写入文件
with open(file_path, 'w') as f:
    f.write(content)

print("文件修改完成")