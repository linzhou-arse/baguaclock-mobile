#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地八字核心计算（基于 sxtwl）
- 以节气定年/月（年柱以立春为岁首；月柱以定气月）
- 支持真太阳时修正（可选）
- 输出结构化 JSON，含最近节气与边界风险标记

依赖：sxtwl （已在本仓库安装）
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta, timezone
import math

try:
    import sxtwl
except Exception as e:
    raise RuntimeError("缺少依赖：请先 pip install sxtwl")

# 天干地支
TIANGAN = "甲乙丙丁戊己庚辛壬癸"
DIZHI = "子丑寅卯辰巳午未申酉戌亥"

TG_LIST = list(TIANGAN)
DZ_LIST = list(DIZHI)

# 24节气名称（按 sxtwl.getJieQi() 的索引顺序）
JIEQI_NAMES = [
    "冬至", "小寒", "大寒", "立春", "雨水", "惊蛰", "春分", "清明", "谷雨",
    "立夏", "小满", "芒种", "夏至", "小暑", "大暑", "立秋", "处暑", "白露",
    "秋分", "寒露", "霜降", "立冬", "小雪", "大雪"
]

# 口径配置
@dataclass
class Rules:
    use_true_solar_time: bool = True  # 是否按真太阳时修正
    jieqi_as_year: bool = True        # 年柱以立春为岁首（sxtwl 默认 getYearGZ() 即立春口径）
    jieqi_as_month: bool = True       # 月柱以节气为月首（定气，getMonthGZ()）
    boundary_hours: float = 2.0       # 边界风险阈值（小时）

@dataclass
class Location:
    lon: float  # 经度，东经为正
    lat: float  # 纬度（暂未用）

@dataclass
class Output:
    pillars: Dict[str, str]
    nearest_jieqi: Dict[str, Any]
    is_boundary_risky: bool
    normalized_input: Dict[str, Any]


def tgdz_to_str(tg_idx: int, dz_idx: int) -> str:
    return f"{TG_LIST[tg_idx]}{DZ_LIST[dz_idx]}"


def correct_true_solar_time(dt_local: datetime, lon: float) -> datetime:
    """按经度做真太阳时近似修正（每度4分钟，不计均时差）。"""
    # 东八区子午线是120度，计算与本地经度的差值
    tz_meridian = 120.0  # 东八区子午线
    minutes = (lon - tz_meridian) * 4.0  # 每度4分钟
    return dt_local + timedelta(minutes=minutes)


def find_nearest_jieqi(day_obj) -> Dict[str, Any]:
    """查找前后最近节气（按天扫描），返回 {'prev': {...}, 'next': {...}}。"""
    # 前一个节气
    prev_day = day_obj
    prev_info = None
    for _ in range(370):
        if prev_day.hasJieQi():
            jd = prev_day.getJieQiJD()
            t = sxtwl.JD2DD(jd)
            prev_info = {"name": JIEQI_NAMES[prev_day.getJieQi()],
                         "time": f"{int(t.Y):04d}-{int(t.M):02d}-{int(t.D):02d} {int(t.h):02d}:{int(t.m):02d}:{int(round(t.s)):02d}"}
            break
        prev_day = prev_day.before(1)
    # 后一个节气
    next_day = day_obj
    next_info = None
    for _ in range(370):
        if next_day.hasJieQi():
            jd = next_day.getJieQiJD()
            t = sxtwl.JD2DD(jd)
            next_info = {"name": JIEQI_NAMES[next_day.getJieQi()],
                         "time": f"{int(t.Y):04d}-{int(t.M):02d}-{int(t.D):02d} {int(t.h):02d}:{int(t.m):02d}:{int(round(t.s)):02d}"}
            break
        next_day = next_day.after(1)
    return {"prev": prev_info, "next": next_info}


