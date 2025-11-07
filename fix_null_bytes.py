#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix null bytes in bagua_clock.py
"""

# Read the file in binary mode
with open('bagua_clock.py', 'rb') as f:
    content = f.read()

# Count null bytes
null_count = content.count(b'\x00')
print(f'Found {null_count} null bytes')

# Remove null bytes
cleaned = content.replace(b'\x00', b'')

# Write back
with open('bagua_clock.py', 'wb') as f:
    f.write(cleaned)

print(f'Removed {null_count} null bytes')
print('File cleaned successfully!')

