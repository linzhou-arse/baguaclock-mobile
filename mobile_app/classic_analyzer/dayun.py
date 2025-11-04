#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大运分析模块

依据：
《三命通会》卷一〈论大运〉、〈论天月德〉
《渊海子平》大运总论
《子平真诠》日主强弱取用
《滴天髓》身旺身弱取舍
《穷通宝鉴》旺衰平衡原则

核心改动：
1. 起运年龄按节气实差 ÷ 3 计算（精确到小时）
2. 顺逆行以年干阴阳与性别确定，首步大运从月柱干支顺/逆推
3. 大运干支列表包含每步十神、五行贡献、精确起止年龄
4. 吉凶评估结合日主强弱、干支五行权重与十神取舍
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

try:
    import sxtwl  # type: ignore
except Exception as exc:  # pragma: no cover - 环境缺少依赖时抛出
    raise RuntimeError("缺少依赖：请先安装 sxtwl") from exc

from classic_analyzer.common import (
    TIANGAN_WUXING,
    SHENG_MAP,
    SHENG_REVERSE,
    KE_MAP,
    KE_REVERSE,
    summarize_branch_elements,
    summarize_ganzhi_elements,
    evaluate_day_master_strength,
    get_ten_god,
    clamp_score,
)


class DayunAnalyzer:
    """
    大运分析器
    """

    TIAN_GAN = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    DI_ZHI = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

    ROLE_KEYS = ('same', 'resource', 'drain', 'wealth', 'officer')
    ROLE_LABELS = {
        'same': '\u6bd4\u52ab',
        'resource': '\u5370\u661f',
        'drain': '\u98df\u4f24',
        'wealth': '\u8d22\u661f',
        'officer': '\u5b98\u6740',
    }
    TEN_GOD_ROLE = {
        '\u6bd4\u80a9': 'same',
        '\u52ab\u8d22': 'same',
        '\u6b63\u5370': 'resource',
        '\u504f\u5370': 'resource',
        '\u98df\u795e': 'drain',
        '\u4f24\u5b98': 'drain',
        '\u6b63\u8d22': 'wealth',
        '\u504f\u8d22': 'wealth',
        '\u6b63\u5b98': 'officer',
        '\u4e03\u6740': 'officer',
    }
    TEN_GOD_DISPLAY = {
        '\u6bd4\u80a9': '\u6bd4\u80a9',
        '\u52ab\u8d22': '\u52ab\u8d22',
        '\u6b63\u5370': '\u6b63\u5370',
        '\u504f\u5370': '\u504f\u5370',
        '\u98df\u795e': '\u98df\u795e',
        '\u4f24\u5b98': '\u4f24\u5b98',
        '\u6b63\u8d22': '\u6b63\u8d22',
        '\u504f\u8d22': '\u504f\u8d22',
        '\u6b63\u5b98': '\u6b63\u5b98',
        '\u4e03\u6740': '\u4e03\u6740',
    }
    IDEAL_ROLE_RATIOS = {
        '\u65fa': {
            'same': 0.10,
            'resource': 0.15,
            'drain': 0.25,
            'wealth': 0.25,
            'officer': 0.25,
        },
        '\u8870': {
            'same': 0.25,
            'resource': 0.25,
            'drain': 0.15,
            'wealth': 0.15,
            'officer': 0.20,
        },
    }

    JIEQI_NAMES = [
        "冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨",
        "立夏", "小满", "芒种", "夏至", "小暑", "大暑", "立秋", "处暑", "白露",
        "秋分", "寒露", "霜降", "立冬", "小雪", "大雪",
    ]

    @classmethod
    def analyze_dayun(cls, pillars: Dict[str, Any], birth_info: Dict[str, Any], gender: str = '男') -> Dict[str, Any]:
        """
        综合分析大运
        Args:
            pillars: {'year': ('甲','子'), 'month':('乙','丑'), ...}
            birth_info: 需包含阳历出生时间信息
            gender: '男' 或 '女'
        Returns:
            {
                'qiyun_info': {...},
                'profile': {...},           # 日主强弱
                'dayun_list': [...],        # 完整大运表
                'current_dayun': {...},     # 当前大运
                'jixiong_info': {...}       # 当前大运吉凶详评
            }
        """
        birth_dt, tzinfo = cls._build_birth_datetime(birth_info)
        profile = evaluate_day_master_strength(pillars)

        qiyun_info = cls._calculate_qiyun(pillars, birth_info, gender, birth_dt, tzinfo)
        dayun_list = cls._arrange_dayun(pillars, qiyun_info, profile, birth_dt)

        analysis_dt = cls._get_analysis_datetime(birth_info, tzinfo)
        current_dayun = cls._judge_current_dayun(dayun_list, birth_dt, analysis_dt)
        jixiong_info = cls._judge_dayun_jixiong(current_dayun, pillars, profile)

        return {
            'qiyun_info': qiyun_info,
            'profile': {
                'element': profile.element,
                'strength': profile.strength,
                'support_power': round(profile.support_power, 2),
                'pressure_power': round(profile.pressure_power, 2),
                'distribution': {k: round(v, 2) for k, v in profile.distribution.items()},
            },
            'dayun_list': dayun_list,
            'current_dayun': current_dayun,
            'jixiong_info': jixiong_info,
        }

    # ──────────────────────────── 基础时间处理 ────────────────────────────
    @classmethod
    def _build_birth_datetime(cls, birth_info: Dict[str, Any]) -> (datetime, timezone):
        tz_offset = birth_info.get('timezone_offset', 8.0)
        tzinfo = timezone(timedelta(hours=float(tz_offset)))

        year = birth_info.get('solar_year') or birth_info.get('year')
        month = birth_info.get('solar_month') or birth_info.get('month')
        day = birth_info.get('solar_day') or birth_info.get('day')
        hour = birth_info.get('solar_hour', birth_info.get('hour', 0))
        minute = birth_info.get('solar_minute', birth_info.get('minute', 0))
        second = birth_info.get('solar_second', birth_info.get('second', 0))

        birth_dt = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second), tzinfo=tzinfo)

        if birth_info.get('use_true_solar_time', True):
            longitude = birth_info.get('longitude')
            if longitude is not None:
                minutes = (float(longitude) - 120.0) * 4.0  # 每度四分钟
                birth_dt += timedelta(minutes=minutes)

        return birth_dt, tzinfo

    @classmethod
    def _get_analysis_datetime(cls, birth_info: Dict[str, Any], tzinfo: timezone) -> datetime:
        analysis_dt = birth_info.get('analysis_datetime')
        if isinstance(analysis_dt, datetime):
            if analysis_dt.tzinfo is None:
                analysis_dt = analysis_dt.replace(tzinfo=tzinfo)
            return analysis_dt
        return datetime.now(tzinfo)

    # ──────────────────────────── 节气 & 起运 ────────────────────────────
    @classmethod
    def _calculate_qiyun(
        cls,
        pillars: Dict[str, Any],
        birth_info: Dict[str, Any],
        gender: str,
        birth_dt: datetime,
        tzinfo: timezone,
    ) -> Dict[str, Any]:
        year_gan = pillars['year'][0]
        is_yang_year = year_gan in ['甲', '丙', '戊', '庚', '壬']

        if gender == '男':
            shun_ni = '顺行' if is_yang_year else '逆行'
        else:
            shun_ni = '逆行' if is_yang_year else '顺行'

        prev_jieqi = cls._seek_jieqi(birth_dt, direction='prev')
        next_jieqi = cls._seek_jieqi(birth_dt, direction='next')

        birth_dt_utc = birth_dt.astimezone(timezone.utc)

        if shun_ni == '顺行':
            target = next_jieqi
            hours_diff = (target['datetime_utc'] - birth_dt_utc).total_seconds() / 3600.0
            if hours_diff <= 0:
                # 极端情况下继续向后取
                target = cls._seek_jieqi(target['datetime_utc'].astimezone(tzinfo), direction='next')
                hours_diff = (target['datetime_utc'] - birth_dt_utc).total_seconds() / 3600.0
        else:
            target = prev_jieqi
            hours_diff = (birth_dt_utc - target['datetime_utc']).total_seconds() / 3600.0
            if hours_diff <= 0:
                target = cls._seek_jieqi(target['datetime_utc'].astimezone(tzinfo), direction='prev')
                hours_diff = (birth_dt_utc - target['datetime_utc']).total_seconds() / 3600.0

        days_diff = hours_diff / 24.0
        age_exact = days_diff / 3.0  # 每三日折岁
        age_exact = max(age_exact, 0.0)

        start_age_year = math.ceil(age_exact - 1e-6)
        target_local = target['datetime_utc'].astimezone(tzinfo)

        age_desc = cls._format_age_description(age_exact)

        return {
            'shun_ni': shun_ni,
            'is_yang_year': is_yang_year,
            'qiyun_hours': round(hours_diff, 2),
            'qiyun_days': round(days_diff, 2),
            'qiyun_age_exact': round(age_exact, 2),
            'qiyun_age': int(start_age_year),
            'qiyun_age_desc': age_desc,
            'reference_jieqi': {
                'name': target['name'],
                'time_local': target_local.strftime('%Y-%m-%d %H:%M:%S'),
                'time_utc': target['datetime_utc'].strftime('%Y-%m-%d %H:%M:%S'),
                'type': '未来节气' if shun_ni == '顺行' else '过去节气',
            },
        }

    @classmethod
    def _seek_jieqi(cls, reference_dt: datetime, direction: str) -> Dict[str, Any]:
        current = sxtwl.fromSolar(reference_dt.year, reference_dt.month, reference_dt.day)

        for _ in range(400):
            if current.hasJieQi():
                jd = current.getJieQiJD()
                idx = current.getJieQi()
                dt_utc = cls._jd_to_datetime_utc(jd)
                return {
                    'name': cls.JIEQI_NAMES[idx],
                    'datetime_utc': dt_utc,
                    'jd': jd,
                }
            current = current.after(1) if direction == 'next' else current.before(1)

        raise RuntimeError("无法查到相邻节气，请检查输入时间是否合理")

    @staticmethod
    def _jd_to_datetime_utc(jd: float) -> datetime:
        dd = sxtwl.JD2DD(jd)
        year = int(dd.Y)
        month = int(dd.M)
        day = int(dd.D)
        hour = int(dd.h)
        minute = int(dd.m)
        second = int(round(dd.s))

        if second >= 60:
            second -= 60
            minute += 1
        if minute >= 60:
            minute -= 60
            hour += 1
        dt = datetime(year, month, day, hour, minute, second, tzinfo=timezone.utc)
        return dt

    @staticmethod
    def _format_age_description(age: float) -> str:
        years = int(age)
        months = int(round((age - years) * 12))
        if months >= 12:
            years += 1
            months -= 12
        if years == 0:
            return f"{months}个月"
        if months == 0:
            return f"{years}岁"
        return f"{years}岁{months}个月"

    # ──────────────────────────── 排列大运 ────────────────────────────
    @classmethod
    def _arrange_dayun(
        cls,
        pillars: Dict[str, Any],
        qiyun_info: Dict[str, Any],
        profile,
        birth_dt: datetime,
    ) -> List[Dict[str, Any]]:
        """排列大运 - P2修复：正确的首步大运起点计算"""
        month_gan = pillars['month'][0]
        month_zhi = pillars['month'][1]
        day_gan = pillars['day'][0]

        gan_index = cls.TIAN_GAN.index(month_gan)
        zhi_index = cls.DI_ZHI.index(month_zhi)

        direction = 1 if qiyun_info['shun_ni'] == '顺行' else -1

        start_age_exact = qiyun_info['qiyun_age_exact']
        dayun_list: List[Dict[str, Any]] = []

        # 🔥 P2修复：正确的首步大运起点（从月柱顺逆推算）
        for step in range(12):  # 至少覆盖 120 岁
            # 次月从月柱幹支顺逆推算（并并不先不后地推算）
            gan_index = (gan_index + direction) % len(cls.TIAN_GAN)
            zhi_index = (zhi_index + direction) % len(cls.DI_ZHI)

            gan = cls.TIAN_GAN[gan_index]
            zhi = cls.DI_ZHI[zhi_index]
            ganzhi = gan + zhi

            start_exact = start_age_exact + step * 10
            end_exact = start_exact + 10

            ten_god = get_ten_god(day_gan, gan)
            branch_elements = summarize_branch_elements(zhi)
            combined_elements = summarize_ganzhi_elements(gan, zhi)

            dayun_list.append({
                'index': step + 1,
                'ganzhi': ganzhi,
                'gan': gan,
                'zhi': zhi,
                'ten_god': ten_god,
                'start_age_exact': round(start_exact, 2),
                'end_age_exact': round(end_exact, 2),
                'start_age': int(math.floor(start_exact + 1e-6)),
                'end_age': int(math.floor(end_exact - 1e-6)),
                'branch_elements': {k: round(v, 2) for k, v in branch_elements.items()},
                'combined_elements': {k: round(v, 2) for k, v in combined_elements.items()},
            })

        return dayun_list

    # ──────────────────────────── 当前大运 ────────────────────────────
    @staticmethod
    def _judge_current_dayun(dayun_list: List[Dict[str, Any]], birth_dt: datetime, analysis_dt: datetime) -> Optional[Dict[str, Any]]:
        """判断当前步大运 - P2修复：正确确定大运步数而不是恒为第1步"""
        if not dayun_list:
            return None

        age_years = (analysis_dt - birth_dt).total_seconds() / (365.2425 * 24 * 3600)
        age_years = max(age_years, 0.0)

        # 🔥 P2修复：正确遍历查找对应的大运步数（不是恒为第1步）
        for entry in dayun_list:
            if entry['start_age_exact'] <= age_years < entry['end_age_exact']:
                selected = dict(entry)
                selected['current_age'] = round(age_years, 2)
                selected['progress_in_current'] = round((age_years - entry['start_age_exact']) / 10.0, 2)  # 在当前大运步中的进度（0-1）
                return selected
        
        # 未到起运或已超出列表范围
        if age_years < dayun_list[0]['start_age_exact']:
            selected = dict(dayun_list[0])
            selected['current_age'] = round(age_years, 2)
            selected['note'] = '未交大运，仍走小运'
            return selected

        selected = dict(dayun_list[-1])
        selected['current_age'] = round(age_years, 2)
        selected['note'] = '已超过排定大运范围'
        return selected

    @staticmethod
    def _element_for_role(day_element: str, role: str) -> str:
        if role == 'same':
            return day_element
        if role == 'resource':
            return SHENG_REVERSE.get(day_element, day_element)
        if role == 'drain':
            return SHENG_MAP.get(day_element, day_element)
        if role == 'wealth':
            return KE_MAP.get(day_element, day_element)
        if role == 'officer':
            return KE_REVERSE.get(day_element, day_element)
        return day_element

    @classmethod
    def _role_ratios(cls, profile) -> Dict[str, float]:
        distribution = getattr(profile, 'distribution', {})
        total = sum(distribution.values()) or 1.0
        day_element = getattr(profile, 'element', '')
        ratios: Dict[str, float] = {}
        for role in cls.ROLE_KEYS:
            element = cls._element_for_role(day_element, role)
            ratios[role] = distribution.get(element, 0.0) / total
        return ratios

    @classmethod
    def _role_influence(cls, combined: Dict[str, float], profile) -> Dict[str, float]:
        total = sum(combined.values()) or 1.0
        influence: Dict[str, float] = {}
        day_element = getattr(profile, 'element', '')
        for role in cls.ROLE_KEYS:
            element = cls._element_for_role(day_element, role)
            influence[role] = combined.get(element, 0.0) / total
        return influence

    @staticmethod
    def _display_element(element: str) -> str:
        return element or '\u672a\u77e5'

    @staticmethod
    def _display_strength(strength: str) -> str:
        return strength or '\u672a\u77e5'

    @classmethod
    def _display_ten_god(cls, ten_god: str) -> str:
        if not ten_god:
            return '\u672a\u77e5\u5341\u795e'
        return cls.TEN_GOD_DISPLAY.get(ten_god, ten_god)

    @staticmethod
    def _display_ganzhi(ganzhi: Optional[str]) -> str:
        return ganzhi or '\u672a\u77e5'

    @staticmethod
    def _format_percent(value: float) -> str:
        clamped = max(min(value, 1.0), -1.0)
        return '{:.1f}%'.format(clamped * 100.0)

    @classmethod
    def _summarize_role_delta(cls, role_needs: Dict[str, float]) -> str:
        parts: List[str] = []
        for role in cls.ROLE_KEYS:
            delta = role_needs.get(role, 0.0)
            formatted = '{:+.1f}%'.format(delta * 100.0)
            parts.append('{}{}'.format(cls.ROLE_LABELS[role], formatted))
        return '\u3001'.join(parts)

    # ──────────────────────────── 吉凶判定 ────────────────────────────
    @staticmethod
    def _judge_dayun_jixiong(
        dayun: Optional[Dict[str, Any]],
        pillars: Dict[str, Any],
        profile,
    ) -> Dict[str, Any]:
        """
        大运吉凶判定 - 基于《子平真诠》《滴天髓》《穷通宝鉴》理论
        ✅ 修复：移除打分系统，改为喜忌判断
        ✅ 新增：五行过旺特殊判断（土多金埋、水多木漂等）
        传统命理不打分，只论大运喜忌
        """
        if not dayun:
            return {
                'jixiong': '未知',
                'score': 0,  # 不打分
                'detail': '未能确定当前大运',
                'xiji': '未知',
                'classic_basis': ''
            }

        day_element = profile.element
        strength = profile.strength
        distribution = profile.distribution if hasattr(profile, 'distribution') else {}

        resource_element = SHENG_REVERSE[day_element]
        drain_element = SHENG_MAP[day_element]
        wealth_element = KE_MAP[day_element]
        officer_element = KE_REVERSE[day_element]

        combined = dayun['combined_elements']

        # ✅ 新增：检查五行过旺（土多金埋、水多木漂等）
        # 五行过旺阈值
        WUXING_EXCESS_THRESHOLD = 3.5

        # 五行过旺对应的受克五行和生克关系
        WUXING_BURIED_MAP = {
            '土': {'buried': '金', 'generator': '火'},  # 土多金埋，火生土
            '水': {'buried': '木', 'generator': '金'},  # 水多木漂，金生水
            '火': {'buried': '土', 'generator': '木'},  # 火多土焦，木生火
            '木': {'buried': '火', 'generator': '水'},  # 木多火塞，水生木
            '金': {'buried': '水', 'generator': '土'},  # 金多水浊，土生金
        }

        # 检查是否有五行过旺且埋克日主
        excess_element = None
        for element, threshold in [('土', WUXING_EXCESS_THRESHOLD), ('水', WUXING_EXCESS_THRESHOLD),
                                   ('火', WUXING_EXCESS_THRESHOLD), ('木', WUXING_EXCESS_THRESHOLD),
                                   ('金', WUXING_EXCESS_THRESHOLD)]:
            if distribution.get(element, 0) >= threshold:
                buried_info = WUXING_BURIED_MAP.get(element, {})
                if buried_info.get('buried') == day_element:
                    excess_element = element
                    break

        # ✅ 如果有五行过旺（如土多金埋），使用特殊理论
        # 🔥 修复：即使日主判断为"弱"（被埋），也要使用特殊理论
        if excess_element:
            buried_info = WUXING_BURIED_MAP[excess_element]
            generator_element = buried_info['generator']

            # 土多金埋：喜木疏土、水淘洗，忌土埋金、火生土
            favorable = {
                wealth_element: '财星（疏土）',  # 木疏土
                drain_element: '食伤（淘洗）',   # 水淘洗
            }
            unfavorable = {
                excess_element: '印星（埋金）',  # 土埋金
                generator_element: '官杀（生土埋金）',  # 火生土
                day_element: '比劫（无用）',     # 金无用
            }

            # 经典依据
            if excess_element == '土' and day_element == '金':
                classic_basis = '《穷通宝鉴》：九月辛金，火土为病，水木为药。《子平真诠》：土多金埋，须以损印为用。《滴天髓》：金赖土生，土多金埋。'
            elif excess_element == '水' and day_element == '木':
                classic_basis = '《滴天髓》：木赖水生，水多木漂。《子平真诠》：印太多，须以损印为用。'
            elif excess_element == '火' and day_element == '土':
                classic_basis = '《滴天髓》：土赖火生，火多土焦。'
            elif excess_element == '木' and day_element == '火':
                classic_basis = '《滴天髓》：火赖木生，木多火塞。'
            elif excess_element == '金' and day_element == '水':
                classic_basis = '《滴天髓》：水赖金生，金多水浊。'
            else:
                classic_basis = f'《滴天髓》：五行过旺理论（{excess_element}多{day_element}埋）'

        # ✅ 否则使用常规理论：身旺喜泄耗，身弱喜生扶
        # 🔥 修复：兼容新的日主强弱等级（旺/中旺/中和/中弱/弱）
        elif strength in ['旺', '中旺']:  # 身强
            favorable = {
                drain_element: '食神伤官',
                wealth_element: '财星',
                officer_element: '官杀',
            }
            unfavorable = {
                day_element: '比劫',
                resource_element: '印星',
            }
            classic_basis = '《子平真诠》：身旺喜泄耗（食伤、财、官杀），忌生扶（印、比劫）'
        elif strength in ['弱', '中弱']:  # 身弱
            favorable = {
                day_element: '比劫',
                resource_element: '印星',
            }
            unfavorable = {
                drain_element: '食神伤官',
                wealth_element: '财星',
                officer_element: '官杀',
            }
            classic_basis = '《子平真诠》：身弱喜生扶（印、比劫），忌泄耗（食伤、财、官杀）'
        else:  # 中和
            favorable = {
                drain_element: '食神伤官',
                wealth_element: '财星',
            }
            unfavorable = {
                day_element: '比劫',
                resource_element: '印星',
            }
            classic_basis = '《子平真诠》：中和格局，用神随运而定，平衡为贵'

        # ✅ 计算喜忌强度（不打分，只判断强弱）
        fav_strength = sum(combined.get(el, 0.0) for el in favorable.keys())
        unfav_strength = sum(combined.get(el, 0.0) for el in unfavorable.keys())

        # ✅ 判断吉凶（基于喜忌强度对比）
        if fav_strength > unfav_strength * 2:
            level = '大吉'
            xiji = '大喜'
        elif fav_strength > unfav_strength:
            level = '小吉'
            xiji = '小喜'
        elif fav_strength == unfav_strength or abs(fav_strength - unfav_strength) < 0.5:
            level = '平运'
            xiji = '平'
        elif unfav_strength > fav_strength:
            level = '小凶'
            xiji = '小忌'
        else:
            level = '大凶'
            xiji = '大忌'

        # ✅ 生成详细说明（不包含分数）
        detail_lines = [
            f"【大运干支】{dayun['ganzhi']}（{dayun['ten_god']}）",
            f"",
            f"【大运五行】",
            f"  木：{combined.get('木', 0):.1f}  火：{combined.get('火', 0):.1f}  土：{combined.get('土', 0):.1f}  金：{combined.get('金', 0):.1f}  水：{combined.get('水', 0):.1f}",
            f"",
            f"【喜忌判断】{xiji}",
        ]

        fav_desc = [f"{name}（{el}{combined.get(el, 0):.1f}）" for el, name in favorable.items() if combined.get(el, 0) > 0]
        unfav_desc = [f"{name}（{el}{combined.get(el, 0):.1f}）" for el, name in unfavorable.items() if combined.get(el, 0) > 0]

        if fav_desc:
            detail_lines.append("  喜神：" + "，".join(fav_desc))
        if unfav_desc:
            detail_lines.append("  忌神：" + "，".join(unfav_desc))

        # 添加说明
        detail_lines.append("")
        detail_lines.append("【分析说明】")
        # 🔥 修复：兼容新的日主强弱等级
        if strength in ['旺', '中旺']:  # 身强
            detail_lines.append(f"  日主{day_element}身旺，大运带来{', '.join([f'{k}{v:.1f}' for k, v in combined.items() if v > 0])}。")
            detail_lines.append(f"  其中喜神（泄耗）：{', '.join([f'{k}{v:.1f}' for k, v in combined.items() if k in favorable and v > 0])}。")
            if any(combined.get(k, 0) > 0 for k in unfavorable):
                detail_lines.append(f"  其中忌神（生扶）：{', '.join([f'{k}{v:.1f}' for k, v in combined.items() if k in unfavorable and v > 0])}。")
        elif strength in ['弱', '中弱']:  # 身弱
            detail_lines.append(f"  日主{day_element}身弱，大运带来{', '.join([f'{k}{v:.1f}' for k, v in combined.items() if v > 0])}。")
            detail_lines.append(f"  其中喜神（生扶）：{', '.join([f'{k}{v:.1f}' for k, v in combined.items() if k in favorable and v > 0])}。")
            if any(combined.get(k, 0) > 0 for k in unfavorable):
                detail_lines.append(f"  其中忌神（泄耗）：{', '.join([f'{k}{v:.1f}' for k, v in combined.items() if k in unfavorable and v > 0])}。")
        else:  # 中和
            detail_lines.append(f"  日主{day_element}中和，大运带来{', '.join([f'{k}{v:.1f}' for k, v in combined.items() if v > 0])}。")
            detail_lines.append(f"  其中喜神（平衡）：{', '.join([f'{k}{v:.1f}' for k, v in combined.items() if k in favorable and v > 0])}。")
            if any(combined.get(k, 0) > 0 for k in unfavorable):
                detail_lines.append(f"  其中忌神（失衡）：{', '.join([f'{k}{v:.1f}' for k, v in combined.items() if k in unfavorable and v > 0])}。")

        # ✅ 特殊情况说明（不打分，只说明）
        detail_lines.append("")
        detail_lines.append("【特殊提示】")
        # 🔥 修复：兼容新的日主强弱等级
        if strength in ['旺', '中旺'] and combined.get(day_element, 0) >= 1.5:
            detail_lines.append("  ⚠ 比劫过旺，需防破财、争斗。")
        if strength in ['弱', '中弱'] and combined.get(officer_element, 0) >= 0.8:
            detail_lines.append("  ⚠ 官杀重而日主弱，需防压力、疾病。")
        if strength in ['弱', '中弱'] and combined.get(resource_element, 0) > 0:
            detail_lines.append("  ✓ 印星相扶，有贵人相助。")
        if strength == '中和':
            detail_lines.append("  ℹ 日主中和，大运平衡为贵，需看具体配合。")

        detail_lines.append(f"")
        detail_lines.append(f"【经典依据】")
        detail_lines.append(f"  {classic_basis}")

        return {
            'jixiong': level,
            'score': 0,  # 不打分
            'detail': "\n".join(detail_lines),
            'xiji': xiji,  # 喜忌判断
            'favorable_elements': {el: round(combined.get(el, 0), 2) for el in favorable.keys()},
            'unfavorable_elements': {el: round(combined.get(el, 0), 2) for el in unfavorable.keys()},
            'classic_basis': classic_basis,
        }


def analyze_dayun_complete(pillars: Dict[str, Any], birth_info: Dict[str, Any], gender: str = '男') -> Dict[str, Any]:
    """
    兼容旧接口
    """
    return DayunAnalyzer.analyze_dayun(pillars, birth_info, gender)
