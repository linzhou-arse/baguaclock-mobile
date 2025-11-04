#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
格局分析模块 - 基于《渊海子平》理论
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from classic_analyzer.common import (
    DIZHI_CANGGAN_WEIGHTS,
    TIANGAN_WUXING,
    DIZHI_WUXING,
    get_ten_god,
    clamp_score,
)


class GejuAnalyzer:
    """格局分析器 - 基于《渊海子平》理论"""
    
    # 十神关系表（基于《渊海子平》）
    TEN_GOD_RELATIONS = {
        '正官': {'description': '阴见阳为官，阳见阴为鬼', 'level': '贵'},
        '偏官': {'description': '阳见阳，阴见阴，谓之偏官', 'level': '权'},
        '正财': {'description': '阴见阳财，阳见阴财', 'level': '富'},
        '偏财': {'description': '阳见阳财，阴见阴财', 'level': '财'},
        '正印': {'description': '以阳见阴，以阴见阳，谓之正印', 'level': '文'},
        '偏印': {'description': '阳见阳，阴见阴，谓之偏印', 'level': '智'},
        '食神': {'description': '我生彼之谓也，阳见阴，阴见阳', 'level': '寿'},
        '伤官': {'description': '我生彼之谓也，阳见阳，阴见阴', 'level': '艺'},
        '比肩': {'description': '同类之阴阳，阳见阳，阴见阴', 'level': '义'},
        '劫财': {'description': '同类之阴阳，阳见阴，阴见阳', 'level': '争'},
    }
    
    # 格局等级表（基于《渊海子平》）
    # ✅ 修复：移除打分，改为成败判断
    GEJU_LEVELS = {
        '正官格': {
            'level': '上等',
            'description': '正官须在月中求，无破无伤贵不休',
            'classic': '《渊海子平》：正官格者，月令正官，无破无伤，主贵。'
        },
        '偏官格': {
            'level': '上等',
            'description': '偏官有制化为权，唾手登云发少年',
            'classic': '《渊海子平》：偏官有制化为权，无制则为七杀。'
        },
        '正财格': {
            'level': '中上',
            'description': '正财吾妻之财也，精神康强然后可以享用',
            'classic': '《渊海子平》：正财格者，月令正财，身旺财旺，主富。'
        },
        '偏财格': {
            'level': '中上',
            'description': '偏财乃众人之财也，惟恐兄弟姊妹有夺之',
            'classic': '《渊海子平》：偏财格者，月令偏财，忌比劫夺财。'
        },
        '正印格': {
            'level': '上等',
            'description': '有官无印，即非真官；有印无官，反成其福',
            'classic': '《渊海子平》：正印格者，月令正印，主文贵。'
        },
        '偏印格': {
            'level': '中等',
            'description': '偏印多智虑，兼丰厚',
            'classic': '《渊海子平》：偏印格者，月令偏印，主智慧。'
        },
        '印绶格': {
            'level': '上等',
            'description': '印绶生身，日主旺相，文贵之命',
            'classic': '《渊海子平》：印绶格者，印星生身，主文贵。'
        },
        '食神格': {
            'level': '中上',
            'description': '食神有气胜财官，先要他强旺本干',
            'classic': '《渊海子平》：食神格者，月令食神，主寿禄。'
        },
        '伤官格': {
            'level': '中等',
            'description': '伤官务要伤尽，伤之不尽，官来乘旺',
            'classic': '《渊海子平》：伤官格者，伤官务要伤尽，不见官星。'
        },
        '比肩格': {
            'level': '中等',
            'description': '比肩兄弟朋友，同类相助',
            'classic': '《渊海子平》：比肩格者，月令比肩，喜财官食伤。'
        },
        '劫财格': {
            'level': '中下',
            'description': '劫财破耗防小人，不克妻',
            'classic': '《渊海子平》：劫财格者，月令劫财，忌财星。'
        },
        '建禄格': {
            'level': '中等',
            'description': '建禄身旺，喜财官食伤，忌比劫重叠',
            'classic': '《渊海子平》：建禄格者，月令建禄，身旺喜泄耗。'
        },
        '伤官配印格': {
            'level': '上上等',
            'description': '伤官配印，贵不可言，主科名仕途，福禄双全',
            'classic': '《子平真诠》：伤官配印，贵不可言。《渊海子平》：伤官配印，科甲有准。'
        },
        '食神制杀格': {
            'level': '上等',
            'description': '食神制杀，权贵显达，主武职或领导才能',
            'classic': '《子平真诠》：食神制杀，权贵显达。《滴天髓》：食神制杀，功名显达。'
        },
        '财官双美格': {
            'level': '上等',
            'description': '财官双美，富贵双全，主名利双收',
            'classic': '《渊海子平》：财官双美，富贵双全。《三命通会》：财官双美，名利双收。'
        },
        '官印相生格': {
            'level': '上等',
            'description': '官印相生，贵气可期，主文贵仕途',
            'classic': '《渊海子平》：官印相生，贵气可期。《子平真诠》：官印相生，文贵仕途。'
        },
        # 🔥 新增：特殊命格和贵格
        '魁罡格': {
            'level': '上等',
            'description': '魁罡格，主聪慧果断，刚烈不屈，忌见财官',
            'classic': '《三命通会》：魁罡格，刚烈不屈，忌见财官。《兰台妙选》：魁罡格，主聪慧果断。'
        },
        '日禄格': {
            'level': '上等',
            'description': '日禄格，主衣禄丰足，自立自强，喜见财官',
            'classic': '《三命通会》：日禄格，主衣禄丰足。《兰台妙选》：日禄格，喜见财官。'
        },
        '日德格': {
            'level': '上等',
            'description': '日德格，主聪慧仁厚，德行高尚，忌刑冲',
            'classic': '《三命通会》：日德格，主聪慧仁厚。《兰台妙选》：日德格，忌刑冲。'
        },
        '金神格': {
            'level': '上等',
            'description': '金神格，主刚毅果敢，需火制方吉',
            'classic': '《三命通会》：金神格，主刚毅果敢。《兰台妙选》：金神格，需火制方吉。'
        },
        '六秀格': {
            'level': '上等',
            'description': '六秀格，主聪明秀丽，才华横溢',
            'classic': '《兰台妙选》：六秀格，主聪明秀丽，才华横溢。'
        },
        '福德格': {
            'level': '上等',
            'description': '福德格，主福禄双全，平安顺遂',
            'classic': '《兰台妙选》：福德格，主福禄双全，平安顺遂。'
        },
    }
    
    @classmethod
    def analyze_geju(cls, pillars: Dict[str, Tuple[str, str]], day_master: Optional[str] = None) -> Dict[str, Any]:
        """
        格局分析 - 基于《渊海子平》理论
        
        参数:
            pillars: 四柱信息 {'year': ('甲','子'), 'month': ('乙','丑'), 'day': ('丙','寅'), 'hour': ('丁','卯')}
            day_master: 日主，如果为None则从日柱提取
        
        返回:
            格局分析结果
        """
        if not pillars or 'day' not in pillars:
            raise ValueError('分析格局需要完整的四柱信息')
        
        day_master = day_master or pillars['day'][0]
        month_branch = pillars['month'][1]
        
        # 1. 分析月令用神（基于《渊海子平》理论）
        month_yongshen = cls._analyze_month_yongshen(day_master, month_branch, pillars)
        
        # 2. 分析格局类型
        geju_type = cls._determine_geju_type(day_master, month_branch, pillars)
        
        # 3. 分析格局强弱
        geju_strength = cls._analyze_geju_strength(day_master, pillars)
        
        # 4. 分析格局喜忌
        geju_xiji = cls._analyze_geju_xiji(day_master, geju_type, pillars)

        # ✅ 5. 判断格局成败（不打分）
        geju_chengbai = cls._judge_geju_chengbai(geju_type, geju_strength, month_yongshen, pillars, day_master)

        return {
            'geju_type': geju_type,
            'geju_level': cls._get_geju_level(geju_type),
            'chengbai': geju_chengbai['chengbai'],  # 格局成败
            'month_yongshen': month_yongshen,
            'geju_strength': geju_strength,
            'geju_xiji': geju_xiji,
            'description': cls._get_geju_description(geju_type, geju_strength),
            'advice': cls._get_geju_advice(geju_type, geju_strength, geju_xiji),
            'classic_basis': geju_chengbai['classic_basis'],  # 经典依据

            # ✅ 三关判断（不打分，只判断成败）
            'huwei_level': geju_chengbai['huwei'],
            'zhenjia_level': geju_chengbai['zhenjia'],
            'qingzhuo_level': geju_chengbai['qingzhuo'],
        }
    
    @classmethod
    def _analyze_month_yongshen(cls, day_master: str, month_branch: str, pillars: Dict[str, Tuple[str, str]]) -> Dict[str, Any]:
        """分析月令用神 - 基于《渊海子平》理论"""
        # 月令用神分析
        month_gan = pillars['month'][0]
        month_ten_god = get_ten_god(day_master, month_gan)
        
        # 分析月令藏干
        month_canggan = DIZHI_CANGGAN_WEIGHTS.get(month_branch, [])
        
        # 分析月令旺衰
        month_wangshuai = cls._analyze_wangshuai(day_master, month_branch)
        
        return {
            'month_gan': month_gan,
            'month_ten_god': month_ten_god,
            'month_canggan': month_canggan,
            'month_wangshuai': month_wangshuai,
            'yongshen_type': cls._determine_yongshen_type(month_ten_god),
            'yongshen_strength': cls._calculate_yongshen_strength(day_master, month_ten_god, month_canggan),
        }
    
    @classmethod
    def _determine_geju_type(cls, day_master: str, month_branch: str, pillars: Dict[str, Tuple[str, str]]) -> str:
        """
        确定格局类型 - 基于《子平真诠》理论
        改进：综合考虑月令藏干、五行强弱、透干情况
        """
        month_gan = pillars['month'][0]
        
        # 1. 分析月令藏干（最重要）
        month_canggan = DIZHI_CANGGAN_WEIGHTS.get(month_branch, [])
        if not month_canggan:
            # 无藏干数据时，退回到月干判断
            month_ten_god = get_ten_god(day_master, month_gan)
            return f'{month_ten_god}格' if month_ten_god else '特殊格'
        
        # 2. 找出月令主气（藏干权重最大的）
        main_canggan = max(month_canggan, key=lambda x: x[1])[0]
        main_ten_god = get_ten_god(day_master, main_canggan)
        
        # 3. 统计四柱五行分布（判断身强弱）
        day_master_wuxing = TIANGAN_WUXING.get(day_master, '')
        wuxing_count = {}
        
        # 统计天干五行
        for pos in ['year', 'month', 'day', 'hour']:
            gan = pillars[pos][0]
            wx = TIANGAN_WUXING.get(gan, '')
            if wx:
                wuxing_count[wx] = wuxing_count.get(wx, 0) + 1.0
        
        # 统计地支藏干五行（带权重）
        for pos in ['year', 'month', 'day', 'hour']:
            zhi = pillars[pos][1]
            canggan_list = DIZHI_CANGGAN_WEIGHTS.get(zhi, [])
            for cg, weight in canggan_list:
                wx = TIANGAN_WUXING.get(cg, '')
                if wx:
                    wuxing_count[wx] = wuxing_count.get(wx, 0) + weight * 0.5  # 藏干权重减半
        
        # 计算日主五行总强度
        day_master_total = wuxing_count.get(day_master_wuxing, 0)
        total_wuxing = sum(wuxing_count.values())
        day_master_ratio = day_master_total / total_wuxing if total_wuxing > 0 else 0
        
        # 4. 根据《子平真诠》原则判断格局
        # 原则：月令为先，透干次之，身强身弱再次之
        
        # 🔥 修复：优先识别特殊命格和贵格（日柱特殊格局、从格、化格等）
        # 4.0.0 检查日柱特殊格局（魁罡、日禄、日德、金神、六秀、福德等）
        day_gan = pillars['day'][0]
        day_zhi = pillars['day'][1]
        day_pillar = (day_gan, day_zhi)
        
        # 魁罡格（日柱）
        kuigang_pillars = {('庚','辰'), ('庚','戌'), ('壬','辰'), ('壬','戌')}
        if day_pillar in kuigang_pillars:
            # 检查是否符合魁罡格条件（忌财官）
            caixing_count = 0
            guanxing_count = 0
            for pos in ['year', 'month', 'hour']:
                gan = pillars[pos][0]
                ten_god = get_ten_god(day_master, gan)
                if ten_god in ['正财', '偏财']:
                    caixing_count += 1
                elif ten_god in ['正官', '偏官']:
                    guanxing_count += 1
            if caixing_count == 0 and guanxing_count == 0:
                return '魁罡格'  # 魁罡格成立
        
        # 日禄格（日柱）- 日干坐禄位
        rilu_pillars = {('甲','寅'), ('乙','卯'), ('丙','巳'), ('丁','午'), 
                        ('戊','巳'), ('己','午'), ('庚','申'), ('辛','酉'), ('壬','亥'), ('癸','子')}
        if day_pillar in rilu_pillars:
            # 检查是否符合日禄格条件（喜财官）
            caixing_count = 0
            guanxing_count = 0
            for pos in ['year', 'month', 'hour']:
                gan = pillars[pos][0]
                ten_god = get_ten_god(day_master, gan)
                if ten_god in ['正财', '偏财']:
                    caixing_count += 1
                elif ten_god in ['正官', '偏官']:
                    guanxing_count += 1
            if caixing_count >= 1 or guanxing_count >= 1:
                return '日禄格'  # 日禄格成立
        
        # 日德格（日柱）
        ride_pillars = {('甲','寅'), ('丙','辰'), ('戊','辰'), ('庚','辰'), ('壬','戌')}
        if day_pillar in ride_pillars:
            # 检查是否有刑冲（简化判断）
            return '日德格'
        
        # 金神格（日柱）
        jinshen_pillars = {('癸','巳'), ('己','巳'), ('乙','丑')}
        if day_pillar in jinshen_pillars:
            # 检查是否有火制（简化判断：看是否有火）
            has_fire = False
            for pos in ['year', 'month', 'hour']:
                gan = pillars[pos][0]
                if TIANGAN_WUXING.get(gan) == '火':
                    has_fire = True
                    break
            if has_fire:
                return '金神格'  # 金神格成立
        
        # 六秀格（日柱）
        liuxiu_pillars = {('丙','午'), ('丁','未'), ('戊','午'), ('己','未'), ('庚','辰'), ('辛','巳')}
        if day_pillar in liuxiu_pillars:
            return '六秀格'
        
        # 福德格（日柱）
        fude_pillars = {('甲','子'), ('乙','亥'), ('丙','寅'), ('丁','卯'), 
                        ('戊','午'), ('己','巳'), ('庚','申'), ('辛','酉'), ('壬','子'), ('癸','亥')}
        if day_pillar in fude_pillars:
            return '福德格'
        
        # 🔥 修复：优先检查五行过旺特殊情况（土多金埋、水多木漂等）
        # 如果存在五行过旺导致日主被埋的情况，不应该判断为普通格局
        WUXING_EXCESS_THRESHOLD = 3.5
        WUXING_BURIED_MAP = {
            '土': {'buried': '金'},  # 土多金埋
            '水': {'buried': '木'},  # 水多木漂
            '火': {'buried': '土'},  # 火多土焦
            '木': {'buried': '火'},  # 木多火塞
            '金': {'buried': '水'},  # 金多水浊
        }
        
        # 检查是否有五行过旺且埋克日主
        has_excess_buried = False
        for element, threshold in [('土', WUXING_EXCESS_THRESHOLD), ('水', WUXING_EXCESS_THRESHOLD),
                                   ('火', WUXING_EXCESS_THRESHOLD), ('木', WUXING_EXCESS_THRESHOLD),
                                   ('金', WUXING_EXCESS_THRESHOLD)]:
            if wuxing_count.get(element, 0) >= threshold:
                buried_info = WUXING_BURIED_MAP.get(element, {})
                if buried_info.get('buried') == day_master_wuxing:
                    has_excess_buried = True
                    break
        
        # 🔥 修复：优先识别高级格局（伤官配印、食神制杀、财官双美、官印相生等）
        # 统计十神分布
        shishen_stats = {
            '伤官': 0, '食神': 0, '正印': 0, '偏印': 0,
            '正官': 0, '偏官': 0, '正财': 0, '偏财': 0,
            '比肩': 0, '劫财': 0
        }
        
        # 统计天干十神
        for pos in ['year', 'month', 'day', 'hour']:
            gan = pillars[pos][0]
            ten_god = get_ten_god(day_master, gan)
            if ten_god in shishen_stats:
                shishen_stats[ten_god] += 1
        
        # 统计地支十神（主气和中气）
        for pos in ['year', 'month', 'day', 'hour']:
            zhi = pillars[pos][1]
            canggan_list = DIZHI_CANGGAN_WEIGHTS.get(zhi, [])
            for cg, weight in canggan_list:
                if weight >= 0.3:  # 只统计主气和中气
                    ten_god = get_ten_god(day_master, cg)
                    if ten_god in shishen_stats:
                        shishen_stats[ten_god] += weight * 0.5
        
        # 4.0.1 检查伤官配印格局（上等格局）
        # 🔥 修复：如果存在五行过旺导致日主被埋的情况，不判断为伤官配印格
        # 因为这种情况下，印星过多反而有害，不是"配印"的格局
        yinxing_total = shishen_stats['正印'] + shishen_stats['偏印']
        if not has_excess_buried and shishen_stats['伤官'] >= 1 and yinxing_total >= 2.0:
            if yinxing_total < 4.0:  # 印星多但不能太多
                # 🔥 修复：还要检查伤官是否被过度克制
                # 如果伤官被印星重重克制，失去作用，也不应该判断为伤官配印格
                # 简化判断：如果印星强度远大于伤官（3倍以上），则伤官被埋，格局不成立
                shangguan_strength = shishen_stats['伤官']
                if yinxing_total < shangguan_strength * 3:  # 印星不能过度克制伤官
                    return '伤官配印格'
        
        # 4.0.2 检查食神制杀格局（上等格局）
        if shishen_stats['食神'] >= 1 and shishen_stats['偏官'] >= 1:
            # 食神制杀：食神透出，七杀也透出或在地支
            return '食神制杀格'
        
        # 4.0.3 检查财官双美格局（上等格局）
        caixing_total = shishen_stats['正财'] + shishen_stats['偏财']
        guanxing_total = shishen_stats['正官'] + shishen_stats['偏官']
        if caixing_total >= 1 and guanxing_total >= 1:
            # 财官双美：财星和官星都透出或在地支
            return '财官双美格'
        
        # 4.0.4 检查官印相生格局（上等格局）
        if shishen_stats['正官'] >= 1 and yinxing_total >= 1:
            # 官印相生：正官透出，印星也透出或在地支
            return '官印相生格'
        
        # 4.1 如果月干透出主气十神，优先按透出的定格
        month_ten_god = get_ten_god(day_master, month_gan)
        if month_ten_god == main_ten_god:
            # 月干透出主气，格局纯正
            return f'{month_ten_god}格'
        
        # 4.2 月干未透主气，按五行强弱和主气综合判断
        # 如果日主极旺（≥40%），且主气为印星或比劫，可能是从印格、从比格
        if day_master_ratio >= 0.4:
            if main_ten_god in ['正印', '偏印']:
                return '印绶格'  # 或称"印格"
            elif main_ten_god in ['比肩', '劫财']:
                return '建禄格'  # 或称"比劫格"
        
        # 4.3 日主偏弱（<25%），优先取印星和比劫为用
        if day_master_ratio < 0.25:
            # 看月令主气是否为印星或比劫
            if main_ten_god in ['正印', '偏印', '比肩', '劫财']:
                return f'{main_ten_god}格'
            else:
                # 月令不是印比，但日主弱，仍按月令主气定格
                return f'{main_ten_god}格'
        
        # 4.4 日主适中，按月令主气定格
        return f'{main_ten_god}格' if main_ten_god else '特殊格'
    
    @classmethod
    def _analyze_geju_strength(cls, day_master: str, pillars: Dict[str, Tuple[str, str]]) -> Dict[str, Any]:
        """分析格局强弱 - 基于《渊海子平》理论"""
        # 分析日主强弱
        day_master_strength = cls._analyze_day_master_strength(day_master, pillars)
        
        # 分析用神强弱
        yongshen_strength = cls._analyze_yongshen_strength(day_master, pillars)
        
        # 分析格局平衡
        balance = cls._analyze_geju_balance(day_master, pillars)
        
        return {
            'day_master_strength': day_master_strength,
            'yongshen_strength': yongshen_strength,
            'balance': balance,
            'overall_strength': cls._calculate_overall_strength(day_master_strength, yongshen_strength, balance),
        }
    
    @classmethod
    def _analyze_geju_xiji(cls, day_master: str, geju_type: str, pillars: Dict[str, Tuple[str, str]]) -> Dict[str, Any]:
        """分析格局喜忌 - 基于《渊海子平》理论"""
        # 分析喜神
        xishen = cls._analyze_xishen(day_master, geju_type, pillars)
        
        # 分析忌神
        jishen = cls._analyze_jishen(day_master, geju_type, pillars)
        
        # 分析用神
        yongshen = cls._analyze_yongshen(day_master, geju_type, pillars)
        
        return {
            'xishen': xishen,
            'jishen': jishen,
            'yongshen': yongshen,
            'xiji_balance': cls._calculate_xiji_balance(xishen, jishen, yongshen),
        }
    
    @classmethod
    def _analyze_wangshuai(cls, day_master: str, month_branch: str) -> str:
        """分析旺衰 - 基于《渊海子平》理论"""
        # 简化版旺衰分析
        day_master_wuxing = TIANGAN_WUXING.get(day_master, '')
        month_branch_wuxing = DIZHI_WUXING.get(month_branch, '')
        
        if day_master_wuxing == month_branch_wuxing:
            return '旺'
        elif month_branch_wuxing in ['木', '火', '土', '金', '水']:
            # 根据五行生克关系判断
            if month_branch_wuxing in ['木', '火'] and day_master_wuxing in ['木', '火']:
                return '旺'
            elif month_branch_wuxing in ['金', '水'] and day_master_wuxing in ['金', '水']:
                return '旺'
            else:
                return '衰'
        else:
            return '平'
    
    @classmethod
    def _determine_yongshen_type(cls, month_ten_god: str) -> str:
        """确定用神类型"""
        if month_ten_god in ['正官', '偏官']:
            return '官杀'
        elif month_ten_god in ['正财', '偏财']:
            return '财星'
        elif month_ten_god in ['正印', '偏印']:
            return '印星'
        elif month_ten_god in ['食神', '伤官']:
            return '食伤'
        elif month_ten_god in ['比肩', '劫财']:
            return '比劫'
        else:
            return '特殊'
    
    @classmethod
    def _calculate_yongshen_strength(cls, day_master: str, month_ten_god: str, month_canggan: List[Tuple[str, float]]) -> float:
        """
        计算用神强度
        🔥 修复：使用真实日主而不是固定 '甲'
        """
        base_strength = 0.5
        for gan, weight in month_canggan:
            # 使用传入的真实日主计算十神
            if get_ten_god(day_master, gan) == month_ten_god:
                base_strength += weight * 0.3
        return min(base_strength, 1.0)
    
    @classmethod
    def _analyze_day_master_strength(cls, day_master: str, pillars: Dict[str, Tuple[str, str]]) -> str:
        """分析日主强弱"""
        # 简化版日主强弱分析
        day_master_wuxing = TIANGAN_WUXING.get(day_master, '')
        month_branch_wuxing = DIZHI_WUXING.get(pillars['month'][1], '')
        
        if day_master_wuxing == month_branch_wuxing:
            return '旺'
        else:
            return '衰'
    
    @classmethod
    def _analyze_yongshen_strength(cls, day_master: str, pillars: Dict[str, Tuple[str, str]]) -> str:
        """分析用神强弱"""
        # 简化版用神强弱分析
        return '中'
    
    @classmethod
    def _analyze_geju_balance(cls, day_master: str, pillars: Dict[str, Tuple[str, str]]) -> str:
        """分析格局平衡"""
        # 简化版格局平衡分析
        return '平衡'
    
    @classmethod
    def _calculate_overall_strength(cls, day_master_strength: str, yongshen_strength: str, balance: str) -> str:
        """计算整体强弱"""
        if day_master_strength == '旺' and yongshen_strength == '旺' and balance == '平衡':
            return '强'
        elif day_master_strength == '衰' and yongshen_strength == '衰':
            return '弱'
        else:
            return '中'
    
    @classmethod
    def _analyze_xishen(cls, day_master: str, geju_type: str, pillars: Dict[str, Tuple[str, str]]) -> List[str]:
        """分析喜神"""
        # 🔥 修复：高级格局和特殊命格的喜神判断
        if geju_type == '伤官配印格':
            return ['印星', '比劫']  # 伤官配印：喜印星护身，比劫帮身
        elif geju_type == '食神制杀格':
            return ['食神', '财星']  # 食神制杀：喜食神制杀，财星生食神
        elif geju_type == '财官双美格':
            return ['官杀', '印星']  # 财官双美：喜官杀护财，印星护官
        elif geju_type == '官印相生格':
            return ['官杀', '印星']  # 官印相生：喜官杀生印，印星护官
        elif geju_type == '魁罡格':
            return ['比劫', '食伤']  # 魁罡格：喜比劫帮身，食伤泄秀，忌财官
        elif geju_type == '日禄格':
            return ['财星', '官杀']  # 日禄格：喜财官，忌比劫夺财
        elif geju_type == '日德格':
            return ['印星', '官杀']  # 日德格：喜印星、官杀，忌刑冲
        elif geju_type == '金神格':
            return ['火', '官杀']  # 金神格：喜火制，喜官杀
        elif geju_type == '六秀格':
            return ['印星', '官杀']  # 六秀格：喜印星、官杀
        elif geju_type == '福德格':
            return ['印星', '官杀']  # 福德格：喜印星、官杀
        # 基于格局类型分析喜神
        elif '官' in geju_type:
            return ['印星', '比劫']
        elif '财' in geju_type:
            return ['食伤', '官杀']
        elif '印' in geju_type:
            return ['官杀', '比劫']
        elif '食' in geju_type or '伤' in geju_type:
            return ['财星', '比劫']
        else:
            return ['印星', '比劫']
    
    @classmethod
    def _analyze_jishen(cls, day_master: str, geju_type: str, pillars: Dict[str, Tuple[str, str]]) -> List[str]:
        """分析忌神"""
        # 🔥 修复：高级格局和特殊命格的忌神判断
        if geju_type == '伤官配印格':
            return ['财星', '官杀']  # 伤官配印：忌财星破印，官杀与伤官相冲
        elif geju_type == '食神制杀格':
            return ['印星', '比劫']  # 食神制杀：忌印星制食神，比劫生杀
        elif geju_type == '财官双美格':
            return ['比劫', '食伤']  # 财官双美：忌比劫夺财，食伤克官
        elif geju_type == '官印相生格':
            return ['财星', '食伤']  # 官印相生：忌财星破印，食伤克官
        elif geju_type == '魁罡格':
            return ['财星', '官杀']  # 魁罡格：忌财官
        elif geju_type == '日禄格':
            return ['比劫', '印星']  # 日禄格：忌比劫夺财，印星过多
        elif geju_type == '日德格':
            return ['财星', '比劫']  # 日德格：忌财星破印，比劫争财
        elif geju_type == '金神格':
            return ['水', '金']  # 金神格：忌水，忌金多
        elif geju_type == '六秀格':
            return ['比劫', '食伤']  # 六秀格：忌比劫争财，食伤泄秀过多
        elif geju_type == '福德格':
            return ['比劫', '食伤']  # 福德格：忌比劫争财，食伤泄秀过多
        # 基于格局类型分析忌神
        elif '官' in geju_type:
            return ['食伤', '财星']
        elif '财' in geju_type:
            return ['比劫', '印星']
        elif '印' in geju_type:
            return ['财星', '食伤']
        elif '食' in geju_type or '伤' in geju_type:
            return ['印星', '官杀']
        else:
            return ['食伤', '财星']
    
    @classmethod
    def _analyze_yongshen(cls, day_master: str, geju_type: str, pillars: Dict[str, Tuple[str, str]]) -> List[str]:
        """分析用神"""
        # 基于格局类型分析用神
        if '官' in geju_type:
            return ['印星', '比劫']
        elif '财' in geju_type:
            return ['食伤', '官杀']
        elif '印' in geju_type:
            return ['官杀', '比劫']
        elif '食' in geju_type or '伤' in geju_type:
            return ['财星', '比劫']
        else:
            return ['印星', '比劫']
    
    @classmethod
    def _calculate_xiji_balance(cls, xishen: List[str], jishen: List[str], yongshen: List[str]) -> str:
        """计算喜忌平衡"""
        if len(xishen) > len(jishen):
            return '喜神多'
        elif len(jishen) > len(xishen):
            return '忌神多'
        else:
            return '平衡'
    
    @classmethod
    def _judge_geju_chengbai(cls, geju_type: str, geju_strength: Dict[str, Any],
                             month_yongshen: Dict[str, Any], pillars: Dict[str, Tuple[str, str]],
                             day_master: str) -> Dict[str, Any]:
        """
        判断格局成败 - 基于《渊海子平》理论
        ✅ 修复：不打分，只判断成败

        传统命理不打分，只论格局成败：
        1. 护卫关：用神是否有护卫
        2. 真假关：格局是否成立（月令透出、无破坏）
        3. 清浊关：五行是否清纯
        """
        # 1. 护卫关判断
        huwei = cls._judge_huwei(day_master, pillars, geju_type)

        # 2. 真假关判断
        zhenjia = cls._judge_zhenjia(geju_type, pillars, pillars['month'][1])

        # 3. 清浊关判断
        qingzhuo = cls._judge_qingzhuo(pillars, day_master)

        # 🔥 修复：高级格局和特殊命格直接判断为格局大成
        special_geju_list = ['伤官配印格', '食神制杀格', '财官双美格', '官印相生格',
                            '魁罡格', '日禄格', '日德格', '金神格', '六秀格', '福德格']
        if geju_type in special_geju_list:
            chengbai = '格局大成'
            if geju_type == '伤官配印格':
                classic_basis = '《子平真诠》：伤官配印，贵不可言。《渊海子平》：伤官配印，科甲有准，福禄双全。'
            elif geju_type == '食神制杀格':
                classic_basis = '《子平真诠》：食神制杀，权贵显达。《滴天髓》：食神制杀，功名显达。'
            elif geju_type == '财官双美格':
                classic_basis = '《渊海子平》：财官双美，富贵双全。《三命通会》：财官双美，名利双收。'
            elif geju_type == '官印相生格':
                classic_basis = '《渊海子平》：官印相生，贵气可期。《子平真诠》：官印相生，文贵仕途。'
            elif geju_type == '魁罡格':
                classic_basis = '《三命通会》：魁罡格，刚烈不屈，忌见财官。《兰台妙选》：魁罡格，主聪慧果断。'
            elif geju_type == '日禄格':
                classic_basis = '《三命通会》：日禄格，主衣禄丰足。《兰台妙选》：日禄格，喜见财官。'
            elif geju_type == '日德格':
                classic_basis = '《三命通会》：日德格，主聪慧仁厚。《兰台妙选》：日德格，忌刑冲。'
            elif geju_type == '金神格':
                classic_basis = '《三命通会》：金神格，主刚毅果敢。《兰台妙选》：金神格，需火制方吉。'
            elif geju_type == '六秀格':
                classic_basis = '《兰台妙选》：六秀格，主聪明秀丽，才华横溢。'
            elif geju_type == '福德格':
                classic_basis = '《兰台妙选》：福德格，主福禄双全，平安顺遂。'
        # 综合判断格局成败
        # ✅ 修正：真假关"格局成立" + 清浊关"较清" → 应该是"格局成立"
        elif zhenjia == '格局成立' and huwei == '有护卫' and qingzhuo in ['清', '较清']:
            chengbai = '格局大成'
            classic_basis = '《渊海子平》：格局成立，有护卫，五行清纯，格局大成。'
        elif zhenjia == '格局成立' and (huwei == '有护卫' or qingzhuo in ['清', '较清']):
            chengbai = '格局成立'
            classic_basis = '《渊海子平》：格局成立，有护卫或五行清纯，格局成立。'
        elif zhenjia == '格局成立' and qingzhuo == '中':
            chengbai = '格局勉强'
            classic_basis = '《渊海子平》：格局成立，但无护卫且五行中和，格局勉强。'
        elif zhenjia == '格局成立':
            chengbai = '格局勉强'
            classic_basis = '《渊海子平》：格局成立，但无护卫且五行混杂，格局勉强。'
        elif zhenjia == '格局有瑕':
            chengbai = '格局有瑕'
            classic_basis = '《渊海子平》：格局有瑕疵，需大运补救。'
        else:
            chengbai = '格局破败'
            classic_basis = '《渊海子平》：格局不成立或有破格，格局破败。'

        return {
            'chengbai': chengbai,
            'huwei': huwei,
            'zhenjia': zhenjia,
            'qingzhuo': qingzhuo,
            'classic_basis': classic_basis,
        }
    
    @classmethod
    def _get_geju_level(cls, geju_type: str) -> str:
        """
        获取格局等级 - 基于《渊海子平》理论
        ✅ 修复：不打分，直接返回格局等级
        """
        return cls.GEJU_LEVELS.get(geju_type, {}).get('level', '中等')
    
    @classmethod
    def _get_geju_description(cls, geju_type: str, geju_strength: Dict[str, Any]) -> str:
        """获取格局描述"""
        base_desc = cls.GEJU_LEVELS.get(geju_type, {}).get('description', '特殊格局')
        strength_desc = f"，格局{geju_strength.get('overall_strength', '中')}等"
        return base_desc + strength_desc
    
    @classmethod
    def _get_geju_advice(cls, geju_type: str, geju_strength: Dict[str, Any], geju_xiji: Dict[str, Any]) -> str:
        """获取格局建议"""
        if geju_strength.get('overall_strength') == '强':
            return '格局强旺，宜顺势而为，可考虑扩张发展'
        elif geju_strength.get('overall_strength') == '弱':
            return '格局偏弱，宜保守稳健，注重积累与提升'
        else:
            return '格局平衡，宜稳中求进，注重协调与配合'

    # ✅ 修复：添加三关判断方法（不打分）

    @classmethod
    def _judge_huwei(cls, day_master: str, pillars: Dict[str, Tuple[str, str]], geju_type: str) -> str:
        """
        护卫关判断 - 基于《渊海子平》理论
        护卫关：检查用神是否有护卫（印星、比劫等）
        ✅ 修复：不打分，只判断有无护卫
        """
        # 提取所有天干
        all_gans = [pillars['year'][0], pillars['month'][0], pillars['day'][0], pillars['hour'][0]]

        # 统计护卫数量
        huwei_count = 0

        # 根据格局类型判断需要的护卫
        if '官' in geju_type:
            # 官格需要印星护卫（官印相生）
            for gan in all_gans:
                ten_god = get_ten_god(day_master, gan)
                if ten_god in ['正印', '偏印']:
                    huwei_count += 1
        elif '财' in geju_type:
            # 财格需要食伤护卫（食伤生财）
            for gan in all_gans:
                ten_god = get_ten_god(day_master, gan)
                if ten_god in ['食神', '伤官']:
                    huwei_count += 1
        elif '印' in geju_type:
            # 印格需要官杀护卫（官印相生）
            for gan in all_gans:
                ten_god = get_ten_god(day_master, gan)
                if ten_god in ['正官', '偏官']:
                    huwei_count += 1
        elif '食' in geju_type or '伤' in geju_type:
            # 食伤格需要财星护卫（食伤生财）
            for gan in all_gans:
                ten_god = get_ten_god(day_master, gan)
                if ten_god in ['正财', '偏财']:
                    huwei_count += 1

        # 判断护卫情况
        if huwei_count >= 2:
            return '有护卫'
        elif huwei_count == 1:
            return '护卫弱'
        else:
            return '无护卫'

    @classmethod
    def _judge_zhenjia(cls, geju_type: str, pillars: Dict[str, Tuple[str, str]], month_branch: str) -> str:
        """
        真假关判断 - 基于《渊海子平》理论
        真假关：检查格局是否成立（月令透出、无破坏等）
        ✅ 修复：不打分，只判断成败
        """
        # 检查月令是否透出
        month_gan = pillars['month'][0]

        # 检查是否有破格因素
        day_master = pillars['day'][0]
        all_gans = [pillars['year'][0], pillars['month'][0], pillars['hour'][0]]

        # 统计破格因素数量
        break_count = 0

        # 官格怕伤官（伤官见官，为祸百端）
        if '正官' in geju_type:
            for gan in all_gans:
                ten_god = get_ten_god(day_master, gan)
                if ten_god == '伤官':
                    break_count += 1

        # 财格怕比劫（比劫夺财）
        if '财' in geju_type:
            for gan in all_gans:
                ten_god = get_ten_god(day_master, gan)
                if ten_god in ['比肩', '劫财']:
                    break_count += 1

        # 印格怕财星（财坏印）
        if '印' in geju_type:
            for gan in all_gans:
                ten_god = get_ten_god(day_master, gan)
                if ten_god in ['正财', '偏财']:
                    break_count += 1

        # 判断格局真假
        if month_gan and break_count == 0:
            return '格局成立'
        elif month_gan and break_count == 1:
            return '格局有瑕'
        elif month_gan:
            return '格局破败'
        else:
            return '格局虚浮'

    @classmethod
    def _judge_qingzhuo(cls, pillars: Dict[str, Tuple[str, str]], day_master: str) -> str:
        """
        清浊关判断 - 基于《渊海子平》理论
        清浊关：检查五行是否清浊（杂气、混杂等）
        ✅ 修复：不打分，只判断清浊
        """
        # 统计五行分布
        wuxing_count = {}
        all_gans = [pillars['year'][0], pillars['month'][0], pillars['day'][0], pillars['hour'][0]]

        for gan in all_gans:
            wuxing = TIANGAN_WUXING.get(gan, '')
            if wuxing:
                wuxing_count[wuxing] = wuxing_count.get(wuxing, 0) + 1

        # 五行种类越少越清
        wuxing_types = len(wuxing_count)

        # 检查是否有主导五行
        max_count = max(wuxing_count.values()) if wuxing_count else 0

        # 判断清浊
        if wuxing_types <= 2 and max_count >= 3:
            return '清'  # 五行纯粹，有主导
        elif wuxing_types == 3 and max_count >= 2:
            return '较清'  # 三种五行，有主导
        elif wuxing_types <= 3:
            return '中'  # 三种五行，无主导
        elif wuxing_types == 4:
            return '较浊'  # 四种五行
        else:
            return '浊'  # 五行混杂
