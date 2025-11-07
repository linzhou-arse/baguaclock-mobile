#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
经典原文检索工具

用途：
- 从项目内“中国命学六书”文件夹的原文中检索并提取可展示的片段
- 当前支持：《穷通宝鉴》按“月支×日主天干”检索调候条目

原则：
- 仅做检索与截取，不编造、不改写
- 返回原文片段，尽量包含一个完整句子
"""
from __future__ import annotations

import os
from typing import List, Optional

# 仓库根目录（运行时当前工作目录即仓库根）
REPO_ROOT = os.getcwd()
BOOKS_DIR = os.path.join(REPO_ROOT, '中国命学六书')
QTB_PATH = os.path.join(BOOKS_DIR, '《穷通宝鉴》.txt')

BRANCH_TO_MONTH_CN = {
    '寅': '正', '卯': '二', '辰': '三',
    '巳': '四', '午': '五', '未': '六',
    '申': '七', '酉': '八', '戌': '九',
    '亥': '十', '子': '十一', '丑': '十二',
}

# 天干对应五行名（用于构造检索词，如“辛金”）
TIANGAN_ELEMENT = {
    '甲': '木', '乙': '木',
    '丙': '火', '丁': '火',
    '戊': '土', '己': '土',
    '庚': '金', '辛': '金',
    '壬': '水', '癸': '水',
}

def _read_text_file(path: str) -> Optional[str]:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return None


def _extract_sentence(text: str, start_idx: int, max_span: int = 80) -> str:
    """从 start_idx 开始，截取到最近的句号“。”，尽量返回一个完整句子。"""
    if start_idx < 0 or start_idx >= len(text):
        return ''
    end = text.find('。', start_idx)
    if end == -1:
        end = min(len(text) - 1, start_idx + max_span)
    snippet = text[start_idx:end + 1]
    # 去掉换行与多余空白
    return '：' + ' '.join(snippet.strip().split())


def find_qiongtong_tiaohou_snippet(day_master: str, month_branch: str) -> str:
    """
    在《穷通宝鉴》原文中检索“<某月><某干><元素/日>”条目，返回一句原文片段。
    例如：month_branch='戌'、day_master='辛' -> 检索“九月辛金”或“九月辛日”。
    找不到则返回空字符串。
    """
    text = _read_text_file(QTB_PATH)
    if not text:
        return ''

    month_cn = BRANCH_TO_MONTH_CN.get(month_branch)
    if not month_cn:
        return ''

    element = TIANGAN_ELEMENT.get(day_master, '')
    candidates: List[str] = []
    # 常见写法优先
    if element:
        candidates.append(f"{month_cn}月{day_master}{element}")  # 如：九月辛金
    candidates.append(f"{month_cn}月{day_master}日")           # 如：九月辛日
    candidates.append(f"{month_cn}月{day_master}")              # 兜底：九月辛

    for term in candidates:
        idx = text.find(term)
        if idx != -1:
            return f"《穷通宝鉴》{_extract_sentence(text, idx)}"
    return ''


__all__ = [
    'find_qiongtong_tiaohou_snippet',
]

