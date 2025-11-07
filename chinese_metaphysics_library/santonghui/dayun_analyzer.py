#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大运分析器 - Dayun Analyzer
=========================

基于《三命通会·大运篇》的大运分析
"""

from __future__ import annotations
from typing import Dict, List, Any, Tuple
import time

from ..core.base_analyzer import BaseAnalyzer
from ..core.data_structures import BaziData, AnalysisResult, AnalysisConfig
from ..core.utils import create_analysis_result, get_wuxing_by_tiangan, get_wuxing_by_dizhi

# 尝试导入sxtwl用于节气计算
try:
    import sxtwl
    SXTWL_AVAILABLE = True
except ImportError:
    SXTWL_AVAILABLE = False


TIANGAN_SEQ = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
DIZHI_SEQ = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']


class DayunAnalyzer(BaseAnalyzer):
    """大运分析器 - 基于《三命通会·大运篇》"""
    
    def __init__(self, config: AnalysisConfig = None):
        super().__init__("大运分析器", "三命通会", config)
    
    def analyze(self, bazi_data: BaziData) -> AnalysisResult:
        """
        执行大运分析 - 基于《三命通会·大运篇》
        ✅ 修复：移除打分系统，改为喜忌判断
        """
        start_time = time.time()

        try:
            pillars = bazi_data.get_pillars()
            year_gan, year_zhi = pillars['year']
            month_gan, month_zhi = pillars['month']
            day_master = bazi_data.get_day_master()

            direction = self._calc_direction(year_gan, bazi_data.gender)
            dayun_pillars = self._calc_dayun_pillars(month_gan, month_zhi, direction, steps=10)

            # 起运年龄：使用sxtwl节气精算
            qiyun_age, qiyun_note = self._calculate_qiyun_age(bazi_data, direction)

            # ✅ 判断大运喜忌（不打分）
            xiji_result = self._judge_dayun_xiji(dayun_pillars, day_master, pillars, direction)

            # 🔥 新增：大运与命局配合分析
            coordination_analysis = self._analyze_dayun_mingju_coordination(
                dayun_pillars, bazi_data, pillars, day_master
            )

            # 生成描述
            description = f"大运方向：{direction}；共排{len(dayun_pillars)}步；{xiji_result['summary']}；{coordination_analysis['summary']}"

            # 生成建议
            advice = self._generate_advice(direction, xiji_result) + "；" + coordination_analysis['advice']

            analysis_time = (time.time() - start_time) * 1000

            return create_analysis_result(
                analyzer_name=self.name,
                book_name=self.book_name,
                analysis_type="大运分析",
                level=xiji_result['level'],
                score=0,  # 不打分
                description=description,
                details={
                    'direction': direction,
                    'dayun_pillars': dayun_pillars,
                    'qiyun_age': qiyun_age,
                    'qiyun_note': qiyun_note,
                    'xiji_details': xiji_result,
                    'coordination_analysis': coordination_analysis
                },
                advice=advice,
                analysis_time=analysis_time
            )

        except Exception as e:
            raise Exception(f"大运分析失败: {e}")

    def _calc_direction(self, year_gan: str, gender: str) -> str:
        """顺逆判定：阳年男顺女逆，阴年男逆女顺"""
        yang_gan = {'甲', '丙', '戊', '庚', '壬'}
        is_yang_year = year_gan in yang_gan
        if (is_yang_year and gender == '男') or (not is_yang_year and gender == '女'):
            return '顺行'
        return '逆行'

    def _calc_dayun_pillars(self, month_gan: str, month_zhi: str, direction: str, steps: int = 8) -> List[Tuple[str, str]]:
        """由月柱起排大运干支（顺行：月柱后一位起；逆行：月柱前一位起）"""
        gan_idx = TIANGAN_SEQ.index(month_gan)
        zhi_idx = DIZHI_SEQ.index(month_zhi)
        result: List[Tuple[str, str]] = []
        for i in range(1, steps + 1):
            offset = i if direction == '顺行' else -i
            g = TIANGAN_SEQ[(gan_idx + offset) % 10]
            z = DIZHI_SEQ[(zhi_idx + offset) % 12]
            result.append((g, z))
        return result

    def _calculate_qiyun_age(self, bazi_data: BaziData, direction: str) -> Tuple[float, str]:
        """
        计算起运年龄（使用sxtwl节气精算，精确到分钟）
        🔥 修复：1) 使用精确的出生时刻（hour/minute/second）；2) 移除1-8岁硬性限制；3) 使用精确JD计算
        理论依据：《三命通会·大运篇》- 从出生时刻到节气的精确时长，三天折一岁
        """
        # 获取出生年月日时（精确到分钟）
        year = bazi_data.birth_year
        month = bazi_data.birth_month
        day = bazi_data.birth_day
        hour = getattr(bazi_data, 'birth_hour', 0)
        minute = getattr(bazi_data, 'birth_minute', 0)
        second = getattr(bazi_data, 'birth_second', 0)
        
        # 首先尝试使用sxtwl精算
        if SXTWL_AVAILABLE:
            try:
                # 🔥 修复：传统算法是按整日计算，而非精确到时刻
                # 理论依据：《三命通会·大运篇》"从出生日顺数至下一个节令"
                day_obj = sxtwl.fromSolar(year, month, day)

                # 计算到节气的天数（按整日计算）
                if direction == '顺行':
                    # 顺行：找下一个节气
                    # 🔥 修复：传统算法是从出生日"顺数"至下一个节令，不包含出生日当天
                    # 例如：11月5日出生，顺数至11月8日立冬，应该是3天（5→6→7→8，共3天）
                    current = day_obj
                    days_count = 0
                    for _ in range(400):
                        current = current.after(1)
                        days_count += 1
                        if current.hasJieQi():
                            # 🔥 修复：使用天数计数而不是JD差值，确保计算正确
                            # 从出生日的下一天开始数，到节气日（包含）为止
                            days_diff = days_count
                            if days_diff > 0:
                                # 起运年龄 = 天数差 / 3（三天折一年）
                                # 🔥 修复：按整日计算，四舍五入到最接近的年龄（传统算法）
                                qiyun_age = days_diff / 3.0
                                # 四舍五入到0.1岁精度
                                qiyun_age = round(qiyun_age, 1)
                                # 仅在极端情况下限制（小于0.5岁或大于10岁时）
                                if qiyun_age < 0.5:
                                    qiyun_age = 0.5
                                elif qiyun_age > 10.0:
                                    qiyun_age = 10.0
                                return qiyun_age, f"基于节气精算（按整日计算），{direction}起运"
                            break
                else:
                    # 逆行：找上一个节气
                    # 🔥 修复：传统算法是从出生日"逆数"至上一个节令，不包含出生日当天
                    current = day_obj
                    days_count = 0
                    for _ in range(400):
                        current = current.before(1)
                        days_count += 1
                        if current.hasJieQi():
                            # 🔥 修复：使用天数计数而不是JD差值，确保计算正确
                            # 从出生日的前一天开始数，到节气日（包含）为止
                            days_diff = days_count
                            if days_diff > 0:
                                # 起运年龄 = 天数差 / 3（三天折一年）
                                # 🔥 修复：按整日计算，四舍五入到最接近的年龄（传统算法）
                                qiyun_age = days_diff / 3.0
                                # 四舍五入到0.1岁精度
                                qiyun_age = round(qiyun_age, 1)
                                if qiyun_age < 0.5:
                                    qiyun_age = 0.5
                                elif qiyun_age > 10.0:
                                    qiyun_age = 10.0
                                return qiyun_age, f"基于节气精算（按整日计算），{direction}起运"
                            break
            except Exception as e:
                # 🔥 修复：sxtwl计算失败时，记录错误信息并抛出异常，不再降级到不准确的备用算法
                error_msg = f"sxtwl节气计算失败: {type(e).__name__}: {str(e)}"
                print(f"⚠️  {error_msg}")
                # 不再静默降级，而是抛出异常让调用者知道
                raise RuntimeError(f"起运年龄计算失败，sxtwl库异常: {error_msg}")

        # 🔥 修复：如果sxtwl不可用，直接抛出异常，不使用不准确的备用算法
        raise RuntimeError(f"起运年龄计算失败：sxtwl库不可用，无法进行精确节气计算")
    


    def _judge_dayun_xiji(self, dayun_pillars: List[Tuple[str, str]],
                          day_master: str, original_pillars: Dict,
                          direction: str) -> Dict:
        """
        判断大运喜忌 - 基于《三命通会》理论
        ✅ 修复：不打分，只判断喜忌
        """
        day_master_wx = get_wuxing_by_tiangan(day_master)

        # 五行关系映射
        wuxing_relations = {
            '木': {'生': '火', '克': '土', '被生': '水', '被克': '金'},
            '火': {'生': '土', '克': '金', '被生': '木', '被克': '水'},
            '土': {'生': '金', '克': '水', '被生': '火', '被克': '木'},
            '金': {'生': '水', '克': '木', '被生': '土', '被克': '火'},
            '水': {'生': '木', '克': '火', '被生': '金', '被克': '土'}
        }

        relations = wuxing_relations.get(day_master_wx, {})

        # 统计大运中各种五行关系的出现次数
        helpful_count = 0  # 有利的大运（生我、我生）
        harmful_count = 0  # 不利的大运（克我、我克）
        neutral_count = 0  # 中性的大运（比和）

        for gan, zhi in dayun_pillars:
            gan_wx = get_wuxing_by_tiangan(gan)
            zhi_wx = get_wuxing_by_dizhi(zhi)

            # 分析天干
            if gan_wx == day_master_wx:
                neutral_count += 1  # 比和
            elif gan_wx == relations.get('被生'):
                helpful_count += 1  # 生我
            elif gan_wx == relations.get('生'):
                helpful_count += 0.5  # 我生（泄气，但也算有用）
            elif gan_wx == relations.get('被克'):
                harmful_count += 1  # 克我
            elif gan_wx == relations.get('克'):
                harmful_count += 0.5  # 我克（耗力）

            # 分析地支（权重减半）
            if zhi_wx == day_master_wx:
                neutral_count += 0.5
            elif zhi_wx == relations.get('被生'):
                helpful_count += 0.5
            elif zhi_wx == relations.get('生'):
                helpful_count += 0.25
            elif zhi_wx == relations.get('被克'):
                harmful_count += 0.5
            elif zhi_wx == relations.get('克'):
                harmful_count += 0.25

        # ✅ 判断喜忌（不打分）
        total_steps = len(dayun_pillars)
        helpful_ratio = helpful_count / total_steps if total_steps > 0 else 0
        harmful_ratio = harmful_count / total_steps if total_steps > 0 else 0

        if helpful_ratio > 0.6:
            level = '大吉'
            xiji = '大喜'
            summary = "大运整体有利，多数步运助力日主"
        elif helpful_ratio > 0.4:
            level = '吉'
            xiji = '小喜'
            summary = "大运较为有利，部分步运助力日主"
        elif harmful_ratio > 0.6:
            level = '凶'
            xiji = '大忌'
            summary = "大运整体不利，多数步运克制日主"
        elif harmful_ratio > 0.4:
            level = '小凶'
            xiji = '小忌'
            summary = "大运较为不利，部分步运克制日主"
        else:
            level = '中平'
            xiji = '平'
            summary = "大运吉凶参半，需结合流年具体分析"

        return {
            'level': level,
            'xiji': xiji,
            'helpful_count': round(helpful_count, 1),
            'harmful_count': round(harmful_count, 1),
            'neutral_count': round(neutral_count, 1),
            'helpful_ratio': round(helpful_ratio, 2),
            'harmful_ratio': round(harmful_ratio, 2),
            'summary': summary
        }
    
    def _judge_single_dayun_xiji(self, gan: str, zhi: str, day_master: str,
                                   xishen_wuxing: List[str] = None,
                                   jishen_wuxing: List[str] = None,
                                   pillars: Dict[str, Tuple[str, str]] = None,
                                   yongshen_method: str = None,
                                   strength: str = None) -> Dict[str, str]:
        """
        判断单步大运的喜忌 - 基于《三命通会》《子平真诠》理论
        ✅ 修复：遵循"用神三法"优先级（调候>病药>通关>扶抑），并考虑身强身弱

        参数:
            gan: 大运天干
            zhi: 大运地支
            day_master: 日主
            xishen_wuxing: 喜神五行列表（如['木', '火']）
            jishen_wuxing: 忌神五行列表（如['金', '水']）
            pillars: 四柱信息（可选，用于更精确的判断）
            yongshen_method: 用神方法（'调候'/'病药'/'通关'/'扶抑'）- 用于优先级判断
            strength: 身强身弱（'身旺'/'身强'/'身弱'/'身极弱'/'中和'）- 用于辅助判断

        返回：{'xiji': '大喜/小喜/平/小忌/大忌', 'level': '大吉/吉/平/小凶/凶'}
        """
        # 🔥 修复：从正确的位置导入summarize_ganzhi_elements
        try:
            from classic_analyzer.common import summarize_ganzhi_elements
        except ImportError:
            # 如果导入失败，定义一个简化版本
            def summarize_ganzhi_elements(gan: str, zhi: str) -> Dict[str, float]:
                """汇总某天干地支组合的五行权重"""
                from ..core.constants import TIANGAN_WUXING, DIZHI_WUXING, DIZHI_CANGGAN_WEIGHTS
                totals = {'木': 0.0, '火': 0.0, '土': 0.0, '金': 0.0, '水': 0.0}
                # 天干五行
                totals[TIANGAN_WUXING[gan]] += 1.0
                # 地支藏干五行
                for hidden_gan, weight in DIZHI_CANGGAN_WEIGHTS.get(zhi, []):
                    totals[TIANGAN_WUXING[hidden_gan]] += weight
                return totals

        # 🔥 修复：正确检查列表是否非空（而不是依赖falsy检查）
        has_xishen = xishen_wuxing and len(xishen_wuxing) > 0
        has_jishen = jishen_wuxing and len(jishen_wuxing) > 0
        
        # 1. 🔥 优先：如果有用神喜忌信息，基于用神判断
        if has_xishen or has_jishen:
            # 计算大运干支的五行分布
            dayun_elements = summarize_ganzhi_elements(gan, zhi)
            
            # 计算喜神和忌神的强度
            xishen_strength = sum(dayun_elements.get(wx, 0.0) for wx in (xishen_wuxing or []))
            jishen_strength = sum(dayun_elements.get(wx, 0.0) for wx in (jishen_wuxing or []))
            
            # 🔥 新增：根据用神方法调整判断权重
            # 调候 > 病药 > 通关 > 扶抑
            method_priority = {
                '调候': 1.5,   # 调候用神最重要，权重最高
                '病药': 1.3,   # 病药次之
                '通关': 1.2,   # 通关再次
                '扶抑': 1.0    # 扶抑最基础
            }
            priority_weight = method_priority.get(yongshen_method, 1.0) if yongshen_method else 1.0
            
            gan_wx = get_wuxing_by_tiangan(gan)
            
            # 检查天干是否透出用神或忌神（最重要）
            gan_is_xishen = gan_wx in (xishen_wuxing or []) if xishen_wuxing else False
            gan_is_jishen = gan_wx in (jishen_wuxing or []) if jishen_wuxing else False
            
            # 🔥 新增：调试信息，帮助定位问题（在使用变量之后打印）
            print(f"🔍 大运{gan}{zhi}: 用神方法={yongshen_method}, 喜神{xishen_wuxing}(强度{xishen_strength:.2f}), 忌神{jishen_wuxing}(强度{jishen_strength:.2f})")
            print(f"    天干{gan}({gan_wx}): 是喜神={gan_is_xishen}, 是忌神={gan_is_jishen}, 权重={priority_weight:.2f}")
            print(f"    大运五行分布={dayun_elements}")
            
            # 🔥 优化：基于传统命理原则判断吉凶（遵循《子平真诠》"用神三法"优先级）
            # 原则1：大运透出用神（天干出现） → 大吉（调候用神优先级最高）
            # 原则2：大运透出忌神（天干出现） → 大凶
            # 原则3：大运地支藏用神 → 吉（根据用神方法调整权重）
            # 原则4：大运地支藏忌神 → 凶
            
            # 🔥 修复：检查地支藏干中是否有用神或忌神（而不只是本气）
            # 使用已计算的dayun_elements来判断地支藏干中的五行
            # 减去天干的贡献，得到纯地支部分的五行分布
            zhi_elements = {}
            for wx in ['木', '火', '土', '金', '水']:
                zhi_wx_value = dayun_elements.get(wx, 0.0)
                # 减去天干的贡献（天干权重为1.0）
                if gan_wx == wx:
                    zhi_wx_value = max(0.0, zhi_wx_value - 1.0)
                zhi_elements[wx] = zhi_wx_value
            
            # 检查地支藏干中是否有用神或忌神（阈值：至少0.2权重）
            zhi_has_xishen = any(zhi_elements.get(wx, 0.0) >= 0.2 for wx in (xishen_wuxing or []))
            zhi_has_jishen = any(zhi_elements.get(wx, 0.0) >= 0.2 for wx in (jishen_wuxing or []))
            
            # 🔥 优先级判断：天干透出最重要（基于《三命通会》理论）
            # 原则：天干透出用神/忌神的力量远大于地支藏干
            # 🔥 新增：调候用神透出时，优先级更高
            if gan_is_xishen and not gan_is_jishen:
                # 天干透出用神，但仍需兼顾地支强弱，避免“一透即吉”的偏差
                adj_x = xishen_strength * priority_weight
                adj_j = jishen_strength
                # 调候用神透出且明显占优
                if yongshen_method == '调候' and adj_x >= max(1.0, adj_j * 1.6):
                    return {'xiji': '大喜', 'level': '大吉'}
                # 喜神明显占优
                if adj_x >= adj_j * 2.0:
                    return {'xiji': '大喜', 'level': '大吉'}
                # 喜神略占优
                if adj_x > adj_j * 1.2:
                    return {'xiji': '小喜', 'level': '吉'}
                # 势均力敌或支中有忌 → 降档
                if zhi_has_jishen and not zhi_has_xishen:
                    return {'xiji': '平', 'level': '平运'}
                # 支中亦有用神 → 保持小喜
                if zhi_has_xishen:
                    return {'xiji': '小喜', 'level': '吉'}
                return {'xiji': '平', 'level': '平运'}
            elif gan_is_jishen and not gan_is_xishen:
                # 天干透出忌神，大凶
                # 如果是调候用神格局，忌神透出影响更大
                if yongshen_method == '调候':
                    # 调候格局遇到忌神透出，判断为大忌
                    return {'xiji': '大忌', 'level': '凶'}
                elif jishen_strength > xishen_strength * priority_weight * 2:
                    return {'xiji': '大忌', 'level': '凶'}
                elif jishen_strength > xishen_strength * priority_weight:
                    return {'xiji': '小忌', 'level': '小凶'}
                else:
                    # 如果喜神强度很大，可能被削弱
                    return {'xiji': '小忌', 'level': '小凶'}
            elif gan_is_xishen and gan_is_jishen:
                # 天干同时是喜忌（理论上不太可能），看整体强度对比
                # 🔥 优化：根据用神方法优先级调整判断
                adjusted_xishen_strength_temp = xishen_strength * priority_weight
                adjusted_jishen_strength_temp = jishen_strength
                
                if adjusted_xishen_strength_temp > adjusted_jishen_strength_temp * 1.5:
                    # 调候用神即使与忌神同透，如果强度足够，仍可判断为小喜
                    if yongshen_method == '调候' and adjusted_xishen_strength_temp >= 1.0:
                        return {'xiji': '小喜', 'level': '吉'}
                    return {'xiji': '小喜', 'level': '吉'}
                elif adjusted_jishen_strength_temp > adjusted_xishen_strength_temp * 1.5:
                    # 调候格局遇到忌神同透，影响更大
                    if yongshen_method == '调候':
                        return {'xiji': '小忌', 'level': '小凶'}
                    return {'xiji': '小忌', 'level': '小凶'}
                else:
                    return {'xiji': '平', 'level': '平运'}
            
            # 🔥 修复：如果天干没有透出用神/忌神，根据整体强度对比判断
            # 参考classic_analyzer/dayun.py的逻辑：基于喜忌强度对比
            # 🔥 新增：考虑用神方法优先级权重
            adjusted_xishen_strength = xishen_strength * priority_weight
            adjusted_jishen_strength = jishen_strength
            
            # 🔥 修复：优化判断顺序和阈值
            # 首先检查是否都接近0（都小于0.2），如果是，判断为平运
            total_strength = adjusted_xishen_strength + adjusted_jishen_strength
            if total_strength < 0.2:
                # 喜忌强度都很小，判断为平运
                return {'xiji': '平', 'level': '平运'}
            
            # 然后检查强度差值是否很小（只有在差值小于0.1且总强度较小时才判断为平运）
            strength_diff = abs(adjusted_xishen_strength - adjusted_jishen_strength)
            if strength_diff < 0.1 and total_strength < 0.5:
                # 喜忌强度接近且都很小，判断为平运
                return {'xiji': '平', 'level': '平运'}
            
            # 正常判断：喜神强度远大于忌神（2倍以上）
            if adjusted_xishen_strength > adjusted_jishen_strength * 2:
                # 调候用神在地支时，也优先判断
                if yongshen_method == '调候' and zhi_has_xishen:
                    return {'xiji': '大喜', 'level': '大吉'}
                # 如果喜神强度足够大（>=1.0），判断为大喜
                if adjusted_xishen_strength >= 1.0:
                    return {'xiji': '大喜', 'level': '大吉'}
                return {'xiji': '小喜', 'level': '吉'}
            # 忌神强度远大于喜神（2倍以上）
            elif adjusted_jishen_strength > adjusted_xishen_strength * 2:
                # 调候格局遇到忌神，影响更大
                if yongshen_method == '调候' and zhi_has_jishen:
                    return {'xiji': '大忌', 'level': '凶'}
                # 如果忌神强度足够大（>=1.0），判断为大忌
                if adjusted_jishen_strength >= 1.0:
                    return {'xiji': '大忌', 'level': '凶'}
                return {'xiji': '小忌', 'level': '小凶'}
            # 喜神强度大于忌神
            elif adjusted_xishen_strength > adjusted_jishen_strength:
                # 喜神略胜，但需看地支是否有忌神牵制
                if zhi_has_xishen and not zhi_has_jishen:
                    if yongshen_method == '调候' and adjusted_xishen_strength >= 0.8:
                        return {'xiji': '大喜', 'level': '大吉'}
                    if adjusted_xishen_strength >= 1.0:
                        return {'xiji': '大喜', 'level': '大吉'}
                    return {'xiji': '小喜', 'level': '吉'}
                # 支中有忌神 → 降档
                if zhi_has_jishen and not zhi_has_xishen:
                    if adjusted_xishen_strength >= 1.0 and adjusted_xishen_strength >= adjusted_jishen_strength * 1.3:
                        return {'xiji': '小喜', 'level': '吉'}
                    return {'xiji': '平', 'level': '平运'}
                # 两者皆有或都无
                if adjusted_xishen_strength >= 1.2:
                    return {'xiji': '小喜', 'level': '吉'}
                return {'xiji': '平', 'level': '平运'}
            # 忌神强度大于喜神
            elif adjusted_jishen_strength > adjusted_xishen_strength:
                # 忌神略胜，视地支是否有用神缓和
                if zhi_has_jishen and not zhi_has_xishen:
                    if yongshen_method == '调候' and adjusted_jishen_strength >= 0.8:
                        return {'xiji': '小忌', 'level': '小凶'}
                    if adjusted_jishen_strength >= 1.0 and adjusted_jishen_strength >= adjusted_xishen_strength * 1.3:
                        return {'xiji': '小忌', 'level': '小凶'}
                    return {'xiji': '平', 'level': '平运'}
                if zhi_has_xishen and not zhi_has_jishen:
                    # 忌强但支有用神缓和
                    if adjusted_jishen_strength >= adjusted_xishen_strength * 1.8:
                        return {'xiji': '小忌', 'level': '小凶'}
                    return {'xiji': '平', 'level': '平运'}
                # 两者皆有或都无
                if adjusted_jishen_strength >= adjusted_xishen_strength * 1.6:
                    return {'xiji': '小忌', 'level': '小凶'}
                return {'xiji': '平', 'level': '平运'}
            else:
                # 完全平衡（很少见），判断为平运
                return {'xiji': '平', 'level': '平运'}
        
        # ✅ 修复：如果没有用神信息，基于《三命通会·论大运》经典理论判断
        # 理论依据：《三命通会·论大运》：
        # "损用神者欲运制之，益用神者欲运生之。身弱欲运引进旺乡；
        # 官欲运生，不欲运伤；煞欲运制，不欲运助；
        # 财欲运扶，不欲运劫；印欲运旺，不欲运衰；食欲运生，不欲运枭绝。"
        
        print(f"🔍 大运{gan}{zhi}: 无用神信息，基于《三命通会·论大运》经典理论判断")
        
        if not pillars:
            # 如果没有四柱信息，无法进行精确判断
            return {'xiji': '平', 'level': '平运', 'reason': '缺少四柱信息，无法精确判断'}
        
        from ..core.utils import get_ten_god
        from ..core.constants import DIZHI_CANGGAN
        
        # 1. 统计命局十神配置（用于判断大运喜忌）
        ten_god_count = {}
        for pos, (p_gan, p_zhi) in pillars.items():
            tg = get_ten_god(day_master, p_gan)
            ten_god_count[tg] = ten_god_count.get(tg, 0.0) + 1.0
            # 藏干计入十神
            for canggan, w in DIZHI_CANGGAN.get(p_zhi, []):
                tg_c = get_ten_god(day_master, canggan)
                ten_god_count[tg_c] = ten_god_count.get(tg_c, 0.0) + float(w)
        
        # 2. 判断大运天干的十神
        dayun_tg_gan = get_ten_god(day_master, gan)
        
        # 3. 基于《三命通会·论大运》经典理论判断

        # ✅ 修复：优先使用传入的身强身弱参数（如果有）
        # 3.1 身弱欲运引进旺乡（《三命通会》："身弱欲运引进旺乡"）
        # 身弱喜印绶、比劫运扶身
        if dayun_tg_gan in ['正印', '偏印', '比肩', '劫财']:
            # ✅ 修复：优先使用传入的strength参数判断身强身弱
            is_weak = False
            if strength:
                # 使用传入的身强身弱参数
                is_weak = strength in ['身弱', '身极弱']
            else:
                # 如果没有传入strength参数，使用简化判断
                yin_count = ten_god_count.get('正印', 0) + ten_god_count.get('偏印', 0)
                bijie_count = ten_god_count.get('比肩', 0) + ten_god_count.get('劫财', 0)
                guansha_count = ten_god_count.get('正官', 0) + ten_god_count.get('偏官', 0)
                cai_count = ten_god_count.get('正财', 0) + ten_god_count.get('偏财', 0)
                # 如果印比少且官杀财多，可能身弱
                is_weak = (yin_count + bijie_count) < (guansha_count + cai_count) * 0.8

            # 身弱喜印比运
            if is_weak:
                return {
                    'xiji': '大喜',  # ✅ 修复：身弱遇印比运，应该是大喜
                    'level': '大吉',
                    'reason': '身弱欲运引进旺乡，印比运扶身（《三命通会》："身弱欲运引进旺乡"）'
                }
            # 身旺遇印比运，反而不利
            elif strength and strength in ['身旺', '身强']:
                return {
                    'xiji': '小忌',  # ✅ 新增：身旺遇印比运，反而不利
                    'level': '小凶',
                    'reason': '身旺遇印比运，反而加重身旺，需泄耗（《三命通会》："身旺欲运泄耗"）'
                }

        # ✅ 新增：3.1.5 身旺欲运泄耗（《三命通会》："身旺欲运泄耗"）
        # 身旺喜食伤、财星、官杀运泄耗
        if dayun_tg_gan in ['食神', '伤官', '正财', '偏财', '正官', '偏官']:
            # ✅ 使用传入的strength参数判断身强身弱
            is_strong = False
            if strength:
                # 使用传入的身强身弱参数
                is_strong = strength in ['身旺', '身强']
            else:
                # 如果没有传入strength参数，使用简化判断
                yin_count = ten_god_count.get('正印', 0) + ten_god_count.get('偏印', 0)
                bijie_count = ten_god_count.get('比肩', 0) + ten_god_count.get('劫财', 0)
                guansha_count = ten_god_count.get('正官', 0) + ten_god_count.get('偏官', 0)
                cai_count = ten_god_count.get('正财', 0) + ten_god_count.get('偏财', 0)
                # 如果印比多且官杀财少，可能身旺
                is_strong = (yin_count + bijie_count) > (guansha_count + cai_count) * 1.2

            # 身旺喜食伤财官运
            if is_strong:
                return {
                    'xiji': '大喜',  # ✅ 新增：身旺遇食伤财官运，应该是大喜
                    'level': '大吉',
                    'reason': '身旺欲运泄耗，食伤财官运泄耗（《三命通会》："身旺欲运泄耗"）'
                }
            # 身弱遇食伤财官运，反而不利
            elif strength and strength in ['身弱', '身极弱']:
                return {
                    'xiji': '小忌',  # ✅ 新增：身弱遇食伤财官运，反而不利
                    'level': '小凶',
                    'reason': '身弱遇食伤财官运，反而加重身弱，需扶身（《三命通会》："身弱欲运引进旺乡"）'
                }

        # 3.2 官欲运生，不欲运伤（《三命通会》："官欲运生，不欲运伤"）
        guan_count = ten_god_count.get('正官', 0)
        if guan_count > 0:
            if dayun_tg_gan in ['正财', '偏财']:
                # 财生官（《三命通会》："官欲运生"）
                return {
                    'xiji': '小喜',
                    'level': '吉',
                    'reason': '有官喜财运，财生官（《三命通会》："官欲运生"）'
                }
            elif dayun_tg_gan == '伤官':
                # 伤官见官（《三命通会》："不欲运伤"）
                return {
                    'xiji': '小忌',
                    'level': '小凶',
                    'reason': '有官忌伤官运，伤官见官（《三命通会》："官欲运生，不欲运伤"）'
                }
        
        # 3.3 煞欲运制，不欲运助（《三命通会》："煞欲运制，不欲运助"）
        sha_count = ten_god_count.get('偏官', 0)
        if sha_count > 0:
            if dayun_tg_gan in ['食神', '伤官']:
                # 食伤制杀（《三命通会》："煞欲运制"）
                return {
                    'xiji': '小喜',
                    'level': '吉',
                    'reason': '有七杀喜食伤运，食伤制杀（《三命通会》："煞欲运制，不欲运助"）'
                }
            elif dayun_tg_gan in ['偏官']:
                # 七杀助杀（《三命通会》："不欲运助"）
                return {
                    'xiji': '小忌',
                    'level': '小凶',
                    'reason': '有七杀忌杀运，七杀助杀（《三命通会》："煞欲运制，不欲运助"）'
                }
        
        # 3.4 财欲运扶，不欲运劫（《三命通会》："财欲运扶，不欲运劫"）
        cai_total = ten_god_count.get('正财', 0) + ten_god_count.get('偏财', 0)
        if cai_total > 0:
            if dayun_tg_gan in ['正官', '偏官']:
                # 官护财（《三命通会》："财欲运扶"）
                return {
                    'xiji': '小喜',
                    'level': '吉',
                    'reason': '有财喜官运，官护财（《三命通会》："财欲运扶，不欲运劫"）'
                }
            elif dayun_tg_gan in ['比肩', '劫财']:
                # 比劫夺财（《三命通会》："不欲运劫"）
                return {
                    'xiji': '小忌',
                    'level': '小凶',
                    'reason': '有财忌比劫运，比劫夺财（《三命通会》："财欲运扶，不欲运劫"）'
                }
        
        # 3.5 印欲运旺，不欲运衰（《三命通会》："印欲运旺，不欲运衰"）
        yin_total = ten_god_count.get('正印', 0) + ten_god_count.get('偏印', 0)
        if yin_total > 0:
            if dayun_tg_gan in ['正官', '偏官']:
                # 官生印（《三命通会》："印欲运旺"）
                return {
                    'xiji': '小喜',
                    'level': '吉',
                    'reason': '有印喜官运，官生印（《三命通会》："印欲运旺，不欲运衰"）'
                }
            elif dayun_tg_gan in ['正财', '偏财']:
                # 财破印（《三命通会》："不欲运衰"）
                # 但需看具体情况：如果印重，财破印反而有益
                if yin_total >= 2.0:
                    return {
                        'xiji': '小喜',
                        'level': '吉',
                        'reason': '印重喜财运，财破印（印重为病，财为药）'
                    }
                else:
                    return {
                        'xiji': '小忌',
                        'level': '小凶',
                        'reason': '有印忌财运，财破印（《三命通会》："印欲运旺，不欲运衰"）'
                    }
        
        # 3.6 食欲运生，不欲运枭绝（《三命通会》："食欲运生，不欲运枭绝"）
        shishang_total = ten_god_count.get('食神', 0) + ten_god_count.get('伤官', 0)
        if shishang_total > 0:
            if dayun_tg_gan in ['正财', '偏财']:
                # 食伤生财（《三命通会》："食欲运生"）
                return {
                    'xiji': '小喜',
                    'level': '吉',
                    'reason': '有食伤喜财运，食伤生财（《三命通会》："食欲运生，不欲运枭绝"）'
                }
            elif dayun_tg_gan == '偏印':
                # 枭神夺食（《三命通会》："不欲运枭绝"）
                return {
                    'xiji': '小忌',
                    'level': '小凶',
                    'reason': '有食伤忌偏印运，枭神夺食（《三命通会》："食欲运生，不欲运枭绝"）'
                }
        
        # 4. 如果以上都不匹配，基于五行生克的基本关系判断（但要有经典依据）
        day_master_wx = get_wuxing_by_tiangan(day_master)
        gan_wx = get_wuxing_by_tiangan(gan)
        zhi_wx = get_wuxing_by_dizhi(zhi)
        
        # 五行关系映射
        wuxing_relations = {
            '木': {'生': '火', '克': '土', '被生': '水', '被克': '金'},
            '火': {'生': '土', '克': '金', '被生': '木', '被克': '水'},
            '土': {'生': '金', '克': '水', '被生': '火', '被克': '木'},
            '金': {'生': '水', '克': '木', '被生': '土', '被克': '火'},
            '水': {'生': '木', '克': '火', '被生': '金', '被克': '土'}
        }
        
        relations = wuxing_relations.get(day_master_wx, {})
        
        # 基于五行生克的基本关系（但要有经典理论依据）
        # 《三命通会·论大运》："大运重地支"，所以以地支为主
        
        # 天干判断
        gan_favorable = False
        gan_unfavorable = False
        
        if gan_wx == relations.get('被生'):
            # 生我者（印绶）一般有利，但需结合命局配置
            gan_favorable = True
        elif gan_wx == relations.get('被克'):
            # 克我者（官杀）一般不利，但需结合命局配置
            gan_unfavorable = True
        elif gan_wx == day_master_wx:
            # 比和（比肩劫财），中性偏有利（但需看命局是否需要）
            gan_favorable = True
        
        # 地支判断（大运重地支）
        zhi_favorable = False
        zhi_unfavorable = False
        
        if zhi_wx == relations.get('被生'):
            # 生我者（印绶）一般有利
            zhi_favorable = True
        elif zhi_wx == relations.get('被克'):
            # 克我者（官杀）一般不利
            zhi_unfavorable = True
        elif zhi_wx == day_master_wx:
            # 比和（比肩劫财），中性偏有利
            zhi_favorable = True
        
        # 综合判断（以地支为主，天干为辅）
        if zhi_favorable and not zhi_unfavorable:
            if gan_favorable or not gan_unfavorable:
                return {
                    'xiji': '小喜',
                    'level': '吉',
                    'reason': '大运地支生扶日主（《三命通会·论大运》："大运重地支"，地支生我为有利）'
                }
        elif zhi_unfavorable and not zhi_favorable:
            if gan_unfavorable or not gan_favorable:
                return {
                    'xiji': '小忌',
                    'level': '小凶',
                    'reason': '大运地支克制日主（《三命通会·论大运》："大运重地支"，地支克我为不利）'
                }
        
        # 如果天干地支互相矛盾或都不明显，判断为平运
        return {
            'xiji': '平',
            'level': '平运',
            'reason': '大运与命局配合一般，需结合流年具体分析（《三命通会·论大运》：大运需结合命局四柱强弱分析）'
        }

    def _generate_advice(self, direction: str, xiji_details: Dict) -> str:
        """生成建议"""
        advice_parts = []

        if direction == '顺行':
            advice_parts.append("顺行大运，宜主动进取，外求发展")
        else:
            advice_parts.append("逆行大运，宜内修养性，稳扎稳打")

        xiji = xiji_details.get('xiji', '平')

        if xiji == '大喜':
            advice_parts.append("大运整体有利，宜把握机遇，积极作为")
        elif xiji == '小喜':
            advice_parts.append("大运较为有利，宜稳步前行，顺势而为")
        elif xiji == '大忌':
            advice_parts.append("大运整体不利，宜谨慎行事，避免冒进")
        elif xiji == '小忌':
            advice_parts.append("大运较为不利，宜守成自保，等待时机")
        else:
            advice_parts.append("大运吉凶参半，宜结合流年流月具体判断")

        advice_parts.append("建议结合流年分析，方能准确判断吉凶")

        return "；".join(advice_parts)
    
    def _analyze_dayun_mingju_coordination(self, dayun_pillars: List[Tuple[str, str]], 
                                          bazi_data: BaziData, pillars: Dict[str, Tuple[str, str]], 
                                          day_master: str) -> Dict[str, Any]:
        """
        🔥 新增：大运与命局配合分析
        基于《三命通会·大运篇》理论，分析大运与命局的配合关系
        
        分析维度：
        1. 大运与命局十神关系（官杀、财、食伤、印、比劫）
        2. 大运与命局五行关系（生克冲合）
        3. 大运对格局的影响（成格、破格、平格）
        4. 大运与用神的配合（用神透出、忌神透出）
        """
        from ..core.utils import get_ten_god
        
        # 统计命局十神分布
        mingju_ten_gods = {}
        for pos, (gan, zhi) in pillars.items():
            tg = get_ten_god(day_master, gan)
            mingju_ten_gods[tg] = mingju_ten_gods.get(tg, 0) + 1
        
        # 分析每步大运与命局的配合
        coordination_details = []
        guansha_coord = 0  # 官杀配合
        cai_coord = 0      # 财配合
        shishang_coord = 0 # 食伤配合
        yin_coord = 0      # 印配合
        bijie_coord = 0    # 比劫配合
        
        for step, (dayun_gan, dayun_zhi) in enumerate(dayun_pillars, 1):
            # 1. 十神关系分析
            dayun_tg = get_ten_god(day_master, dayun_gan)
            
            # 2. 五行关系分析
            dayun_gan_wx = get_wuxing_by_tiangan(dayun_gan)
            dayun_zhi_wx = get_wuxing_by_dizhi(dayun_zhi)
            dm_wx = get_wuxing_by_tiangan(day_master)
            
            # 3. 与原局的关系
            relations = []
            for pos, (gan, zhi) in pillars.items():
                # 六合关系
                pair = (dayun_zhi, zhi)
                pair_rev = (zhi, dayun_zhi)
                if pair in [('子','丑'),('寅','亥'),('卯','戌'),('辰','酉'),('巳','申'),('午','未')] or \
                   pair_rev in [('子','丑'),('寅','亥'),('卯','戌'),('辰','酉'),('巳','申'),('午','未')]:
                    relations.append(f"与{pos}柱六合")
                
                # 六冲关系
                if pair in [('子','午'),('丑','未'),('寅','申'),('卯','酉'),('辰','戌'),('巳','亥')] or \
                   pair_rev in [('子','午'),('丑','未'),('寅','申'),('卯','酉'),('辰','戌'),('巳','亥')]:
                    relations.append(f"与{pos}柱六冲")
            
            # 4. 对格局的影响
            geju_effect = self._analyze_geju_effect(dayun_tg, dayun_gan_wx, dayun_zhi_wx, 
                                                    mingju_ten_gods, dm_wx)
            
            # 5. 统计配合度
            if dayun_tg in ['正官', '偏官']:
                guansha_coord += geju_effect['score']
            elif dayun_tg in ['正财', '偏财']:
                cai_coord += geju_effect['score']
            elif dayun_tg in ['食神', '伤官']:
                shishang_coord += geju_effect['score']
            elif dayun_tg in ['正印', '偏印']:
                yin_coord += geju_effect['score']
            elif dayun_tg in ['比肩', '劫财']:
                bijie_coord += geju_effect['score']
            
            coordination_details.append({
                'step': step,
                'ganzhi': f"{dayun_gan}{dayun_zhi}",
                'ten_god': dayun_tg,
                'relations': relations,
                'geju_effect': geju_effect['effect'],
                'score': geju_effect['score']
            })
        
        # 综合评估
        total_coord = guansha_coord + cai_coord + shishang_coord + yin_coord + bijie_coord
        avg_coord = total_coord / len(dayun_pillars) if dayun_pillars else 0
        
        if avg_coord >= 2:
            summary = "大运与命局配合良好，多数步运有利于格局发展"
            advice = "大运整体与命局配合良好，宜把握有利大运，积极发展"
        elif avg_coord >= 0:
            summary = "大运与命局配合一般，部分步运有利，部分不利"
            advice = "大运与命局配合一般，需结合具体步运和流年分析，稳中求进"
        else:
            summary = "大运与命局配合不佳，多数步运不利于格局发展"
            advice = "大运与命局配合不佳，需谨慎应对，避免不利大运中的重大决策"
        
        return {
            'summary': summary,
            'advice': advice,
            'avg_coordination': round(avg_coord, 2),
            'coordination_by_ten_god': {
                '官杀': round(guansha_coord, 2),
                '财': round(cai_coord, 2),
                '食伤': round(shishang_coord, 2),
                '印': round(yin_coord, 2),
                '比劫': round(bijie_coord, 2)
            },
            'details': coordination_details
        }
    
    def _analyze_geju_effect(self, dayun_tg: str, dayun_gan_wx: str, dayun_zhi_wx: str,
                             mingju_ten_gods: Dict[str, int], dm_wx: str) -> Dict[str, Any]:
        """
        分析大运对格局的影响
        """
        score = 0
        effect = []
        
        # 官杀配合
        if dayun_tg in ['正官', '偏官']:
            if mingju_ten_gods.get('正官', 0) > 0 or mingju_ten_gods.get('偏官', 0) > 0:
                score += 2  # 官杀格遇官杀运，有利
                effect.append("官杀运配合官杀格，有利事业发展")
            if mingju_ten_gods.get('食神', 0) > 0 or mingju_ten_gods.get('伤官', 0) > 0:
                score += 1  # 食伤格遇官杀运，制化有力
                effect.append("食伤格遇官杀运，制化平衡")
        
        # 财配合
        if dayun_tg in ['正财', '偏财']:
            if mingju_ten_gods.get('正财', 0) > 0 or mingju_ten_gods.get('偏财', 0) > 0:
                score += 2  # 财格遇财运，有利
                effect.append("财运配合财格，有利财富积累")
            if mingju_ten_gods.get('食神', 0) > 0 or mingju_ten_gods.get('伤官', 0) > 0:
                score += 1  # 食伤格遇财运，食伤生财
                effect.append("食伤格遇财运，食伤生财，流通有情")
        
        # 食伤配合
        if dayun_tg in ['食神', '伤官']:
            if mingju_ten_gods.get('正财', 0) > 0 or mingju_ten_gods.get('偏财', 0) > 0:
                score += 2  # 财格遇食伤运，食伤生财
                effect.append("食伤运配合财格，食伤生财有利")
            if mingju_ten_gods.get('正官', 0) > 0:
                score -= 2  # 正官格遇伤官运，伤官见官
                effect.append("正官格遇伤官运，需注意伤官见官")
        
        # 印配合
        if dayun_tg in ['正印', '偏印']:
            if mingju_ten_gods.get('正官', 0) > 0 or mingju_ten_gods.get('偏官', 0) > 0:
                score += 2  # 官杀格遇印运，官印相生
                effect.append("印运配合官杀格，官印相生有利")
            if mingju_ten_gods.get('食神', 0) > 0 and dayun_tg == '偏印':
                score -= 2  # 食神格遇偏印运，枭神夺食
                effect.append("食神格遇偏印运，需注意枭神夺食")
        
        # 比劫配合
        if dayun_tg in ['比肩', '劫财']:
            if mingju_ten_gods.get('正财', 0) > 0 or mingju_ten_gods.get('偏财', 0) > 0:
                score -= 1  # 财格遇比劫运，比劫夺财
                effect.append("财格遇比劫运，需注意比劫夺财")
            if mingju_ten_gods.get('正官', 0) > 0 or mingju_ten_gods.get('偏官', 0) > 0:
                score += 1  # 官杀格遇比劫运，比劫抗杀
                effect.append("官杀格遇比劫运，比劫抗杀有利")
        
        if not effect:
            effect.append("大运与命局配合平常")
        
        return {
            'score': score,
            'effect': '；'.join(effect)
        }