def compute_pillars(dt_local: datetime, rules: Rules, loc: Optional[Location]) -> Tuple[Dict[str, str], Dict[str, Any], bool]:
    """核心：根据本地时间与规则，返回四柱、节气信息与边界风险。"""
    # 真太阳时可选修正
    use_dt = dt_local
    if rules.use_true_solar_time and loc is not None:
        use_dt = correct_true_solar_time(dt_local, loc.lon)

    # 获取 sxtwl 的 day 对象（按修正后的日期）
    day_obj = sxtwl.fromSolar(use_dt.year, use_dt.month, use_dt.day)

    # 日柱、时柱（注意：时柱用修正后的小时）
    day_gz = day_obj.getDayGZ()
    hour_gz = day_obj.getHourGZ(use_dt.hour)

    # 月柱、年柱（以节气为界）
    month_gz = day_obj.getMonthGZ()
    year_gz = day_obj.getYearGZ()  # 默认以立春为界

    pillars = {
        "year": tgdz_to_str(year_gz.tg, year_gz.dz),
        "month": tgdz_to_str(month_gz.tg, month_gz.dz),
        "day": tgdz_to_str(day_gz.tg, day_gz.dz),
        "hour": tgdz_to_str(hour_gz.tg, hour_gz.dz),
    }

    # 最近节气
    jq_info = find_nearest_jieqi(day_obj)

    # 边界风险：子时切换近似 + 节气当日标记（无法精确到小时）
    boundary = False
    try:
        # 子时/整偶时边界（近似：整双小时为换支点）
        minute_of_day = use_dt.hour * 60 + use_dt.minute
        to_even = min(minute_of_day % 120, 120 - (minute_of_day % 120))
        hour_boundary_hours = to_even / 60.0
        boundary = hour_boundary_hours <= rules.boundary_hours
        # 若当日恰为节气日，也提示边界
        if day_obj.hasJieQi():
            boundary = True
    except Exception:
        pass

    return pillars, jq_info, boundary


def compute_bazi(
    year: int, month: int, day: int, hour: int, minute: int = 0, second: int = 0,
    tz_offset_hours: float = 8.0,
    rules: Optional[Rules] = None,
    location: Optional[Location] = None,
) -> Output:
    rules = rules or Rules()
    tz = timezone(timedelta(hours=tz_offset_hours))
    dt_local = datetime(year, month, day, hour, minute, second, tzinfo=tz)

    pillars, jq_info, boundary = compute_pillars(dt_local, rules, location)

    normalized = {
        "utc_offset": f"{tz.utcoffset(None).total_seconds()/3600:+.0f}:00",
        "use_true_solar_time": rules.use_true_solar_time,
        "jieqi_as_year": rules.jieqi_as_year,
        "jieqi_as_month": rules.jieqi_as_month,
        "geo": ({"lon": location.lon, "lat": location.lat} if location else None)
    }

    return Output(
        pillars=pillars,
        nearest_jieqi=jq_info,
        is_boundary_risky=boundary,
        normalized_input=normalized,
    )


def compute_bazi_json(**kwargs) -> Dict[str, Any]:
    out = compute_bazi(**kwargs)
    d = asdict(out)
    return d


if __name__ == "__main__":
    # 简单 CLI：python sxtwl_adapter.py 1992 2 4 10
    import sys, json
    if len(sys.argv) < 5:
        print("用法: python sxtwl_adapter.py YYYY MM DD HH [MM [SS]]")
        sys.exit(1)
    Y, M, D, H = map(int, sys.argv[1:5])
    m = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    s = int(sys.argv[6]) if len(sys.argv) > 6 else 0
    result = compute_bazi_json(year=Y, month=M, day=D, hour=H, minute=m, second=s,
                               tz_offset_hours=8.0,
                               rules=Rules(use_true_solar_time=True),
                               location=Location(lon=112.98, lat=28.2))  # 长沙经纬度
    print(json.dumps(result, ensure_ascii=False, indent=2))

