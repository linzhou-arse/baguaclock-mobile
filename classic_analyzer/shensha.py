#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
神煞分析模块（ASCII 版本，使用 Unicode 转义避免乱码）

🔥 重要说明：十神与神煞是两个不同的概念
- 十神：基于天干生克关系（我生、生我、我克、克我、同我），用于分析日主与其他天干的关系
- 神煞：基于地支组合关系（三合局、六合局、刑冲害等），用于分析特殊的地支组合影响

神煞计算依据：
- 三合局：申子辰（水局）、寅午戌（火局）、巳酉丑（金局）、亥卯未（木局）
- 六合局：子丑合、寅亥合、卯戌合、辰酉合、巳申合、午未合
- 劫煞：基于三合局计算，如申子辰局见巳为劫煞（水绝于巳）
- 其他神煞：天乙贵人、桃花、驿马等，各有其计算规则
"""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from classic_lookup_tables import ClassicLookupTables


TIANYI_TABLE = {
    '\u7532': ['\u4e11', '\u672a'], '\u4e59': ['\u5b50', '\u7533'],
    '\u4e19': ['\u4ea4', '\u9149'], '\u4e01': ['\u4ea4', '\u9149'],
    '\u620a': ['\u4e11', '\u672a'], '\u5df1': ['\u5b50', '\u7533'],
    '\u5e9a': ['\u4e11', '\u5348'], '\u8f9b': ['\u5bc5', '\u5348'],
    '\u58ec': ['\u536f', '\u5df3'], '\u7678': ['\u536f', '\u5df3'],
}
WENCHANG_TABLE = {
    '\u7532': '\u5df3', '\u4e59': '\u5348', '\u4e19': '\u7533', '\u4e01': '\u9149',
    '\u620a': '\u7533', '\u5df1': '\u9149', '\u5e9a': '\u4ea4', '\u8f9b': '\u5b50',
    '\u58ec': '\u5bc5', '\u7678': '\u536f',
}
LUSHEN_TABLE = {
    '\u7532': '\u5bc5', '\u4e59': '\u536f', '\u4e19': '\u5df3', '\u4e01': '\u5348',
    '\u620a': '\u5df3', '\u5df1': '\u5348', '\u5e9a': '\u7533', '\u8f9b': '\u9149',
    '\u58ec': '\u4ea4', '\u7678': '\u5b50',
}
YANGREN_TABLE = {
    '\u7532': '\u536f', '\u4e19': '\u5348', '\u620a': '\u5348', '\u5e9a': '\u9149', '\u58ec': '\u5b50'
}
TAOHUA_TABLE = {
    '\u5bc5': '\u536f', '\u536f': '\u536f', '\u620c': '\u536f',
    '\u5df3': '\u5348', '\u9149': '\u5348', '\u4e11': '\u5348',
    '\u7533': '\u9149', '\u5b50': '\u9149', '\u8fb0': '\u9149',
    '\u4ea4': '\u5b50', '\u536f': '\u5b50', '\u672a': '\u5b50',
}
# 扩展为完整的60个干支空亡表（《三命通会》六甲旬空法）
KONGWANG_TABLE = {
    # 甲子旬：甲子～癸酉，空戌亥
    '\u7532\u5b50': ['\u620c', '\u4ea4'], '\u4e59\u4e11': ['\u620c', '\u4ea4'], '\u4e19\u5bc5': ['\u620c', '\u4ea4'],
    '\u4e01\u536f': ['\u620c', '\u4ea4'], '\u620a\u8fb0': ['\u620c', '\u4ea4'], '\u5df1\u5df3': ['\u620c', '\u4ea4'],
    '\u5e9a\u5348': ['\u620c', '\u4ea4'], '\u8f9b\u672a': ['\u620c', '\u4ea4'], '\u58ec\u7533': ['\u620c', '\u4ea4'],
    '\u7678\u9149': ['\u620c', '\u4ea4'],
    # 甲戌旬：甲戌～癸未，空申酉
    '\u7532\u620c': ['\u7533', '\u9149'], '\u4e59\u4ea4': ['\u7533', '\u9149'], '\u4e19\u5b50': ['\u7533', '\u9149'],
    '\u4e01\u4e11': ['\u7533', '\u9149'], '\u620a\u5bc5': ['\u7533', '\u9149'], '\u5df1\u536f': ['\u7533', '\u9149'],
    '\u5e9a\u8fb0': ['\u7533', '\u9149'], '\u8f9b\u5df3': ['\u7533', '\u9149'], '\u58ec\u5348': ['\u7533', '\u9149'],
    '\u7678\u672a': ['\u7533', '\u9149'],
    # 甲申旬：甲申～癸巳，空午未
    '\u7532\u7533': ['\u5348', '\u672a'], '\u4e59\u9149': ['\u5348', '\u672a'], '\u4e19\u620c': ['\u5348', '\u672a'],
    '\u4e01\u4ea4': ['\u5348', '\u672a'], '\u620a\u5b50': ['\u5348', '\u672a'], '\u5df1\u4e11': ['\u5348', '\u672a'],
    '\u5e9a\u5bc5': ['\u5348', '\u672a'], '\u8f9b\u536f': ['\u5348', '\u672a'], '\u58ec\u8fb0': ['\u5348', '\u672a'],
    '\u7678\u5df3': ['\u5348', '\u672a'],
    # 甲午旬：甲午～癸卯，空辰巳
    '\u7532\u5348': ['\u8fb0', '\u5df3'], '\u4e59\u672a': ['\u8fb0', '\u5df3'], '\u4e19\u7533': ['\u8fb0', '\u5df3'],
    '\u4e01\u9149': ['\u8fb0', '\u5df3'], '\u620a\u620c': ['\u8fb0', '\u5df3'], '\u5df1\u4ea4': ['\u8fb0', '\u5df3'],
    '\u5e9a\u5b50': ['\u8fb0', '\u5df3'], '\u8f9b\u4e11': ['\u8fb0', '\u5df3'], '\u58ec\u5bc5': ['\u8fb0', '\u5df3'],
    '\u7678\u536f': ['\u8fb0', '\u5df3'],
    # 甲辰旬：甲辰～癸丑，空寅卯
    '\u7532\u8fb0': ['\u5bc5', '\u536f'], '\u4e59\u5df3': ['\u5bc5', '\u536f'], '\u4e19\u5348': ['\u5bc5', '\u536f'],
    '\u4e01\u672a': ['\u5bc5', '\u536f'], '\u620a\u7533': ['\u5bc5', '\u536f'], '\u5df1\u9149': ['\u5bc5', '\u536f'],
    '\u5e9a\u620c': ['\u5bc5', '\u536f'], '\u8f9b\u4ea4': ['\u5bc5', '\u536f'], '\u58ec\u5b50': ['\u5bc5', '\u536f'],
    '\u7678\u4e11': ['\u5bc5', '\u536f'],
    # 甲寅旬：甲寅～癸亥，空子丑
    '\u7532\u5bc5': ['\u5b50', '\u4e11'], '\u4e59\u536f': ['\u5b50', '\u4e11'], '\u4e19\u8fb0': ['\u5b50', '\u4e11'],
    '\u4e01\u5df3': ['\u5b50', '\u4e11'], '\u620a\u5348': ['\u5b50', '\u4e11'], '\u5df1\u672a': ['\u5b50', '\u4e11'],
    '\u5e9a\u7533': ['\u5b50', '\u4e11'], '\u8f9b\u9149': ['\u5b50', '\u4e11'], '\u58ec\u620c': ['\u5b50', '\u4e11'],
    '\u7678\u4ea4': ['\u5b50', '\u4e11'],
}
LIUSHI_JIAZI = [
    '\u7532\u5b50', '\u4e59\u4e11', '\u4e19\u5bc5', '\u4e01\u536f', '\u620a\u8fb0', '\u5df1\u5df3', '\u5e9a\u5348', '\u8f9b\u672a', '\u58ec\u7533', '\u7678\u9149',
    '\u7532\u620c', '\u4e59\u4ea4', '\u4e19\u5b50', '\u4e01\u4e11', '\u620a\u5bc5', '\u5df1\u536f', '\u5e9a\u8fb0', '\u8f9b\u5df3', '\u58ec\u5348', '\u7678\u672a',
    '\u7532\u7533', '\u4e59\u9149', '\u4e19\u620c', '\u4e01\u4ea4', '\u620a\u5b50', '\u5df1\u4e11', '\u5e9a\u5bc5', '\u8f9b\u536f', '\u58ec\u8fb0', '\u7678\u5df3',
    '\u7532\u5348', '\u4e59\u672a', '\u4e19\u7533', '\u4e01\u9149', '\u620a\u620c', '\u5df1\u4ea4', '\u5e9a\u5b50', '\u8f9b\u4e11', '\u58ec\u5bc5', '\u7678\u536f',
    '\u7532\u8fb0', '\u4e59\u5df3', '\u4e19\u5348', '\u4e01\u672a', '\u620a\u7533', '\u5df1\u9149', '\u5e9a\u620c', '\u8f9b\u4ea4', '\u58ec\u5b50', '\u7678\u4e11',
    '\u7532\u5bc5', '\u4e59\u536f', '\u4e19\u8fb0', '\u4e01\u5df3', '\u620a\u5348', '\u5df1\u672a', '\u5e9a\u7533', '\u8f9b\u9149', '\u58ec\u620c', '\u7678\u4ea4',
]
HUAGAI_TABLE = {
    '\u5bc5': '\u620c', '\u536f': '\u620c', '\u672a': '\u620c',
    '\u7533': '\u8fb0', '\u5b50': '\u8fb0', '\u8fb0': '\u8fb0',
    '\u5df3': '\u4e11', '\u9149': '\u4e11', '\u4e11': '\u4e11',
    '\u4ea4': '\u672a', '\u536f': '\u672a', '\u672a': '\u672a',
}
YIMA_TABLE = {
    '\u5bc5': '\u7533', '\u536f': '\u7533', '\u620c': '\u7533',
    '\u7533': '\u5bc5', '\u5b50': '\u5bc5', '\u8fb0': '\u5bc5',
    '\u5df3': '\u4ea4', '\u9149': '\u4ea4', '\u4e11': '\u4ea4',
    '\u4ea4': '\u5df3', '\u536f': '\u5df3', '\u672a': '\u5df3',
}
HONGYAN_TABLE = {
    '\u7532': '\u5348', '\u4e59': '\u7533', '\u4e19': '\u5bc5', '\u4e01': '\u672a', '\u620a': '\u8fb0',
    '\u5df1': '\u8fb0', '\u5e9a': '\u620c', '\u8f9b': '\u9149', '\u58ec': '\u5b50', '\u7678': '\u7533',
}
GUCHEN_TABLE = {
    '\u4ea4': '\u5bc5', '\u5b50': '\u5bc5', '\u4e11': '\u5bc5',
    '\u5bc5': '\u5df3', '\u536f': '\u5df3', '\u8fb0': '\u5df3',
    '\u5df3': '\u7533', '\u5348': '\u7533', '\u672a': '\u7533',
    '\u7533': '\u4ea4', '\u9149': '\u4ea4', '\u620c': '\u4ea4',
}
GUASU_TABLE = {
    '\u4ea4': '\u620c', '\u5b50': '\u620c', '\u4e11': '\u620c',
    '\u5bc5': '\u4e11', '\u536f': '\u4e11', '\u8fb0': '\u4e11',
    '\u5df3': '\u8fb0', '\u5348': '\u8fb0', '\u672a': '\u8fb0',
    '\u7533': '\u672a', '\u9149': '\u672a', '\u620c': '\u672a',
}
# 天德贵人表 - 按《三命通会·神煞篇》修正（月支对应）
# 天德贵人：正月在丁，二月在申，三月在壬，四月在辛，五月在亥，六月在甲，
# 七月在癸，八月在寅，九月在丙，十月在乙，十一月在巳，十二月在庚
TIANDE_TABLE = {
    '\u5bc5': '\u4e01',  # 寅月（正月）- 丁
    '\u536f': '\u7533',  # 卯月（二月）- 申（坤位）
    '\u8fb0': '\u58ec',  # 辰月（三月）- 壬
    '\u5df3': '\u8f9b',  # 巳月（四月）- 辛
    '\u5348': '\u4ea5',  # 午月（五月）- 亥
    '\u672a': '\u7532',  # 未月（六月）- 甲
    '\u7533': '\u7678',  # 申月（七月）- 癸
    '\u9149': '\u5bc5',  # 酉月（八月）- 寅
    '\u620c': '\u4e19',  # 戌月（九月）- 丙
    '\u4ea5': '\u4e59',  # 亥月（十月）- 乙
    '\u5b50': '\u5df3',  # 子月（十一月）- 巳（巽位）
    '\u4e11': '\u5e9a',  # 丑月（十二月）- 庚
}
YUEDE_TABLE = {
    '\u5bc5': '\u4e01', '\u536f': '\u4e01', '\u620c': '\u4e01',
    '\u7533': '\u7678', '\u5b50': '\u7678', '\u8fb0': '\u7678',
    '\u4ea4': '\u4e59', '\u536f': '\u4e59', '\u672a': '\u4e59',
    '\u5df3': '\u8f9b', '\u9149': '\u8f9b', '\u4e11': '\u8f9b',
}

# ✅ 修复：劫煞按三合局计算（基于《三命通会》原文）
# 《三命通会》："水绝在巳，申子辰以巳为劫煞；火绝在亥，寅午戌以亥为劫煞；
#                金绝在寅，巳酉丑以寅为劫煞；木绝在申，亥卯未以申为劫煞"
# 三合局的劫煞位：
# - 申子辰（水局）：劫煞在巳（水绝于巳）
# - 寅午戌（火局）：劫煞在亥（火绝于亥）
# - 巳酉丑（金局）：劫煞在寅（金绝于寅）
# - 亥卯未（木局）：劫煞在申（木绝于申）
SANHE_JIESHA_MAP = {
    # 申子辰水局 -> 劫煞在巳
    ('申', '子', '辰'): '巳',
    # 寅午戌火局 -> 劫煞在亥
    ('寅', '午', '戌'): '亥',
    # 巳酉丑金局 -> 劫煞在寅
    ('巳', '酉', '丑'): '寅',
    # 亥卯未木局 -> 劫煞在申
    ('亥', '卯', '未'): '申',
}

# 旧的劫煞表（已废弃，保留用于兼容）
JIESHA_TABLE_OLD = {
    '\u5bc5': '\u5df3', '\u536f': '\u5df3', '\u620c': '\u5df3',
    '\u7533': '\u4ea4', '\u5b50': '\u4ea4', '\u8fb0': '\u4ea4',
    '\u4ea4': '\u5b50', '\u536f': '\u5b50', '\u672a': '\u5b50',
    '\u5df3': '\u536f', '\u9149': '\u536f', '\u4e11': '\u536f',
}

# 亡神煞表
WANGSHEN_TABLE = {
    '\u5bc5': '\u7533', '\u536f': '\u7533', '\u620c': '\u7533',
    '\u7533': '\u5bc5', '\u5b50': '\u5bc5', '\u8fb0': '\u5bc5',
    '\u4ea4': '\u5df3', '\u536f': '\u5df3', '\u672a': '\u5df3',
    '\u5df3': '\u4ea4', '\u9149': '\u4ea4', '\u4e11': '\u4ea4',
}

# 勾绞煞表（简化处理）
GOUJIAO_TABLE = {
    '\u7532': {'gou': '\u536f', 'jiao': '\u9149'},  # 甲日阳干
    '\u4e19': {'gou': '\u536f', 'jiao': '\u9149'},  # 丙日阳干
    '\u620a': {'gou': '\u536f', 'jiao': '\u9149'},  # 戊日阳干
    '\u5e9a': {'gou': '\u536f', 'jiao': '\u9149'},  # 庚日阳干
    '\u58ec': {'gou': '\u536f', 'jiao': '\u9149'},  # 壬日阳干
    '\u4e59': {'gou': '\u9149', 'jiao': '\u536f'},  # 乙日阴干
    '\u4e01': {'gou': '\u9149', 'jiao': '\u536f'},  # 丁日阴干
    '\u5df1': {'gou': '\u9149', 'jiao': '\u536f'},  # 己日阴干
    '\u8f9b': {'gou': '\u9149', 'jiao': '\u536f'},  # 辛日阴干
    '\u7678': {'gou': '\u9149', 'jiao': '\u536f'},  # 癸日阴干
}

# 十恶大败煞表（日柱）
SHI_E_DA_BAI = [
    '\u7532\u8fb0', '\u4e59\u5df3', '\u4e19\u5348', '\u4e01\u672a', '\u620a\u7533', 
    '\u5df1\u9149', '\u5e9a\u620c', '\u8f9b\u4ea4', '\u58ec\u5b50', '\u7678\u4e11'
]

# 雷霆煞表
LEITING_TABLE = {
    1: '\u5b50',   # 正月子
    2: '\u5bc5',   # 二月寅
    3: '\u8fb0',   # 三月辰
    4: '\u5348',   # 四月午
    5: '\u7533',   # 五月申
    6: '\u620c',   # 六月戌
    7: '\u5b50',   # 七月子
    8: '\u5bc5',   # 八月寅
    9: '\u8fb0',   # 九月辰
    10: '\u5348',  # 十月午
    11: '\u7533',  # 十一月申
    12: '\u620c',  # 十二月戌
}

# 剑锋煞表
JIANFENG_TABLE = {
    # 甲子旬剑辰锋戌，甲午旬剑戌锋辰，甲寅旬剑午锋申，
    # 甲申旬剑子锋寅，甲辰旬剑申锋午，甲戌旬剑寅锋子
    '\u7532\u5b50': {'jian': '\u8fb0', 'feng': '\u620c'},  # 甲子旬
    '\u7532\u5348': {'jian': '\u620c', 'feng': '\u8fb0'},  # 甲午旬
    '\u7532\u5bc5': {'jian': '\u5348', 'feng': '\u7533'},  # 甲寅旬
    '\u7532\u7533': {'jian': '\u5b50', 'feng': '\u5bc5'},  # 甲申旬
    '\u7532\u8fb0': {'jian': '\u7533', 'feng': '\u5348'},  # 甲辰旬
    '\u7532\u620c': {'jian': '\u5bc5', 'feng': '\u5b50'},  # 甲戌旬
}

# 病符煞表（太岁后一辰）
BINGFU_TABLE = {
    '\u5bc5': '\u4e11', '\u536f': '\u5bc5', '\u620c': '\u536f',
    '\u7533': '\u9149', '\u5b50': '\u5df3', '\u8fb0': '\u7533',
    '\u4ea4': '\u672a', '\u536f': '\u4e11', '\u672a': '\u5bc5',
    '\u5df3': '\u536f', '\u9149': '\u7533', '\u4e11': '\u5b50',
}

# 死符煞表（病符对冲）
SIFU_TABLE = {
    '\u4e11': '\u5bc5', '\u5bc5': '\u536f', '\u536f': '\u620c',
    '\u620c': '\u7533', '\u7533': '\u5b50', '\u5b50': '\u8fb0',
    '\u8fb0': '\u5df3', '\u5df3': '\u4ea4', '\u4ea4': '\u672a',
    '\u672a': '\u9149', '\u9149': '\u4e11', '\u4e11': '\u5bc5',
}

POSITION_LABELS = {
    'year': '\u5e74\u67f1',
    'month': '\u6708\u67f1',
    'day': '\u65e5\u67f1',
    'hour': '\u65f6\u67f1',
}


class ShenShaAnalyzer:
    """\u795e\u7160\u5206\u6790\u5668\u3002"""
    LOOKUP = ClassicLookupTables()
    _OVERRIDE_DONE = False

    @classmethod
    def _ensure_tables(cls) -> None:
        if cls._OVERRIDE_DONE:
            return
        tables = cls.LOOKUP
        tables.TIANYI_GUIREN = TIANYI_TABLE
        tables.WENCHANG_GUIREN = WENCHANG_TABLE
        tables.LUSHEN = LUSHEN_TABLE
        tables.YANGREN = YANGREN_TABLE
        tables.TAOHUA = TAOHUA_TABLE
        tables.KONGWANG_TABLE = KONGWANG_TABLE
        tables.LIUSHI_JIAZI = LIUSHI_JIAZI
        tables.HUAGAI = HUAGAI_TABLE
        tables.YIMA = YIMA_TABLE
        tables.HONGYAN = HONGYAN_TABLE
        tables.GUCHEN = GUCHEN_TABLE
        tables.GUASU = GUASU_TABLE
        tables.TIANDE = TIANDE_TABLE
        tables.YUEDE = YUEDE_TABLE
        # 新增神煞表
        # ✅ 修复：劫煞不再使用简单查表，改用三合局计算
        # tables.JIESHA = JIESHA_TABLE_OLD  # 已废弃
        tables.WANGSHEN = WANGSHEN_TABLE
        tables.GOUJIAO = GOUJIAO_TABLE
        tables.SHI_E_DA_BAI = SHI_E_DA_BAI
        tables.LEITING = LEITING_TABLE
        tables.JIANFENG = JIANFENG_TABLE
        tables.BINGFU = BINGFU_TABLE
        tables.SIFU = SIFU_TABLE
        cls._OVERRIDE_DONE = True

    @classmethod
    def analyze_shensha(cls, pillars: Dict[str, Tuple[str, str]], birth_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        \u795e\u7160\u5206\u6790\u3002
        
        \u53c2\u6570:
            pillars: {'year': ('\u7532','\u5b50'), ...}
            birth_info: {'gender': '\u7537/\u5973', ...}
        
        \u8fd4\u56de:
            {
                'ji_sha': [...],
                'xiong_sha': [...],
                'level': '\u5927\u5409/\u5c0f\u5409/\u5e73/\u5c0f\u51f6/\u5927\u51f6',
                'analysis': '...',
            }
        """
        cls._ensure_tables()

        gender = birth_info.get('gender', '\u672a\u77e5')
        stems = {k: v[0] for k, v in pillars.items()}
        branches = {k: v[1] for k, v in pillars.items()}

        ji_sha: List[Dict[str, str]] = []
        xiong_sha: List[Dict[str, str]] = []

        cls._check_tianyi(stems, branches, ji_sha)
        cls._check_wenchang(stems, branches, ji_sha)
        cls._check_lushen(stems, branches, ji_sha)
        cls._check_yangren(stems, branches, ji_sha, xiong_sha)
        cls._check_taohua(branches, ji_sha)
        cls._check_huagai(branches, ji_sha)
        cls._check_yima(branches, ji_sha)
        cls._check_hongyan(stems, branches, ji_sha)
        cls._check_guchen_guas(branches, ji_sha, xiong_sha, gender)
        cls._check_kongwang(pillars['day'], branches, xiong_sha)
        cls._check_tiande_yuede(stems, branches, ji_sha)
        # 新增神煞检查
        cls._check_jiesha(branches, xiong_sha)
        cls._check_wangshen(branches, xiong_sha)
        cls._check_goujiao(stems, branches, xiong_sha)
        cls._check_shi_e_da_bai(pillars['day'], xiong_sha)
        cls._check_leiting(birth_info, xiong_sha)
        cls._check_jianfeng(pillars, xiong_sha)
        cls._check_bingfu(birth_info, branches, xiong_sha)
        cls._check_sifu(branches, xiong_sha)

        summary = cls._summarize(ji_sha, xiong_sha)
        summary.update({
            'ji_sha': ji_sha,
            'xiong_sha': xiong_sha,
            'ji_sha_count': len(ji_sha),
            'xiong_sha_count': len(xiong_sha),
        })
        return summary

    # 判定方法
    @staticmethod
    def _translate_position(pillar: str, branch: str) -> str:
        return f"{POSITION_LABELS.get(pillar, pillar)} {branch}"

    @classmethod
    def _check_tianyi(cls, stems, branches, ji_sha):
        """
        天乙贵人：仅在年月日时四柱中检查，无位置限制。

        经典依据：
        《渊海子平》："天乙贵人最吉，逢凶化吉，遇难呈祥。"
        《三命通会》："天乙者，乃天上之神，在紫微垣、阊阖门外，与太乙并列，事天皇大帝，下游三辰，家在己丑斗牛之次，出乎己未井鬼之舍，执玉衡较量天人之事，名曰在乙也。其神最尊贵，所至之处，一切凶煞隐然而避。"

        查法：甲戊庚牛羊，乙己鼠猴乡，丙丁猪鸡位，壬癸兔蛇藏，六辛逢马虎，此是贵人方。
        """
        targets = cls.LOOKUP.TIANYI_GUIREN.get(stems['day'], [])
        for pillar, branch in branches.items():
            if branch in targets:
                cls._append(
                    ji_sha,
                    name='天乙贵人',
                    level='大吉',
                    position=cls._translate_position(pillar, branch),
                    description='天乙贵人照命，逢凶化吉，遇难呈祥。命中有贵人，一生多得他人相助。',
                    classic_source='《渊海子平》《三命通会》'
                )

    @classmethod
    def _check_wenchang(cls, stems, branches, ji_sha):
        """
        文昌贵人：仅在年月日时四柱中检查。

        经典依据：
        《渊海子平》："文昌者，食神之临官也。主聪明智慧，学业有成。"

        查法：甲乙巳午报君知，丙戊申宫丁己鸡，庚猪辛鼠壬逢虎，癸人见卯入云梯。
        """
        target = cls.LOOKUP.WENCHANG_GUIREN.get(stems['day'])
        if not target:
            return
        for pillar, branch in branches.items():
            if branch == target:
                cls._append(
                    ji_sha,
                    name='文昌贵人',
                    level='中吉',
                    position=cls._translate_position(pillar, branch),
                    description='文昌贵人，主聪明智慧，学业有成，利于科举功名。',
                    classic_source='《渊海子平》'
                )

    @classmethod
    def _check_lushen(cls, stems, branches, ji_sha):
        """
        禄神：仅在年月日时四柱中检查。

        经典依据：
        《三命通会》："禄者，爵禄也。当得势而享，乃谓之禄。"
        《渊海子平》："禄神临身，福禄丰厚。"

        查法：甲禄在寅，乙禄在卯，丙戊禄在巳，丁己禄在午，庚禄在申，辛禄在酉，壬禄在亥，癸禄在子。
        """
        target = cls.LOOKUP.LUSHEN.get(stems['day'])
        if not target:
            return
        for pillar, branch in branches.items():
            if branch == target:
                cls._append(
                    ji_sha,
                    name='禄神',
                    level='中吉',
                    position=cls._translate_position(pillar, branch),
                    description='禄神临身，福禄丰厚，主衣食无忧，财源稳定。',
                    classic_source='《三命通会》《渊海子平》'
                )

    @classmethod
    def _check_yangren(cls, stems, branches, ji_sha, xiong_sha):
        """
        羊刃：日支见为凶；其他柱见为小凶。阳干有，阴干无。

        经典依据：
        《三命通会·总论诸神煞》："羊刃者，劫财之神也。阳刃者，阳之极也，阴刃者，阴之极也。
        甲木羊刃在卯，乙木羊刃在寅，丙戊羊刃在午，丁己羊刃在巳，庚金羊刃在酉，辛金羊刃在申，
        壬水羊刃在子，癸水羊刃在亥。"

        注意：羊刃主刑伤破败，但羊刃驾杀（羊刃+七杀）可成格局。
        """
        target = cls.LOOKUP.YANGREN.get(stems['day'])
        if not target:
            return
        for pillar, branch in branches.items():
            if branch == target:
                if pillar == 'day':
                    cls._append(
                        xiong_sha,
                        name='羊刃',
                        level='大凶',
                        position=cls._translate_position(pillar, branch),
                        description='日支羊刃，性刚刑克，主刑伤破败，需谨慎行事。但羊刃驾杀可成格。',
                        classic_source='《三命通会·总论诸神煞》'
                    )
                else:
                    cls._append(
                        xiong_sha,
                        name='羊刃',
                        level='小凶',
                        position=cls._translate_position(pillar, branch),
                        description='羊刃在他柱，主性刚易怒，需注意控制情绪。',
                        classic_source='《三命通会·总论诸神煞》'
                    )

    @classmethod
    def _check_taohua(cls, branches, ji_sha):
        """
        桃花（咸池）：以年支为基准，三合法查法。

        经典依据：
        《三命通会·总论诸神煞》："咸池者，取日入之义，万物暗昧之时也。日出扶桑，入于咸池，
        故五行沐浴之地曰咸池。亥卯未在子，巳酉丑在午，申子辰在酉，寅午戌在卯。"

        注意：桃花吉凶难定，主人缘好、异性缘佳，但也易招桃花劫，需结合命局判断。
        """
        base = branches['year']
        target = cls.LOOKUP.TAOHUA.get(base)
        if not target:
            return
        for pillar, branch in branches.items():
            if branch == target:
                cls._append(
                    ji_sha,
                    name='桃花',
                    level='中性',
                    position=cls._translate_position(pillar, branch),
                    description='桃花咸池，主人缘好、异性缘佳，但也需防桃花劫，吉凶需结合命局判断。',
                    classic_source='《三命通会·总论诸神煞》'
                )

    @classmethod
    def _check_huagai(cls, branches, ji_sha):
        """
        华盖：以日支为基准，三合法查法。

        经典依据：
        《三命通会》："华盖者，喻如宝盖，天有此星其形如盖，多主孤寡，纵贵亦不免孤独。"

        查法：寅午戌见戌，亥卯未见未，申子辰见辰，巳酉丑见丑。

        注意：华盖吉凶难定，主艺术才华、清高孤傲，但也主孤独，需结合命局判断。
        """
        target = cls.LOOKUP.HUAGAI.get(branches['day'])
        if not target:
            return
        for pillar, branch in branches.items():
            if branch == target:
                cls._append(
                    ji_sha,
                    name='华盖',
                    level='中性',
                    position=cls._translate_position(pillar, branch),
                    description='华盖高概，主艺术才华、清高孤傲，但也主孤独，吉凶需结合命局判断。',
                    classic_source='《三命通会》'
                )

    @classmethod
    def _check_yima(cls, branches, ji_sha):
        """驿马：以年支为基准，四支阳数推法。主奔波迁移。《三命通会》：驿马主走动变迁。"""
        target = cls.LOOKUP.YIMA.get(branches['year'])
        if not target:
            return
        for pillar, branch in branches.items():
            if branch == target:
                cls._append(
                    ji_sha,
                    name='\u9a7f\u9a6c',
                    level='\u5c0f\u5409',
                    position=cls._translate_position(pillar, branch),
                    description='\u9a7f\u9a6c\u5f00\u901a\uff0c\u591a\u6613\u4f20\u884c\u4e0a\u4e0b\uff0c\u5904\u7406\u5916\u51fa\u4e8b\u52a1\u6709\u5229\u3002',
                    classic_source='《三命通会》'
                )

    @classmethod
    def _check_hongyan(cls, stems, branches, ji_sha):
        """红艳煞：以日干为基准推算。主异性缘。《兰台妙选》：红艳主桃花异性缘。"""
        target = cls.LOOKUP.HONGYAN.get(stems['day'])
        if not target:
            return
        for pillar, branch in branches.items():
            if branch == target:
                cls._append(
                    ji_sha,
                    name='\u7ea2\u8273\u6740',
                    level='\u5c0f\u5409',
                    position=cls._translate_position(pillar, branch),
                    description='\u7ea2\u8273\u52a8\u5fc3\uff0c\u611f\u60c5\u70ed\u7ea2\uff0c\u5fc5\u9632\u60c5\u7cbe\u7cbe\u529b\u4e0d\u7a33\u3002',
                    classic_source='《兰台妙选》'
                )

    @classmethod
    def _check_guchen_guas(cls, branches, ji_sha, xiong_sha, gender):
        """孤辰寡宿：以年支三合局为基准。女性寡宿为凶，男性为平。《三命通会》：孤辰寡宿主孤独。"""
        year_branch = branches['year']
        guchen_target = cls.LOOKUP.GUCHEN.get(year_branch)
        if guchen_target:
            for pillar, branch in branches.items():
                if pillar != 'year' and branch == guchen_target:
                    cls._append(
                        xiong_sha,
                        name='\u5b64\u8fdf',
                        level='\u5c0f\u51f6',
                        position=cls._translate_position(pillar, branch),
                        description='\u5b64\u8fdf\u9047\u573a\uff0c\u4eba\u6c14\u53d8\u51b7\uff0c\u4e92\u52a9\u5fc5\u52a0\u5fc3\u3002',
                        classic_source='《三命通会·总论诸神煞》'
                    )

        guasu_target = cls.LOOKUP.GUASU.get(year_branch)
        if guasu_target:
            for pillar, branch in branches.items():
                if pillar != 'year' and branch == guasu_target:
                    # 女性寡宿为凶，男性为平
                    level = '\u5c0f\u51f6' if gender == '\u5973' else '\u5e73'
                    desc = '\u5ac1\u5bb0\u7a33\u6b63\uff0c\u6ce8\u91cd\u7ecf\u8425\uff0c\u8c28\u9632\u60c5\u7cbe\u51b2\u649e\u3002'
                    weight = -5 if gender == '\u5973' else 0  # 女性-5分，男性0分
                    cls._append(
                        xiong_sha if level != '\u5e73' else ji_sha,
                        name='\u5b64\u5bbf',
                        level=level,
                        position=cls._translate_position(pillar, branch),
                        description=desc,
                        weight=weight
                    )

    @classmethod
    def _check_kongwang(cls, day_pillar: Tuple[str, str], branches, xiong_sha) -> None:
        """旬空（空亡）：仅检查日柱和时柱。日空为凶，时空更严重。《三命通会》：空亡主虚耗。"""
        day_ganzhi = ''.join(day_pillar)
        if day_ganzhi not in cls.LOOKUP.LIUSHI_JIAZI:
            return
        idx = cls.LOOKUP.LIUSHI_JIAZI.index(day_ganzhi)
        void_branches = cls.LOOKUP.KONGWANG_TABLE.get(day_ganzhi, [])

        # 仅检查日柱和时柱是否空亡
        for pillar in ['day', 'hour']:
            branch = branches.get(pillar)
            if branch and branch in void_branches:
                if pillar == 'hour':
                    level = '\u5927\u51f6'  # 时柱空亡更严重
                    desc = '\u65ec\u7a7a\u5165\u65f6\uff0c\u6027\u683c\u6267\u62d6\uff0c\u4e8b\u4e1a\u6f5c\u529b\u526a\u8f85\uff0c\u9700\u4e0b\u529b\u514b\u670d\u3002'
                    weight = -10  # 时柱空亡，大凶，权重-10分
                else:
                    level = '\u5c0f\u51f6'  # 日柱空亡
                    desc = '\u65ec\u7a7a\u5165\u65e5\uff0c\u5a0d\u51fa\u7279\u5f01\uff0c\u8eab\u4fd7\u6a5f\u9047\u6ac3\uff0c\u4e2b\u5987\u95bf\u9589\u3002'
                    weight = -6  # 日柱空亡，小凶，权重-6分
                cls._append(
                    xiong_sha,
                    name='\u65ec\u7a7a',
                    level=level,
                    position=cls._translate_position(pillar, branch),
                    description=desc,
                    weight=weight
                )

    @classmethod
    def _check_tiande_yuede(cls, stems, branches, ji_sha):
        """天德月德：天德以月支为基准，月德以月支为基准。需见干为吉。《三命通会》：天德月德最吉。"""
        month_branch = branches['month']

        # 天德：以月支为基准，推天干（按《三命通会·神煞篇》）
        tiande_target = cls.LOOKUP.TIANDE.get(month_branch)
        if tiande_target:
            # 检查四柱天干中是否有天德贵人
            for pillar, stem in stems.items():
                if stem == tiande_target:
                    cls._append(
                        ji_sha,
                        name='\u5929\u5fb7\u8d35\u4eba',
                        level='\u5927\u5409',
                        position=cls._translate_position(pillar, branches[pillar]),
                        description='\u5929\u5fb7\u53ca\u4eba\uff0c\u5409\u8054\u4e00\u8eab\uff0c\u4e8b\u5347\u5409\u8d24\u3002',
                        classic_source='《三命通会》'
                    )
                    break

        # 月德：以月支为基准，推天干
        yuede_target = cls.LOOKUP.YUEDE.get(month_branch)
        if yuede_target and yuede_target in stems.values():
            cls._append(
                ji_sha,
                name='\u6708\u5fb7',
                level='\u5927\u5409',
                position='\u6708\u5fb7',
                description='\u6708\u5fb7\u5149\u7167\uff0c\u5409\u559c\u52a0\u8eab\uff0c\u53ef\u53d7\u957f\u8fdb\u76c8\u3002',
                classic_source='《三命通会》'
            )

    @staticmethod
    def _append(target_list: List[Dict[str, str]], name: str, level: str, position: str, description: str, classic_source: str = ''):
        """
        添加神煞到列表

        参数说明：
        - name: 神煞名称
        - level: 等级（大吉/中吉/小吉/大凶/中凶/小凶/中性）
        - position: 位置（年柱/月柱/日柱/时柱）
        - description: 描述
        - classic_source: 经典出处（《三命通会》原文引用）

        注意：根据《三命通会》"吉凶神煞，不可拘定；轻重较量，要在通变"的原则，
        神煞的吉凶不能简单打分，需要结合整体命局和神煞组合来判断。
        """
        target_list.append({
            'name': name,
            'level': level,
            'position': position,
            'description': description,
            'classic_source': classic_source,
        })

    @staticmethod
    def _summarize(ji_sha: List[Dict[str, str]], xiong_sha: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        神煞综合总结

        基于《三命通会·神煞篇》理论：
        "吉凶神煞，不可拘定；轻重较量，要在通变。"

        因此，本方法只统计神煞数量和类型，不进行简单的数值打分。
        神煞的吉凶需要结合整体命局、神煞组合、以及具体情况来综合判断。
        """
        ji_count = len(ji_sha)
        xiong_count = len(xiong_sha)

        # 确定等级（基于吉凶神煞的数量对比，而非简单打分）
        if ji_count > xiong_count * 2:
            level = '大吉'
            description = f"吉神{ji_count}项，凶神{xiong_count}项，吉神占优"
        elif ji_count > xiong_count:
            level = '小吉'
            description = f"吉神{ji_count}项，凶神{xiong_count}项，吉多于凶"
        elif ji_count == xiong_count:
            level = '中平'
            description = f"吉神{ji_count}项，凶神{xiong_count}项，吉凶参半"
        elif xiong_count > ji_count * 2:
            level = '大凶'
            description = f"吉神{ji_count}项，凶神{xiong_count}项，凶神占优"
        else:
            level = '小凶'
            description = f"吉神{ji_count}项，凶神{xiong_count}项，凶多于吉"

        # 添加重要提示
        description += "。注：神煞吉凶需结合命局整体判断，不可拘泥于数量。"

        return {
            'level': level,
            'analysis': description,
        }

    # ✅ 修复：劫煞按三合局计算
    @classmethod
    def _check_jiesha(cls, branches, xiong_sha):
        """
        劫煞：按三合局计算。主破财、是非。
        《三命通会》："水绝在巳，申子辰以巳为劫煞；火绝在亥，寅午戌以亥为劫煞；
                      金绝在寅，巳酉丑以寅为劫煞；木绝在申，亥卯未以申为劫煞"
        
        🔥 修复：允许劫煞出现在多个位置（年柱、月柱、日柱、时柱），每个位置都记录
        """
        # 获取四柱地支
        all_branches = [branches.get('year'), branches.get('month'), branches.get('day'), branches.get('hour')]
        all_branches = [b for b in all_branches if b]  # 过滤None

        # 检查是否有三合局
        for sanhe_branches, jiesha_branch in SANHE_JIESHA_MAP.items():
            # 检查四柱中是否包含三合局的所有地支
            sanhe_count = sum(1 for b in sanhe_branches if b in all_branches)

            # 🔥 修复：传统三合局要求3个地支才算完整，只有完整三合局才能算劫煞
            # 根据《三命通会》原文，三合局必须完整（3个地支）才算成局
            if sanhe_count >= 3:  # 要求完整三合局（3个地支）
                # 🔥 修复：检查四柱中所有劫煞位（可能有多个位置）
                found_count = 0
                for pillar, branch in branches.items():
                    if branch == jiesha_branch:
                        # 找到劫煞，记录这个位置
                        sanhe_desc = ''.join(sanhe_branches)
                        cls._append(
                            xiong_sha,
                            name='劫煞',
                            level='小凶',
                            position=cls._translate_position(pillar, branch),
                            description=f'{sanhe_desc}局见{jiesha_branch}为劫煞，主破财、是非，遇此神请谨慎行事。',
                            classic_source='《三命通会·论劫煞亡神》'
                        )
                        found_count += 1
                
                # 如果找到了劫煞，检查下一个三合局（可能有多个三合局）
                if found_count > 0:
                    continue  # 继续检查下一个三合局，而不是return

    @classmethod
    def _check_wangshen(cls, branches, xiong_sha):
        """亡神煞：以年支为基准，四支阳数推法。主破财、是非。《三命通会》：亡神主破财。"""
        year_branch = branches['year']
        target = cls.LOOKUP.WANGSHEN.get(year_branch)
        if not target:
            return
        for pillar, branch in branches.items():
            if branch == target:
                cls._append(
                    xiong_sha,
                    name='\u4ea1\u795e\u786e',
                    level='\u5c0f\u51f6',
                    position=cls._translate_position(pillar, branch),
                    description='\u4ea1\u795e\u786e\u4e3b\u7834\u8d22\u3001\u662f\u975e\uff0c\u9047\u6b64\u795e\u8bf7\u8c28\u614e\u884c\u4e8b\u3002',
                    classic_source='《三命通会·总论诸神煞》'
                )

    @classmethod
    def _check_goujiao(cls, stems, branches, xiong_sha):
        """勾绞煞：以日干阴阳和性别判断。主是非、纠纷。《三命通会》：勾绞主是非。"""
        day_stem = stems['day']
        goujiao_info = cls.LOOKUP.GOUJIAO.get(day_stem)
        if not goujiao_info:
            return

        gou_target = goujiao_info['gou']
        jiao_target = goujiao_info['jiao']

        for pillar, branch in branches.items():
            if branch == gou_target:
                cls._append(
                    xiong_sha,
                    name='\u52fe\u7edd\u786e',
                    level='\u5c0f\u51f6',
                    position=cls._translate_position(pillar, branch),
                    description='\u52fe\u7edd\u786e\u4e3b\u662f\u975e\u3001\u7ea0\u7eb7\uff0c\u9047\u6b64\u795e\u8bf7\u8c28\u614e\u884c\u4e8b\u3002',
                    classic_source='《三命通会·总论诸神煞》'
                )
            elif branch == jiao_target:
                cls._append(
                    xiong_sha,
                    name='\u7edd\u52fe\u786e',
                    level='\u5c0f\u51f6',
                    position=cls._translate_position(pillar, branch),
                    description='\u7edd\u52fe\u786e\u4e3b\u662f\u975e\u3001\u7ea0\u7eb7\uff0c\u9047\u6b64\u795e\u8bf7\u8c28\u614e\u884c\u4e8b\u3002',
                    classic_source='《三命通会·总论诸神煞》'
                )

    @classmethod
    def _check_shi_e_da_bai(cls, day_pillar, xiong_sha):
        """十恶大败煞：以日柱为准。主破财、败家。《三命通会》：十恶大败主破败。"""
        day_ganzhi = ''.join(day_pillar)
        if day_ganzhi in cls.LOOKUP.SHI_E_DA_BAI:
            cls._append(
                xiong_sha,
                name='\u5341\u6076\u5927\u8d25\u7159',
                level='\u5927\u51f6',
                position=cls._translate_position('day', day_pillar[1]),
                description='\u5341\u6076\u5927\u8d25\u7159\u4e3b\u7834\u8d22\u3001\u8d25\u5bb6\uff0c\u9047\u6b64\u795e\u8bf7\u7279\u522b\u8c28\u614e\u8d22\u7269\u7ba1\u7406\u3002',
                classic_source='《渊海子平》'
            )

    @classmethod
    def _check_leiting(cls, birth_info, xiong_sha):
        """
        雷霆煞：以出生月份为准。吉凶难定，需看组合。

        经典依据：
        《三命通会·总论诸神煞》："雷霆煞。正七二八子寅方，三九四十辰午当；五十一申六二戌，必主雷轰虎咬亡。
        又云：'正七下加子，二八在寅方，三九居辰上，四十午位伤，五十一申位，六十二戌方。'正月起，子顺行六阳位。

        此煞人命遇之，如逢禄，贵；吉星临压，则吉，好行阴骘，为法官掌雷霆行符敕水之人，或成佛作祖之辈。
        如遇羊刃、的煞、飞廉等会，命限必凶，主堕于天真雷伤、虎啖、天谴、瘟疫或溺水、囹圄死。"

        注意：雷霆煞吉凶难定，遇吉星则吉，遇凶煞则凶，不可简单判断为凶煞。
        """
        month = birth_info.get('month')
        if not month:
            return

        target = cls.LOOKUP.LEITING.get(month)
        if not target:
            return

        cls._append(
            xiong_sha,  # 暂时放在凶煞列表，但level标记为中性
            name='雷霆煞',
            level='中性',  # 吉凶难定
            position=f"{month}月{target}",
            description='雷霆煞，吉凶难定。如逢禄贵吉星则吉，好行阴骘，为法官掌雷霆行符敕水之人；如遇羊刃凶煞则凶，主雷伤虎咬之灾。需结合命局整体判断。',
            classic_source='《三命通会·总论诸神煞》'
        )

    @classmethod
    def _check_jianfeng(cls, pillars, xiong_sha):
        """剑锋煞：以日柱为准。主血光、刀伤。《三命通会》：剑锋主血光。"""
        day_pillar = ''.join(pillars['day'])
        jianfeng_info = cls.LOOKUP.JIANFENG.get(day_pillar)
        if not jianfeng_info:
            return

        # 检查四柱中是否有剑或锋
        for pillar_name, (stem, branch) in pillars.items():
            if branch == jianfeng_info['jian']:
                cls._append(
                    xiong_sha,
                    name='\u5251\u950b\u786e(\u5251)',
                    level='\u5c0f\u51f6',
                    position=cls._translate_position(pillar_name, branch),
                    description='\u5251\u950b\u786e\u4e3b\u8840\u5149\u3001\u5200\u4f24\uff0c\u9047\u6b64\u795e\u8bf7\u7279\u522b\u6ce8\u610f\u5b89\u5168\u3002',
                    classic_source='《三命通会·总论诸神煞》'
                )
            elif branch == jianfeng_info['feng']:
                cls._append(
                    xiong_sha,
                    name='\u5251\u950b\u786e(\u950b)',
                    level='\u5c0f\u51f6',
                    position=cls._translate_position(pillar_name, branch),
                    description='\u5251\u950b\u786e\u4e3b\u8840\u5149\u3001\u5200\u4f24\uff0c\u9047\u6b64\u795e\u8bf7\u7279\u522b\u6ce8\u610f\u5b89\u5168\u3002',
                    classic_source='《三命通会·总论诸神煞》'
                )

    @classmethod
    def _check_bingfu(cls, birth_info, branches, xiong_sha):
        """病符煞：以出生年份地支为准。主疾病。《三命通会》：病符主疾病。"""
        year = birth_info.get('year')
        if not year:
            return

        # 简化处理，以年支为准
        year_branch = branches['year']
        target = cls.LOOKUP.BINGFU.get(year_branch)
        if not target:
            return

        for pillar, branch in branches.items():
            if branch == target:
                cls._append(
                    xiong_sha,
                    name='\u75c5\u7b26\u786e',
                    level='\u5c0f\u51f6',
                    position=cls._translate_position(pillar, branch),
                    description='\u75c5\u7b26\u786e\u4e3b\u75be\u75c5\uff0c\u9047\u6b64\u795e\u8bf7\u6ce8\u610f\u8eab\u4f53\u5065\u5eb7\u3002',
                    classic_source='《三命通会·总论诸神煞》'
                )

    @classmethod
    def _check_sifu(cls, branches, xiong_sha):
        """死符煞：以年支为准。主灾祸、死亡。《三命通会》：死符主灾祸。"""
        year_branch = branches['year']
        target = cls.LOOKUP.SIFU.get(year_branch)
        if not target:
            return

        for pillar, branch in branches.items():
            if branch == target:
                cls._append(
                    xiong_sha,
                    name='\u6b7b\u7b26\u786e',
                    level='\u5927\u51f6',
                    position=cls._translate_position(pillar, branch),
                    description='\u6b7b\u7b26\u786e\u4e3b\u707e\u7978\u3001\u6b7b\u4ea1\uff0c\u9047\u6b64\u795e\u8bf7\u7279\u522b\u8c28\u614e\u3002',
                    classic_source='《三命通会·总论诸神煞》'
                )


def analyze_shensha_complete(pillars: Dict[str, Tuple[str, str]], birth_info: Dict[str, Any]) -> Dict[str, Any]:
    return ShenShaAnalyzer.analyze_shensha(pillars, birth_info)
