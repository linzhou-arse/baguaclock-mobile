#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《渊海子平》统一分析器 - 十神分布、身强身弱判定、格局分析
✅ 第二阶段修复：增强格局分析和理论深度
"""

from __future__ import annotations
from typing import Dict, Tuple, List, Union, Any
from ..core.base_analyzer import BaseAnalyzer
from ..core.data_structures import BaziData, AnalysisResult, AnalysisConfig
from ..core.utils import create_analysis_result, get_ten_god, get_wuxing_by_tiangan, get_wuxing_by_dizhi
from ..core.constants import DIZHI_CANGGAN


class YuanhaizipingAnalyzer(BaseAnalyzer):
    """《渊海子平》统一分析器"""
    
    def __init__(self, config: AnalysisConfig = None):
        super().__init__("渊海子平统一分析器", "渊海子平", config)
    
    def analyze(self, bazi_data: BaziData) -> AnalysisResult:
        """
        执行十神与强弱分析，并识别主要格局
        ✅ 已修复：
        1. 完整的身强身弱判断（基于支持力与制约力对比，《子平真诠》理论）
        2. 格局以月令为主，不只看十神数量
        3. 动态评分，不再硬编码60分
        """
        pillars = bazi_data.get_pillars()
        day_master = bazi_data.get_day_master()
        month_branch = bazi_data.get_month_branch()
        month_gan = pillars['month'][0]

        # 统计十神分布
        ten_god_count: Dict[str, float] = {}
        for pos, (gan, zhi) in pillars.items():
            tg = get_ten_god(day_master, gan)
            ten_god_count[tg] = ten_god_count.get(tg, 0.0) + 1.0
            # 藏干计入十神
            for canggan, w in DIZHI_CANGGAN.get(zhi, []):
                tg_c = get_ten_god(day_master, canggan)
                ten_god_count[tg_c] = ten_god_count.get(tg_c, 0.0) + float(w)

        # ✅ 完整的身强身弱判断：基于支持力与制约力对比（《子平真诠》理论）
        strength_score, strength_details = self._comprehensive_strength_analysis(
            day_master, pillars, month_branch
        )

        # ✅ 修复：基于新的强度等级判断（支持更多细分等级）
        strength_level = strength_details.get('strength_level', '中和')
        
        # 映射到原有强度等级（保持兼容性）
        if strength_level in ['身极旺', '身旺']:
            strength = '身旺'
            strength_delta = 8
        elif strength_level in ['身强', '身偏强']:
            strength = '身强'
            strength_delta = 4
        elif '中和' in strength_level:
            strength = '中和'
            strength_delta = 0
        elif strength_level in ['身偏弱', '身弱']:
            strength = '身弱'
            strength_delta = -4
        else:  # 身极弱
            strength = '身极弱'
            strength_delta = -8

        # ✅ 格局以月令为主（月支藏干的本气十神）
        # ✅ 修复：传入ten_god_count和pillars以识别高级格局（如伤官配印格）
        # ✅ 修复：pillars用于检查印星是否透干、有根，以及财星坏印等破格条件
        month_pattern = self._determine_pattern_by_month(day_master, month_branch, month_gan, ten_god_count, pillars)

        # 主要十神（用于辅助分析）
        main_tg = max(ten_god_count.items(), key=lambda x: x[1])[0] if ten_god_count else '未知'

        # 识别格局
        patterns = self._identify_patterns(ten_god_count, main_tg, strength_delta, month_pattern)

        # ✅ 计算基础分和格局加分
        base_score = self._calculate_base_score(month_pattern, strength_delta)
        pattern_bonus = self._calculate_pattern_bonus(month_pattern, strength_delta, ten_god_count)

        # ✅ 修复：不打分，只判断吉凶
        # 根据格局和身强身弱判断吉凶
        if month_pattern in ['正官格', '正财格', '正印格'] and strength in ['身旺', '身强', '中和']:
            level = '大吉'
        elif month_pattern and strength in ['身旺', '身强', '中和']:
            level = '吉'
        elif strength == '中和':
            level = '中平'
        elif strength in ['身弱', '身极弱']:
            level = '凶'
        else:
            level = '中平'

        score = 0  # 不打分

        # 生成描述
        pattern_str = f"；主格：{month_pattern}" if month_pattern else ""
        description = f"十神主导：{main_tg}；{strength}（得令{strength_details['deling']:.0f}%+得地{strength_details['dedi']:.0f}%+得气{strength_details['deqi']:.0f}%）{pattern_str}"
        advice = self._advice(main_tg, strength_delta, patterns, month_pattern)

        # 🔥 新增：完整财运分析（基于《渊海子平·论正财》《论偏财》）
        try:
            wealth_analysis = self._analyze_wealth_comprehensive(
                day_master, pillars, month_branch, ten_god_count, strength, strength_score, month_pattern
            )
        except Exception as e:
            print(f"⚠️ 财运分析失败: {e}")
            import traceback
            traceback.print_exc()
            wealth_analysis = {}
        
        # 🔥 新增：完整事业分析（基于《渊海子平·正官论》《论偏官》）
        try:
            career_analysis = self._analyze_career_comprehensive(
                day_master, pillars, month_branch, ten_god_count, strength, strength_score, month_pattern
            )
        except Exception as e:
            print(f"⚠️ 事业分析失败: {e}")
            import traceback
            traceback.print_exc()
            career_analysis = {}
        
        # 🔥 新增：完整婚姻分析（基于《渊海子平》婚姻理论）
        try:
            marriage_analysis = self._analyze_marriage_comprehensive(
                day_master, pillars, bazi_data.gender, ten_god_count, strength, bazi_data.birth_year, bazi_data, month_pattern
            )
        except Exception as e:
            print(f"⚠️ 婚姻分析失败: {e}")
            import traceback
            traceback.print_exc()
            marriage_analysis = {}
        
        # 🔥 新增：完整六亲分析（基于《渊海子平·六亲章》）
        try:
            sixqin_analysis = self._analyze_sixqin_comprehensive(
                day_master, pillars, bazi_data.gender, ten_god_count, strength, birth_year=bazi_data.birth_year if hasattr(bazi_data, 'birth_year') else None
            )
        except Exception as e:
            print(f"⚠️ 六亲分析失败: {e}")
            import traceback
            traceback.print_exc()
            sixqin_analysis = {}
        
        # 🔥 新增：完整健康分析（基于《渊海子平·论疾病》）
        try:
            health_analysis = self._analyze_health_comprehensive(
                day_master, pillars, ten_god_count
            )
        except Exception as e:
            print(f"⚠️ 健康分析失败: {e}")
            import traceback
            traceback.print_exc()
            health_analysis = {}
        
        # 🔥 新增：性格分析（基于《渊海子平·论性情》）
        try:
            character_analysis = self._analyze_character_comprehensive(
                day_master, pillars, ten_god_count, strength, month_pattern
            )
        except Exception as e:
            print(f"⚠️ 性格分析失败: {e}")
            import traceback
            traceback.print_exc()
            character_analysis = {}

        return create_analysis_result(
            analyzer_name=self.name,
            book_name=self.book_name,
            analysis_type="十神与强弱分析",
            level=level,
            score=score,
            description=description,
            details={
                'ten_god_count': ten_god_count,
                'strength': strength,
                'strength_score': strength_score,
                'strength_details': strength_details,
                'main_ten_god': main_tg,
                'month_pattern': month_pattern,
                'patterns': patterns,
                'base_score': base_score,
                'pattern_bonus': pattern_bonus,
                # 🔥 新增：完整分析结果
                'wealth_analysis': wealth_analysis,
                'career_analysis': career_analysis,
                'marriage_analysis': marriage_analysis,
                'sixqin_analysis': sixqin_analysis,
                'health_analysis': health_analysis,
                'character_analysis': character_analysis
            },
            advice=advice
        )

    def _comprehensive_strength_analysis(self, day_master: str, pillars: Dict, month_branch: str) -> Tuple[float, Dict]:
        """
        完整的身强身弱分析 - 基于《子平真诠》《渊海子平》经典理论
        ✅ 修复：不再使用"得令40% + 得地30% + 得气30%"的加权评分
        改为基于支持力与制约力对比的经典判断方法
        
        理论依据：
        - 《子平真诠》："日主强弱，看支持力与制约力对比"
        - 支持力（比劫印绶）与制约力（财官食伤）的对比
        - 结合得令、得地、得气的综合判断
        """
        dm_wx = get_wuxing_by_tiangan(day_master)

        # ✅ 修复：基于经典理论判断身强身弱，而不是加权评分
        # 1. 分析支持力（比劫印绶）和制约力（财官食伤）
        support_power = 0.0
        pressure_power = 0.0
        
        # 五行关系
        sheng_map = {'木': '水', '火': '木', '土': '火', '金': '土', '水': '金'}  # 生我者（印绶）
        wo_sheng = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}  # 我生者（食伤）
        ke_map = {'木': '金', '火': '水', '土': '木', '金': '火', '水': '土'}  # 克我者（官杀）
        wo_ke = {'木': '土', '火': '金', '土': '水', '金': '木', '水': '火'}  # 我克者（财星）
        
        # 统计四柱五行分布（包括藏干）
        for pos, (gan, zhi) in pillars.items():
            gan_wx = get_wuxing_by_tiangan(gan)
            weight = 1.0
            
            # 支持力：日主本身、印绶（生我者）
            if gan_wx == dm_wx:
                support_power += weight * 1.5  # 日主本身
            elif gan_wx == sheng_map.get(dm_wx):
                support_power += weight * 1.0  # 印绶
            
            # 制约力：官杀（克我者）、财星（我克者）、食伤（我生者）
            if gan_wx == ke_map.get(dm_wx):
                pressure_power += weight * 1.0  # 官杀
            elif gan_wx == wo_ke.get(dm_wx):
                pressure_power += weight * 0.8  # 财星
            elif gan_wx == wo_sheng.get(dm_wx):
                pressure_power += weight * 0.6  # 食伤
            
            # 地支藏干
            for canggan, cg_weight in DIZHI_CANGGAN.get(zhi, []):
                cg_wx = get_wuxing_by_tiangan(canggan)
                branch_weight = weight * cg_weight
                
                # 支持力（藏干）
                if cg_wx == dm_wx:
                    support_power += branch_weight * 1.0
                elif cg_wx == sheng_map.get(dm_wx):
                    support_power += branch_weight * 0.8
                
                # 制约力（藏干）
                if cg_wx == ke_map.get(dm_wx):
                    pressure_power += branch_weight * 0.8
                elif cg_wx == wo_ke.get(dm_wx):
                    pressure_power += branch_weight * 0.6
                elif cg_wx == wo_sheng.get(dm_wx):
                    pressure_power += branch_weight * 0.4
        
        # 2. 判断得令（布尔值，用于综合判断）
        mb_wx = get_wuxing_by_dizhi(month_branch)
        deling = (mb_wx == dm_wx or mb_wx == sheng_map.get(dm_wx))
        # 保留百分比显示（用于用户显示）
        deling_score = 100 if deling else 0
        
        # 3. 判断得地（布尔值，用于综合判断）
        dedi = False
        for pos, (gan, zhi) in pillars.items():
            if pos == 'day':
                continue
            for canggan, _ in DIZHI_CANGGAN.get(zhi, []):
                if get_wuxing_by_tiangan(canggan) == dm_wx:
                    dedi = True
                    break
            if dedi:
                break
        # 保留百分比显示（用于用户显示）
        dedi_score = 100 if dedi else 0
        
        # 4. 判断得气（布尔值，用于综合判断）
        deqi = False
        for pos, (gan, zhi) in pillars.items():
            if pos == 'day':
                continue
            gan_wx = get_wuxing_by_tiangan(gan)
            if gan_wx == dm_wx or gan_wx == sheng_map.get(dm_wx):
                deqi = True
                break
        # 保留百分比显示（用于用户显示）
        deqi_score = 100 if deqi else 0
        
        # 5. 基于支持力与制约力对比判断强度等级
        total_power = support_power + pressure_power
        ratio = support_power / total_power if total_power > 0 else 0.5
        
        # 根据经典理论判断强度等级
        if ratio >= 0.65:
            strength_level = '身极旺' if deling else '身旺'
            strength_score = 90.0 if deling else 80.0
        elif ratio >= 0.55:
            if deling and dedi:
                strength_level = '身强'
                strength_score = 70.0
            elif deling or dedi:
                strength_level = '身偏强'
                strength_score = 60.0
            else:
                strength_level = '中和偏强'
                strength_score = 55.0
        elif ratio >= 0.45:
            if deling and dedi:
                strength_level = '中和'
                strength_score = 50.0
            else:
                strength_level = '中和偏弱'
                strength_score = 45.0
        elif ratio >= 0.35:
            if deling or dedi:
                strength_level = '身偏弱'
                strength_score = 40.0
            else:
                strength_level = '身弱'
                strength_score = 30.0
        else:
            strength_level = '身弱' if deling else '身极弱'
            strength_score = 30.0 if deling else 20.0
        
        # 转换为与原有等级兼容的格式（用于后续判断）
        if strength_level in ['身极旺', '身旺']:
            strength_score = max(70.0, strength_score)
        elif strength_level in ['身强', '身偏强']:
            strength_score = max(55.0, strength_score)
        elif strength_level in ['中和', '中和偏强', '中和偏弱']:
            strength_score = max(45.0, strength_score)
        elif strength_level in ['身偏弱', '身弱']:
            strength_score = max(30.0, strength_score)
        else:
            strength_score = 20.0

        details = {
            'deling': deling_score,  # 保留用于显示（百分比）
            'dedi': dedi_score,      # 保留用于显示（百分比）
            'deqi': deqi_score,      # 保留用于显示（百分比）
            'total': strength_score,
            'strength_level': strength_level,  # 新增：强度等级
            'support_power': support_power,   # 新增：支持力
            'pressure_power': pressure_power, # 新增：制约力
            'ratio': ratio                     # 新增：支持力占比
        }
        
        return strength_score, details

    def _calculate_deling(self, day_master_wx: str, month_branch: str) -> float:
        """计算得令分数（0-100）"""
        mb_wx = get_wuxing_by_dizhi(month_branch)

        # 五行关系
        sheng_map = {'木': '水', '火': '木', '土': '火', '金': '土', '水': '金'}
        wo_sheng = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        ke_map = {'木': '金', '火': '水', '土': '木', '金': '火', '水': '土'}

        if mb_wx == day_master_wx:
            return 100  # 月令同五行，得令
        elif mb_wx == sheng_map.get(day_master_wx):
            return 80  # 月令生我，得生
        elif mb_wx == wo_sheng.get(day_master_wx):
            return 30  # 我生月令，泄气
        elif mb_wx == ke_map.get(day_master_wx):
            return 10  # 月令克我，受克
        else:
            return 40  # 我克月令，耗力

    def _calculate_dedi(self, day_master_wx: str, pillars: Dict) -> float:
        """计算得地分数（0-100）：地支通根情况"""
        root_score = 0.0
        total_branches = 0

        for pos, (gan, zhi) in pillars.items():
            if pos == 'day':  # 日支权重最高
                weight = 1.5
            elif pos == 'month':  # 月支次之
                weight = 1.2
            else:  # 年支、时支
                weight = 1.0

            total_branches += weight

            # 检查地支藏干中是否有同五行
            for canggan, cg_weight in DIZHI_CANGGAN.get(zhi, []):
                cg_wx = get_wuxing_by_tiangan(canggan)
                if cg_wx == day_master_wx:
                    root_score += weight * cg_weight * 100

        return min(100, root_score / total_branches * 100) if total_branches > 0 else 0

    def _calculate_deqi(self, day_master_wx: str, pillars: Dict) -> float:
        """计算得气分数（0-100）：天干透出情况"""
        appear_count = 0
        total_gans = 0

        for pos, (gan, zhi) in pillars.items():
            if pos == 'day':  # 跳过日主自己
                continue

            total_gans += 1
            gan_wx = get_wuxing_by_tiangan(gan)

            # 同五行或生我的五行
            sheng_map = {'木': '水', '火': '木', '土': '火', '金': '土', '水': '金'}
            if gan_wx == day_master_wx:
                appear_count += 1.0  # 同五行
            elif gan_wx == sheng_map.get(day_master_wx):
                appear_count += 0.8  # 生我

        return (appear_count / total_gans * 100) if total_gans > 0 else 0

    def _determine_pattern_by_month(self, day_master: str, month_branch: str, month_gan: str, 
                                    ten_god_count: Dict[str, float] = None, pillars: Dict = None) -> str:
        """
        根据月令确定格局
        ✅ 新增：格局以月令为主，符合《渊海子平》理论
        ✅ 修复：识别高级格局（如伤官配印格、食神制杀格等）
        ✅ 修复：严格按照《子平真诠》理论，检查成格和破格条件
        """
        from ..core.utils import get_ten_god
        
        # 优先看月干
        month_ten_god = get_ten_god(day_master, month_gan)

        # 基础格局映射
        pattern_map = {
            '正官': '正官格',
            '偏官': '七杀格',
            '正财': '正财格',
            '偏财': '偏财格',
            '食神': '食神格',
            '伤官': '伤官格',
            '正印': '正印格',
            '偏印': '偏印格',
            '比肩': '建禄格',
            '劫财': '羊刃格'
        }
        
        base_pattern = pattern_map.get(month_ten_god, '普通格局')
        
        # ✅ 修复：识别高级格局（基于《子平真诠》《渊海子平》理论）
        # ✅ 修复：严格按照经典理论，检查成格和破格条件
        if ten_god_count:
            # 1. 伤官配印格（上上等）- 根据《子平真诠》：伤官配印，贵不可言
            if month_ten_god == '伤官':
                yin_count = ten_god_count.get('正印', 0) + ten_god_count.get('偏印', 0)

                # ✅ 修复：检查1 - 印星数量必须足够（至少>=0.8）
                # 理论依据：《子平真诠》："伤官佩印者，印能制伤，所以为贵"
                # 印星太弱（<0.8）不足以制伤官，不能成格
                if yin_count < 0.8:
                    return '伤官格'  # 印星太弱或无印星，基础格局

                # ✅ 修复：检查2 - 财星是否坏印（破格条件）
                # 理论依据：《子平真诠》："伤官佩印，不宜逢财"
                if pillars:
                    cai_count = ten_god_count.get('正财', 0) + ten_god_count.get('偏财', 0)
                    if cai_count >= 1.0 and cai_count >= yin_count * 1.5:
                        return '伤官格'  # 财星坏印，破格

                # ✅ 修复：检查3 - 伤官见官（破格条件）
                # 理论依据：《子平真诠》："伤官见官，为祸百端"
                guan_count = ten_god_count.get('正官', 0) if ten_god_count else 0
                if guan_count > 0:
                    return '伤官格'  # 伤官见官，破格

                # ✅ 修复：检查4 - 印星是否有力（有根或透干）
                # 理论依据：《子平真诠》："印星有根，方能制伤"
                if pillars:
                    # 检查印星是否透干
                    yin_tougan = False
                    for pos, (gan, zhi) in pillars.items():
                        if get_ten_god(day_master, gan) in ['正印', '偏印']:
                            yin_tougan = True
                            break

                    # 检查印星是否有根（地支藏干本气>=0.6）
                    yin_has_root = False
                    for pos, (gan, zhi) in pillars.items():
                        for canggan, w in DIZHI_CANGGAN.get(zhi, []):
                            if get_ten_god(day_master, canggan) in ['正印', '偏印'] and w >= 0.6:
                                yin_has_root = True
                                break

                    # ✅ 修复：印星必须透干或有根，否则不能成格
                    # 如果印星无力（无根无透），不能真正制约伤官
                    if not yin_tougan and not yin_has_root:
                        return '伤官格'  # 印星无力，不能成格

                # ✅ 所有条件满足，识别为"伤官配印格"
                return '伤官配印格'
            
            # 2. 食神制杀格（上等）- 根据《子平真诠》：食神制杀，权贵显达
            if month_ten_god == '食神':
                qisha_count = ten_god_count.get('偏官', 0)
                # ✅ 修复：只要有七杀即可，不需要>=0.5
                # 关键是食神能制约七杀，不是数量要达到多少
                if qisha_count > 0:  # 有七杀配合即可
                    return '食神制杀格'
            
            # 3. 官印相生格（上等）
            if month_ten_god in ['正官', '偏官']:
                yin_count = ten_god_count.get('正印', 0) + ten_god_count.get('偏印', 0)
                # ✅ 修复：只要有印星即可，不需要>=1.0
                # 关键是官能生印，印能生身，不是数量要达到多少
                if yin_count > 0:  # 有印星配合即可
                    return '官印相生格'
            
            # 4. 财官相生格（上等）
            if month_ten_god in ['正财', '偏财']:
                guan_count = ten_god_count.get('正官', 0) + ten_god_count.get('偏官', 0)
                # ✅ 修复：只要有官星即可，不需要>=0.5
                # 关键是财能生官，不是数量要达到多少
                if guan_count > 0:  # 有官星配合即可
                    return '财官相生格'
        
        return base_pattern

    def _calculate_base_score(self, month_pattern: str, strength_delta: int) -> float:
        """
        根据格局类型计算基础分
        ✅ 新增：不同格局有不同的基础分
        """
        pattern_scores = {
            '正官格': 68.0,
            '七杀格': 62.0,
            '正财格': 65.0,
            '偏财格': 63.0,
            '食神格': 66.0,
            '伤官格': 58.0,
            '正印格': 64.0,
            '偏印格': 60.0,
            '建禄格': 62.0,
            '羊刃格': 56.0,
            '普通格局': 60.0
        }

        return pattern_scores.get(month_pattern, 60.0)

    def _calculate_pattern_bonus(self, month_pattern: str, strength_delta: int, ten_god_count: Dict[str, float]) -> float:
        """
        根据格局成败计算加成分
        ✅ 新增：格局成败判断
        """
        bonus = 0.0
        strong = strength_delta > 0

        # 官杀格：身强喜官杀，身弱忌官杀
        if '官' in month_pattern or '杀' in month_pattern:
            bonus += 10 if strong else -10
            # 有印化杀
            if ten_god_count.get('正印', 0) + ten_god_count.get('偏印', 0) > 0:
                bonus += 5

        # 财格：身强喜财，身弱忌财
        elif '财' in month_pattern:
            bonus += 8 if strong else -8
            # 食伤生财
            if ten_god_count.get('食神', 0) + ten_god_count.get('伤官', 0) > 0:
                bonus += 4

        # 食伤格：身强可用，身弱泄气
        elif '食神' in month_pattern or '伤官' in month_pattern:
            bonus += 6 if strong else -6

        # 印格：身弱喜印，身强忌印
        elif '印' in month_pattern:
            bonus += 10 if not strong else -6

        # 建禄羊刃：身弱喜比劫，身强忌比劫
        elif '建禄' in month_pattern or '羊刃' in month_pattern:
            bonus += 8 if not strong else -8

        return bonus

    def _identify_patterns(self, ten_god_count: Dict[str, float], main_tg: str,
                          strength_delta: int, month_pattern: str) -> List[str]:
        """
        识别主要格局
        ✅ 已修复：以月令格局为主
        """
        patterns = [month_pattern] if month_pattern else []

        # 身强身弱的特殊格局
        if strength_delta > 4:
            patterns.append('身旺')
        elif strength_delta < -4:
            patterns.append('身弱')

        return patterns

    def _advice(self, main_tg: str, strength_delta: int, patterns: List[str] = None, month_pattern: str = None) -> str:
        """
        生成建议
        ✅ 已修复：根据月令格局和身强身弱给出建议
        """
        strong = strength_delta > 0

        # 根据月令格局给建议
        if month_pattern:
            if '正官格' in month_pattern:
                return "正官格，宜循规守纪，求取功名；身弱需先扶身，身强可任官职。"
            elif '七杀格' in month_pattern:
                return "七杀格，宜有制化，忌身弱；有印化杀为贵，有食伤制杀亦吉。"
            elif '正财格' in month_pattern:
                return "正财格，宜勤俭持家，稳健求财；身强财旺可大富，身弱忌贪财。"
            elif '偏财格' in month_pattern:
                return "偏财格，宜投资理财，把握机遇；身强可求横财，身弱宜守成。"
            elif '食神格' in month_pattern:
                return "食神格，宜才艺谋生，温和待人；忌枭神夺食，喜财星泄秀。"
            elif '伤官格' in month_pattern:
                return "伤官格，宜技艺专长，创新求变；伤官见官为祸百端，需有印化或财泄。"
            elif '正印格' in month_pattern:
                return "正印格，宜学习进修，文化事业；身弱喜印扶身，身强忌印过重。"
            elif '偏印格' in month_pattern:
                return "偏印格，宜偏门技艺，独特专长；忌食神同见（枭神夺食），需有财星制印。"
            elif '建禄格' in month_pattern:
                return "建禄格，宜自立创业，团队合作；身弱喜比劫扶身，身强需财官泄耗。"
            elif '羊刃格' in month_pattern:
                return "羊刃格，宜武职军警，刚强果断；需有官杀制刃（羊刃驾杀），否则易有凶险。"

        # 通用建议
        if strong:
            return "身强宜泄耗，喜食伤生财、财生官，忌比劫印绶过重。"
        else:
            return "身弱宜扶抑，喜印绶比劫扶身，忌官杀财星过重。"
    
    def _analyze_wealth_comprehensive(self, day_master: str, pillars: Dict, month_branch: str, 
                                      ten_god_count: Dict[str, float], strength: str, strength_score: float,
                                      month_pattern: str = None) -> Dict:
        """
        🔥 完整财运分析 - 基于《渊海子平·论正财》《论偏财》
        
        理论依据：
        - 《论正财》：正财者，吾妻之财也。财要得时，不要财多。财多生官，要须身健。
        - 《论偏财》：偏财者，乃众人之财也。财弱亦待历旺乡而荣。财盛无所往而不妙，且恐身势无力耳。
        
        分析项目（15项）：
        1. 财星识别（正财、偏财、位置）
        2. 财星当令（月令为财）
        3. 财星透干（天干有财）
        4. 财星得地（地支有财根）
        5. 财星有源（食伤生财）
        6. 财星有护（官杀护财）
        7. 财星数量评估
        8. 正财vs偏财比例
        9. 明财vs暗财
        10. 身强身弱与财运关系
        11. 财运等级判断
        12. 财运时机（大运、流年）
        13. 求财方式建议
        14. 适合行业
        15. 需要注意的年份
        """
        dm_wx = get_wuxing_by_tiangan(day_master)
        
        # 1. 财星识别
        wealth_stars = {'正财': [], '偏财': []}
        wealth_positions = {'year': [], 'month': [], 'day': [], 'hour': []}
        
        for pos, (gan, zhi) in pillars.items():
            tg = get_ten_god(day_master, gan)
            if tg == '正财':
                wealth_stars['正财'].append((pos, gan))
                wealth_positions[pos].append(('天干', gan, '正财'))
            elif tg == '偏财':
                wealth_stars['偏财'].append((pos, gan))
                wealth_positions[pos].append(('天干', gan, '偏财'))
            
            # 检查藏干中的财星
            for canggan, w in DIZHI_CANGGAN.get(zhi, []):
                tg_c = get_ten_god(day_master, canggan)
                if tg_c == '正财':
                    wealth_positions[pos].append(('藏干', canggan, '正财', w))
                elif tg_c == '偏财':
                    wealth_positions[pos].append(('藏干', canggan, '偏财', w))
        
        # 2. 财星当令（月令为财）
        month_gan = pillars['month'][0]
        month_tg = get_ten_god(day_master, month_gan)
        wealth_in_month = month_tg in ['正财', '偏财']
        
        # 检查月支藏干中的财星
        month_zhi = pillars['month'][1]
        month_zhi_has_wealth = False
        for canggan, w in DIZHI_CANGGAN.get(month_zhi, []):
            if get_ten_god(day_master, canggan) in ['正财', '偏财']:
                month_zhi_has_wealth = True
                break
        
        # 3. 财星透干
        wealth_tougan = len(wealth_stars['正财']) + len(wealth_stars['偏财']) > 0
        
        # 4. 财星得地（地支有财根）
        wealth_dedi = sum(len([x for x in wealth_positions[pos] if x[0] == '藏干']) 
                          for pos in ['year', 'month', 'day', 'hour']) > 0
        
        # 5. 财星有源（食伤生财）
        has_shishang = ten_god_count.get('食神', 0) + ten_god_count.get('伤官', 0) > 0
        wealth_has_source = has_shishang
        
        # 6. 财星有护（官杀护财）
        has_guansha = ten_god_count.get('正官', 0) + ten_god_count.get('偏官', 0) > 0
        wealth_has_protection = has_guansha
        
        # 7. 财星数量评估
        total_wealth_count = ten_god_count.get('正财', 0) + ten_god_count.get('偏财', 0)
        zhengcai_count = ten_god_count.get('正财', 0)
        piancai_count = ten_god_count.get('偏财', 0)
        
        # 8. 正财vs偏财比例
        if total_wealth_count > 0:
            zhengcai_ratio = zhengcai_count / total_wealth_count
            piancai_ratio = piancai_count / total_wealth_count
        else:
            zhengcai_ratio = 0
            piancai_ratio = 0
        
        # 9. 明财vs暗财
        mingcai = len(wealth_stars['正财']) + len(wealth_stars['偏财'])  # 天干透出
        ancai = total_wealth_count - mingcai  # 藏干中的财
        
        # 10. 身强身弱与财运关系（基于《渊海子平》原文）
        # "财要得时，不要财多。若财多则自家日本有力，可以胜任"
        # "力不任财，祸患百出"
        strong = strength in ['身旺', '身强']
        wealth_strength_match = False
        if total_wealth_count > 0:
            if strong and total_wealth_count >= 2:
                wealth_strength_match = True  # 身强财多，可以胜任
            elif not strong and total_wealth_count <= 1:
                wealth_strength_match = True  # 身弱财少，勉强可用
            elif strong and total_wealth_count < 2:
                wealth_strength_match = False  # 身强财少，需要财多
            else:
                wealth_strength_match = False  # 身弱财多，力不任财
        
        # 11. 财库分析（基于《渊海子平·论财库》《三命通会·财库论》）
        caiku_info = self._analyze_caiku(day_master, pillars, total_wealth_count)
        
        # 12. 财运等级判断（基于《渊海子平》理论）
        # ✅ 修复：传入格局信息和其他必要参数，考虑格局对财运的影响（如伤官配印格）
        # ✅ 修复：传入财库信息，优先判断日坐财库的情况
        wealth_level = self._determine_wealth_level(
            total_wealth_count, wealth_in_month, wealth_tougan, wealth_dedi,
            wealth_has_source, wealth_has_protection, strong, strength_score, 
            month_pattern, pillars, ten_god_count, caiku_info
        )
        
        # 12. 财运评估描述
        wealth_description = self._generate_wealth_description(
            total_wealth_count, zhengcai_count, piancai_count, wealth_in_month,
            wealth_tougan, wealth_dedi, wealth_has_source, wealth_has_protection,
            strong, wealth_strength_match
        )
        
        # 13. 求财方式建议
        wealth_method = self._suggest_wealth_method(
            zhengcai_count, piancai_count, wealth_has_source, strong
        )
        
        # 14. 适合行业
        suitable_industries = self._suggest_industries(
            zhengcai_count, piancai_count, wealth_has_source, wealth_has_protection
        )
        
        # 🔥 新增：深度解释机制（矛盾解释、格局机制详解）
        deep_explanation = self._generate_wealth_deep_explanation(
            total_wealth_count, wealth_level, month_pattern, wealth_has_source,
            strong, ten_god_count, pillars, day_master
        )
        
        # 🔥 新增：人生策略建议（财富密码、心性修炼）
        yin_count = ten_god_count.get('正印', 0) + ten_god_count.get('偏印', 0)
        life_strategy = self._generate_wealth_life_strategy(
            wealth_level, month_pattern, wealth_has_source, strong, 
            zhengcai_count, piancai_count, total_wealth_count, yin_count
        )
        
        return {
            'wealth_stars': wealth_stars,
            'wealth_positions': wealth_positions,
            'wealth_in_month': wealth_in_month,
            'month_zhi_has_wealth': month_zhi_has_wealth,
            'wealth_tougan': wealth_tougan,
            'wealth_dedi': wealth_dedi,
            'wealth_has_source': wealth_has_source,
            'wealth_has_protection': wealth_has_protection,
            'total_wealth_count': total_wealth_count,
            'zhengcai_count': zhengcai_count,
            'piancai_count': piancai_count,
            'zhengcai_ratio': zhengcai_ratio,
            'piancai_ratio': piancai_ratio,
            'mingcai': mingcai,
            'ancai': ancai,
            'wealth_strength_match': wealth_strength_match,
            'wealth_level': wealth_level,
            'wealth_description': wealth_description,
            'wealth_method': wealth_method,
            'suitable_industries': suitable_industries,
            'caiku_info': caiku_info,  # 财库信息
            'deep_explanation': deep_explanation,  # 🔥 新增：深度解释
            'life_strategy': life_strategy  # 🔥 新增：人生策略
        }
    
    def _determine_wealth_level(self, total_wealth: float, in_month: bool, tougan: bool,
                                dedi: bool, has_source: bool, has_protection: bool,
                                strong: bool, strength_score: float, month_pattern: str = None,
                                pillars: Dict = None, ten_god_count: Dict[str, float] = None,
                                caiku_info: Dict = None) -> str:
        """
        判断财运等级 - 基于《渊海子平》理论
        ✅ 修复：添加阈值判断，避免财星数量接近0时判断为"贫困"
        ✅ 修复：考虑格局影响，但需综合考虑身强身弱、印星有力、财星坏印等因素
        ✅ 修复：优先判断日坐财库的情况，根据组合提升财运等级
        """
        # ✅ 修复：优先判断日坐财库的情况（基于《渊海子平·论财库》理论）
        if caiku_info and caiku_info.get('zuo_caiku', False):
            # 日坐财库是非常利财的特殊组合，传统命理："日坐财库，无人不富"
            # 根据组合情况判断财运等级
            # ✅ 修复：如果有食伤生财（has_source），即使无明财也应该至少是"大富"
            # 参考伤官配印格的逻辑：间接生财能力强，主大富
            # ✅ 增强：如果同时有伤官配印格，进一步提升财运等级
            if total_wealth >= 0.5 and has_source:
                # 日坐财库 + 有财星 + 食伤生财 = 巨富
                if month_pattern and '伤官配印' in month_pattern:
                    # 日坐财库 + 伤官配印格 + 有财星 + 食伤生财 = 极富
                    return '巨富'  # 双重利好，主巨富
                return '巨富'
            elif total_wealth >= 0.5:
                # 日坐财库 + 有财星 = 大富
                if month_pattern and '伤官配印' in month_pattern:
                    # 日坐财库 + 伤官配印格 + 有财星 = 巨富
                    return '巨富'  # 双重利好，主巨富
                return '大富'
            elif has_source:
                # ✅ 修复：日坐财库 + 食伤生财（无明财）的情况
                # 理论依据：《渊海子平·论财库》："日坐财库，无人不富"
                # 但是，如果财星0个，说"大富"太夸张，应该说"中等偏上"或"小富"更合理
                # 关键：日坐财库是"潜在财源"，需要大运引动财星才能真正发财
                if month_pattern and '伤官配印' in month_pattern:
                    # 日坐财库 + 伤官配印格 + 食伤生财（无明财）= 双重利好，间接生财能力强
                    # 但无明财，只能是"中等偏上"
                    return '中等偏上（日坐财库+伤官配印，潜在财源，需大运引动财星）'  # ✅ 修复
                return '中等偏上（日坐财库，潜在财源，需大运引动财星）'  # ✅ 修复：日坐财库+食伤生财，但无明财，只能中等偏上
            else:
                # 日坐财库（无明财无源）= 中等（开库后可提升）
                return '中等'  # 开库后可提升至小富或中等
        # ✅ 修复：伤官配印格的财运判断（基于经典理论和实际分析）
        # 理论依据：
        # 1. 《子平真诠》：伤官配印，贵不可言（主"贵"而非直接"富"）
        # 2. 伤官配印格的特点：间接生财，名望带财，富大于贵，稳中求富
        # 3. 关键要素：身强身弱、印星有力、财星是否坏印、力量平衡
        if month_pattern and '伤官配印' in month_pattern:
            # 检查财星是否坏印（破格的最大风险）
            if ten_god_count and pillars:
                # 计算印星和财星的数量
                yin_count = ten_god_count.get('正印', 0) + ten_god_count.get('偏印', 0)
                cai_count = ten_god_count.get('正财', 0) + ten_god_count.get('偏财', 0)
                shangguan_count = ten_god_count.get('伤官', 0)
                
                # 检查印星是否有力（有根有气）- 简化判断：印星数量>=1.0认为有力
                yin_youli = yin_count >= 1.0
                
                # 检查财星是否坏印（财星过旺会破格）
                # 根据理论：财星克制印星，如果财星过旺而印星较弱，会破格
                caixing_huaiyin = False
                if cai_count > 0 and yin_count > 0:
                    # 如果财星数量超过印星数量，且财星>=1.0，可能坏印
                    if cai_count >= 1.0 and cai_count >= yin_count * 1.5:
                        caixing_huaiyin = True
                
                # 检查伤官与印星力量平衡
                # 简化判断：印星不能过度克制伤官（印星数量不能是伤官的3倍以上）
                pingheng = True
                if shangguan_count > 0:
                    if yin_count >= shangguan_count * 3:
                        pingheng = False  # 印星过重，伤官被埋
                
                # 综合判断财运等级
                if caixing_huaiyin:
                    # 财星坏印，格局被破坏，财运受影响
                    if total_wealth < 0.5:
                        return '中等'  # 无明财，财星坏印，只能中等
                    else:
                        return '小富'  # 有财但坏印，只能小富
                elif not yin_youli:
                    # 印星无力，格局不真，财运一般
                    if total_wealth < 0.5:
                        return '中等'  # 无明财，印星无力，只能中等
                    else:
                        return '中等'  # 有财但印星无力，只能中等
                elif not pingheng:
                    # 力量不平衡，格局受影响
                    if total_wealth < 0.5:
                        return '中等'  # 无明财，力量不平衡，只能中等
                    else:
                        return '中等'  # 有财但力量不平衡，只能中等
                else:
                    # 格局清纯，符合伤官配印的条件
                    # 根据理论："间接生财，名望带财，富大于贵，稳中求富"
                    # ✅ 修复：伤官配印格"富大于贵"，格局清纯时应该给予更高的财运等级
                    # 关键因素：是否有食伤生财（has_source）是判断财运等级的重要依据
                    if has_source:
                        # 有食伤生财：伤官配印格 + 食伤生财 = 间接生财能力强，主大富或巨富
                        if total_wealth >= 0.5:
                            # 有财星且有食伤生财：财源充足，主巨富
                            return '巨富'  # 伤官配印格+食伤生财+有财星，间接生财能力强，主巨富
                        else:
                            # ✅ 修复：无明财但有食伤生财，需要更谨慎判断
                            # 理论依据：《子平真诠》："伤官佩印者，印能制伤，所以为贵"（主贵而非直接富）
                            # 无明财（财星0个）意味着没有直接财源，只能通过间接方式生财
                            # 即使有食伤，也需要财星来承接，否则只能是"潜在财源"
                            if not strong:  # 身弱更符合伤官配印的偏好
                                return '中等偏上（潜在财源，需大运引动财星）'  # ✅ 修复：无明财，只能中等偏上
                            else:
                                return '中等（潜在财源，需大运引动财星）'  # ✅ 修复：身强且无明财，只能中等
                    else:
                        # 无食伤生财：主要通过名望地位间接生财，稳中求富
                        if total_wealth < 0.5:
                            # 无明财也无食伤生财：通过名望间接生财，稳中求富
                            if not strong:  # 身弱更符合伤官配印的偏好
                                return '中等'  # 身弱，间接生财，稳中求富
                            else:
                                return '中等'  # 身强，格局不如身弱好，中等
                        else:
                            # 有财星但无食伤生财：有财但间接生财能力弱
                            if not strong:
                                return '中等'  # 身弱，有财但间接生财能力弱，中等
                            else:
                                return '小富'  # 身强，有财但间接生财能力弱，小富
            else:
                # 如果没有必要的参数（ten_god_count 或 pillars 为 None），使用简化判断
                # ✅ 修复：即使没有详细参数，也要考虑是否有食伤生财
                if has_source:
                    # 有食伤生财：间接生财能力强
                    if total_wealth >= 0.5:
                        return '大富'  # 有财且有食伤生财，主大富
                    else:
                        return '大富'  # 无明财但有食伤生财，间接生财能力强，主大富
                else:
                    # 无食伤生财：主要通过名望地位间接生财，稳中求富
                    if total_wealth < 0.5:
                        return '中等'  # 无明财，间接生财，稳中求富
                    else:
                        return '中等'  # 有财但无食伤生财，中等
        
        # ✅ 修复：其他特殊格局的判断
        if month_pattern:
            if '食神制杀' in month_pattern:
                # 食神制杀格：权贵显达，通过权力地位得财
                if total_wealth < 0.5:
                    return '大富'  # ✅ 无明财但格局贵，主大富（《渊海子平》：食神制杀，英雄独压万人）
                else:
                    return '巨富'  # 有财且格局贵，主巨富
            elif '财官双美' in month_pattern or '财官相生' in month_pattern:
                # 财官双美格：富贵双全（《渊海子平》：财官相生，主富贵）
                # ✅ 修复：财官双美格"富贵双全"，即使无明财也应该给予较高等级
                if total_wealth < 0.5:
                    # 无明财但格局好，通过官星地位得财，主大富
                    if has_source:
                        return '大富'  # 有食伤生财，财源充足
                    else:
                        return '大富'  # 财官双美格主富贵双全，即使无明财也主大富
                else:
                    return '巨富'  # 有财且格局好，富贵双全，主巨富
            elif '官印相生' in month_pattern:
                # 官印相生格：主贵，通过官职得财（《渊海子平》：官印相生，主贵）
                # ✅ 修复：官印相生格"主贵"，通过官职得财，即使无明财也应该给予较高等级
                if total_wealth < 0.5:
                    # 无明财但格局好，通过官职地位得财，主大富
                    if has_source:
                        return '大富'  # 有食伤生财，财源充足
                    else:
                        return '大富'  # 官印相生格主贵，通过官职得财，主大富
                else:
                    return '巨富'  # 有财且格局好，主巨富
            elif '伤官生财' in month_pattern:
                # 伤官生财格：伤官转生财星，凶化为吉，主富（《渊海子平》将伤官生财列为外十八格之一）
                # ✅ 新增：伤官生财格的财运判断
                if total_wealth < 0.5:
                    # 无明财但有伤官，通过技艺才华生财
                    return '大富'  # 伤官生财格，主富，间接生财能力强
                else:
                    return '巨富'  # 有财且伤官生财，财源充足，主巨富
            elif '印化杀' in month_pattern:
                # 印化杀格：印绶化解七杀，化杀为权，贵不可言（《子平真诠》：印化杀，主贵）
                # ✅ 新增：印化杀格的财运判断
                if total_wealth < 0.5:
                    # 无明财但格局贵，通过权力地位得财
                    if has_source:
                        return '大富'  # 有食伤生财，财源充足
                    else:
                        return '大富'  # 印化杀格主贵，通过权力得财，主大富
                else:
                    return '巨富'  # 有财且格局贵，主巨富
        
        # ✅ 修复：考虑藏干权重，如果财星数量小于0.5，视为无财
        if total_wealth < 0.5:
            return '无财'
        
        # ✅ 修复：基于《渊海子平·论正财》"得时为上，得位次之"理论判断，不再使用简单score累加
        # 理论依据：
        # - 《渊海子平·论正财》："财要得时，不要财多。若财多则自家日本有力，可以胜任"
        # - 《渊海子平》："财要得时乘旺，自家日主有力，皆能发福"
        # - "得时为上"：财星当令（在月令）最重要
        # - "得位次之"：财星透干、得地次之
        
        # 1. 财星得时得地（当令+透干+得地）：最上等
        if in_month and tougan and dedi:
            # 财星得时得地，且身强能胜任
            if strong and total_wealth >= 2:
                return '巨富'  # 财星得时得地，身强财多，主巨富（《渊海子平》："财要得时乘旺，自家日主有力，皆能发福"）
            elif strong:
                return '大富'  # 财星得时得地，身强，主大富
            elif total_wealth >= 2:
                # 财多但身弱，需检查是否有护财
                if has_protection:
                    return '大富'  # 财星得时得地，有官护财，主大富（《三命通会》："凡财格，喜见官星显露，别无伤损"）
                else:
                    return '中等'  # 财多身弱，力不任财，只能中等（《渊海子平》："力不任财，祸患百出"）
            else:
                return '中等'  # 财星得时得地，但财不多，主中等
        
        # 2. 财星得时且透干：上等
        elif in_month and tougan:
            # 财星得时且透干，但可能不得地
            if strong and total_wealth >= 2:
                return '大富'  # 财星得时且透干，身强财多，主大富
            elif strong:
                return '中等'  # 财星得时且透干，身强但财不多，主中等
            elif total_wealth >= 2:
                # 财多但身弱，力不任财
                if has_protection:
                    return '中等'  # 有官护财，勉强可用，主中等
                else:
                    return '小富'  # 财多身弱，力不任财，主小富（《渊海子平》："力不任财，祸患百出"）
            else:
                return '中等'  # 财星得时且透干，但财不多，主中等
        
        # 3. 财星得时且得地：上等
        elif in_month and dedi:
            # 财星得时且得地，但可能不透干
            if strong and total_wealth >= 2:
                return '大富'  # 财星得时且得地，身强财多，主大富
            elif strong:
                return '中等'  # 财星得时且得地，身强但财不多，主中等
            else:
                return '中等'  # 财星得时且得地，但身弱或财不多，主中等
        
        # 4. 财星得时（当令）：基础条件
        elif in_month:
            # 财星得时，但可能不透干、不得地
            if strong and total_wealth >= 2:
                return '中等'  # 财星得时，身强财多，主中等
            elif strong:
                return '中等'  # 财星得时，身强，主中等
            else:
                return '小富'  # 财星得时，但身弱或财不多，主小富
        
        # 5. 财星透干且得地（但不得时）：中等
        elif tougan and dedi:
            # 财星透干且得地，但不得时
            if strong and total_wealth >= 2:
                return '中等'  # 财星透干且得地，身强财多，主中等
            elif strong:
                return '小富'  # 财星透干且得地，身强，主小富
            else:
                return '小富'  # 财星透干且得地，但身弱或财不多，主小富
        
        # 6. 财星透干（但不得时、不得地）：中等偏下
        elif tougan:
            # 财星透干，但不得时、不得地
            if strong and total_wealth >= 2:
                return '小富'  # 财星透干，身强财多，主小富
            else:
                return '小富'  # 财星透干，但其他条件不足，主小富
        
        # 7. 财星得地（但不得时、不透干）：中等偏下
        elif dedi:
            # 财星得地，但不得时、不透干
            if strong and total_wealth >= 2:
                return '小富'  # 财星得地，身强财多，主小富
            else:
                return '小富'  # 财星得地，但其他条件不足，主小富
        
        # 8. 其他情况（财星不得时、不透干、不得地）：根据身强身弱和财的数量判断
        else:
            # 财星不得时、不透干、不得地，基础条件较差
            if strong and total_wealth >= 2:
                return '小富'  # 身强财多，但财星不得时，主小富
            elif strong:
                return '贫困'  # 身强但财少且不得时，主贫困
            elif total_wealth >= 2:
                # 财多但身弱，且财星不得时，力不任财
                return '贫困'  # 财多身弱，且财星不得时，力不任财，主贫困（《渊海子平》："力不任财，祸患百出"）
            else:
                return '贫困'  # 财星不得时、不透干、不得地，且财不多，主贫困
    
    def _generate_wealth_description(self, total_wealth: float, zhengcai: float, piancai: float,
                                     in_month: bool, tougan: bool, dedi: bool,
                                     has_source: bool, has_protection: bool,
                                     strong: bool, strength_match: bool) -> str:
        """
        生成财运描述 - 基于《渊海子平》原文
        ✅ 修复：添加阈值判断，避免财星数量接近0时产生矛盾描述
        """
        descriptions = []
        
        # ✅ 修复：考虑藏干权重，如果财星数量小于0.5（天干财星权重为1.0），视为无财
        # 这样可以避免"财星数量：0个"但描述说"财星得地"的矛盾
        if total_wealth < 0.5:
            if has_source:
                return "命局无明财，视为「财星不显」。但如有食伤，代表才华与技艺，财富多通过专业技能、智慧谋略（食伤）获得，属于间接生财模式。"
            else:
                return "命局无明财，视为「财星不显」。需通过大运流年引动财星方能得财。"
        
        # ✅ 修复：只有财星数量足够时才添加"财星得地"等描述
        if in_month:
            descriptions.append("财星当令（月令为财）")
        if tougan:
            descriptions.append("财星透干")
        if dedi and total_wealth >= 0.5:  # ✅ 修复：确保财星数量足够才说"得地"
            descriptions.append("财星得地（有根）")
        if has_source:
            descriptions.append("食伤生财（有源）")
        if has_protection:
            descriptions.append("官杀护财")
        
        # ✅ 修复：只有财星数量足够时才判断正财/偏财为主
        if total_wealth >= 0.5:
            if zhengcai > piancai:
                descriptions.append("正财为主，主稳定收入")
            elif piancai > zhengcai:
                descriptions.append("偏财为主，主横财机遇")
        
        if strong and total_wealth >= 2:
            descriptions.append("身强财旺，可以胜任，宜大富")
        elif not strong and total_wealth > 1:
            descriptions.append("身弱财多，力不任财，需先扶身")
        elif not strong and total_wealth <= 1:
            descriptions.append("身弱财少，勉强可用")
        
        if not descriptions:
            return "财星平常，需后天努力。"
        
        return "；".join(descriptions) + "。"
    
    def _suggest_wealth_method(self, zhengcai: float, piancai: float, 
                               has_source: bool, strong: bool) -> List[str]:
        """
        建议求财方式 - 基于《渊海子平》理论
        """
        methods = []
        
        if zhengcai > piancai:
            methods.append("稳健求财（正财为主，宜勤俭持家）")
        elif piancai > zhengcai:
            methods.append("投资理财（偏财为主，宜把握机遇）")
        
        if has_source:
            methods.append("技能生财（食伤生财，靠才华技艺）")
        
        if strong:
            methods.append("可求大财（身强能胜任）")
        else:
            methods.append("宜守成（身弱不宜贪财）")
        
        return methods if methods else ["需待大运流年逢财时，方能引动财源"]
    
    def _suggest_industries(self, zhengcai: float, piancai: float,
                           has_source: bool, has_protection: bool) -> List[str]:
        """
        建议适合行业
        """
        industries = []
        
        if zhengcai > 0:
            industries.append("稳定收入行业（金融、房地产、传统制造业）")
        
        if piancai > 0:
            industries.append("投资理财行业（证券、期货、创业投资）")
        
        if has_source:
            industries.append("技能服务行业（咨询、设计、技术开发）")
        
        if has_protection:
            industries.append("有护的行业（与政府、大企业合作）")
        
        return industries if industries else ["需根据格局和大运具体分析"]
    
    def _generate_wealth_deep_explanation(self, total_wealth: float, wealth_level: str,
                                         month_pattern: str, has_source: bool, strong: bool,
                                         ten_god_count: Dict[str, float], pillars: Dict,
                                         day_master: str) -> str:
        """
        生成财富深度解释 - 包括矛盾解释、格局机制详解
        
        理论依据：
        - 《渊海子平·论财》：解释财星不显但大富的矛盾
        - 《子平真诠·论格局》：解释格局如何间接生财
        """
        explanations = []
        
        # 1. 矛盾解释：财星不显但大富
        if total_wealth < 0.5 and wealth_level in ['大富', '巨富']:
            if month_pattern and '伤官配印' in month_pattern:
                explanations.append(
                    "表面矛盾：财星不显（八字原局中代表财富的元素极弱）与财运评估" +
                    f"（{wealth_level}）看似矛盾。" +
                    "内在统一性：此为「因技艺、智慧而致富」的典型标志。您命格为伤官配印，" +
                    "伤官代表才华、技艺、口才；印星代表学识、思考、声誉。财富并非来自投机或继承，" +
                    "而是通过将独特的思维（伤官）与系统化的知识（印星）相结合，创造出巨大的价值。" +
                    "此为「以技生财」、「以名得利」。格局机制：伤官配印格的核心在于印星制约伤官的狂傲不羁，" +
                    "使其才华能用于正途并得以升华；而伤官的灵动又缓解了印星过旺带来的沉闷。" +
                    "《子平真诠》云：「伤官佩印者，印能制伤，所以为贵。」但需注意，此格局「富大于贵」，"
                )
                if has_source:
                    explanations[-1] += "且有食伤生财，间接生财能力强，故能达至" + wealth_level + "。"
                else:
                    explanations[-1] += "主要通过名望地位间接生财，稳中求富。"
            elif month_pattern and '食神制杀' in month_pattern:
                explanations.append(
                    "表面矛盾：财星不显但财运评估为" + wealth_level + "。" +
                    "内在统一性：食神制杀格以权贵显达，通过权力地位得财。" +
                    "格局机制：食神制约七杀，以暴制暴，化凶为吉。" +
                    "《渊海子平》云：「食神制杀，英雄独压万人。」此格局间接生财，权威带财，"
                )
                explanations[-1] += "故能达至" + wealth_level + "。"
            elif has_source:
                explanations.append(
                    "表面矛盾：财星不显但财运评估为" + wealth_level + "。" +
                    "内在统一性：命局无明财，但食伤代表才华与技艺，财富通过专业技能、智慧谋略获得，" +
                    "属于间接生财模式。《渊海子平·论食伤生财》云：「食伤生财，财源广进。」" +
                    "此为「因技艺、智慧而致富」的典型标志。"
                )
        
        # 2. 格局机制详解
        if month_pattern:
            if '伤官配印' in month_pattern:
                yin_count = ten_god_count.get('正印', 0) + ten_god_count.get('偏印', 0)
                shangguan_count = ten_god_count.get('伤官', 0)
                
                if yin_count > 0 and shangguan_count > 0:
                    explanations.append(
                        "格局机制详解：伤官配印格的核心在于印星（数量" + f"{yin_count:.1f}" + "）" +
                        "与伤官（数量" + f"{shangguan_count:.1f}" + "）的力量平衡。" +
                        "印星制约伤官的狂傲不羁，使其才华能用于正途；而伤官的灵动又缓解了印星过旺带来的沉闷。" +
                        "关键在于：印星不能过度克制伤官（制伤过度），伤官不能反克印星（破印）。" +
                        "当格局清纯时，间接生财能力强，富大于贵。"
                    )
            elif '食神制杀' in month_pattern:
                shishen_count = ten_god_count.get('食神', 0)
                qisha_count = ten_god_count.get('偏官', 0)
                
                if shishen_count > 0 and qisha_count > 0:
                    explanations.append(
                        "格局机制详解：食神制杀格的核心在于食神（数量" + f"{shishen_count:.1f}" + "）" +
                        "制约七杀（数量" + f"{qisha_count:.1f}" + "），以暴制暴，化凶为吉。" +
                        "关键在于：食神必须有力才能制杀，否则反被七杀所制。" +
                        "此格局间接生财，通过权威地位得财，英雄独压万人。"
                    )
            elif '官印相生' in month_pattern:
                explanations.append(
                    "格局机制详解：官印相生格的核心在于官生印、印生身，五行流通。" +
                    "官星代表贵气、地位，印星代表学识、后盾。二者相生，贵气带财，" +
                    "间接生财能力强。关键在于：官印必须力量相当，不能一方过强或过弱。"
                )
            elif '伤官生财' in month_pattern:
                explanations.append(
                    "格局机制详解：伤官生财格的核心在于伤官转生财星，凶化为吉。" +
                    "伤官代表才华、技艺，财星代表财富。伤官生财，直接生财，" +
                    "技艺生财，财富来源明确。关键在于：伤官必须有力且不被印星过度克制。"
                )
            elif '正官格' in month_pattern or '七杀格' in month_pattern:
                guan_count = ten_god_count.get('正官', 0) + ten_god_count.get('偏官', 0)
                if guan_count > 0:
                    guan_type = '正官格' if ten_god_count.get('正官', 0) > 0 else '七杀格'
                    explanations.append(
                        f"格局机制详解：{guan_type}的核心在于官星（数量{guan_count:.1f}）的作用。" +
                        ("正官代表贵气、地位，主文贵；" if '正官' in guan_type else "七杀代表压力、挑战，需有制化；") +
                        "关键在于：身强可任官职，身弱需先扶身。" +
                        "《渊海子平》云：「正官乃贵气之物，大忌刑冲破害。大抵要行官旺乡，月令是也。」"
                    )
            elif '正财格' in month_pattern or '偏财格' in month_pattern:
                cai_count = ten_god_count.get('正财', 0) + ten_god_count.get('偏财', 0)
                if cai_count > 0:
                    cai_type = '正财格' if ten_god_count.get('正财', 0) > ten_god_count.get('偏财', 0) else '偏财格'
                    explanations.append(
                        f"格局机制详解：{cai_type}的核心在于财星（数量{cai_count:.1f}）的作用。" +
                        ("正财代表稳定收入，主勤俭持家；" if '正财' in cai_type else "偏财代表横财机遇，主投资理财；") +
                        "关键在于：身强财旺可大富，身弱财多需先扶身。" +
                        "《渊海子平》云：「财要得时，不要财多。若财多则自家日本有力，可以胜任。」"
                    )
            elif '正印格' in month_pattern or '偏印格' in month_pattern:
                yin_count = ten_god_count.get('正印', 0) + ten_god_count.get('偏印', 0)
                if yin_count > 0:
                    yin_type = '正印格' if ten_god_count.get('正印', 0) > ten_god_count.get('偏印', 0) else '偏印格'
                    explanations.append(
                        f"格局机制详解：{yin_type}的核心在于印星（数量{yin_count:.1f}）的作用。" +
                        ("正印代表学识、后盾，主文贵、稳定；" if '正印' in yin_type else "偏印代表独特学识，主偏门技艺；") +
                        "关键在于：身弱喜印扶身，身强忌印过重。" +
                        "《渊海子平》云：「印绶者，生我之神也。印多身旺，喜财星破印。」"
                    )
            elif '食神格' in month_pattern:
                shishen_count = ten_god_count.get('食神', 0)
                if shishen_count > 0:
                    explanations.append(
                        f"格局机制详解：食神格的核心在于食神（数量{shishen_count:.1f}）的作用。" +
                        "食神代表才华、技艺、温和，主才艺谋生。" +
                        "关键在于：身强可用食神泄秀，身弱忌食神过重。" +
                        "《渊海子平》云：「食神者，我生之神也。食神制杀，英雄独压万人。」"
                    )
            elif '建禄格' in month_pattern or '羊刃格' in month_pattern:
                bijie_count = ten_god_count.get('比肩', 0) + ten_god_count.get('劫财', 0)
                if bijie_count > 0:
                    ge_type = '建禄格' if '建禄' in month_pattern else '羊刃格'
                    explanations.append(
                        f"格局机制详解：{ge_type}的核心在于比劫（数量{bijie_count:.1f}）的作用。" +
                        ("建禄代表日主临官禄位，主自立创业；" if '建禄' in ge_type else "羊刃代表日主极旺，主刚强果断；") +
                        "关键在于：身弱喜比劫扶身，身强需财官泄耗。" +
                        "《渊海子平》云：「建禄格，身旺喜财官；羊刃格，需官杀制刃。」"
                    )
        
        # 3. 身强身弱与财运关系详解
        if total_wealth > 0:
            if strong and total_wealth >= 2:
                explanations.append(
                    "身强财旺：身强（日主有力）且财多（财星数量" + f"{total_wealth:.1f}" + "），" +
                    "可以胜任，宜大富。《渊海子平》云：「财要得时，不要财多。若财多则自家日本有力，可以胜任。」"
                )
            elif not strong and total_wealth > 1:
                explanations.append(
                    "身弱财多：身弱（日主无力）但财多（财星数量" + f"{total_wealth:.1f}" + "），" +
                    "力不任财，需先扶身。《渊海子平》云：「力不任财，祸患百出。」" +
                    "需通过大运流年扶身（印绶、比劫）后才能胜任财星。"
                )
            elif not strong and total_wealth <= 1:
                explanations.append(
                    "身弱财少：身弱且财少（财星数量" + f"{total_wealth:.1f}" + "），勉强可用，" +
                    "但需大运流年扶身才能提升财运。"
                )
        
        if not explanations:
            return "财运分析较为常规，无明显矛盾或特殊格局机制需要深度解读。"
        
        return "。".join(explanations) + "。"
    
    def _generate_wealth_life_strategy(self, wealth_level: str, month_pattern: str,
                                      has_source: bool, strong: bool,
                                      zhengcai: float, piancai: float, total_wealth: float,
                                      yin_count: float = 0) -> Dict[str, str]:
        """
        生成财富人生策略建议 - 包括财富密码、心性修炼等
        
        理论依据：
        - 《渊海子平·论求财》：不同格局的求财方式
        - 《子平真诠·论格局》：格局对人生策略的影响
        """
        strategy = {
            'wealth_password': '',  # 财富密码
            'career_direction': '',  # 事业方向
            'mindset_cultivation': '',  # 心性修炼
            'key_points': []  # 关键要点
        }
        
        # 1. 财富密码（基于格局和财运等级）
        if month_pattern and '伤官配印' in month_pattern:
            strategy['wealth_password'] = (
                "您的财富源于「才华」与「知识」的深度结合。" +
                "专注于将您的专业技能打磨到极致，成为所在领域的顶尖专家，财富会随之而来。" +
                "避免追逐短线投机，专注于长期价值创造。"
            )
        elif month_pattern and '食神制杀' in month_pattern:
            strategy['wealth_password'] = (
                "您的财富源于「权威」与「地位」。" +
                "通过建立专业权威、获得行业地位，财富会随之而来。" +
                "避免过度依赖个人能力，注重团队协作和权力结构。"
            )
        elif month_pattern and ('正官格' in month_pattern or '七杀格' in month_pattern):
            strategy['wealth_password'] = (
                "您的财富源于「贵气」与「地位」。" +
                "通过官职地位、权威影响力获得财富。" +
                "专注于建立稳定的职业路径，等待大运流年扶身。"
            )
        elif month_pattern and ('正财格' in month_pattern or '偏财格' in month_pattern):
            strategy['wealth_password'] = (
                "您的财富源于「财星」的直接作用。" +
                ("正财格：通过稳定的工作、稳健的投资获得财富，主勤俭持家；" if '正财' in month_pattern else "偏财格：通过把握机遇、投资理财获得财富，主横财机遇。") +
                "专注于建立稳定的收入来源或把握投资时机。"
            )
        elif month_pattern and ('正印格' in month_pattern or '偏印格' in month_pattern):
            strategy['wealth_password'] = (
                "您的财富源于「学识」与「声誉」。" +
                "通过知识积累、文化教育、学术研究获得财富。" +
                "专注于提升学识水平，建立专业声誉，财富会随之而来。"
            )
        elif month_pattern and '食神格' in month_pattern:
            strategy['wealth_password'] = (
                "您的财富源于「才华」与「技艺」。" +
                "通过才艺展示、技能服务获得财富。" +
                "专注于提升专业技能，建立个人品牌，财富会随之而来。"
            )
        elif has_source:
            strategy['wealth_password'] = (
                "您的财富源于「技能」与「智慧」。" +
                "通过专业技能、智慧谋略获得财富，属于间接生财模式。" +
                "专注于提升专业技能，建立个人品牌，财富会随之而来。"
            )
        elif zhengcai > piancai:
            strategy['wealth_password'] = (
                "您的财富源于「稳定收入」。" +
                "通过稳定的工作、稳健的投资获得财富。" +
                "专注于建立稳定的收入来源，避免高风险投资。"
            )
        elif piancai > zhengcai:
            strategy['wealth_password'] = (
                "您的财富源于「机遇」与「投资」。" +
                "通过把握机遇、投资理财获得财富。" +
                "专注于市场分析，把握投资时机，但需控制风险。"
            )
        else:
            strategy['wealth_password'] = (
                "您的财富需通过后天努力获得。" +
                "专注于提升自身能力，等待大运流年引动财星。"
            )
        
        # 2. 事业方向（基于格局）
        if month_pattern and '伤官配印' in month_pattern:
            strategy['career_direction'] = (
                "技术权威、资深专家、策划大师、文化教育工作者等角色非常适合您。" +
                "您不适合刻板的官僚体系，但在需要深度思考和创新的领域，能成为「无冕之王」。"
            )
        elif month_pattern and '食神制杀' in month_pattern:
            strategy['career_direction'] = (
                "军警、管理、企业高管、权威专家等角色非常适合您。" +
                "通过权威地位和团队管理获得成功。"
            )
        elif month_pattern and ('正官格' in month_pattern or '七杀格' in month_pattern):
            strategy['career_direction'] = (
                "公职、事业单位、企业管理等角色非常适合您。" +
                "通过稳定的职业路径和权威地位获得成功。"
            )
        elif month_pattern and ('正财格' in month_pattern or '偏财格' in month_pattern):
            strategy['career_direction'] = (
                "金融、投资、企业管理等角色非常适合您。" +
                ("正财格：适合稳定收入的行业；" if '正财' in month_pattern else "偏财格：适合投资理财的行业。") +
                "通过财星作用获得成功。"
            )
        elif month_pattern and ('正印格' in month_pattern or '偏印格' in month_pattern):
            strategy['career_direction'] = (
                "文化教育、学术研究、出版传媒等角色非常适合您。" +
                "通过学识积累和声誉建立获得成功。"
            )
        elif month_pattern and '食神格' in month_pattern:
            strategy['career_direction'] = (
                "技能服务、咨询、设计、技术开发等角色非常适合您。" +
                "通过才艺展示和技能服务获得成功。"
            )
        elif has_source:
            strategy['career_direction'] = (
                "技能服务、咨询、设计、技术开发等角色非常适合您。" +
                "通过专业技能和智慧谋略获得成功。"
            )
        else:
            strategy['career_direction'] = (
                "需根据大运流年具体分析。" +
                "建议在稳定行业中发展，等待大运引动财星。"
            )
        
        # 3. 心性修炼（基于格局和身强身弱）
        if month_pattern and '伤官配印' in month_pattern:
            if yin_count >= 3:  # 印星过旺，可能土重埋金
                strategy['mindset_cultivation'] = (
                    "「土重埋金」的格局容易带来固执和压抑感。" +
                    "需有意识地保持开放心态，主动社交，融入能激发您活力的圈子，" +
                    "避免因清高而自我封闭。"
                )
            else:
                strategy['mindset_cultivation'] = (
                    "伤官配印格需要平衡才华与理性。" +
                    "避免过度张扬才华（伤官过旺），也避免过度保守（印星过旺）。" +
                    "保持开放心态，主动学习，融入能激发您活力的圈子。"
                )
        elif not strong:
            strategy['mindset_cultivation'] = (
                "身弱的格局容易带来不自信和依赖感。" +
                "需有意识地提升自身能力，培养独立自主的性格，" +
                "避免过度依赖他人，等待大运扶身后再发力。"
            )
        elif strong and total_wealth < 0.5:
            strategy['mindset_cultivation'] = (
                "身强但财少的格局容易带来急躁和不满。" +
                "需有意识地保持耐心，专注于提升自身能力，" +
                "等待大运流年引动财星，避免急于求成。"
            )
        else:
            strategy['mindset_cultivation'] = (
                "保持积极向上的心态，专注于提升自身能力，" +
                "根据大运流年的变化调整策略。"
            )
        
        # 4. 关键要点
        if wealth_level in ['大富', '巨富']:
            strategy['key_points'].append("财运等级较高，需善用机遇，避免过度贪婪")
        if has_source:
            strategy['key_points'].append("有食伤生财，需专注于专业技能提升")
        if not strong:
            strategy['key_points'].append("身弱需先扶身，等待大运流年扶身后再发力")
        if total_wealth < 0.5:
            strategy['key_points'].append("财星不显，需通过大运流年引动财星")
        
        return strategy
    
    def _analyze_career_comprehensive(self, day_master: str, pillars: Dict, month_branch: str,
                                      ten_god_count: Dict[str, float], strength: str, strength_score: float,
                                      month_pattern: str = None) -> Dict:
        """
        🔥 完整事业分析 - 基于《渊海子平·正官论》《论偏官》
        
        理论依据：
        - 《正官论》：正官乃贵气之物，大忌刑冲破害。大抵要行官旺乡，月令是也。
        - 《论偏官》：偏官即七杀，要制伏。制伏得位，运复经行制伏之乡，此大贵之命也。
        
        分析项目（12项）：
        1. 官星识别（正官、七杀、位置）
        2. 官星当令（月令为官）
        3. 官星透干
        4. 官星得地
        5. 官星有制化（食伤制杀、印化杀）
        6. 官印相生
        7. 财官相生
        8. 事业格局类型
        9. 事业方向建议
        10. 适合行业
        11. 事业发展时机
        12. 需要注意的年份
        """
        # 1. 官星识别
        official_stars = {'正官': [], '偏官': []}
        official_positions = {'year': [], 'month': [], 'day': [], 'hour': []}
        
        for pos, (gan, zhi) in pillars.items():
            tg = get_ten_god(day_master, gan)
            if tg == '正官':
                official_stars['正官'].append((pos, gan))
                official_positions[pos].append(('天干', gan, '正官'))
            elif tg == '偏官':
                official_stars['偏官'].append((pos, gan))
                official_positions[pos].append(('天干', gan, '偏官'))
            
            # 检查藏干中的官星
            for canggan, w in DIZHI_CANGGAN.get(zhi, []):
                tg_c = get_ten_god(day_master, canggan)
                if tg_c == '正官':
                    official_positions[pos].append(('藏干', canggan, '正官', w))
                elif tg_c == '偏官':
                    official_positions[pos].append(('藏干', canggan, '偏官', w))
        
        # 2. 官星当令
        month_gan = pillars['month'][0]
        month_tg = get_ten_god(day_master, month_gan)
        official_in_month = month_tg in ['正官', '偏官']
        
        # 3. 官星透干
        official_tougan = len(official_stars['正官']) + len(official_stars['偏官']) > 0
        
        # 4. 官星得地
        official_dedi = sum(len([x for x in official_positions[pos] if x[0] == '藏干']) 
                           for pos in ['year', 'month', 'day', 'hour']) > 0
        
        # 5. 官星有制化
        has_shishang = ten_god_count.get('食神', 0) + ten_god_count.get('伤官', 0) > 0
        has_yin = ten_god_count.get('正印', 0) + ten_god_count.get('偏印', 0) > 0
        official_has_control = has_shishang or has_yin
        
        # 6. 官印相生
        guanyin_xiangsheng = (ten_god_count.get('正官', 0) > 0 or ten_god_count.get('偏官', 0) > 0) and has_yin
        
        # 7. 财官相生
        caiguan_xiangsheng = (ten_god_count.get('正官', 0) > 0 or ten_god_count.get('偏官', 0) > 0) and \
                             (ten_god_count.get('正财', 0) > 0 or ten_god_count.get('偏财', 0) > 0)
        
        # 计算官星总数（提前计算，供后面使用）
        total_official = ten_god_count.get('正官', 0) + ten_god_count.get('偏官', 0)
        zhengguan_count = ten_god_count.get('正官', 0)
        qisha_count = ten_god_count.get('偏官', 0)
        
        # 8. 事业格局类型（详细分析）
        career_pattern_info = self._determine_career_pattern_detailed(
            official_in_month, month_tg, has_shishang, has_yin, caiguan_xiangsheng,
            official_tougan, official_dedi, official_has_control, total_official, strength
        )
        career_pattern = career_pattern_info.get('pattern', '普通格局')
        
        # 9. 命格贵贱判断（基于《子平真诠》《渊海子平》）
        # ✅ 修复：传入正确的参数（month_pattern和ten_god_count是关键）
        nobility_info = self._judge_nobility(
            month_pattern=month_pattern,
            ten_god_count=ten_god_count,
            pattern=career_pattern,
            in_month=official_in_month,
            tougan=official_tougan,
            dedi=official_dedi,
            has_control=official_has_control,
            guanyin=guanyin_xiangsheng,
            caiguan=caiguan_xiangsheng,
            strength=strength
        )
        
        # 10. 事业方向建议
        career_direction = self._suggest_career_direction(
            official_stars, has_shishang, has_yin, caiguan_xiangsheng, strength, month_pattern
        )
        
        # 11. 适合行业
        suitable_career_industries = self._suggest_career_industries(
            official_stars, has_shishang, has_yin, caiguan_xiangsheng, month_pattern
        )
        
        # 🔥 新增：深度解释机制（矛盾解释、格局机制详解）
        deep_explanation = self._generate_career_deep_explanation(
            total_official, career_pattern, nobility_info.get('level', '普通'),
            month_pattern, ten_god_count, pillars, day_master, strength
        )
        
        # 🔥 新增：人生策略建议（事业密码、心性修炼）
        strong = strength in ['身旺', '身强']
        life_strategy = self._generate_career_life_strategy(
            nobility_info.get('level', '普通'), month_pattern, has_shishang, has_yin,
            strong, total_official, career_pattern
        )
        
        return {
            'official_stars': official_stars,
            'official_positions': official_positions,
            'official_in_month': official_in_month,
            'official_tougan': official_tougan,
            'official_dedi': official_dedi,
            'official_has_control': official_has_control,
            'guanyin_xiangsheng': guanyin_xiangsheng,
            'caiguan_xiangsheng': caiguan_xiangsheng,
            'total_official': total_official,
            'zhengguan_count': zhengguan_count,
            'qisha_count': qisha_count,
            'career_pattern': career_pattern,
            'career_pattern_detail': career_pattern_info.get('detail', ''),
            'career_pattern_reason': career_pattern_info.get('reason', ''),
            'nobility_level': nobility_info.get('level', '普通'),
            'nobility_reason': nobility_info.get('reason', ''),
            'career_direction': career_direction,
            'suitable_career_industries': suitable_career_industries,
            'strength': strength,  # ✅ 新增：返回身强身弱状态
            'deep_explanation': deep_explanation,  # 🔥 新增：深度解释
            'life_strategy': life_strategy  # 🔥 新增：人生策略
        }
    
    def _determine_career_pattern_detailed(self, in_month: bool, month_tg: str, 
                                          has_shishang: bool, has_yin: bool, caiguan: bool,
                                          tougan: bool, dedi: bool, has_control: bool,
                                          total_official: float, strength: str) -> Dict:
        """判断事业格局类型（详细版，包含分析依据）"""
        strong = strength in ['身旺', '身强']
        
        if month_tg == '正官':
            if has_yin:
                pattern = '官印相生格'
                detail = '月令正官，有印化官，官印相生，贵不可言'
                reason = '官印相生，文贵之命'
            elif caiguan:
                pattern = '财官相生格'
                detail = '月令正官，有财生官，财官相生，富贵双全'
                reason = '财官相生，富贵可期'
            else:
                pattern = '正官格'
                detail = '月令正官，无破无伤，主贵'
                reason = '正官格成，贵气之物'
        elif month_tg == '偏官':
            if has_shishang:
                pattern = '食伤制杀格'
                detail = '月令七杀，有食伤制杀，制伏得位，大贵之命'
                reason = '七杀有制化为权，唾手登云发少年'
            elif has_yin:
                pattern = '印化杀格'
                detail = '月令七杀，有印化杀，化杀为权'
                reason = '印化七杀，贵不可言'
            else:
                pattern = '七杀格'
                detail = '月令七杀，需有制化'
                reason = '七杀无制，凶险异常'
        elif in_month:
            pattern = '官星当令'
            detail = '官星在月令，有官星当令'
            reason = '官星当令，主贵'
        else:
            # ✅ 增强：详细说明为什么是普通格局
            pattern = '普通格局'
            if total_official == 0:
                detail = '命局无官星，既无正官也无七杀'
                reason = '无官星，不以官贵论，为普通格局'
            elif not tougan and not dedi:
                detail = f'官星数量{total_official:.1f}个，但既不透干也不得地，力量微弱'
                reason = '官星不显不藏，力量不足，为普通格局'
            elif not in_month:
                detail = f'官星不在月令，虽{"透干" if tougan else ""}{"得地" if dedi else ""}，但不当令，力量有限'
                reason = '官星不当令，不以贵论，为普通格局'
            else:
                detail = '官星配置一般，无特殊组合'
                reason = '官星配置普通，无贵格特征'
        
        return {
            'pattern': pattern,
            'detail': detail,
            'reason': reason
        }
    
    def _judge_nobility(self, month_pattern: str = None, ten_god_count: Dict[str, float] = None,
                       pattern: str = None, in_month: bool = False, tougan: bool = False, dedi: bool = False,
                       has_control: bool = False, guanyin: bool = False, caiguan: bool = False, strength: str = '') -> Dict:
        """
        判断命格贵贱 - 基于《子平真诠》《渊海子平》《三命通会》
        ✅ 修复：不再通过"有官星就贵，无官星就普通"的简单规则判断
        ✅ 修复：基于格局特征和经典理论依据判断，识别高级格局
        """
        # ✅ 修复：优先检查上等贵格（基于month_pattern识别的高级格局）
        if month_pattern:
            # 1. 伤官配印格（上等贵格）- 《子平真诠》："伤官佩印者，印能制伤，所以为贵"
            if '伤官配印' in month_pattern:
                # 检查格局是否清纯（印星有力、财星不坏印）
                if ten_god_count:
                    yin_count = ten_god_count.get('正印', 0) + ten_god_count.get('偏印', 0)
                    cai_count = ten_god_count.get('正财', 0) + ten_god_count.get('偏财', 0)
                    shangguan_count = ten_god_count.get('伤官', 0)
                    
                    if yin_count >= 1.0 and shangguan_count > 0:
                        # 印星有力且有伤官，格局成立
                        if cai_count >= 1.0 and cai_count >= yin_count * 1.5:
                            # 财星坏印，格局被破坏
                            return {
                                'level': '中等贵格',
                                'reason': '伤官配印格，但财星坏印，格局层次降低（《子平真诠》：伤官佩印，不宜逢财）'
                            }
                        else:
                            return {
                                'level': '上等贵格',
                                'reason': '伤官配印格，印绶制伤，反凶为吉，主文贵、学识、权柄（《子平真诠》：伤官佩印者，印能制伤，所以为贵。《渊海子平》：伤官见印绶，贵不可言）'
                            }
            
            # 2. 食神制杀格（上等贵格）- 《渊海子平》：食神制杀，英雄独压万人
            if '食神制杀' in month_pattern:
                if ten_god_count:
                    shishen_count = ten_god_count.get('食神', 0)
                    qisha_count = ten_god_count.get('偏官', 0)
                    
                    if shishen_count > 0 and qisha_count > 0:
                        return {
                            'level': '上等贵格',
                            'reason': '食神制杀格，以食神制约七杀，以暴制暴，主武贵、权威、胆识（《渊海子平》：食神制杀，英雄独压万人）'
                        }
            
            # 3. 官印相生格（上等贵格）
            if '官印相生' in month_pattern or '官印相生' in (pattern or ''):
                return {
                    'level': '上等贵格',
                    'reason': '官印相生格，官生印，印生身，五行流通，主贵气、地位、威望（《渊海子平》：有官无印，即非真官；有印无官，反成其福）'
                }
            
            # 4. 伤官生财格（上等贵格）- 《渊海子平》将伤官生财列为外十八格之一
            if '伤官生财' in month_pattern:
                if ten_god_count:
                    shangguan_count = ten_god_count.get('伤官', 0)
                    cai_count = ten_god_count.get('正财', 0) + ten_god_count.get('偏财', 0)
                    
                    if shangguan_count > 0 and cai_count > 0:
                        return {
                            'level': '上等贵格',
                            'reason': '伤官生财格，伤官转生财星，凶化为吉，主富、技艺生财（《渊海子平》将伤官生财列为外十八格之一）'
                        }
            
            # 5. 印化杀格（上等贵格）
            if '印化杀' in month_pattern or '印化杀' in (pattern or ''):
                return {
                    'level': '上等贵格',
                    'reason': '印化杀格，印绶化解七杀，化杀为权，贵不可言（《子平真诠》：印化杀，主贵）'
                }
            
            # 6. 财官相生格（中等贵格）
            if '财官相生' in month_pattern or '财官相生' in (pattern or ''):
                return {
                    'level': '中等贵格',
                    'reason': '财官相生格，财生官，官生印，富贵双全（《渊海子平》：财官相生，主富贵）'
                }
        
        # ✅ 修复：基于经典理论判断中等贵格
        # 1. 正官格成（中等贵格）
        if '正官格' in (pattern or '') and in_month and tougan:
            return {
                'level': '中等贵格',
                'reason': '正官格成，月令正官且透干，主贵（《渊海子平》：正官乃贵气之物，大忌刑冲破害。大抵要行官旺乡，月令是也）'
            }
        
        # 2. 七杀格有制化（中等贵格）
        if '七杀格' in (pattern or '') and has_control:
            return {
                'level': '中等贵格',
                'reason': '七杀有制化，可为贵格（《渊海子平》：偏官即七杀，要制伏。制伏得位，运复经行制伏之乡，此大贵之命也）'
            }
        
        # 3. 禄神格（中等贵格）- 《渊海子平》：禄神为养命之源
        if ten_god_count and (ten_god_count.get('比肩', 0) >= 1.0 or ten_god_count.get('劫财', 0) >= 1.0):
            # 简化判断：如果比劫在月令且透干，可能是禄神格
            if in_month and (pattern or '').find('禄') >= 0:
                return {
                    'level': '中等贵格',
                    'reason': '禄神格，日主临官禄位，得月令之气，主福气、安稳之贵（《渊海子平》：禄神为养命之源，得之多主安稳富足）'
                }
        
        # ✅ 修复：即使无官星，也要检查是否有其他贵格特征
        # 如果没有识别到任何贵格，才判断为普通格局
        if month_pattern:
            # 还有其他特殊格局（如专旺格、从格等）
            if '专旺' in month_pattern or '从' in month_pattern:
                return {
                    'level': '中等贵格',
                    'reason': f'{month_pattern}，特殊格局，需结合大运具体分析（《穷通宝鉴》《兰台妙选》：专旺格、从格需具体分析）'
                }
        
        # 普通格局（无特殊贵格特征）
        return {
            'level': '普通格局',
            'reason': '无官星或官星不显，且无特殊贵格特征（如伤官配印、食神制杀等），不以贵论'
        }
    
    def _determine_career_pattern(self, in_month: bool, month_tg: str, 
                                  has_shishang: bool, has_yin: bool, caiguan: bool) -> str:
        """判断事业格局类型（简化版，保持向后兼容）"""
        if month_tg == '正官':
            if has_yin:
                return '官印相生格'
            elif caiguan:
                return '财官相生格'
            else:
                return '正官格'
        elif month_tg == '偏官':
            if has_shishang:
                return '食伤制杀格'
            elif has_yin:
                return '印化杀格'
            else:
                return '七杀格'
        elif in_month:
            return '官星当令'
        else:
            return '普通格局'
    
    def _suggest_career_direction(self, official_stars: Dict, has_shishang: bool,
                                 has_yin: bool, caiguan: bool, strength: str, month_pattern: str = None) -> List[str]:
        """建议事业方向"""
        directions = []
        strong = strength in ['身旺', '身强']
        
        # ✅ 新增：优先考虑特殊格局（即使无官星）
        if month_pattern:
            if '伤官配印' in month_pattern:
                # 伤官配印格：主文贵、学识、权柄
                directions.append("文化教育方向（伤官配印格，主文贵、学识、权柄）")
                directions.append("学术研究、出版传媒、教育培训")
                if strong:
                    directions.append("可任要职（身强能胜任，印绶制伤，反凶为吉）")
                else:
                    directions.append("宜辅助岗位（身弱需扶身，但格局清纯仍可任要职）")
                return directions
            elif '食神制杀' in month_pattern:
                # 食神制杀格：主武贵、权威、胆识
                directions.append("技术管理方向（食神制杀格，主武贵、权威、胆识）")
                directions.append("技术类管理、工程师、IT行业、军工")
                if strong:
                    directions.append("可任要职（身强能胜任，食神制杀，英雄独压万人）")
                else:
                    directions.append("宜辅助岗位（身弱需扶身，但制杀有力仍可任要职）")
                return directions
            elif '官印相生' in month_pattern:
                # 官印相生格：主贵气、地位、威望
                directions.append("公职方向（官印相生格，主贵气、地位、威望）")
                directions.append("政府机关、事业单位、国有企业")
                if strong:
                    directions.append("可任要职（身强能胜任，官印相生，五行流通）")
                else:
                    directions.append("宜辅助岗位（身弱需扶身，但格局成真仍可任要职）")
                return directions
            elif '伤官生财' in month_pattern:
                # 伤官生财格：主富、技艺生财
                directions.append("商业方向（伤官生财格，主富、技艺生财）")
                directions.append("技能服务、创意设计、技术开发、创业")
                if strong:
                    directions.append("可任要职（身强能胜任，伤官生财，凶化为吉）")
                else:
                    directions.append("宜辅助岗位（身弱需扶身，但技艺生财仍可任要职）")
                return directions
        
        # 原有逻辑（基于官星）
        if len(official_stars['正官']) > 0:
            directions.append("公职方向（正官主贵，适合政府、事业单位）")
        
        if len(official_stars['偏官']) > 0:
            if has_shishang:
                directions.append("技术管理（食伤制杀，适合技术类管理）")
            elif has_yin:
                directions.append("文职管理（印化杀，适合文化教育管理）")
            else:
                directions.append("武职或高风险行业（七杀无制，需谨慎）")
        
        if caiguan:
            directions.append("经商从政（财官相生，权力生财）")
        
        if strong:
            directions.append("可任要职（身强能胜任）")
        else:
            directions.append("宜辅助岗位（身弱需扶身）")
        
        return directions if directions else ["需根据格局和大运具体分析"]
    
    def _suggest_career_industries(self, official_stars: Dict, has_shishang: bool,
                                   has_yin: bool, caiguan: bool, month_pattern: str = None) -> List[str]:
        """建议适合行业"""
        industries = []
        
        # ✅ 新增：优先考虑特殊格局（即使无官星）
        if month_pattern:
            if '伤官配印' in month_pattern:
                # 伤官配印格：主文贵、学识、权柄
                industries.append("文化教育行业（学校、培训机构、文化传媒）")
                industries.append("学术研究机构（科研院所、高等院校）")
                industries.append("出版传媒行业（出版社、媒体、文化公司）")
                industries.append("教育培训行业（教育培训、在线教育）")
                industries.append("智库咨询行业（政策研究、管理咨询）")
                if has_shishang:
                    industries.append("技能培训行业（职业技能培训、认证机构）")
                return industries
            elif '食神制杀' in month_pattern:
                # 食神制杀格：主武贵、权威、胆识
                industries.append("技术类管理行业（技术总监、CTO、技术管理）")
                industries.append("工程师行业（软件工程师、硬件工程师、系统架构师）")
                industries.append("IT互联网行业（互联网、软件、通信）")
                industries.append("军工行业（国防、军工、航空航天）")
                industries.append("智能制造行业（自动化、机器人、智能制造）")
                return industries
            elif '官印相生' in month_pattern:
                # 官印相生格：主贵气、地位、威望
                industries.append("政府机关（公务员、政府机构）")
                industries.append("事业单位（事业单位、公共机构）")
                industries.append("国有企业（国有企业、央企）")
                industries.append("金融机构（银行、证券、保险）")
                return industries
            elif '伤官生财' in month_pattern:
                # 伤官生财格：主富、技艺生财
                industries.append("技能服务行业（咨询、设计、技术服务）")
                industries.append("创意设计行业（平面设计、产品设计、建筑设计）")
                industries.append("技术开发行业（软件开发、技术研发、科技创新）")
                industries.append("创业投资行业（创业、投资、风险投资）")
                industries.append("文化艺术行业（艺术创作、文化创意、娱乐）")
                return industries
        
        # 原有逻辑（基于官星）
        if len(official_stars['正官']) > 0:
            industries.append("政府机关、事业单位、国有企业")
        
        if len(official_stars['偏官']) > 0:
            if has_shishang:
                industries.append("技术类管理、工程师、IT行业")
            elif has_yin:
                industries.append("文化教育、研究机构、学术领域")
            else:
                industries.append("军警、法律、高风险行业")
        
        if caiguan:
            industries.append("金融、投资、企业管理")
        
        return industries if industries else ["需根据格局和大运具体分析"]
    
    def _generate_career_deep_explanation(self, total_official: float, career_pattern: str,
                                        nobility_level: str, month_pattern: str,
                                        ten_god_count: Dict[str, float], pillars: Dict,
                                        day_master: str, strength: str) -> str:
        """
        生成事业深度解释 - 包括矛盾解释、格局机制详解
        
        理论依据：
        - 《渊海子平·正官论》《论偏官》：解释普通格局但上等贵格的矛盾
        - 《子平真诠·论格局》：解释格局如何间接生贵
        """
        explanations = []
        
        # 1. 矛盾解释：普通格局但上等贵格
        if career_pattern == '普通格局' and nobility_level in ['上等贵格', '中等贵格']:
            if month_pattern and '伤官配印' in month_pattern:
                explanations.append(
                    "表面矛盾：普通格局（命局无代表官职的「官星」）与命格贵贱（" + nobility_level + "）看似矛盾。" +
                    "内在统一性：此为「清贵」与「权势」的区别。无官星，意味着不走传统的行政仕途，" +
                    "不依赖体制内的官位。但「伤官配印」成格，是极高的文贵、学术贵或技术权威的象征。" +
                    "它代表您在专业领域内能凭借过人的才智和学识获得极高的声望、地位和话语权，" +
                    "此为「行业权威」而非「行政官员」。" +
                    "格局机制：伤官配印格的核心在于印星制约伤官的狂傲不羁，" +
                    "使其才华能用于正途并得以升华；而伤官的灵动又缓解了印星过旺带来的沉闷。" +
                    "《子平真诠》云：「伤官佩印者，印能制伤，所以为贵。」" +
                    "此格局主文贵、学识、权柄，但不走传统仕途，而是成为「无冕之王」。"
                )
            elif month_pattern and '食神制杀' in month_pattern:
                explanations.append(
                    "表面矛盾：普通格局但命格贵贱为" + nobility_level + "。" +
                    "内在统一性：食神制杀格以权贵显达，通过权力地位得贵。" +
                    "格局机制：食神制约七杀，以暴制暴，化凶为吉。" +
                    "《渊海子平》云：「食神制杀，英雄独压万人。」" +
                    "此格局间接生贵，权威带贵，英雄独压万人。"
                )
            elif month_pattern and '官印相生' in month_pattern:
                explanations.append(
                    "表面矛盾：普通格局但命格贵贱为" + nobility_level + "。" +
                    "内在统一性：官印相生格以贵气显达，通过官生印、印生身，五行流通得贵。" +
                    "格局机制：官生印、印生身，五行流通，贵气带财。" +
                    "关键在于：官印必须力量相当，不能一方过强或过弱。"
                )
        
        # 2. 格局机制详解
        if month_pattern:
            if '伤官配印' in month_pattern:
                yin_count = ten_god_count.get('正印', 0) + ten_god_count.get('偏印', 0)
                shangguan_count = ten_god_count.get('伤官', 0)
                
                if yin_count > 0 and shangguan_count > 0:
                    explanations.append(
                        "格局机制详解：伤官配印格的核心在于印星（数量" + f"{yin_count:.1f}" + "）" +
                        "与伤官（数量" + f"{shangguan_count:.1f}" + "）的力量平衡。" +
                        "印星制约伤官的狂傲不羁，使其才华能用于正途；而伤官的灵动又缓解了印星过旺带来的沉闷。" +
                        "关键在于：印星不能过度克制伤官（制伤过度），伤官不能反克印星（破印）。" +
                        "当格局清纯时，间接生贵能力强，主文贵、学识、权柄，富大于贵。"
                    )
            elif '食神制杀' in month_pattern:
                shishen_count = ten_god_count.get('食神', 0)
                qisha_count = ten_god_count.get('偏官', 0)
                
                if shishen_count > 0 and qisha_count > 0:
                    explanations.append(
                        "格局机制详解：食神制杀格的核心在于食神（数量" + f"{shishen_count:.1f}" + "）" +
                        "制约七杀（数量" + f"{qisha_count:.1f}" + "），以暴制暴，化凶为吉。" +
                        "关键在于：食神必须有力才能制杀，否则反被七杀所制。" +
                        "此格局间接生贵，通过权威地位得贵，英雄独压万人。"
                    )
            elif '官印相生' in month_pattern:
                guan_count = ten_god_count.get('正官', 0) + ten_god_count.get('偏官', 0)
                yin_count = ten_god_count.get('正印', 0) + ten_god_count.get('偏印', 0)
                
                if guan_count > 0 and yin_count > 0:
                    explanations.append(
                        "格局机制详解：官印相生格的核心在于官星（数量" + f"{guan_count:.1f}" + "）" +
                        "与印星（数量" + f"{yin_count:.1f}" + "）的力量平衡。" +
                        "官生印、印生身，五行流通，贵气带财。" +
                        "关键在于：官印必须力量相当，不能一方过强或过弱。" +
                        "此格局间接生贵，通过贵气地位得贵。"
                    )
        
        # 3. 身强身弱与事业关系详解
        strong = strength in ['身旺', '身强']
        if total_official > 0:
            if strong and total_official >= 1:
                explanations.append(
                    "身强官旺：身强（日主有力）且官星有力（官星数量" + f"{total_official:.1f}" + "），" +
                    "可以胜任官职。《渊海子平》云：「正官乃贵气之物，大忌刑冲破害。大抵要行官旺乡，月令是也。」"
                )
            elif not strong and total_official > 0.5:
                explanations.append(
                    "身弱官重：身弱（日主无力）但官星过重（官星数量" + f"{total_official:.1f}" + "），" +
                    "力不任官，需先扶身。《渊海子平》云：「力不任官，祸患百出。」" +
                    "需通过大运流年扶身（印绶、比劫）后才能胜任官职。"
                )
        
        if not explanations:
            return "事业分析较为常规，无明显矛盾或特殊格局机制需要深度解读。"
        
        return "。".join(explanations) + "。"
    
    def _generate_career_life_strategy(self, nobility_level: str, month_pattern: str,
                                     has_shishang: bool, has_yin: bool, strong: bool,
                                     total_official: float, career_pattern: str) -> Dict[str, str]:
        """
        生成事业人生策略建议 - 包括事业密码、心性修炼等
        
        理论依据：
        - 《渊海子平·论求官》：不同格局的求官方式
        - 《子平真诠·论格局》：格局对人生策略的影响
        """
        strategy = {
            'career_password': '',  # 事业密码
            'development_direction': '',  # 发展方向
            'mindset_cultivation': '',  # 心性修炼
            'key_points': []  # 关键要点
        }
        
        # 1. 事业密码（基于格局和贵贱等级）
        if month_pattern and '伤官配印' in month_pattern:
            strategy['career_password'] = (
                "您的事业源于「才华」与「知识」的深度结合。" +
                "专注于将您的专业技能打磨到极致，成为所在领域的顶尖专家，" +
                "在需要深度思考和创新的领域，能成为「无冕之王」。"
            )
        elif month_pattern and '食神制杀' in month_pattern:
            strategy['career_password'] = (
                "您的事业源于「权威」与「地位」。" +
                "通过建立专业权威、获得行业地位，事业会随之而来。" +
                "避免过度依赖个人能力，注重团队协作和权力结构。"
            )
        elif month_pattern and '官印相生' in month_pattern:
            strategy['career_password'] = (
                "您的事业源于「贵气」与「地位」。" +
                "通过官生印、印生身，五行流通，获得贵气和地位。" +
                "专注于建立稳定的职业路径，等待大运流年扶身。"
            )
        elif total_official > 0:
            strategy['career_password'] = (
                "您的事业源于「官星」。" +
                "通过稳定的工作、稳健的发展获得事业成功。" +
                "专注于建立稳定的职业路径，避免高风险选择。"
            )
        else:
            strategy['career_password'] = (
                "您的事业需通过后天努力获得。" +
                "专注于提升自身能力，等待大运流年引动官星。"
            )
        
        # 2. 发展方向（基于格局）
        if month_pattern and '伤官配印' in month_pattern:
            strategy['development_direction'] = (
                "技术权威、资深专家、策划大师、文化教育工作者等角色非常适合您。" +
                "您不适合刻板的官僚体系，但在需要深度思考和创新的领域，能成为「无冕之王」。"
            )
        elif month_pattern and '食神制杀' in month_pattern:
            strategy['development_direction'] = (
                "军警、管理、企业高管、权威专家等角色非常适合您。" +
                "通过权威地位和团队管理获得成功。"
            )
        elif month_pattern and '官印相生' in month_pattern:
            strategy['development_direction'] = (
                "公职、事业单位、国有企业等角色非常适合您。" +
                "通过稳定的职业路径获得成功。"
            )
        elif total_official > 0:
            strategy['development_direction'] = (
                "需根据大运流年具体分析。" +
                "建议在稳定行业中发展，等待大运引动官星。"
            )
        else:
            strategy['development_direction'] = (
                "需根据大运流年具体分析。" +
                "建议在稳定行业中发展，等待大运引动官星。"
            )
        
        # 3. 心性修炼（基于格局和身强身弱）
        if month_pattern and '伤官配印' in month_pattern:
            strategy['mindset_cultivation'] = (
                "伤官配印格需要平衡才华与理性。" +
                "避免过度张扬才华（伤官过旺），也避免过度保守（印星过旺）。" +
                "保持开放心态，主动学习，融入能激发您活力的圈子。"
            )
        elif not strong:
            strategy['mindset_cultivation'] = (
                "身弱的格局容易带来不自信和依赖感。" +
                "需有意识地提升自身能力，培养独立自主的性格，" +
                "避免过度依赖他人，等待大运扶身后再发力。"
            )
        elif strong and total_official < 0.5:
            strategy['mindset_cultivation'] = (
                "身强但官少的格局容易带来急躁和不满。" +
                "需有意识地保持耐心，专注于提升自身能力，" +
                "等待大运流年引动官星，避免急于求成。"
            )
        else:
            strategy['mindset_cultivation'] = (
                "保持积极向上的心态，专注于提升自身能力，" +
                "根据大运流年的变化调整策略。"
            )
        
        # 4. 关键要点
        if nobility_level in ['上等贵格', '中等贵格']:
            strategy['key_points'].append("贵格等级较高，需善用机遇，避免过度依赖体制")
        if has_shishang:
            strategy['key_points'].append("有食伤，需专注于专业技能提升")
        if not strong:
            strategy['key_points'].append("身弱需先扶身，等待大运流年扶身后再发力")
        if total_official < 0.5:
            strategy['key_points'].append("官星不显，需通过大运流年引动官星")
        
        return strategy
    
    def _analyze_marriage_comprehensive(self, day_master: str, pillars: Dict, gender: str,
                                       ten_god_count: Dict[str, float], strength: str, birth_year: int = None,
                                       bazi_data: BaziData = None, month_pattern: str = '') -> Dict:
        """
        🔥 完整婚姻分析 - 基于《渊海子平》婚姻理论
        
        理论依据：
        - 男命：正财为妻，偏财为情人
        - 女命：正官为夫，七杀为偏夫
        - 日支为配偶宫
        
        分析项目（10项）：
        1. 配偶星识别
        2. 配偶宫分析
        3. 配偶星位置和强弱
        4. 配偶宫与其他柱的关系
        5. 配偶宫破损判断
        6. 婚姻时机分析
        7. 配偶特征分析
        8. 婚姻质量分析
        9. 需要注意的年份
        10. 婚姻建议
        """
        try:
            is_male = gender == '男'
            day_zhi = pillars['day'][1]  # 日支（配偶宫）
            
            # 1. 配偶星识别
            if is_male:
                spouse_star = '正财'  # 男命正财为妻
                spouse_star_count = ten_god_count.get('正财', 0)
                spouse_star_secondary = '偏财'
            else:
                spouse_star = '正官'  # 女命正官为夫
                spouse_star_count = ten_god_count.get('正官', 0)
                spouse_star_secondary = '偏官'
            
            # 2. 配偶宫分析
            spouse_palace_wx = get_wuxing_by_dizhi(day_zhi)
            
            # 3. 配偶星位置
            spouse_star_positions = []
            for pos, (gan, zhi) in pillars.items():
                tg = get_ten_god(day_master, gan)
                if tg == spouse_star:
                    spouse_star_positions.append(pos)
            
            # 4. 配偶宫破损判断（冲、刑、害）
            palace_damaged = False
            palace_damage_reasons = []
            
            # 检查与年、月、时的冲刑害关系
            for pos in ['year', 'month', 'hour']:
                other_zhi = pillars[pos][1]
                # 六冲
                if (day_zhi, other_zhi) in [('子', '午'), ('丑', '未'), ('寅', '申'), ('卯', '酉'), 
                                            ('辰', '戌'), ('巳', '亥'), ('午', '子'), ('未', '丑'),
                                            ('申', '寅'), ('酉', '卯'), ('戌', '辰'), ('亥', '巳')]:
                    palace_damaged = True
                    palace_damage_reasons.append(f"{pos}柱{other_zhi}冲配偶宫")
            
            # 5. 婚姻评估（改为字典格式，以便深度解释函数使用）
            if spouse_star_count == 0:
                marriage_assessment = {
                    'quality': '较差',
                    'description': "配偶星不显，藏于日支之中，婚姻缘分相对较晚，或与配偶关系较为含蓄。"
                }
            elif spouse_star_count >= 2:
                marriage_assessment = {
                    'quality': '较好',
                    'description': "配偶星多现，异性缘分较多，需注意感情专一。"
                }
            else:
                marriage_assessment = {
                    'quality': '一般',
                    'description': "配偶星适中，婚姻缘分正常。"
                }
            
            # 6. 配偶特征（基于日支和配偶星）
            spouse_features = self._analyze_spouse_features(day_zhi, spouse_star, spouse_star_count)
            
            # 7. 妻宫特征深度分析（基于日支五行）
            palace_analysis = self._analyze_palace_characteristics(day_zhi, spouse_palace_wx, is_male, pillars, day_master)
            
            # 8. 应期分析（具体年份姻缘信号）- ✅ 真正结合大运流年综合分析
            marriage_timing = self._analyze_marriage_timing(
                spouse_star_count, day_zhi, pillars, is_male, birth_year, day_master, bazi_data
            )
            
            # 🔥 新增：深度解释机制（基于实际配偶星、日支、格局等参数动态生成）
            try:
                deep_explanation = self._generate_marriage_deep_explanation(
                    spouse_star, spouse_star_count, day_zhi, spouse_palace_wx,
                    palace_damaged, palace_damage_reasons, marriage_assessment,
                    palace_analysis, month_pattern, ten_god_count, day_master, is_male
                )
            except Exception as e:
                print(f"⚠️ 生成婚姻深度解释失败: {e}")
                deep_explanation = "婚姻分析较为常规，无明显特殊机制需要深度解读。"
            
            # 🔥 新增：人生策略建议（基于实际婚姻状况动态生成）
            try:
                life_strategy = self._generate_marriage_life_strategy(
                    spouse_star, spouse_star_count, day_zhi, spouse_palace_wx,
                    palace_damaged, marriage_assessment, palace_analysis,
                    month_pattern, is_male, day_master
                )
            except Exception as e:
                print(f"⚠️ 生成婚姻人生策略失败: {e}")
                life_strategy = {
                    'marriage_password': '需根据实际情况具体分析',
                    'relationship_direction': '保持开放心态，主动沟通，理解对方',
                    'communication_advice': '保持和谐的家庭关系',
                    'key_points': ['保持开放心态，主动沟通，理解对方，维护婚姻的和谐']
                }
            
            return {
                'spouse_star': spouse_star,
                'spouse_star_count': spouse_star_count,
                'spouse_star_positions': spouse_star_positions,
                'spouse_palace': day_zhi,
                'spouse_palace_wx': spouse_palace_wx,
                'palace_damaged': palace_damaged,
                'palace_damage_reasons': palace_damage_reasons,
                'marriage_assessment': marriage_assessment,
                'spouse_features': spouse_features,
                'palace_analysis': palace_analysis,
                'marriage_timing': marriage_timing,
                'deep_explanation': deep_explanation,  # 🔥 新增：深度解释
                'life_strategy': life_strategy  # 🔥 新增：人生策略
            }
        except Exception as e:
            print(f"⚠️ _analyze_marriage_comprehensive 内部错误: {e}")
            import traceback
            traceback.print_exc()
            # 返回一个基本的错误字典，而不是空字典
            return {
                'error': str(e),
                'spouse_star': '未知',
                'spouse_star_count': 0,
                'spouse_palace': '未知',
                'marriage_assessment': {'quality': '分析失败', 'description': f'分析过程中出现错误：{str(e)}'}
            }
    
    def _analyze_spouse_features(self, day_zhi: str, spouse_star: str, count: float) -> Dict:
        """分析配偶特征"""
        wx_map = {
            '木': '性格温和、有仁心、身材修长',
            '火': '性格热情、活跃、面红',
            '土': '性格稳重、踏实、身材敦实',
            '金': '性格刚强、果断、面白',
            '水': '性格灵活、聪明、面黑'
        }
        zhi_wx = get_wuxing_by_dizhi(day_zhi)
        return {
            'personality': wx_map.get(zhi_wx, '需综合判断'),
            'appearance': f'基于日支{zhi_wx}五行特征',
            'ability': '需结合配偶星强弱判断'
        }
    
    def _analyze_palace_characteristics(self, day_zhi: str, palace_wx: str, is_male: bool, pillars: Dict, day_master: str) -> Dict:
        """分析配偶宫特征（基于日支五行）"""
        # 日支（配偶宫）五行特征分析
        palace_char_map = {
            '木': {
                'personality': '性格温和、有仁心',
                'pressure': '较轻',
                'relationship': '相对和谐'
            },
            '火': {
                'personality': '性格热情、活跃',
                'pressure': '中等',
                'relationship': '需要沟通'
            },
            '土': {
                'personality': '性格稳重、踏实',
                'pressure': '较重（印星也是忌神时，带有管束和压力）',
                'relationship': '需要更多的沟通与磨合'
            },
            '金': {
                'personality': '性格刚强、果断',
                'pressure': '中等偏重',
                'relationship': '需要协调'
            },
            '水': {
                'personality': '性格灵活、聪明',
                'pressure': '较轻',
                'relationship': '相对和谐'
            }
        }
        
        char_info = palace_char_map.get(palace_wx, {
            'personality': '需综合判断',
            'pressure': '需综合判断',
            'relationship': '需综合判断'
        })
        
        # 判断日支是否为忌神（简化判断：日支五行与日主五行相克或相同可能为忌）
        day_master_wx = get_wuxing_by_tiangan(day_master)
        
        # 判断是否为忌神：日支五行克制日主，或日支为印星但过重
        is_jishen = False
        if palace_wx == '土' and day_master_wx == '金':
            # 土重埋金，土为忌神
            is_jishen = True
        
        description = f"日支{day_zhi}（{palace_wx}）为配偶宫，"
        if is_jishen:
            description += f"是印星也是忌神。这通常意味着配偶{char_info['personality']}，但对您可能也带有一种{char_info['pressure']}，{char_info['relationship']}。"
        else:
            description += f"配偶{char_info['personality']}，{char_info['relationship']}。"
        
        return {
            'palace_wx': palace_wx,
            'characteristics': char_info,
            'is_jishen': is_jishen,
            'description': description
        }
    
    def _generate_marriage_deep_explanation(self, spouse_star: str, spouse_star_count: float,
                                           day_zhi: str, spouse_palace_wx: str,
                                           palace_damaged: bool, palace_damage_reasons: List,
                                           marriage_assessment: Dict, palace_analysis: Dict,
                                           month_pattern: str, ten_god_count: Dict[str, float],
                                           day_master: str, is_male: bool) -> str:
        """
        生成婚姻深度解释 - 基于实际配偶星、日支、格局等参数动态生成
        
        理论依据：
        - 《渊海子平·论婚姻》：配偶星和配偶宫的分析
        - 《三命通会·婚姻应期》：应期分析理论
        """
        explanations = []
        
        # 1. 配偶星机制详解（基于实际数量）
        if spouse_star_count < 0.5:
            star_name = "正财" if is_male else "正官"
            explanations.append(
                f"配偶星机制：{star_name}不显（数量{spouse_star_count:.1f}）。" +
                f"根据《渊海子平·论婚姻》，{star_name}为{'妻星' if is_male else '夫星'}，" +
                f"不显意味着需要大运流年引出藏于地支的{star_name}。" +
                f"婚姻的到来，极大程度上依赖于大运和流年引出藏于地支的{star_name}。"
            )
        elif spouse_star_count >= 1.0:
            star_name = "正财" if is_male else "正官"
            explanations.append(
                f"配偶星机制：{star_name}有力（数量{spouse_star_count:.1f}）。" +
                f"根据《渊海子平·论婚姻》，{star_name}为{'妻星' if is_male else '夫星'}，" +
                f"有力意味着配偶星明显，{'容易遇到合适的对象' if is_male else '容易遇到合适的对象'}，" +
                f"但需结合大运流年分析具体应期。"
            )
        else:
            star_name = "正财" if is_male else "正官"
            explanations.append(
                f"配偶星机制：{star_name}一般（数量{spouse_star_count:.1f}）。" +
                f"根据《渊海子平·论婚姻》，{star_name}为{'妻星' if is_male else '夫星'}，" +
                f"数量一般，需结合大运流年分析具体应期。"
            )
        
        # 2. 配偶宫机制详解（基于实际日支和破损情况）
        if palace_damaged:
            explanations.append(
                f"配偶宫机制：日支{day_zhi}（{spouse_palace_wx}）为配偶宫，但受破损。" +
                f"破损原因：{', '.join(palace_damage_reasons) if palace_damage_reasons else '未知'}。" +
                f"根据《渊海子平·论婚姻》，配偶宫破损会影响婚姻的稳定性，" +
                f"需注意配偶关系的维护，避免因外部因素导致婚姻不顺。"
            )
        else:
            explanations.append(
                f"配偶宫机制：日支{day_zhi}（{spouse_palace_wx}）为配偶宫，未受破损。" +
                f"根据《渊海子平·论婚姻》，配偶宫完整有利于婚姻的稳定性，" +
                f"配偶{palace_analysis.get('characteristics', {}).get('personality', '性格良好')}，" +
                f"关系{palace_analysis.get('characteristics', {}).get('relationship', '相对和谐')}。"
            )
        
        # 3. 配偶宫忌神机制详解（基于实际分析）
        if palace_analysis.get('is_jishen', False):
            day_master_wx = get_wuxing_by_tiangan(day_master)
            explanations.append(
                f"配偶宫忌神机制：日支{day_zhi}（{spouse_palace_wx}）是印星也是忌神。" +
                f"日主为{day_master_wx}，{spouse_palace_wx}为印星，" +
                f"当印星过重时，{'如土重埋金' if (day_master_wx == '金' and spouse_palace_wx == '土') else ''}，" +
                f"配偶虽然{palace_analysis.get('characteristics', {}).get('personality', '性格良好')}，" +
                f"但对您可能也带有一种{palace_analysis.get('characteristics', {}).get('pressure', '压力')}，" +
                f"需要更多的沟通与磨合。"
            )
        
        # 4. 婚姻质量机制详解（基于实际评估）
        if marriage_assessment:
            quality = marriage_assessment.get('quality', '')
            if quality == '较好':
                explanations.append(
                    f"婚姻质量机制：婚姻质量较好。" +
                    f"配偶星{'有力' if spouse_star_count >= 1.0 else '一般'}，" +
                    f"配偶宫{'完整' if not palace_damaged else '受破损'}，" +
                    f"根据《渊海子平·论婚姻》，婚姻质量主要看配偶星和配偶宫的配合，" +
                    f"配合良好则婚姻质量较好。"
                )
            elif quality == '一般':
                explanations.append(
                    f"婚姻质量机制：婚姻质量一般。" +
                    f"配偶星{'一般' if spouse_star_count < 1.0 else '有力'}，" +
                    f"配偶宫{'受破损' if palace_damaged else '完整'}，" +
                    f"根据《渊海子平·论婚姻》，需通过大运流年改善，或注意配偶关系的维护。"
                )
            elif quality == '较差':
                explanations.append(
                    f"婚姻质量机制：婚姻质量较差。" +
                    f"配偶星{'不显' if spouse_star_count < 0.5 else '一般'}，" +
                    f"配偶宫{'受破损' if palace_damaged else '一般'}，" +
                    f"根据《渊海子平·论婚姻》，需通过大运流年改善，特别注意配偶关系的维护，" +
                    f"避免因外部因素导致婚姻不顺。"
                )
        
        # 5. 格局对婚姻的影响（基于实际格局）
        if month_pattern:
            if '伤官配印' in month_pattern:
                shangguan_count = ten_god_count.get('伤官', 0)
                explanations.append(
                    f"格局对婚姻的影响：伤官配印格（伤官数量{shangguan_count:.1f}）。" +
                    f"根据《渊海子平·论婚姻》，伤官配印格主文贵，配偶多为有学识、有文化之人，" +
                    f"但需注意伤官的叛逆性可能影响婚姻关系的和谐，" +
                    f"需通过沟通和理解来维护婚姻。"
                )
            elif '食神制杀' in month_pattern:
                explanations.append(
                    f"格局对婚姻的影响：食神制杀格。" +
                    f"根据《渊海子平·论婚姻》，食神制杀格主权威，配偶多为有权威、有能力之人，" +
                    f"但需注意权威性可能带来压力，需通过相互理解来维护婚姻。"
                )
            elif '正官格' in month_pattern or '七杀格' in month_pattern:
                if not is_male:
                    explanations.append(
                        f"格局对婚姻的影响：官杀格（女命）。" +
                        f"根据《渊海子平·论婚姻》，女命官杀格，配偶星有力，" +
                        f"容易遇到合适的对象，但需注意官杀的约束性，" +
                        f"需通过相互理解来维护婚姻。"
                    )
        
        if not explanations:
            return "婚姻分析较为常规，无明显特殊机制需要深度解读。"
        
        return "。".join(explanations) + "。"
    
    def _generate_marriage_life_strategy(self, spouse_star: str, spouse_star_count: float,
                                        day_zhi: str, spouse_palace_wx: str,
                                        palace_damaged: bool, marriage_assessment: Dict,
                                        palace_analysis: Dict, month_pattern: str,
                                        is_male: bool, day_master: str) -> Dict[str, str]:
        """
        生成婚姻人生策略建议 - 基于实际婚姻状况动态生成
        
        理论依据：
        - 《渊海子平·论婚姻》：不同婚姻状况的相处建议
        - 《三命通会·婚姻应期》：应期分析理论
        """
        strategy = {
            'marriage_password': '',  # 感情密码
            'relationship_direction': '',  # 相处方向
            'communication_advice': '',  # 沟通建议
            'key_points': []  # 关键要点
        }
        
        # 1. 感情密码（基于配偶星和配偶宫）
        if spouse_star_count < 0.5:
            star_name = "妻星" if is_male else "夫星"
            strategy['marriage_password'] = (
                f"您的婚姻关键在于「等待时机」。" +
                f"{star_name}不显（数量{spouse_star_count:.1f}），" +
                f"需要大运流年引出藏于地支的{star_name}。" +
                f"在大运流年有利时，抓住机会，主动寻找合适的对象。"
            )
        elif spouse_star_count >= 1.0:
            star_name = "妻星" if is_male else "夫星"
            strategy['marriage_password'] = (
                f"您的婚姻关键在于「主动把握」。" +
                f"{star_name}有力（数量{spouse_star_count:.1f}），" +
                f"容易遇到合适的对象。" +
                f"需主动把握机会，在合适的时机主动出击，找到合适的对象。"
            )
        else:
            star_name = "妻星" if is_male else "夫星"
            strategy['marriage_password'] = (
                f"您的婚姻关键在于「顺势而为」。" +
                f"{star_name}一般（数量{spouse_star_count:.1f}），" +
                f"需结合大运流年分析具体应期。" +
                f"在大运流年有利时，抓住机会，找到合适的对象。"
            )
        
        # 2. 相处方向（基于配偶宫和格局）
        if palace_damaged:
            strategy['relationship_direction'] = (
                f"配偶宫受破损（日支{day_zhi}），需特别注意配偶关系的维护。" +
                f"避免因外部因素（冲、刑、害）导致婚姻不顺，" +
                f"需通过沟通和理解来维护婚姻的稳定性。"
            )
        elif palace_analysis.get('is_jishen', False):
            strategy['relationship_direction'] = (
                f"日支{day_zhi}是印星也是忌神，配偶{palace_analysis.get('characteristics', {}).get('personality', '性格良好')}，" +
                f"但对您可能也带有一种{palace_analysis.get('characteristics', {}).get('pressure', '压力')}。" +
                f"需通过更多的沟通与磨合来维护婚姻，避免因压力导致婚姻不顺。"
            )
        else:
            personality = palace_analysis.get('characteristics', {}).get('personality', '性格良好')
            relationship = palace_analysis.get('characteristics', {}).get('relationship', '相对和谐')
            strategy['relationship_direction'] = (
                f"配偶{personality}，关系{relationship}。" +
                f"需通过沟通和理解来维护婚姻，保持和谐的家庭关系。"
            )
        
        # 3. 沟通建议（基于实际婚姻状况）
        communication_items = []
        
        if palace_damaged:
            communication_items.append("配偶宫受破损，需特别注意沟通，避免因外部因素导致婚姻不顺")
        
        if palace_analysis.get('is_jishen', False):
            communication_items.append("配偶宫为忌神，需通过更多的沟通与磨合来维护婚姻")
        
        if month_pattern and '伤官配印' in month_pattern:
            communication_items.append("伤官配印格，需注意伤官的叛逆性，通过沟通和理解来维护婚姻")
        
        if month_pattern and '食神制杀' in month_pattern:
            communication_items.append("食神制杀格，需注意权威性带来的压力，通过相互理解来维护婚姻")
        
        if not communication_items:
            communication_items.append("保持开放心态，主动沟通，理解对方，维护婚姻的和谐")
        
        strategy['communication_advice'] = "；".join(communication_items) + "。"
        
        # 4. 关键要点（基于实际婚姻状况）
        if spouse_star_count < 0.5:
            star_name = "妻星" if is_male else "夫星"
            strategy['key_points'].append(f"{star_name}不显，需通过大运流年引出{star_name}")
        
        if palace_damaged:
            strategy['key_points'].append("配偶宫受破损，需特别注意配偶关系的维护")
        
        if palace_analysis.get('is_jishen', False):
            strategy['key_points'].append("配偶宫为忌神，需通过更多的沟通与磨合来维护婚姻")
        
        if month_pattern and '伤官配印' in month_pattern:
            strategy['key_points'].append("伤官配印格，需注意伤官的叛逆性，通过沟通和理解来维护婚姻")
        
        if not strategy['key_points']:
            strategy['key_points'].append("保持开放心态，主动沟通，理解对方，维护婚姻的和谐")
        
        return strategy
    
    def _analyze_marriage_timing(self, spouse_star_count: float, day_zhi: str, pillars: Dict, is_male: bool, 
                                 birth_year: int = None, day_master: str = None, bazi_data: BaziData = None) -> Dict:
        """
        分析婚姻应期（具体年份姻缘信号）
        ✅ 修复：真正结合大运流年综合分析，不是简单筛选年份
        
        理论依据：
        - 《渊海子平·论应期》：应期需大运和流年配合
        - 《三命通会·婚姻应期》：大运有财星/官星，流年引出时才是应期
        """
        timing_years = []
        timing_analysis = []
        timing_years_detail = []
        timing_description = ""
        top_years = []  # ✅ 修复：初始化 top_years，避免未定义错误
        
        if spouse_star_count == 0:
            # 配偶星不显，需要大运流年引出
            if is_male:
                # 男命：正财为妻，需要寻找藏财的年份
                spouse_star = '正财'
                # ✅ 修复：根据日主推算藏财的地支（日主克的为财星）
                # 例如：日主为辛金，辛金克木，寅中藏甲木，卯中藏乙木，辰中藏乙木
                timing_years = self._find_caixing_dizhi(day_master) if day_master else ['寅', '卯', '辰']
                timing_analysis.append("婚姻的到来，极大程度上依赖于大运和流年引出藏于地支的财星（妻星）。")
            else:
                # 女命：正官为夫，需要寻找藏官的年份
                spouse_star = '正官'
                # ✅ 修复：根据日主推算藏官的地支（克日主的为官星）
                # 例如：日主为辛金，克辛金的是丙丁火，巳中藏丙火，午中藏丁火
                timing_years = self._find_guansha_dizhi(day_master) if day_master else ['巳', '午', '未']
                timing_analysis.append("婚姻的到来，极大程度上依赖于大运和流年引出藏于地支的官星（夫星）。")
            
            # ✅ 真正分析：结合大运流年综合分析
            if bazi_data and day_master and birth_year:
                top_years = self._calculate_marriage_timing_with_dayun(
                    spouse_star, timing_years, bazi_data, day_master, is_male, birth_year
                )
            else:
                # 如果没有大运信息，降级使用简单方法
                timing_years_detail = self._calculate_timing_years(
                    timing_years, birth_year=birth_year, years_ahead=80
                )
                # 简单筛选：优先选择18-40岁之间的年份
                preferred_years = [y for y in timing_years_detail if 18 <= y.get('age', 0) <= 40]
                top_years = preferred_years[:3] if len(preferred_years) >= 3 else (preferred_years + [y for y in timing_years_detail if y not in preferred_years][:3-len(preferred_years)] if preferred_years else timing_years_detail[:3])
            
            if top_years:
                # 显示3个最有机会的年份
                year_descriptions = [f"{y.get('year', 0)}年（{y.get('ganzhi', '')}年，{y.get('age', 0)}岁）" for y in top_years]
                years_str = '、'.join(year_descriptions)
                timing_description = f"根据《渊海子平》《三命通会》理论综合分析：结合大运流年，最有机会的应期年份：{years_str}。"
            else:
                # 如果没有计算出具体年份，使用地支描述
                zhi_str = '、'.join([f"{zhi}年" for zhi in timing_years])
                timing_description = f"根据《渊海子平》《三命通会》理论：当流年地支为{zhi_str}时，可能引出藏于地支的{'财星（妻星）' if is_male else '官星（夫星）'}。需结合大运流年动态分析。"
        else:
            # ✅ 新增：配偶星存在的情况，需要分析配偶星出现的大运流年
            if is_male:
                spouse_star = '正财'
            else:
                spouse_star = '正官'
            
            # 查找配偶星出现的大运流年
            if bazi_data and day_master and birth_year:
                # 使用十神年份计算方法
                # ✅ 修复：传入birth_year参数，确保计算年龄
                all_years = self._calculate_ten_god_years(
                    day_master, spouse_star, birth_year=birth_year, years_ahead=80
                )

                # ✅ 修复：添加年龄限制，过滤不合理的年份
                # 理论依据：《三命通会·论应期》："应期必待成年，幼年虽有信号，不以为期"
                min_marriage_age = 16 if is_male else 14  # 男性最小16岁，女性最小14岁（古代最低合理年龄）
                max_marriage_age = 50  # 最大50岁（超过50岁的应期意义不大）
                filtered_years = [y for y in all_years if min_marriage_age <= y.get('age', 0) <= max_marriage_age]

                # ✅ 修复：优先选择18-35岁之间的年份（现代合理婚龄）
                preferred_years = [y for y in filtered_years if 18 <= y.get('age', 0) <= 35]
                top_years = preferred_years[:3] if len(preferred_years) >= 3 else filtered_years[:3]

                if top_years:
                    year_descriptions = [f"{y.get('year', 0)}年（{y.get('ganzhi', '')}年，{y.get('age', 0)}岁）" for y in top_years]
                    years_str = '、'.join(year_descriptions)
                    timing_description = f"根据《渊海子平》《三命通会》理论：配偶星存在，当大运流年逢{spouse_star}时，婚姻应期到来。最有机会的应期年份：{years_str}。"
                    timing_analysis.append(f"配偶星{spouse_star}已存在，需大运流年引动，方能成婚。")
                else:
                    timing_description = f"根据《渊海子平》《三命通会》理论：配偶星{spouse_star}已存在，需结合大运流年动态分析，当大运流年逢{spouse_star}时，婚姻应期到来。"
                    timing_analysis.append(f"配偶星{spouse_star}已存在，需大运流年引动，方能成婚。")
            else:
                timing_description = f"根据《渊海子平》《三命通会》理论：配偶星{spouse_star}已存在，需结合大运流年动态分析，当大运流年逢{spouse_star}时，婚姻应期到来。"
                timing_analysis.append(f"配偶星{spouse_star}已存在，需大运流年引动，方能成婚。")
        
        return {
            'timing_years': timing_years,  # 地支列表（保持兼容）
            'timing_years_detail': top_years if top_years else [],  # ✅ 只返回真正分析出的3个年份
            'timing_description': timing_description,
            'analysis': timing_analysis,
            'suggestion': '以上为结合大运流年综合分析得出的应期年份'
        }
    
    def _calculate_timing_years(self, target_zhi_list: List[str], birth_year: int = None, 
                               years_ahead: int = 80) -> List[Dict]:
        """
        计算应期年份（根据地支列表计算具体公历年份）
        ✅ 修复：完全基于八字推算，不使用AI主观判断（如年龄合理性）
        ✅ 修复：从出生年份开始计算所有符合地支的年份
        
        理论依据：
        - 《三命通会·论太岁》：流年地支决定应期信号
        - 《渊海子平·论应期》：应期由命局和大运流年决定，不能用主观判断限制
        
        Args:
            target_zhi_list: 目标地支列表（如：['寅', '卯', '辰']）- 根据命局推算
            birth_year: 出生年份（必须提供，否则无法推算）
            years_ahead: 从出生年份往后计算多少年（默认80年，覆盖完整人生周期）
        
        Returns:
            应期年份列表，每个元素包含：year, ganzhi, zhi, description
        """
        from datetime import datetime
        from ..core.constants import TIANGAN_LIST, DIZHI_LIST
        
        # ✅ 修复：必须有出生年份才能推算，否则返回空列表
        if not birth_year or birth_year <= 1900:
            return []  # 没有出生年份无法推算
        
        timing_years_detail = []
        
        # ✅ 真实推算：年份转干支函数（基于1984年甲子年作为确定的基准）
        # 理论依据：《三命通会·论太岁》：1984年为甲子年（确定的基准年）
        def year_to_ganzhi(year: int) -> tuple:
            offset = year - 1984  # 1984年是确定的甲子年
            gan = TIANGAN_LIST[offset % 10]
            zhi = DIZHI_LIST[offset % 12]
            return gan, zhi
        
        # ✅ 修复：从出生年份开始计算所有符合地支的年份（不设年龄限制）
        # 基于命理理论：应期完全由八字和大运流年决定
        for i in range(years_ahead):
            year = birth_year + i  # 从出生年份开始推算
            age = year - birth_year  # 计算该年份对应的年龄（仅用于显示）
            
            # ✅ 真实推算：根据年份计算干支（基于1984年甲子年基准）
            gan, zhi = year_to_ganzhi(year)
            
            # ✅ 真实检查：检查年份地支是否在目标地支列表中（根据命局推算）
            if zhi in target_zhi_list:
                timing_years_detail.append({
                    'year': year,
                    'age': age,
                    'ganzhi': f"{gan}{zhi}",
                    'zhi': zhi,
                    'description': f'{year}年（{gan}{zhi}年，{age}岁）'
                })
        
        return timing_years_detail
    
    def _calculate_marriage_timing_with_dayun(self, spouse_star: str, target_zhi_list: List[str], 
                                             bazi_data: BaziData, day_master: str, is_male: bool, 
                                             birth_year: int) -> List[Dict]:
        """
        结合大运流年综合分析婚姻应期
        ✅ 真正分析：不是猜测，而是基于大运和流年的配合
        
        理论依据：
        - 《渊海子平·论应期》：大运有财星/官星，流年引出时才是应期
        - 《三命通会·婚姻应期》：大运天干或地支有配偶星，流年地支符合条件时，为应期
        
        分析步骤：
        1. 计算大运干支和年龄范围
        2. 分析每个大运是否有财星/官星（对婚姻有利）
        3. 分析每个流年：流年地支符合条件 + 大运有利 = 应期
        4. 综合评分，选择最好的3个
        """
        from datetime import datetime
        from ..core.constants import TIANGAN_LIST, DIZHI_LIST, DIZHI_CANGGAN
        
        # 1. 计算大运方向
        year_gan = bazi_data.get_pillars()['year'][0]
        month_gan, month_zhi = bazi_data.get_pillars()['month']
        gender_str = '男' if is_male else '女'
        
        yang_gan = {'甲', '丙', '戊', '庚', '壬'}
        is_yang_year = year_gan in yang_gan
        direction = '顺行' if (is_yang_year and is_male) or (not is_yang_year and not is_male) else '逆行'
        
        # 2. 计算大运干支列表（前10步大运）
        gan_idx = TIANGAN_LIST.index(month_gan)
        zhi_idx = DIZHI_LIST.index(month_zhi)
        direction_offset = 1 if direction == '顺行' else -1
        
        dayun_list = []
        for step in range(10):
            offset = (step + 1) * direction_offset
            gan = TIANGAN_LIST[(gan_idx + offset) % 10]
            zhi = DIZHI_LIST[(zhi_idx + offset) % 12]
            dayun_list.append({
                'step': step + 1,
                'gan': gan,
                'zhi': zhi,
                'ganzhi': f"{gan}{zhi}"
            })
        
        # 3. 计算起运年龄（使用sxtwl精确计算）
        qiyun_age = self._calculate_qiyun_age_for_timing(bazi_data, direction)
        
        # 4. 分析每个大运是否有配偶星（对婚姻有利）
        dayun_beneficial = []  # 存储有利的大运信息
        for i, dayun in enumerate(dayun_list):
            start_age = qiyun_age + i * 10
            end_age = start_age + 10
            
            # 分析大运天干是否有配偶星
            dayun_tg = get_ten_god(day_master, dayun['gan'])
            has_spouse_star_in_gan = (dayun_tg == spouse_star) or \
                                    (spouse_star == '正财' and dayun_tg == '偏财') or \
                                    (spouse_star == '正官' and dayun_tg == '七杀')
            
            # 分析大运地支是否藏有配偶星
            has_spouse_star_in_zhi = False
            for canggan, weight in DIZHI_CANGGAN.get(dayun['zhi'], []):
                canggan_tg = get_ten_god(day_master, canggan)
                if canggan_tg == spouse_star or \
                   (spouse_star == '正财' and canggan_tg == '偏财') or \
                   (spouse_star == '正官' and canggan_tg == '七杀'):
                    has_spouse_star_in_zhi = True
                    break
            
            # 如果大运有利，记录该大运的年龄范围
            if has_spouse_star_in_gan or has_spouse_star_in_zhi:
                dayun_beneficial.append({
                    'step': dayun['step'],
                    'ganzhi': dayun['ganzhi'],
                    'start_age': start_age,
                    'end_age': end_age,
                    'start_year': int(birth_year + start_age),
                    'end_year': int(birth_year + end_age),
                    'reason': '大运有' + spouse_star if has_spouse_star_in_gan else '大运地支藏' + spouse_star
                })
        
        # 5. 计算所有符合流年地支条件的年份（从出生年份开始，80年内）
        candidate_years = []
        for i in range(80):
            year = birth_year + i
            age = year - birth_year
            
            # 计算流年干支
            offset = year - 1984  # 1984年是甲子年
            gan = TIANGAN_LIST[offset % 10]
            zhi = DIZHI_LIST[offset % 12]
            
            # 检查流年地支是否符合条件
            if zhi not in target_zhi_list:
                continue
            
            # 检查该年份是否在有利的大运范围内
            in_beneficial_dayun = False
            beneficial_dayun_info = None
            for dy in dayun_beneficial:
                if dy['start_year'] <= year <= dy['end_year']:
                    in_beneficial_dayun = True
                    beneficial_dayun_info = dy
                    break
            
            # 只有在大运有利且流年地支符合条件时，才是应期
            # ✅ 修复：添加合理的年龄下限（根据经典理论，古代女性最小14-16岁，男性16-18岁）
            # 理论依据：《三命通会·论应期》："应期必待成年，幼年虽有信号，不以为期"
            min_marriage_age = 16 if is_male else 14  # 男性最小16岁，女性最小14岁（古代最低合理年龄）
            if in_beneficial_dayun and age >= min_marriage_age:
                # 综合评分：大运有利 + 流年地支符合 + 年龄合理 = 应期
                score = 100 if in_beneficial_dayun else 0
                candidate_years.append({
                    'year': year,
                    'age': age,
                    'ganzhi': f"{gan}{zhi}",
                    'zhi': zhi,
                    'dayun': beneficial_dayun_info['ganzhi'] if beneficial_dayun_info else '',
                    'reason': beneficial_dayun_info['reason'] if beneficial_dayun_info else '',
                    'score': score,
                    'description': f'{year}年（{gan}{zhi}年，{age}岁），大运{beneficial_dayun_info["ganzhi"] if beneficial_dayun_info else ""}'
                })
        
        # 6. 如果没有在大运有利范围内的年份，降级：选择流年地支符合条件且年龄较合理的年份
        if not candidate_years:
            # 降级：只根据流年地支筛选，优先选择合理年龄范围内的年份
            min_marriage_age = 16 if is_male else 14  # 与上面保持一致
            for i in range(80):
                year = birth_year + i
                age = year - birth_year
                if age < min_marriage_age or age > 50:
                    continue
                
                offset = year - 1984
                gan = TIANGAN_LIST[offset % 10]
                zhi = DIZHI_LIST[offset % 12]
                
                if zhi in target_zhi_list:
                    candidate_years.append({
                        'year': year,
                        'age': age,
                        'ganzhi': f"{gan}{zhi}",
                        'zhi': zhi,
                        'dayun': '',
                        'reason': '流年地支符合条件',
                        'score': 50,  # 降级评分
                        'description': f'{year}年（{gan}{zhi}年，{age}岁）'
                    })
        
        # 7. 按评分排序，选择最好的3个
        candidate_years.sort(key=lambda x: (-x['score'], x['age']))  # 按评分降序，年龄升序
        top_years = candidate_years[:3]
        
        return top_years
    
    def _find_caixing_dizhi(self, day_master: str) -> List[str]:
        """
        根据日主推算藏有财星（正财/偏财）的地支
        理论依据：《渊海子平·论正财》：我克者为财
        """
        from ..core.constants import TIANGAN_WUXING, WUXING_KE_MAP, DIZHI_CANGGAN
        
        # 获取日主五行
        day_master_wx = TIANGAN_WUXING.get(day_master, '')
        if not day_master_wx:
            return ['寅', '卯', '辰']  # 默认值
        
        # 日主克的五行是财星的五行
        # WUXING_KE_MAP[day_master_wx] 返回日主克的五行
        caixing_wx = WUXING_KE_MAP.get(day_master_wx, '')
        if not caixing_wx:
            return ['寅', '卯', '辰']  # 默认值
        
        # 找到属于该五行的天干（这些天干对日主来说是财星）
        # 例如：日主为辛（金），辛金克木，木的天干是甲、乙
        wx_to_tiangan = {
            '木': ['甲', '乙'],
            '火': ['丙', '丁'],
            '土': ['戊', '己'],
            '金': ['庚', '辛'],
            '水': ['壬', '癸']
        }
        caixing_tiangan = wx_to_tiangan.get(caixing_wx, [])
        
        # 找到藏有这些天干的地支
        caixing_dizhi = []
        for zhi, canggan_list in DIZHI_CANGGAN.items():
            for canggan, weight in canggan_list:
                if canggan in caixing_tiangan and weight >= 0.5:  # 只考虑权重>=0.5的藏干
                    if zhi not in caixing_dizhi:
                        caixing_dizhi.append(zhi)
                    break
        
        return caixing_dizhi if caixing_dizhi else ['寅', '卯', '辰']  # 如果没找到，使用默认值
    
    def _find_guansha_dizhi(self, day_master: str) -> List[str]:
        """
        根据日主推算藏有官杀（正官/七杀）的地支
        理论依据：《渊海子平·论正官》：克我者为官杀
        """
        from ..core.constants import TIANGAN_WUXING, WUXING_KE_MAP, DIZHI_CANGGAN
        
        # 获取日主五行
        day_master_wx = TIANGAN_WUXING.get(day_master, '')
        if not day_master_wx:
            return ['巳', '午', '未']  # 默认值
        
        # 克日主的五行是官杀的五行
        guansha_wx = WUXING_KE_MAP.get(day_master_wx, '')
        if not guansha_wx:
            return ['巳', '午', '未']  # 默认值
        
        # 找到属于该五行的天干（这些天干对日主来说是官杀）
        # 例如：日主为辛（金），克金的是火，火的天干是丙、丁
        wx_to_tiangan = {
            '木': ['甲', '乙'],
            '火': ['丙', '丁'],
            '土': ['戊', '己'],
            '金': ['庚', '辛'],
            '水': ['壬', '癸']
        }
        guansha_tiangan = wx_to_tiangan.get(guansha_wx, [])
        
        # 找到藏有这些天干的地支
        guansha_dizhi = []
        for zhi, canggan_list in DIZHI_CANGGAN.items():
            for canggan, weight in canggan_list:
                if canggan in guansha_tiangan and weight >= 0.5:  # 只考虑权重>=0.5的藏干
                    if zhi not in guansha_dizhi:
                        guansha_dizhi.append(zhi)
                    break
        
        return guansha_dizhi if guansha_dizhi else ['巳', '午', '未']  # 如果没找到，使用默认值
    
    def _calculate_qiyun_age_for_timing(self, bazi_data: BaziData, direction: str) -> float:
        """
        计算起运年龄（用于应期分析）
        优先使用sxtwl精确计算，失败则使用简化方法
        """
        try:
            # 尝试使用sxtwl计算
            try:
                import sxtwl
                year = bazi_data.birth_year
                month = bazi_data.birth_month
                day = bazi_data.birth_day
                
                day_obj = sxtwl.fromSolar(year, month, day)
                
                if direction == '顺行':
                    # 顺行：找下一个节气
                    current = day_obj
                    days_count = 0
                    for _ in range(400):
                        current = current.after(1)
                        days_count += 1
                        if current.hasJieQi():
                            days_diff = days_count
                            if days_diff > 0:
                                qiyun_age = days_diff / 3.0
                                qiyun_age = round(qiyun_age, 1)
                                if qiyun_age < 0.5:
                                    qiyun_age = 0.5
                                elif qiyun_age > 10.0:
                                    qiyun_age = 10.0
                                return qiyun_age
                            break
                else:
                    # 逆行：找上一个节气
                    current = day_obj
                    days_count = 0
                    for _ in range(400):
                        current = current.before(1)
                        days_count += 1
                        if current.hasJieQi():
                            days_diff = days_count
                            if days_diff > 0:
                                qiyun_age = days_diff / 3.0
                                qiyun_age = round(qiyun_age, 1)
                                if qiyun_age < 0.5:
                                    qiyun_age = 0.5
                                elif qiyun_age > 10.0:
                                    qiyun_age = 10.0
                                return qiyun_age
                            break
            except Exception:
                pass
            
            # 降级：使用简化方法（默认1岁）
            return 1.0
        except Exception:
            return 1.0
    
    def _analyze_sixqin_comprehensive(self, day_master: str, pillars: Dict, gender: str,
                                      ten_god_count: Dict[str, float], strength: str = '中和', birth_year: int = None) -> Dict:
        """
        🔥 完整六亲分析 - 基于《渊海子平·六亲章》《三命通会·六亲论》
        
        理论依据：
        - 《渊海子平·六亲章》：年柱为父，月柱为母，日支为配偶，时支为子女
        - 《三命通会·六亲论》：正官为父（男命），正印为母，比劫为兄弟，食伤为子女
        
        分析项目（8项）：
        1. 父亲分析（偏财/正官）- 基于《渊海子平》：男命偏财为父，女命正官为父
        2. 母亲分析（正印）
        3. 兄弟姐妹分析（比肩劫财）
        4. 子女分析（食伤）
        5. 六亲关系
        6. 六亲助力
        7. 需要注意的年份
        8. 六亲建议
        """
        # ✅ 修复：根据《渊海子平》理论，男命偏财为父，女命正官为父
        is_male = gender == '男'
        if is_male:
            father_star = ten_god_count.get('偏财', 0)  # 男命偏财为父
        else:
            father_star = ten_god_count.get('正官', 0)  # 女命正官为父
        
        # 1. 父亲分析
        father_analysis = {
            'count': father_star,
            'assessment': '父缘助力较弱' if father_star == 0 else '父缘尚可',
            'position': '年柱为父' if father_star > 0 else '父星不显',
            'star_name': '偏财' if is_male else '正官'
        }
        
        # 2. 母亲分析（正印）- ✅ 增强：详细健康分析（基于十神强弱）
        mother_star = ten_god_count.get('正印', 0)
        pianyin_count = ten_god_count.get('偏印', 0)
        cai_count = ten_god_count.get('正财', 0) + ten_god_count.get('偏财', 0)
        shishang_count = ten_god_count.get('食神', 0) + ten_god_count.get('伤官', 0)
        
        # ✅ 新增：判断正印是否在月令（得令最强）
        month_gan = pillars['month'][0]
        month_tg = get_ten_god(day_master, month_gan)
        mother_in_month = month_tg == '正印'
        
        # ✅ 新增：判断正印是否有根气（检查地支藏干）
        mother_has_root = False
        for pos, (gan, zhi) in pillars.items():
            if pos == 'month':
                # 月支藏干中的正印（权重>=0.3）
                for canggan, w in DIZHI_CANGGAN.get(zhi, []):
                    if get_ten_god(day_master, canggan) == '正印' and w >= 0.3:
                        mother_has_root = True
                        break
            # 其他地支藏干中的正印（权重>=0.5）
            for canggan, w in DIZHI_CANGGAN.get(zhi, []):
                if get_ten_god(day_master, canggan) == '正印' and w >= 0.5:
                    mother_has_root = True
                    break
        
        # ✅ 新增：判断财星是否坏印（财克印）
        caixing_hua_yin = False
        if cai_count > 0 and mother_star > 0:
            if cai_count >= mother_star * 1.2:  # 财星数量超过印星1.2倍
                caixing_hua_yin = True
        
        # ✅ 新增：判断食伤是否泄印（食伤泄身，间接泄印）
        shishang_xie_yin = False
        if shishang_count > 0 and mother_star > 0:
            if shishang_count >= mother_star * 1.5:  # 食伤数量超过印星1.5倍
                shishang_xie_yin = True
        
        # ✅ 新增：综合判断母亲健康
        mother_health = ''
        mother_health_detail = ''
        if mother_star == 0:
            mother_health = '母缘较淡或不在'
            mother_health_detail = '正印不显，母缘较淡，可能早年与母亲分离或缘分较浅'
        elif mother_in_month and mother_has_root:
            if not caixing_hua_yin and not shishang_xie_yin:
                mother_health = '健康长寿'
                mother_health_detail = '正印得令有根，且不受财星坏印、食伤泄印，母亲身体健康，能长寿，贤惠顾家'
            elif caixing_hua_yin:
                mother_health = '亚健康，需注意'
                mother_health_detail = '正印得令有根，但财星坏印，母亲可能因操劳过度而身体欠佳，需注意保养'
            else:
                mother_health = '体弱，需注意'
                mother_health_detail = '正印得令有根，但食伤泄印，母亲可能因过度为子女操心而体弱，需注意休息'
        elif mother_has_root:
            if not caixing_hua_yin:
                mother_health = '基本健康'
                mother_health_detail = '正印有根但不得令，母亲基本健康，但不如得令时强壮'
            else:
                mother_health = '体弱'
                mother_health_detail = '正印有根但不得令，且受财星坏印，母亲身体较弱，需多关心'
        elif mother_star > 0:
            mother_health = '体质偏弱'
            mother_health_detail = '正印无根或根气不足，母亲体质偏弱，需加强保养'
        
        # ❌ 删除：继母判断功能
        # 理论依据不足：《渊海子平》"正印正母；偏印偏母及祖父也"
        # 偏印本身就代表偏母或祖父，不是"偏印盖正印"就是继母
        # 因此删除此判断功能
        
        mother_analysis = {
            'count': mother_star,
            'assessment': '母缘尚可，得母亲或母系长辈关爱较多' if mother_star > 0 else '母缘一般',
            'position': '月柱为母' if mother_star > 0 else '正印不显',
            'health': mother_health,  # ✅ 新增
            'health_detail': mother_health_detail,  # ✅ 新增
            'in_month': mother_in_month,  # ✅ 新增：是否得令
            'has_root': mother_has_root,  # ✅ 新增：是否有根
            'caixing_hua_yin': caixing_hua_yin,  # ✅ 新增：财星坏印
            'shishang_xie_yin': shishang_xie_yin  # ✅ 新增：食伤泄印
            # ❌ 删除：is_stepmother（继母判断功能已删除）
        }
        
        # 3. 兄弟姐妹分析（比肩劫财）- ✅ 修复：确保总数与详细列表一致
        from ..core.constants import TIANGAN_YINYANG

        # ✅ 修复：不再使用ten_god_count中的总数，而是通过详细列表计算总数
        # 这样可以确保总数与详细列表一致

        # ✅ 新增：识别兄弟姐妹的性别（基于比肩劫财的天干阴阳）
        sibling_list = []
        bijian_total_weight = 0.0  # ✅ 新增：比肩总权重
        jiecai_total_weight = 0.0  # ✅ 新增：劫财总权重

        for pos, (gan, zhi) in pillars.items():
            tg = get_ten_god(day_master, gan)
            if tg == '比肩':
                # 比肩：与日主同阴阳，同性（男命为兄，女命为姐）
                sibling_gender = '男' if is_male else '女'
                sibling_type = '兄' if is_male else '姐'
                sibling_list.append({
                    'type': sibling_type,
                    'gender': sibling_gender,
                    'position': pos,
                    'gan': gan,
                    'ten_god': '比肩',
                    'weight': 1.0  # ✅ 新增：透干权重为1.0
                })
                bijian_total_weight += 1.0  # ✅ 新增：累加权重
            elif tg == '劫财':
                # 劫财：与日主异阴阳，异性（男命为妹，女命为弟）
                sibling_gender = '女' if is_male else '男'
                sibling_type = '妹' if is_male else '弟'
                sibling_list.append({
                    'type': sibling_type,
                    'gender': sibling_gender,
                    'position': pos,
                    'gan': gan,
                    'ten_god': '劫财',
                    'weight': 1.0  # ✅ 新增：透干权重为1.0
                })
                jiecai_total_weight += 1.0  # ✅ 新增：累加权重

            # 检查藏干中的比肩劫财
            for canggan, w in DIZHI_CANGGAN.get(zhi, []):
                if w >= 0.3:  # 只统计权重>=0.3的藏干
                    cg_tg = get_ten_god(day_master, canggan)
                    if cg_tg == '比肩':
                        sibling_gender = '男' if is_male else '女'
                        sibling_type = '兄' if is_male else '姐'
                        sibling_list.append({
                            'type': sibling_type,
                            'gender': sibling_gender,
                            'position': pos,
                            'gan': canggan,
                            'ten_god': '比肩',
                            'hidden': True,
                            'weight': w  # ✅ 新增：藏干权重
                        })
                        bijian_total_weight += w  # ✅ 新增：累加权重
                    elif cg_tg == '劫财':
                        sibling_gender = '女' if is_male else '男'
                        sibling_type = '妹' if is_male else '弟'
                        sibling_list.append({
                            'type': sibling_type,
                            'gender': sibling_gender,
                            'position': pos,
                            'gan': canggan,
                            'ten_god': '劫财',
                            'hidden': True,
                            'weight': w  # ✅ 新增：藏干权重
                        })
                        jiecai_total_weight += w  # ✅ 新增：累加权重

        # ✅ 修复：使用详细列表计算的总权重，确保与列表一致
        bijian_count = bijian_total_weight
        jiecai_count = jiecai_total_weight
        sibling_stars = bijian_count + jiecai_count
        
        # ✅ 新增：判断兄弟姐妹能力（基于是否有根气）
        sibling_abilities = []
        for sibling in sibling_list:
            # 检查该比肩劫财是否有根气
            has_root = False
            gan = sibling['gan']
            gan_wx = get_wuxing_by_tiangan(gan)
            for pos_check, (gan_check, zhi_check) in pillars.items():
                # 检查天干
                if gan_check == gan:
                    has_root = True
                    break
                # 检查地支藏干（权重>=0.5）
                for canggan_check, w_check in DIZHI_CANGGAN.get(zhi_check, []):
                    if canggan_check == gan and w_check >= 0.5:
                        has_root = True
                        break
            
            if has_root:
                ability = '能力强，能提供帮助'
            else:
                ability = '能力一般，需互相扶持'
            sibling['ability'] = ability
            sibling_abilities.append(ability)
        
        sibling_analysis = {
            'count': sibling_stars,
            'bijian_count': bijian_count,
            'jiecai_count': jiecai_count,
            'assessment': f'兄弟姐妹缘分{"较多" if sibling_stars >= 2 else "一般" if sibling_stars >= 1 else "较少"}',
            'relationship': '和睦' if sibling_stars > 0 and sibling_stars <= 2 else '一般' if sibling_stars == 0 else '需注意关系',
            'siblings': sibling_list,  # ✅ 新增：详细列表
            'abilities': sibling_abilities  # ✅ 新增：能力评估列表
        }
        
        # 4. 子女分析（食伤）- ✅ 增强：前程与数量预测
        shishen_count = ten_god_count.get('食神', 0)
        shangguan_count = ten_god_count.get('伤官', 0)
        children_stars = shishen_count + shangguan_count
        
        # ✅ 新增：判断食伤是否在时柱（子女宫）
        hour_gan = pillars['hour'][0]
        hour_tg = get_ten_god(day_master, hour_gan)
        children_in_hour = hour_tg in ['食神', '伤官']
        
        # ✅ 新增：判断食伤是否有根气
        children_has_root = False
        for pos, (gan, zhi) in pillars.items():
            if pos == 'hour':
                # 时支藏干中的食伤（权重>=0.3）
                for canggan, w in DIZHI_CANGGAN.get(zhi, []):
                    if get_ten_god(day_master, canggan) in ['食神', '伤官'] and w >= 0.3:
                        children_has_root = True
                        break
            # 其他地支藏干中的食伤（权重>=0.5）
            for canggan, w in DIZHI_CANGGAN.get(zhi, []):
                if get_ten_god(day_master, canggan) in ['食神', '伤官'] and w >= 0.5:
                    children_has_root = True
                    break
        
        # ✅ 新增：综合判断子女数量（考虑身强身弱）
        is_strong = strength in ['身旺', '身强']
        quantity_prediction = ''
        if children_stars == 0:
            quantity_prediction = '无子或难生（需看大运流年引动食伤）'
        elif children_stars == 1:
            quantity_prediction = '1-2个子女（食伤数量较少）'
        elif children_stars == 2:
            quantity_prediction = '2-3个子女（食伤数量适中）'
        elif children_stars >= 3:
            if is_strong:
                quantity_prediction = '3个以上子女（食伤多且身强，能胜任）'
            else:
                quantity_prediction = '2-3个子女（食伤多但身弱，需注意）'
        
        # ✅ 新增：子女前程预测（基于食伤强弱和位置）
        children_future = ''
        children_future_detail = ''
        if children_stars == 0:
            children_future = '子女缘分较淡'
            children_future_detail = '命局无食伤，子女缘分较淡，需大运流年引动食伤方能得子'
        elif children_in_hour and children_has_root:
            if shishen_count > shangguan_count:
                children_future = '子女有福，前程较好'
                children_future_detail = '食神在时柱有根，子女有福气，性格温和，前程较好，能得子女孝顺'
            elif shangguan_count > shishen_count:
                children_future = '子女聪慧，但需引导'
                children_future_detail = '伤官在时柱有根，子女聪慧但性格较强，需适当引导，前程取决于教育'
            else:
                children_future = '子女前程一般'
                children_future_detail = '食伤在时柱有根，子女基本正常，前程需看后天培养'
        elif children_has_root:
            children_future = '子女前程尚可'
            children_future_detail = '食伤有根但不在时柱，子女前程尚可，但不如在时柱时理想'
        elif children_stars > 0:
            children_future = '子女前程一般'
            children_future_detail = '食伤无根或根气不足，子女前程一般，需加强教育培养'
        
        children_analysis = {
            'count': children_stars,
            'shishen_count': shishen_count,
            'shangguan_count': shangguan_count,
            'assessment': f'子女缘分{"较好" if children_stars >= 1 else "一般"}',
            'hour_pillar': pillars['hour'][1],  # 时支为子女宫
            'quantity_prediction': quantity_prediction,  # ✅ 增强
            'future': children_future,  # ✅ 新增：前程
            'future_detail': children_future_detail,  # ✅ 新增：前程详情
            'in_hour': children_in_hour,  # ✅ 新增：是否在时柱
            'has_root': children_has_root  # ✅ 新增：是否有根
        }
        
        # 5. 六亲关系分析（基于《渊海子平》六亲关系理论）
        sixqin_relationship = self._analyze_sixqin_relationship(
            father_star, mother_star, sibling_stars, children_stars, ten_god_count
        )
        
        # 6. 六亲助力分析（基于十神强弱和位置）
        sixqin_help = self._analyze_sixqin_help(
            father_star, mother_star, sibling_stars, children_stars, pillars
        )
        
        # 7. 需要注意的年份（基于大运流年理论）
        # ✅ 修复：使用传入的birth_year参数
        important_years = self._analyze_sixqin_important_years(
            father_star, mother_star, children_stars, ten_god_count,
            day_master=day_master, gender=gender, birth_year=birth_year  # ✅ 修复：传递birth_year参数
        )
        
        # 8. 六亲建议（综合建议）
        sixqin_advice = self._generate_sixqin_advice(
            father_analysis, mother_analysis, sibling_analysis, children_analysis
        )
        
        # 🔥 新增：深度解释机制（基于实际六亲星、十神等参数动态生成）
        try:
            deep_explanation = self._generate_sixqin_deep_explanation(
                father_analysis, mother_analysis, sibling_analysis, children_analysis,
                sixqin_relationship, sixqin_help, is_male, day_master, ten_god_count
            )
        except Exception as e:
            print(f"⚠️ 生成六亲深度解释失败: {e}")
            deep_explanation = "六亲分析较为常规，无明显特殊机制需要深度解读。"
        
        # 🔥 新增：人生策略建议（基于实际六亲状况动态生成）
        try:
            life_strategy = self._generate_sixqin_life_strategy(
                father_analysis, mother_analysis, sibling_analysis, children_analysis,
                sixqin_help, is_male
            )
        except Exception as e:
            print(f"⚠️ 生成六亲人生策略失败: {e}")
            life_strategy = {
                'sixqin_password': '保持开放心态，主动沟通，理解六亲',
                'relationship_direction': '保持和谐的六亲关系',
                'communication_advice': '保持开放心态，主动沟通，理解六亲，维护和谐的六亲关系',
                'key_points': ['保持开放心态，主动沟通，理解六亲，维护和谐的六亲关系']
            }
        
        # ✅ 新增：六亲宫位详细分析（年柱、月柱、时柱）
        palace_analysis = self._analyze_sixqin_palaces(
            pillars, day_master, ten_god_count, is_male
        )
        
        return {
            'father': father_analysis,
            'mother': mother_analysis,
            'siblings': sibling_analysis,
            'children': children_analysis,
            'relationship': sixqin_relationship,
            'help': sixqin_help,
            'important_years': important_years,
            'advice': sixqin_advice,
            'deep_explanation': deep_explanation,  # 🔥 新增：深度解释
            'life_strategy': life_strategy,  # 🔥 新增：人生策略
            'palace_analysis': palace_analysis  # ✅ 新增：六亲宫位详细分析
        }
    
    def _analyze_sixqin_palaces(self, pillars: Dict, day_master: str,
                                ten_god_count: Dict[str, float], is_male: bool) -> Dict:
        """
        六亲宫位详细分析 - 基于《渊海子平·六亲章》
        年柱：父母宫（父亲为主）
        月柱：兄弟宫（兄弟姐妹、母亲为主）
        时柱：子女宫（子女为主）
        """
        palace_details = {}
        
        # 年柱分析（父母宫）
        year_gan, year_zhi = pillars['year']
        year_tg = get_ten_god(day_master, year_gan)
        # 检查年支藏干
        year_zhi_canggans = []
        for canggan, w in DIZHI_CANGGAN.get(year_zhi, []):
            if w >= 0.3:
                cg_tg = get_ten_god(day_master, canggan)
                year_zhi_canggans.append({
                    'gan': canggan,
                    'ten_god': cg_tg,
                    'weight': w
                })
        
        palace_details['year'] = {
            'ganzhi': f'{year_gan}{year_zhi}',
            'gan': year_gan,
            'zhi': year_zhi,
            'gan_ten_god': year_tg,
            'zhi_canggans': year_zhi_canggans,
            'palace_name': '父母宫',
            'main_role': '父亲（年柱为父）',
            'description': f'年柱{year_gan}{year_zhi}为父母宫，年干{year_gan}为{year_tg}，主父亲。'
        }
        
        # 月柱分析（兄弟宫，也主母亲）
        month_gan, month_zhi = pillars['month']
        month_tg = get_ten_god(day_master, month_gan)
        # 检查月支藏干
        month_zhi_canggans = []
        for canggan, w in DIZHI_CANGGAN.get(month_zhi, []):
            if w >= 0.3:
                cg_tg = get_ten_god(day_master, canggan)
                month_zhi_canggans.append({
                    'gan': canggan,
                    'ten_god': cg_tg,
                    'weight': w
                })
        
        palace_details['month'] = {
            'ganzhi': f'{month_gan}{month_zhi}',
            'gan': month_gan,
            'zhi': month_zhi,
            'gan_ten_god': month_tg,
            'zhi_canggans': month_zhi_canggans,
            'palace_name': '兄弟宫（月令）',
            'main_role': '母亲（月柱为母，月令最重）、兄弟姐妹',
            'description': f'月柱{month_gan}{month_zhi}为兄弟宫（月令），月干{month_gan}为{month_tg}，主母亲和兄弟姐妹，月令最重。'
        }
        
        # 时柱分析（子女宫）
        hour_gan, hour_zhi = pillars['hour']
        hour_tg = get_ten_god(day_master, hour_gan)
        # 检查时支藏干
        hour_zhi_canggans = []
        for canggan, w in DIZHI_CANGGAN.get(hour_zhi, []):
            if w >= 0.3:
                cg_tg = get_ten_god(day_master, canggan)
                hour_zhi_canggans.append({
                    'gan': canggan,
                    'ten_god': cg_tg,
                    'weight': w
                })
        
        palace_details['hour'] = {
            'ganzhi': f'{hour_gan}{hour_zhi}',
            'gan': hour_gan,
            'zhi': hour_zhi,
            'gan_ten_god': hour_tg,
            'zhi_canggans': hour_zhi_canggans,
            'palace_name': '子女宫',
            'main_role': '子女（时柱为子女）',
            'description': f'时柱{hour_gan}{hour_zhi}为子女宫，时干{hour_gan}为{hour_tg}，主子女。'
        }
        
        return {
            'year_palace': palace_details['year'],
            'month_palace': palace_details['month'],
            'hour_palace': palace_details['hour'],
            'summary': f'年柱{year_gan}{year_zhi}为父母宫，月柱{month_gan}{month_zhi}为兄弟宫（月令），时柱{hour_gan}{hour_zhi}为子女宫'
        }
    
    def _analyze_sixqin_relationship(self, father_star: float, mother_star: float,
                                     sibling_stars: float, children_stars: float,
                                     ten_god_count: Dict[str, float]) -> Dict:
        """分析六亲关系 - 基于《渊海子平·六亲章》"""
        relationships = []
        
        # 父母关系
        if father_star > 0 and mother_star > 0:
            relationships.append('父母关系：和谐，相互扶持')
        elif father_star == 0 and mother_star > 0:
            relationships.append('父母关系：母系为主，父缘较淡')
        elif father_star > 0 and mother_star == 0:
            relationships.append('父母关系：父系为主，母缘较淡')
        else:
            relationships.append('父母关系：六亲星不显，需看大运流年')
        
        # 兄弟姐妹关系
        if sibling_stars >= 2:
            relationships.append('兄弟姐妹关系：人多，需注意和睦')
        elif sibling_stars == 1:
            relationships.append('兄弟姐妹关系：一般，较少往来')
        else:
            relationships.append('兄弟姐妹关系：较少，多为独生子女或较少兄弟姐妹')
        
        # 与子女关系
        if children_stars >= 2:
            relationships.append('与子女关系：子女较多，需注意教育')
        elif children_stars == 1:
            relationships.append('与子女关系：一般，需加强沟通')
        else:
            relationships.append('与子女关系：需看大运流年，可能较晚得子')
        
        return {
            'summary': '；'.join(relationships),
            'details': relationships
        }
    
    def _analyze_sixqin_help(self, father_star: float, mother_star: float,
                            sibling_stars: float, children_stars: float,
                            pillars: Dict) -> Dict:
        """分析六亲助力 - 基于《三命通会·六亲论》"""
        help_items = []
        
        # 父母助力
        if father_star > 0 or mother_star > 0:
            if mother_star > father_star:
                help_items.append('母系助力较强')
            elif father_star > mother_star:
                help_items.append('父系助力较强')
            else:
                help_items.append('父母双方助力均衡')
        else:
            help_items.append('六亲助力较弱，需靠自己努力')
        
        # 兄弟姐妹助力
        if sibling_stars > 0:
            help_items.append('兄弟姐妹可提供一定帮助')
        else:
            help_items.append('兄弟姐妹助力较少')
        
        # 子女助力
        if children_stars > 0:
            help_items.append('子女有助，晚年可得子女照顾')
        else:
            help_items.append('子女助力需看大运流年')
        
        return {
            'summary': '、'.join(help_items),
            'level': '强' if (father_star + mother_star + sibling_stars) >= 3 else 
                    '中等' if (father_star + mother_star + sibling_stars) >= 1 else '弱'
        }
    
    def _analyze_sixqin_important_years(self, father_star: float, mother_star: float,
                                       children_stars: float, ten_god_count: Dict[str, float],
                                       day_master: str = '', gender: str = '男', birth_year: int = None) -> Dict[str, Any]:
        """
        分析需要注意的年份 - 基于《三命通会·大运流年论》
        ✅ 增强：计算具体年份（类似婚姻应期）
        ✅ 修复：添加birth_year参数，确保计算年龄
        """
        important_years_text = []
        important_years_detail = {}  # ✅ 新增：具体年份详情，格式：{'类型': [年份列表]}
        
        # 父星不显时，大运流年逢偏财（男命）或正官（女命）需注意
        if father_star == 0:
            important_years_text.append('大运流年逢父星（偏财/正官）时，需注意父亲健康或关系变化')
            # ✅ 新增：计算父星年份
            # ✅ 修复：传入birth_year参数，确保计算年龄
            if day_master and gender:
                is_male = gender == '男'
                if is_male:
                    # 男命：偏财为父
                    father_star_ganzhi = self._calculate_ten_god_years(day_master, '偏财', birth_year=birth_year, years_ahead=20)
                else:
                    # 女命：正官为父
                    father_star_ganzhi = self._calculate_ten_god_years(day_master, '正官', birth_year=birth_year, years_ahead=20)
                if father_star_ganzhi:
                    important_years_detail['父星年份'] = father_star_ganzhi
        
        # 母星不显时，大运流年逢正印需注意
        if mother_star == 0:
            important_years_text.append('大运流年逢正印时，需注意母亲健康或关系变化')
            # ✅ 新增：计算正印年份
            # ✅ 修复：传入birth_year参数，确保计算年龄
            if day_master:
                yin_years = self._calculate_ten_god_years(day_master, '正印', birth_year=birth_year, years_ahead=20)
                if yin_years:
                    important_years_detail['正印年份'] = yin_years
        
        # 子女星不显时，大运流年逢食伤需注意
        if children_stars == 0:
            important_years_text.append('大运流年逢食伤时，可能有机会得子，需把握时机')
            # ✅ 新增：计算食伤年份
            # ✅ 修复：传入birth_year参数，确保计算年龄
            if day_master:
                shishang_years = self._calculate_ten_god_years(day_master, ['食神', '伤官'], birth_year=birth_year, years_ahead=20)
                if shishang_years:
                    important_years_detail['食伤年份'] = shishang_years
        
        # 比劫被克时，需注意兄弟姐妹
        if ten_god_count.get('比肩', 0) > 0 or ten_god_count.get('劫财', 0) > 0:
            important_years_text.append('大运流年逢官杀（克比劫）时，需注意兄弟姐妹关系或健康')
            # ✅ 新增：计算官杀年份
            # ✅ 修复：传入birth_year参数，确保计算年龄
            if day_master:
                guansha_years = self._calculate_ten_god_years(day_master, ['正官', '七杀', '偏官'], birth_year=birth_year, years_ahead=20)
                if guansha_years:
                    important_years_detail['官杀年份'] = guansha_years
        
        return {
            'text': important_years_text if important_years_text else ['六亲关系相对稳定，按常规年份关注即可'],
            'detail': important_years_detail  # ✅ 新增：具体年份详情
        }
    
    def _calculate_ten_god_years(self, day_master: str, ten_god_names: Union[List[str], str], 
                                 birth_year: int = None, years_ahead: int = 80) -> List[Dict]:
        """
        计算十神年份（根据十神名称计算具体公历年份）
        ✅ 修复：添加birth_year参数并计算年龄字段
        
        Args:
            day_master: 日主天干
            ten_god_names: 十神名称（可以是单个字符串或列表）
            birth_year: 出生年份（必须提供，用于计算年龄）
            years_ahead: 从出生年份往后计算多少年（默认80年，覆盖完整人生周期）
        
        Returns:
            十神年份列表，每个元素包含：year, ganzhi, gan, zhi, ten_god, age, source, description
        """
        from datetime import datetime
        from ..core.constants import TIANGAN_LIST, DIZHI_LIST, DIZHI_CANGGAN
        from ..core.utils import get_ten_god
        
        # ✅ 修复：必须有出生年份才能计算年龄，否则使用当前年份（向后兼容）
        if birth_year and birth_year > 1900:
            start_year = birth_year
            calculate_age = True
            # ✅ 修复：确保birth_year有效，用于年龄计算
            valid_birth_year = birth_year
        else:
            # 降级：如果没有出生年份，使用当前年份（向后兼容）
            start_year = datetime.now().year
            calculate_age = False
            valid_birth_year = None
        
        # 统一为列表
        if isinstance(ten_god_names, str):
            ten_god_names = [ten_god_names]
        
        ten_god_years = []
        
        # 年份转干支函数（使用1984年甲子年作为基准）
        def year_to_ganzhi(year: int) -> tuple:
            offset = year - 1984  # 1984年是甲子年
            gan = TIANGAN_LIST[offset % 10]
            zhi = DIZHI_LIST[offset % 12]
            return gan, zhi
        
        for i in range(years_ahead):
            year = start_year + i  # ✅ 修复：从出生年份（或当前年份）开始计算
            # ✅ 修复：确保正确计算年龄，即使birth_year参数可能为None，也要使用valid_birth_year
            if calculate_age and valid_birth_year:
                age = year - valid_birth_year
            else:
                age = 0  # 如果没有有效的出生年份，显示0岁
            gan, zhi = year_to_ganzhi(year)
            
            # 检查天干的十神
            gan_tg = get_ten_god(day_master, gan)
            if gan_tg in ten_god_names:
                ten_god_years.append({
                    'year': year,
                    'ganzhi': f"{gan}{zhi}",
                    'gan': gan,
                    'zhi': zhi,
                    'ten_god': gan_tg,
                    'source': '天干',
                    'age': age,  # ✅ 修复：添加年龄字段
                    'description': f'{year}年（{gan}{zhi}年，{age}岁，{gan_tg}透干）' if calculate_age else f'{year}年（{gan}{zhi}年，{gan_tg}透干）'
                })
            
            # 检查地支藏干中的十神（只检查本气和中气，权重>=0.2）
            for canggan, weight in DIZHI_CANGGAN.get(zhi, []):
                if weight >= 0.2:  # 只检查本气和中气
                    cg_tg = get_ten_god(day_master, canggan)
                    if cg_tg in ten_god_names:
                        # 去重：如果天干已经是这个十神，跳过
                        if not any(y['year'] == year and y['ten_god'] == cg_tg for y in ten_god_years):
                            ten_god_years.append({
                                'year': year,
                                'ganzhi': f"{gan}{zhi}",
                                'gan': gan,
                                'zhi': zhi,
                                'ten_god': cg_tg,
                                'source': f'{zhi}中藏{canggan}',
                                'age': age,  # ✅ 修复：添加年龄字段
                                'description': f'{year}年（{gan}{zhi}年，{age}岁，{zhi}中藏{canggan}为{cg_tg}）' if calculate_age else f'{year}年（{gan}{zhi}年，{zhi}中藏{canggan}为{cg_tg}）'
                            })
        
        return ten_god_years
    
    def _generate_sixqin_deep_explanation(self, father_analysis: Dict, mother_analysis: Dict,
                                         sibling_analysis: Dict, children_analysis: Dict,
                                         sixqin_relationship: Dict, sixqin_help: Dict,
                                         is_male: bool, day_master: str,
                                         ten_god_count: Dict[str, float]) -> str:
        """
        生成六亲深度解释 - 基于实际六亲星、十神等参数动态生成
        
        理论依据：
        - 《渊海子平·六亲章》：六亲星的作用机制
        - 《三命通会·六亲论》：六亲关系的形成机制
        """
        explanations = []
        
        # 1. 六亲星机制详解（基于实际数量）
        father_star = father_analysis.get('count', 0)
        mother_star = mother_analysis.get('count', 0)
        sibling_stars = sibling_analysis.get('count', 0)
        children_stars = children_analysis.get('count', 0)
        
        father_star_name = '偏财' if is_male else '正官'
        if father_star == 0:
            explanations.append(
                f"父缘机制：父星（{father_star_name}）不显（数量{father_star:.1f}）。" +
                f"根据《渊海子平·六亲章》，{'男命偏财为父' if is_male else '女命正官为父'}，" +
                f"父星不显意味着父缘助力较弱，需通过大运流年引动父星方能得父助。"
            )
        else:
            explanations.append(
                f"父缘机制：父星（{father_star_name}）有力（数量{father_star:.1f}）。" +
                f"根据《渊海子平·六亲章》，父星有力意味着父缘助力较强，" +
                f"容易得到父亲的帮助和支持。"
            )
        
        mother_star_name = '正印'
        if mother_star == 0:
            explanations.append(
                f"母缘机制：母星（{mother_star_name}）不显（数量{mother_star:.1f}）。" +
                f"根据《渊海子平·六亲章》，正印为母，母星不显意味着母缘助力较弱，" +
                f"需通过大运流年引动母星方能得母助。"
            )
        else:
            explanations.append(
                f"母缘机制：母星（{mother_star_name}）有力（数量{mother_star:.1f}）。" +
                f"根据《渊海子平·六亲章》，母星有力意味着母缘助力较强，" +
                f"容易得到母亲的帮助和支持。"
            )
        
        if sibling_stars == 0:
            explanations.append(
                f"兄弟姐妹机制：比劫不显（数量{sibling_stars:.1f}）。" +
                f"根据《渊海子平·六亲章》，比劫为兄弟姐妹，不显意味着兄弟姐妹助力较少，" +
                f"多为独生子女或较少兄弟姐妹。"
            )
        else:
            explanations.append(
                f"兄弟姐妹机制：比劫有力（数量{sibling_stars:.1f}）。" +
                f"根据《渊海子平·六亲章》，比劫有力意味着兄弟姐妹较多，" +
                f"可提供一定帮助，但需注意和睦相处。"
            )
        
        if children_stars == 0:
            explanations.append(
                f"子女机制：食伤不显（数量{children_stars:.1f}）。" +
                f"根据《渊海子平·六亲章》，食伤为子女，不显意味着子女助力需看大运流年，" +
                f"可能较晚得子，或子女助力较弱。"
            )
        else:
            explanations.append(
                f"子女机制：食伤有力（数量{children_stars:.1f}）。" +
                f"根据《渊海子平·六亲章》，食伤有力意味着子女较多，" +
                f"有助，晚年可得子女照顾，但需注意教育。"
            )
        
        # 2. 六亲关系机制详解（基于实际关系分析）
        if sixqin_relationship:
            relationship_summary = sixqin_relationship.get('summary', '')
            if relationship_summary:
                explanations.append(
                    f"六亲关系机制：{relationship_summary}。" +
                    f"根据《渊海子平·六亲章》，六亲关系主要看六亲星的力量和位置，" +
                    f"力量强则关系好，力量弱则关系一般。"
                )
        
        # 3. 六亲助力机制详解（基于实际助力分析）
        if sixqin_help:
            help_level = sixqin_help.get('level', '')
            help_summary = sixqin_help.get('summary', '')
            if help_level and help_summary:
                explanations.append(
                    f"六亲助力机制：六亲助力{help_level}（{help_summary}）。" +
                    f"根据《三命通会·六亲论》，六亲助力主要看六亲星的总和，" +
                    f"总和大于等于3则助力强，大于等于1则助力中等，小于1则助力弱。"
                )
        
        if not explanations:
            return "六亲分析较为常规，无明显特殊机制需要深度解读。"
        
        return "。".join(explanations) + "。"
    
    def _generate_sixqin_life_strategy(self, father_analysis: Dict, mother_analysis: Dict,
                                       sibling_analysis: Dict, children_analysis: Dict,
                                       sixqin_help: Dict, is_male: bool) -> Dict[str, str]:
        """
        生成六亲人生策略建议 - 基于实际六亲状况动态生成
        
        理论依据：
        - 《渊海子平·六亲章》：不同六亲状况的相处建议
        - 《三命通会·六亲论》：六亲助力分析
        """
        strategy = {
            'sixqin_password': '',  # 六亲密码
            'relationship_direction': '',  # 相处方向
            'communication_advice': '',  # 沟通建议
            'key_points': []  # 关键要点
        }
        
        # 1. 六亲密码（基于实际六亲星）
        father_star = father_analysis.get('count', 0)
        mother_star = mother_analysis.get('count', 0)
        sibling_stars = sibling_analysis.get('count', 0)
        children_stars = children_analysis.get('count', 0)
        total_sixqin = father_star + mother_star + sibling_stars + children_stars
        
        if total_sixqin >= 3:
            strategy['sixqin_password'] = (
                f"您的六亲关键在于「善用助力」。" +
                f"六亲星总和{total_sixqin:.1f}，助力较强。" +
                f"需善用六亲助力，但也要注意和睦相处，避免因助力过多而依赖。"
            )
        elif total_sixqin >= 1:
            strategy['sixqin_password'] = (
                f"您的六亲关键在于「平衡相处」。" +
                f"六亲星总和{total_sixqin:.1f}，助力中等。" +
                f"需平衡六亲关系，既要借助六亲助力，也要靠自己努力。"
            )
        else:
            strategy['sixqin_password'] = (
                f"您的六亲关键在于「自强自立」。" +
                f"六亲星总和{total_sixqin:.1f}，助力较弱。" +
                f"需自强自立，不依赖六亲助力，通过自己的努力获得成功。"
            )
        
        # 2. 相处方向（基于实际六亲状况）
        direction_items = []
        
        if father_star == 0:
            direction_items.append("父星不显，父缘助力较弱，需靠自己努力，不依赖父助")
        elif father_star >= 1.0:
            direction_items.append(f"父星有力（数量{father_star:.1f}），容易得到父亲的帮助和支持，需善用父助")
        
        if mother_star == 0:
            direction_items.append("母星不显，母缘助力较弱，需靠自己努力，不依赖母助")
        elif mother_star >= 1.0:
            direction_items.append(f"母星有力（数量{mother_star:.1f}），容易得到母亲的帮助和支持，需善用母助")
        
        if sibling_stars == 0:
            direction_items.append("比劫不显，兄弟姐妹助力较少，多为独生子女，需靠自己努力")
        elif sibling_stars >= 2:
            direction_items.append(f"比劫有力（数量{sibling_stars:.1f}），兄弟姐妹较多，需注意和睦相处")
        else:
            direction_items.append(f"比劫一般（数量{sibling_stars:.1f}），兄弟姐妹较少，需加强沟通")
        
        if children_stars == 0:
            direction_items.append("食伤不显，子女助力需看大运流年，可能较晚得子")
        elif children_stars >= 2:
            direction_items.append(f"食伤有力（数量{children_stars:.1f}），子女较多，需注意教育")
        else:
            direction_items.append(f"食伤一般（数量{children_stars:.1f}），子女较少，需加强沟通")
        
        strategy['relationship_direction'] = "；".join(direction_items) + "。"
        
        # 3. 沟通建议（基于实际六亲关系）
        communication_items = []
        
        if father_star == 0 and mother_star == 0:
            communication_items.append("父母星都不显，需加强与父母的沟通，改善关系")
        elif father_star > mother_star:
            communication_items.append("父星强于母星，需加强与母亲的沟通，平衡父母关系")
        elif mother_star > father_star:
            communication_items.append("母星强于父星，需加强与父亲的沟通，平衡父母关系")
        
        if sibling_stars >= 2:
            communication_items.append("兄弟姐妹较多，需注意和睦相处，加强沟通")
        elif sibling_stars == 0:
            communication_items.append("兄弟姐妹较少，需加强与朋友和同事的沟通，建立良好的人际关系")
        
        if children_stars >= 2:
            communication_items.append("子女较多，需注意教育，加强沟通，建立良好的亲子关系")
        elif children_stars == 0:
            communication_items.append("子女较少或较晚得子，需耐心等待，在大运流年有利时加强沟通")
        
        if not communication_items:
            communication_items.append("保持开放心态，主动沟通，理解六亲，维护和谐的六亲关系")
        
        strategy['communication_advice'] = "；".join(communication_items) + "。"
        
        # 4. 关键要点（基于实际六亲状况）
        if father_star == 0:
            strategy['key_points'].append("父星不显，需靠自己努力，不依赖父助")
        if mother_star == 0:
            strategy['key_points'].append("母星不显，需靠自己努力，不依赖母助")
        if sibling_stars == 0:
            strategy['key_points'].append("比劫不显，兄弟姐妹助力较少，需靠自己努力")
        if children_stars == 0:
            strategy['key_points'].append("食伤不显，子女助力需看大运流年")
        
        if sixqin_help.get('level') == '弱':
            strategy['key_points'].append("六亲助力较弱，需自强自立，不依赖六亲助力")
        elif sixqin_help.get('level') == '强':
            strategy['key_points'].append("六亲助力较强，需善用助力，但也要注意和睦相处")
        
        if not strategy['key_points']:
            strategy['key_points'].append("保持开放心态，主动沟通，理解六亲，维护和谐的六亲关系")
        
        return strategy
    
    def _generate_sixqin_advice(self, father_analysis: Dict, mother_analysis: Dict,
                                sibling_analysis: Dict, children_analysis: Dict) -> str:
        """生成六亲建议 - 基于《渊海子平》理论"""
        advice_list = []
        
        # 父母建议
        if father_analysis['count'] > 0 or mother_analysis['count'] > 0:
            advice_list.append('与父母保持良好沟通，孝敬父母')
        else:
            advice_list.append('六亲星不显，需通过后天努力改善关系')
        
        # 兄弟姐妹建议
        if sibling_analysis['count'] > 0:
            if sibling_analysis['count'] >= 2:
                advice_list.append('兄弟姐妹较多，需注意和睦相处，避免因财产产生纷争')
            else:
                advice_list.append('珍惜兄弟姐妹情谊，相互扶持')
        
        # 子女建议
        if children_analysis['count'] > 0:
            advice_list.append('重视子女教育，加强陪伴，培养良好亲子关系')
        else:
            advice_list.append('子女缘分需看大运流年，可在大运流年逢食伤时把握机会')
        
        return '；'.join(advice_list)
    
    def _analyze_health_comprehensive(self, day_master: str, pillars: Dict,
                                     ten_god_count: Dict[str, float]) -> Dict:
        """
        🔥 完整健康分析 - 基于《渊海子平·论疾病》
        
        理论依据：
        - 金：肺、大肠、呼吸道
        - 木：肝、胆
        - 水：肾、膀胱
        - 火：心、小肠
        - 土：脾、胃
        
        分析项目（10项）：
        1. 五行与脏腑对应
        2. 五行失衡分析
        3. 十神过旺过弱的影响
        4. 健康隐患识别
        5. 需要注意的器官
        6. 健康时机分析
        7. 健康建议
        8. 饮食建议
        9. 养生方式
        10. 需要注意的年份
        """
        dm_wx = get_wuxing_by_tiangan(day_master)
        day_zhi = pillars['day'][1]
        day_zhi_wx = get_wuxing_by_dizhi(day_zhi)
        
        # 1. 五行与脏腑对应
        organ_map = {
            '金': '肺、大肠、呼吸道',
            '木': '肝、胆',
            '水': '肾、膀胱',
            '火': '心、小肠',
            '土': '脾、胃'
        }
        
        # 2. 健康隐患
        health_risks = []
        if dm_wx == '金':
            health_risks.append(f'日主为{dm_wx}，需注意{organ_map["金"]}的健康')
        if day_zhi_wx == '土':
            health_risks.append(f'日支为{day_zhi}（{day_zhi_wx}），需注意脾胃消化系统')
        
        # 3. 五行失衡分析（包含藏干）
        wuxing_count = {'木': 0.0, '火': 0.0, '土': 0.0, '金': 0.0, '水': 0.0}
        for pos, (gan, zhi) in pillars.items():
            wuxing_count[get_wuxing_by_tiangan(gan)] += 1.0
            wuxing_count[get_wuxing_by_dizhi(zhi)] += 1.0
            # 计入藏干（带权重）
            for canggan, weight in DIZHI_CANGGAN.get(zhi, []):
                canggan_wx = get_wuxing_by_tiangan(canggan)
                wuxing_count[canggan_wx] += float(weight)
        
        max_wx = max(wuxing_count, key=wuxing_count.get)
        min_wx = min(wuxing_count, key=wuxing_count.get)
        total_count = sum(wuxing_count.values())
        
        # 4. 深度健康分析
        # 4.1 土重埋金分析
        tu_mai_jin_analysis = []
        if wuxing_count['土'] >= 3.0 and dm_wx == '金':
            tu_ratio = wuxing_count['土'] / total_count if total_count > 0 else 0
            if tu_ratio >= 0.4:  # 土占比40%以上
                tu_mai_jin_analysis.append({
                    'issue': '土重埋金',
                    'impact': '土多金埋，需防范呼吸不畅、气虚等状况',
                    'systems': ['呼吸系统'],
                    'organs': ['肺', '大肠', '呼吸道'],
                    'suggestion': '宜疏土泄金，多进行呼吸锻炼，避免土重环境'
                })
        
        # 4.2 木弱不堪分析
        mu_ruo_analysis = []
        if wuxing_count['木'] < 1.0:
            mu_ruo_analysis.append({
                'issue': '木极弱',
                'impact': '木弱不堪，代表肝胆功能偏弱，且身体柔韧性不足',
                'systems': ['肝胆系统', '筋骨系统'],
                'organs': ['肝', '胆', '筋骨'],
                'suggestion': '宜补木养肝，多进行伸展运动，注意肝胆养护'
            })
        
        # 4.3 土过旺分析（脾胃系统）
        tu_wang_analysis = []
        if wuxing_count['土'] >= 3.5:
            tu_ratio = wuxing_count['土'] / total_count if total_count > 0 else 0
            if tu_ratio >= 0.45:  # 土占比45%以上
                tu_wang_analysis.append({
                    'issue': '土过旺',
                    'impact': '土过旺，最直接的影响是脾胃、消化系统',
                    'systems': ['脾胃系统', '消化系统'],
                    'organs': ['脾', '胃'],
                    'symptoms': ['腹胀', '消化不良'],
                    'suggestion': '饮食规律，健脾为先，少甜少油'
                })
        
        # 5. 综合健康建议
        health_advice = []
        detailed_advice = []
        
        # 5.1 基础健康建议
        if wuxing_count[max_wx] / total_count >= 0.4:
            health_advice.append(f'{max_wx}过旺，需注意{organ_map[max_wx]}的调理')
        if wuxing_count[min_wx] / total_count < 0.1:
            health_advice.append(f'{min_wx}过弱，需注意{organ_map[min_wx]}的养护')
        
        # 5.2 深度养生建议
        if tu_mai_jin_analysis:
            detailed_advice.append('重点关注"土重埋金"：宜疏土泄金，多进行呼吸锻炼')
        if mu_ruo_analysis:
            detailed_advice.append('木极弱：宜补木养肝，多进行伸展运动，注意肝胆养护')
        if tu_wang_analysis:
            detailed_advice.append('土过旺：养生重在健脾，饮食规律，少甜少油')
        
        # 5.3 综合建议
        if tu_wang_analysis and mu_ruo_analysis:
            detailed_advice.append('养生重在健脾疏肝，饮食规律，并适当进行伸展运动')
        
        # 6. 十神对健康的影响分析（基于《三命通会·论疾病》）
        tengod_health_analysis = []
        if ten_god_count:
            # 印星过重：可能思虑过度，易有脾胃问题
            yin_total = ten_god_count.get('正印', 0) + ten_god_count.get('偏印', 0)
            if yin_total >= 2.0:
                tengod_health_analysis.append({
                    'ten_god': '印星过重',
                    'impact': '印星过重，思虑较多，需注意脾胃消化系统，避免过度思虑',
                    'organs': ['脾', '胃'],
                    'suggestion': '宜放松心情，避免过度思虑，饮食清淡'
                })
            
            # 官杀过旺：压力大，需注意心血管和神经系统
            guansha_total = ten_god_count.get('正官', 0) + ten_god_count.get('七杀', 0)
            if guansha_total >= 1.5:
                tengod_health_analysis.append({
                    'ten_god': '官杀过旺',
                    'impact': '官杀过旺，压力较大，需注意心血管系统和神经系统的健康',
                    'organs': ['心', '血管', '神经'],
                    'suggestion': '宜舒缓压力，保持心情愉悦，注意休息'
                })
            
            # 食伤过旺：容易思虑过度，消耗精神
            shishang_total = ten_god_count.get('食神', 0) + ten_god_count.get('伤官', 0)
            if shishang_total >= 1.5:
                tengod_health_analysis.append({
                    'ten_god': '食伤过旺',
                    'impact': '食伤过旺，思虑较多，容易消耗精神，需注意养心安神',
                    'organs': ['心', '精神'],
                    'suggestion': '宜养心安神，避免过度思考，适当休息'
                })
            
            # 比劫过旺：容易有竞争压力，需注意关节和肌肉
            bijie_total = ten_god_count.get('比肩', 0) + ten_god_count.get('劫财', 0)
            if bijie_total >= 2.0:
                tengod_health_analysis.append({
                    'ten_god': '比劫过旺',
                    'impact': '比劫过旺，竞争压力较大，需注意关节和肌肉的健康',
                    'organs': ['关节', '肌肉'],
                    'suggestion': '宜适度运动，注意关节保护，避免过度竞争'
                })
        
        # 7. 更多五行失衡详细分析
        # 7.1 火过旺分析（心血管系统）
        huo_wang_analysis = []
        if wuxing_count['火'] >= 2.5:
            huo_ratio = wuxing_count['火'] / total_count if total_count > 0 else 0
            if huo_ratio >= 0.35:
                huo_wang_analysis.append({
                    'issue': '火过旺',
                    'impact': '火过旺，易有心血管系统问题，需注意心脏、血液循环',
                    'systems': ['心血管系统'],
                    'organs': ['心', '血管'],
                    'symptoms': ['心悸', '血压偏高'],
                    'suggestion': '宜清淡饮食，控制情绪，避免过劳'
                })
        
        # 7.2 水过弱分析（肾脏系统）
        shui_ruo_analysis = []
        if wuxing_count['水'] < 0.8:
            shui_ruo_analysis.append({
                'issue': '水极弱',
                'impact': '水极弱，代表肾功能偏弱，需注意肾脏和泌尿系统',
                'systems': ['肾脏系统', '泌尿系统'],
                'organs': ['肾', '膀胱'],
                'suggestion': '宜多饮水，注意腰肾保暖，避免过度劳累'
            })
        
        # 7.3 金过弱分析（呼吸系统）
        jin_ruo_analysis = []
        if wuxing_count['金'] < 0.8 and dm_wx == '金':
            jin_ruo_analysis.append({
                'issue': '金极弱',
                'impact': '日主为金但金极弱，呼吸系统功能偏弱，需格外注意',
                'systems': ['呼吸系统'],
                'organs': ['肺', '大肠', '呼吸道'],
                'suggestion': '宜多进行呼吸锻炼，避免烟尘环境，注意保暖'
            })
        
        # 8. 饮食建议（详细）
        diet_advice = []
        # 根据日主五行推荐
        diet_map = {
            '金': '宜食白色食物（白萝卜、梨、银耳）润肺，少辛辣，忌烟酒',
            '木': '宜食绿色食物（青菜、绿豆、绿茶）养肝，少油腻，忌熬夜',
            '水': '宜食黑色食物（黑豆、黑芝麻、海带）补肾，少盐，多温热',
            '火': '宜食红色食物（红枣、红豆、番茄）养心，少辛辣，忌过劳',
            '土': '宜食黄色食物（小米、南瓜、山药）健脾，少甜少油，规律饮食'
        }
        if dm_wx in diet_map:
            diet_advice.append(diet_map[dm_wx])
        
        # 根据五行失衡推荐
        if wuxing_count['木'] < 1.0:
            diet_advice.append('补木：多食绿色蔬菜、绿豆、绿茶、枸杞')
        if wuxing_count['火'] >= 2.5:
            diet_advice.append('制火：少食辛辣、烧烤、油炸，多食清淡食物')
        if wuxing_count['土'] >= 3.5:
            diet_advice.append('疏土：少食甜食、油腻，多食清淡易消化食物')
        if wuxing_count['水'] < 0.8:
            diet_advice.append('补水：多食黑色食物、温热水，少食生冷')
        if wuxing_count['金'] < 0.8:
            diet_advice.append('补金：多食白色食物、润肺食物，少食辛辣')
        
        # 9. 运动建议
        exercise_advice = []
        if tu_mai_jin_analysis:
            exercise_advice.append('推荐：呼吸锻炼（如瑜伽呼吸、太极拳）、有氧运动')
        if mu_ruo_analysis:
            exercise_advice.append('推荐：伸展运动（如瑜伽、普拉提）、柔韧性训练')
        if tu_wang_analysis:
            exercise_advice.append('推荐：轻量运动（如慢走、太极）、避免剧烈运动')
        if huo_wang_analysis:
            exercise_advice.append('推荐：舒缓运动（如瑜伽、冥想）、避免剧烈运动')
        if wuxing_count['水'] < 0.8:
            exercise_advice.append('推荐：温和运动（如太极拳、散步）、注意保暖')
        
        if not exercise_advice:
            exercise_advice.append('推荐：规律运动，适度有氧运动，保持身体活力')
        
        # 10. 季节健康管理
        season_advice = []
        season_map = {
            '金': '秋季需格外注意呼吸系统，避免干燥环境，多润肺',
            '木': '春季是养肝最佳时机，宜早睡早起，多进行户外活动',
            '水': '冬季需格外注意肾脏保暖，避免受寒，多温热饮食',
            '火': '夏季需格外注意心脏和情绪，避免过热过劳，多休息',
            '土': '长夏（夏末秋初）需注意脾胃，避免生冷，饮食规律'
        }
        if dm_wx in season_map:
            season_advice.append(season_map[dm_wx])
        
        # 11. 需要注意的器官列表（增强）
        organs_to_attention = []
        if dm_wx == '金':
            organs_to_attention.extend(['肺', '大肠', '呼吸道'])
        if day_zhi_wx == '土':
            organs_to_attention.extend(['脾', '胃'])
        if wuxing_count['土'] >= 3.5:
            organs_to_attention.append('脾、胃（土过旺）')
        if wuxing_count['木'] < 1.0:
            organs_to_attention.append('肝、胆（木极弱）')
        if wuxing_count['水'] < 0.8:
            organs_to_attention.append('肾、膀胱（水极弱）')
        if wuxing_count['火'] >= 2.5:
            organs_to_attention.append('心、血管（火过旺）')
        if tu_mai_jin_analysis:
            organs_to_attention.extend(['肺', '大肠', '呼吸道（土重埋金）'])
        if jin_ruo_analysis:
            organs_to_attention.extend(['肺', '大肠', '呼吸道（金极弱）'])
        
        # 12. 年龄阶段健康关注点（基于五行和大运周期）
        age_focus = []
        if tu_mai_jin_analysis or jin_ruo_analysis:
            age_focus.append('中老年（40岁后）需重点关注呼吸系统，定期体检')
        if tu_wang_analysis:
            age_focus.append('中年（30-50岁）需重点关注脾胃消化系统，饮食规律')
        if wuxing_count['木'] < 1.0:
            age_focus.append('各年龄段都需注意肝胆养护，避免熬夜和过度饮酒')
        if wuxing_count['水'] < 0.8:
            age_focus.append('中老年（50岁后）需重点关注肾脏功能，注意腰肾保暖')
        
        # 🔥 新增：深度解释机制（基于实际五行、十神等参数动态生成）
        try:
            deep_explanation = self._generate_health_deep_explanation(
                dm_wx, day_zhi_wx, wuxing_count, max_wx, min_wx, total_count,
                tu_mai_jin_analysis, mu_ruo_analysis, tu_wang_analysis,
                huo_wang_analysis, shui_ruo_analysis, jin_ruo_analysis,
                tengod_health_analysis, ten_god_count
            )
        except Exception as e:
            print(f"⚠️ 生成健康深度解释失败: {e}")
            deep_explanation = "健康分析较为常规，无明显五行失衡或特殊健康机制需要深度解读。"
        
        # 🔥 新增：人生策略建议（基于实际健康状况动态生成）
        try:
            life_strategy = self._generate_health_life_strategy(
                dm_wx, wuxing_count, max_wx, min_wx,
                tu_mai_jin_analysis, mu_ruo_analysis, tu_wang_analysis,
                huo_wang_analysis, shui_ruo_analysis, jin_ruo_analysis,
                tengod_health_analysis, organs_to_attention
            )
        except Exception as e:
            print(f"⚠️ 生成健康人生策略失败: {e}")
            life_strategy = {
                'health_password': '保持五行平衡，注意日常养生',
                'maintenance_direction': '保持规律作息，适度运动',
                'daily_care': '保持规律作息，适度运动，饮食均衡',
                'key_points': ['保持五行平衡，注意日常养生，规律作息']
            }
        
        return {
            'day_master_organ': organ_map.get(dm_wx, '需综合判断'),
            'day_zhi_organ': organ_map.get(day_zhi_wx, '需综合判断'),
            'health_risks': health_risks,
            'wuxing_balance': {
                'max': max_wx,
                'min': min_wx,
                'counts': wuxing_count,
                'total': total_count
            },
            'health_advice': health_advice if health_advice else ['保持五行平衡，注意日常养生'],
            'detailed_analysis': {
                'tu_mai_jin': tu_mai_jin_analysis,
                'mu_ruo': mu_ruo_analysis,
                'tu_wang': tu_wang_analysis,
                'huo_wang': huo_wang_analysis,
                'shui_ruo': shui_ruo_analysis,
                'jin_ruo': jin_ruo_analysis
            },
            'tengod_health': tengod_health_analysis,  # 新增：十神健康分析
            'detailed_advice': detailed_advice,
            'diet_advice': diet_advice,  # 新增：详细饮食建议
            'exercise_advice': exercise_advice,  # 新增：运动建议
            'season_advice': season_advice,  # 新增：季节健康管理
            'age_focus': age_focus,  # 新增：年龄阶段关注点
            'organs_to_attention': list(set(organs_to_attention)),  # 去重
            'deep_explanation': deep_explanation,  # 🔥 新增：深度解释
            'life_strategy': life_strategy  # 🔥 新增：人生策略
        }
    
    def _generate_health_deep_explanation(self, dm_wx: str, day_zhi_wx: str,
                                         wuxing_count: Dict[str, float], max_wx: str, min_wx: str, total_count: float,
                                         tu_mai_jin_analysis: List, mu_ruo_analysis: List, tu_wang_analysis: List,
                                         huo_wang_analysis: List, shui_ruo_analysis: List, jin_ruo_analysis: List,
                                         tengod_health_analysis: List, ten_god_count: Dict[str, float]) -> str:
        """
        生成健康深度解释 - 基于实际五行、十神等参数动态生成
        
        理论依据：
        - 《渊海子平·论疾病》：五行失衡导致疾病
        - 《三命通会·论疾病》：十神过旺过弱影响健康
        """
        explanations = []
        
        # 1. 五行失衡机制详解（基于实际五行数量）
        max_ratio = wuxing_count[max_wx] / total_count if total_count > 0 else 0
        min_ratio = wuxing_count[min_wx] / total_count if total_count > 0 else 0
        
        if max_ratio >= 0.4:
            explanations.append(
                f"五行失衡机制：{max_wx}过旺（占比{max_ratio*100:.1f}%），" +
                f"数量{wuxing_count[max_wx]:.1f}，在五元素中占比最高。" +
                f"根据《渊海子平·论疾病》，{max_wx}过旺会导致相关脏腑功能亢进，" +
                f"需通过克制或泄耗来平衡。"
            )
        
        if min_ratio < 0.1:
            explanations.append(
                f"五行失衡机制：{min_wx}过弱（占比{min_ratio*100:.1f}%），" +
                f"数量{wuxing_count[min_wx]:.1f}，在五元素中占比最低。" +
                f"根据《渊海子平·论疾病》，{min_wx}过弱会导致相关脏腑功能不足，" +
                f"需通过生扶来补充。"
            )
        
        # 2. 特殊健康问题机制详解（基于实际分析结果）
        if tu_mai_jin_analysis:
            tu_ratio = wuxing_count['土'] / total_count if total_count > 0 else 0
            explanations.append(
                f"特殊健康机制：土重埋金。" +
                f"日主为金，但土元素占比{tu_ratio*100:.1f}%（数量{wuxing_count['土']:.1f}），" +
                f"过旺的土会埋没金，导致呼吸系统功能受阻。" +
                f"《渊海子平·论疾病》云：「土多金埋，需防范呼吸不畅、气虚等状况。」" +
                f"关键在于疏土泄金，通过木来疏解土，通过水来泄耗土。"
            )
        
        if mu_ruo_analysis:
            mu_count = wuxing_count['木']
            explanations.append(
                f"特殊健康机制：木极弱。" +
                f"木元素数量{mu_count:.1f}，占比极低（{(mu_count/total_count*100) if total_count > 0 else 0:.1f}%）。" +
                f"木主肝胆、筋骨，木弱代表肝胆功能偏弱，且身体柔韧性不足。" +
                f"《渊海子平·论疾病》云：「木弱不堪，需补木养肝。」"
            )
        
        if tu_wang_analysis:
            tu_ratio = wuxing_count['土'] / total_count if total_count > 0 else 0
            explanations.append(
                f"特殊健康机制：土过旺。" +
                f"土元素占比{tu_ratio*100:.1f}%（数量{wuxing_count['土']:.1f}），" +
                f"过旺的土最直接的影响是脾胃、消化系统。" +
                f"《渊海子平·论疾病》云：「土过旺，最直接的影响是脾胃、消化系统。」" +
                f"需通过木来疏解，通过水来泄耗，饮食规律，健脾为先。"
            )
        
        if huo_wang_analysis:
            huo_ratio = wuxing_count['火'] / total_count if total_count > 0 else 0
            explanations.append(
                f"特殊健康机制：火过旺。" +
                f"火元素占比{huo_ratio*100:.1f}%（数量{wuxing_count['火']:.1f}），" +
                f"过旺的火易有心血管系统问题，需注意心脏、血液循环。" +
                f"《渊海子平·论疾病》云：「火过旺，易有心血管系统问题。」" +
                f"需通过水来克制，通过土来泄耗，清淡饮食，控制情绪。"
            )
        
        if shui_ruo_analysis:
            shui_count = wuxing_count['水']
            explanations.append(
                f"特殊健康机制：水极弱。" +
                f"水元素数量{shui_count:.1f}，占比极低。" +
                f"水主肾脏、膀胱，水弱代表肾功能偏弱，需注意肾脏和泌尿系统。" +
                f"《渊海子平·论疾病》云：「水极弱，需注意肾脏和泌尿系统。」"
            )
        
        if jin_ruo_analysis:
            jin_count = wuxing_count['金']
            explanations.append(
                f"特殊健康机制：金极弱。" +
                f"日主为金但金元素数量{jin_count:.1f}，占比极低。" +
                f"金主肺、大肠、呼吸道，金弱代表呼吸系统功能偏弱，需格外注意。" +
                f"《渊海子平·论疾病》云：「金极弱，需注意呼吸系统。」"
            )
        
        # 3. 十神健康影响机制详解（基于实际十神数量）
        if tengod_health_analysis:
            for tg_health in tengod_health_analysis:
                tg_name = tg_health['ten_god']
                if tg_name == '印星过重':
                    yin_total = ten_god_count.get('正印', 0) + ten_god_count.get('偏印', 0)
                    explanations.append(
                        f"十神健康机制：印星过重（数量{yin_total:.1f}）。" +
                        f"印星代表思虑、保护，过重的印星会导致思虑较多，" +
                        f"需注意脾胃消化系统，避免过度思虑。" +
                        f"《三命通会·论疾病》云：「印星过重，思虑较多，易有脾胃问题。」"
                    )
                elif tg_name == '官杀过旺':
                    guansha_total = ten_god_count.get('正官', 0) + ten_god_count.get('偏官', 0)
                    explanations.append(
                        f"十神健康机制：官杀过旺（数量{guansha_total:.1f}）。" +
                        f"官杀代表压力、约束，过旺的官杀会导致压力较大，" +
                        f"需注意心血管系统和神经系统的健康。" +
                        f"《三命通会·论疾病》云：「官杀过旺，压力较大，易有心血管问题。」"
                    )
                elif tg_name == '食伤过旺':
                    shishang_total = ten_god_count.get('食神', 0) + ten_god_count.get('伤官', 0)
                    explanations.append(
                        f"十神健康机制：食伤过旺（数量{shishang_total:.1f}）。" +
                        f"食伤代表才华、消耗，过旺的食伤会导致思虑较多，容易消耗精神，" +
                        f"需注意养心安神。" +
                        f"《三命通会·论疾病》云：「食伤过旺，思虑较多，易消耗精神。」"
                    )
                elif tg_name == '比劫过旺':
                    bijie_total = ten_god_count.get('比肩', 0) + ten_god_count.get('劫财', 0)
                    explanations.append(
                        f"十神健康机制：比劫过旺（数量{bijie_total:.1f}）。" +
                        f"比劫代表竞争、压力，过旺的比劫会导致竞争压力较大，" +
                        f"需注意关节和肌肉的健康。" +
                        f"《三命通会·论疾病》云：「比劫过旺，竞争压力较大，易有关节问题。」"
                    )
        
        if not explanations:
            return "健康分析较为常规，无明显五行失衡或特殊健康机制需要深度解读。"
        
        return "。".join(explanations) + "。"
    
    def _generate_health_life_strategy(self, dm_wx: str, wuxing_count: Dict[str, float],
                                       max_wx: str, min_wx: str,
                                       tu_mai_jin_analysis: List, mu_ruo_analysis: List, tu_wang_analysis: List,
                                       huo_wang_analysis: List, shui_ruo_analysis: List, jin_ruo_analysis: List,
                                       tengod_health_analysis: List, organs_to_attention: List) -> Dict[str, str]:
        """
        生成健康人生策略建议 - 基于实际健康状况动态生成
        
        理论依据：
        - 《渊海子平·论疾病》：不同五行失衡的调理方法
        - 《三命通会·论疾病》：不同十神过旺过弱的调理方法
        """
        strategy = {
            'health_password': '',  # 健康密码
            'maintenance_direction': '',  # 养生方向
            'daily_care': '',  # 日常养护
            'key_points': []  # 关键要点
        }
        
        # 1. 健康密码（基于主要健康问题）
        if tu_mai_jin_analysis:
            strategy['health_password'] = (
                f"您的健康关键在于「疏土泄金」。" +
                f"日主为{dm_wx}，但土元素过旺（数量{wuxing_count['土']:.1f}），" +
                f"导致呼吸系统功能受阻。需通过木来疏解土，通过水来泄耗土，" +
                f"多进行呼吸锻炼，避免土重环境。"
            )
        elif mu_ruo_analysis:
            strategy['health_password'] = (
                f"您的健康关键在于「补木养肝」。" +
                f"木元素极弱（数量{wuxing_count['木']:.1f}），" +
                f"代表肝胆功能偏弱，且身体柔韧性不足。" +
                f"需多进行伸展运动，注意肝胆养护，避免熬夜和过度饮酒。"
            )
        elif tu_wang_analysis:
            strategy['health_password'] = (
                f"您的健康关键在于「健脾疏土」。" +
                f"土元素过旺（数量{wuxing_count['土']:.1f}），" +
                f"最直接的影响是脾胃、消化系统。" +
                f"需饮食规律，健脾为先，少甜少油，多食清淡易消化食物。"
            )
        elif huo_wang_analysis:
            strategy['health_password'] = (
                f"您的健康关键在于「制火养心」。" +
                f"火元素过旺（数量{wuxing_count['火']:.1f}），" +
                f"易有心血管系统问题。" +
                f"需清淡饮食，控制情绪，避免过劳，舒缓运动。"
            )
        elif shui_ruo_analysis:
            strategy['health_password'] = (
                f"您的健康关键在于「补肾养水」。" +
                f"水元素极弱（数量{wuxing_count['水']:.1f}），" +
                f"代表肾功能偏弱。" +
                f"需多饮水，注意腰肾保暖，避免过度劳累，多食黑色食物。"
            )
        elif jin_ruo_analysis:
            strategy['health_password'] = (
                f"您的健康关键在于「补金润肺」。" +
                f"日主为{dm_wx}但金元素极弱（数量{wuxing_count['金']:.1f}），" +
                f"呼吸系统功能偏弱。" +
                f"需多进行呼吸锻炼，避免烟尘环境，注意保暖，多食白色食物。"
            )
        else:
            # 基于五行失衡生成
            max_ratio = wuxing_count[max_wx] / sum(wuxing_count.values()) if sum(wuxing_count.values()) > 0 else 0
            min_ratio = wuxing_count[min_wx] / sum(wuxing_count.values()) if sum(wuxing_count.values()) > 0 else 0
            
            if max_ratio >= 0.3:
                strategy['health_password'] = (
                    f"您的健康关键在于「平衡{max_wx}元素」。" +
                    f"{max_wx}元素过旺，需通过克制或泄耗来平衡，" +
                    f"注意相关脏腑的调理。"
                )
            elif min_ratio < 0.15:
                strategy['health_password'] = (
                    f"您的健康关键在于「补充{min_wx}元素」。" +
                    f"{min_wx}元素过弱，需通过生扶来补充，" +
                    f"注意相关脏腑的养护。"
                )
            else:
                strategy['health_password'] = (
                    "您的健康关键在于「保持五行平衡」。" +
                    "目前五行相对平衡，需注意日常养生，保持规律作息。"
                )
        
        # 2. 养生方向（基于实际健康问题）
        if tu_mai_jin_analysis:
            strategy['maintenance_direction'] = (
                "重点关注呼吸系统：多进行呼吸锻炼（如瑜伽呼吸、太极拳）、" +
                "有氧运动，避免土重环境，宜疏土泄金。"
            )
        elif mu_ruo_analysis:
            strategy['maintenance_direction'] = (
                "重点关注肝胆系统：多进行伸展运动（如瑜伽、普拉提）、" +
                "柔韧性训练，注意肝胆养护，避免熬夜和过度饮酒。"
            )
        elif tu_wang_analysis:
            strategy['maintenance_direction'] = (
                "重点关注脾胃系统：轻量运动（如慢走、太极）、" +
                "饮食规律，健脾为先，少甜少油，避免剧烈运动。"
            )
        elif huo_wang_analysis:
            strategy['maintenance_direction'] = (
                "重点关注心血管系统：舒缓运动（如瑜伽、冥想）、" +
                "清淡饮食，控制情绪，避免剧烈运动，避免过劳。"
            )
        elif shui_ruo_analysis:
            strategy['maintenance_direction'] = (
                "重点关注肾脏系统：温和运动（如太极拳、散步）、" +
                "多饮水，注意腰肾保暖，多食黑色食物，避免过度劳累。"
            )
        elif jin_ruo_analysis:
            strategy['maintenance_direction'] = (
                "重点关注呼吸系统：多进行呼吸锻炼，" +
                "避免烟尘环境，注意保暖，多食白色食物、润肺食物。"
            )
        else:
            # 基于日主五行生成
            organ_map = {
                '金': '呼吸系统',
                '木': '肝胆系统',
                '水': '肾脏系统',
                '火': '心血管系统',
                '土': '脾胃系统'
            }
            main_organ = organ_map.get(dm_wx, '全身系统')
            strategy['maintenance_direction'] = (
                f"重点关注{main_organ}：根据日主{dm_wx}五行，" +
                f"需注意{main_organ}的养护，保持规律作息，适度运动。"
            )
        
        # 3. 日常养护（基于实际健康问题和需要注意的器官）
        daily_care_items = []
        if organs_to_attention:
            daily_care_items.append(f"重点关注的器官：{', '.join(organs_to_attention[:5])}")
        
        if tu_mai_jin_analysis or jin_ruo_analysis:
            daily_care_items.append("日常需多进行呼吸锻炼，避免烟尘环境，注意保暖")
        if mu_ruo_analysis:
            daily_care_items.append("日常需多进行伸展运动，注意肝胆养护，避免熬夜")
        if tu_wang_analysis:
            daily_care_items.append("日常需饮食规律，健脾为先，少甜少油")
        if huo_wang_analysis:
            daily_care_items.append("日常需清淡饮食，控制情绪，避免过劳")
        if shui_ruo_analysis:
            daily_care_items.append("日常需多饮水，注意腰肾保暖，避免过度劳累")
        
        if not daily_care_items:
            daily_care_items.append("保持规律作息，适度运动，饮食均衡")
        
        strategy['daily_care'] = "；".join(daily_care_items) + "。"
        
        # 4. 关键要点（基于实际健康问题）
        if tu_mai_jin_analysis:
            strategy['key_points'].append("土重埋金，需重点关注呼吸系统，多进行呼吸锻炼")
        if mu_ruo_analysis:
            strategy['key_points'].append("木极弱，需重点关注肝胆系统，多进行伸展运动")
        if tu_wang_analysis:
            strategy['key_points'].append("土过旺，需重点关注脾胃系统，饮食规律，健脾为先")
        if huo_wang_analysis:
            strategy['key_points'].append("火过旺，需重点关注心血管系统，清淡饮食，控制情绪")
        if shui_ruo_analysis:
            strategy['key_points'].append("水极弱，需重点关注肾脏系统，多饮水，注意腰肾保暖")
        if jin_ruo_analysis:
            strategy['key_points'].append("金极弱，需重点关注呼吸系统，多进行呼吸锻炼")
        
        if tengod_health_analysis:
            for tg_health in tengod_health_analysis:
                strategy['key_points'].append(f"{tg_health['ten_god']}，需注意{tg_health.get('suggestion', '')}")
        
        if not strategy['key_points']:
            strategy['key_points'].append("保持五行平衡，注意日常养生，规律作息")
        
        return strategy
    
    def _analyze_character_comprehensive(self, day_master: str, pillars: Dict,
                                        ten_god_count: Dict[str, float], strength: str,
                                        month_pattern: str) -> Dict:
        """
        🔥 性格分析 - 基于《渊海子平·论性情》
        
        理论依据：
        - 十天干性格特征
        - 十神性格特征
        - 格局性格特征
        
        分析项目（8项）：
        1. 日主性格
        2. 十神性格
        3. 格局性格
        4. 性格优势
        5. 性格劣势
        6. 性格建议
        7. 适合环境
        8. 需要注意的性格问题
        """
        # 1. 日主性格（基于《渊海子平·干支体象》）
        tiangan_character = {
            '甲': '正直、有担当、向上',
            '乙': '温和、灵活、有韧性',
            '丙': '热情、光明、积极',
            '丁': '细致、温和、有礼',
            '戊': '稳重、诚实、包容',
            '己': '细腻、温和、有耐心',
            '庚': '刚强、果断、有原则',
            '辛': '精细、温和、有才华',
            '壬': '灵活、聪明、有智慧',
            '癸': '细腻、温和、有韧性'
        }
        
        # 2. 十神性格
        ten_god_character = []
        main_tg = max(ten_god_count.items(), key=lambda x: x[1])[0] if ten_god_count else None
        
        tg_char_map = {
            '正官': '正直、负责、守规矩',
            '偏官': '果断、急躁、有魄力',
            '正财': '务实、节俭、稳重',
            '偏财': '豪爽、大方、灵活',
            '正印': '善良、仁慈、有文化',
            '偏印': '多疑、敏感、有才华',
            '食神': '温和、随和、有才艺',
            '伤官': '聪明、叛逆、有才华',
            '比肩': '独立、固执、有主见',
            '劫财': '冲动、竞争、有野心'
        }
        
        if main_tg:
            ten_god_character.append(tg_char_map.get(main_tg, '需综合判断'))
        
        # 3. 性格综合
        strong = strength in ['身旺', '身强']
        character_summary = f"日主{day_master}（{tiangan_character.get(day_master, '需综合判断')}），"
        if main_tg:
            character_summary += f"主导十神{main_tg}（{tg_char_map.get(main_tg, '')}），"
        character_summary += f"身{'强' if strong else '弱'}，"
        if month_pattern:
            character_summary += f"格局{month_pattern}。"
        
        # 🔥 新增：深度解释机制（基于实际日主、十神、格局等参数动态生成）
        try:
            deep_explanation = self._generate_character_deep_explanation(
                day_master, tiangan_character.get(day_master, ''), main_tg,
                ten_god_count, strength, month_pattern, ten_god_character
            )
        except Exception as e:
            print(f"⚠️ 生成性格深度解释失败: {e}")
            deep_explanation = "性格分析较为常规，无明显特殊机制需要深度解读。"
        
        # 🔥 新增：人生策略建议（基于实际性格特征动态生成）
        try:
            life_strategy = self._generate_character_life_strategy(
                day_master, tiangan_character.get(day_master, ''), main_tg,
                ten_god_count, strength, month_pattern, strong
            )
        except Exception as e:
            print(f"⚠️ 生成性格人生策略失败: {e}")
            life_strategy = {
                'character_password': '深入了解自己的性格特点，发挥优势，克服劣势',
                'cultivation_direction': '保持开放心态，主动学习，不断提升自己',
                'self_improvement': '保持开放心态，主动学习，不断提升自己',
                'key_points': ['保持开放心态，主动学习，不断提升自己']
            }
        
        return {
            'day_master_character': tiangan_character.get(day_master, '需综合判断'),
            'ten_god_character': ten_god_character,
            'character_summary': character_summary,
            'strength_impact': '身强则性格较为外向、主动' if strong else '身弱则性格较为内向、被动',
            'deep_explanation': deep_explanation,  # 🔥 新增：深度解释
            'life_strategy': life_strategy  # 🔥 新增：人生策略
        }
    
    def _generate_character_deep_explanation(self, day_master: str, day_master_char: str,
                                            main_tg: str, ten_god_count: Dict[str, float],
                                            strength: str, month_pattern: str,
                                            ten_god_character: List) -> str:
        """
        生成性格深度解释 - 基于实际日主、十神、格局等参数动态生成
        
        理论依据：
        - 《渊海子平·论性情》：性格形成的机制
        - 《子平真诠·论格局》：格局对性格的影响
        """
        explanations = []
        
        # 1. 日主性格机制详解（基于实际日主）
        if day_master_char:
            explanations.append(
                f"日主性格机制：日主为{day_master}，性格特征为{day_master_char}。" +
                f"根据《渊海子平·论性情》，十天干各有其性格特征，" +
                f"{day_master}的性格特点是{day_master_char}，这是您性格的基础。"
            )
        
        # 2. 十神性格机制详解（基于实际主导十神）
        if main_tg:
            main_tg_count = ten_god_count.get(main_tg, 0)
            tg_char_map = {
                '正官': '正直、负责、守规矩',
                '偏官': '果断、急躁、有魄力',
                '正财': '务实、节俭、稳重',
                '偏财': '豪爽、大方、灵活',
                '正印': '善良、仁慈、有文化',
                '偏印': '多疑、敏感、有才华',
                '食神': '温和、随和、有才艺',
                '伤官': '聪明、叛逆、有才华',
                '比肩': '独立、固执、有主见',
                '劫财': '冲动、竞争、有野心'
            }
            tg_char = tg_char_map.get(main_tg, '')
            if tg_char:
                explanations.append(
                    f"十神性格机制：主导十神{main_tg}（数量{main_tg_count:.1f}），" +
                    f"性格特征为{tg_char}。" +
                    f"根据《渊海子平·论性情》，十神代表不同的性格特征，" +
                    f"{main_tg}主导意味着您的性格中{tg_char}的特征较为突出。"
                )
        
        # 3. 身强身弱对性格的影响（基于实际身强身弱）
        strong = strength in ['身旺', '身强']
        if strong:
            explanations.append(
                f"身强身弱机制：身{'强' if strong else '弱'}。" +
                f"根据《渊海子平·论性情》，身强则性格较为外向、主动，" +
                f"容易表达自己的想法和情感，做事果断，有主见。"
            )
        else:
            explanations.append(
                f"身强身弱机制：身弱。" +
                f"根据《渊海子平·论性情》，身弱则性格较为内向、被动，" +
                f"容易依赖他人，做事较为谨慎，需要他人的支持和帮助。"
            )
        
        # 4. 格局对性格的影响（基于实际格局）
        if month_pattern:
            if '伤官配印' in month_pattern:
                shangguan_count = ten_god_count.get('伤官', 0)
                yin_count = ten_god_count.get('正印', 0) + ten_god_count.get('偏印', 0)
                explanations.append(
                    f"格局性格机制：伤官配印格（伤官数量{shangguan_count:.1f}，印星数量{yin_count:.1f}）。" +
                    f"根据《渊海子平·论性情》，伤官配印格主文贵，" +
                    f"性格特点是才华与理性的结合，既有伤官的创新和叛逆，" +
                    f"又有印星的稳重和学识，形成独特的性格特征。"
                )
            elif '食神制杀' in month_pattern:
                shishen_count = ten_god_count.get('食神', 0)
                qisha_count = ten_god_count.get('偏官', 0)
                explanations.append(
                    f"格局性格机制：食神制杀格（食神数量{shishen_count:.1f}，七杀数量{qisha_count:.1f}）。" +
                    f"根据《渊海子平·论性情》，食神制杀格主权威，" +
                    f"性格特点是温和与果断的结合，既有食神的温和和才艺，" +
                    f"又有七杀的果断和魄力，形成权威的性格特征。"
                )
            elif '正官格' in month_pattern:
                explanations.append(
                    f"格局性格机制：正官格。" +
                    f"根据《渊海子平·论性情》，正官格主贵，" +
                    f"性格特点是正直、负责、守规矩，有强烈的责任感和使命感。"
                )
            elif '正财格' in month_pattern or '偏财格' in month_pattern:
                cai_type = '正财格' if '正财' in month_pattern else '偏财格'
                cai_char = '务实、节俭、稳重' if '正财' in month_pattern else '豪爽、大方、灵活'
                explanations.append(
                    f"格局性格机制：{cai_type}。" +
                    f"根据《渊海子平·论性情》，{cai_type}主富，" +
                    f"性格特点是{cai_char}，注重实际利益，善于理财和投资。"
                )
            elif '正印格' in month_pattern or '偏印格' in month_pattern:
                yin_type = '正印格' if '正印' in month_pattern else '偏印格'
                yin_char = '善良、仁慈、有文化' if '正印' in month_pattern else '多疑、敏感、有才华'
                explanations.append(
                    f"格局性格机制：{yin_type}。" +
                    f"根据《渊海子平·论性情》，{yin_type}主文贵，" +
                    f"性格特点是{yin_char}，注重学识和思考，有强烈的学习欲望。"
                )
        
        # 5. 性格形成机制综合（基于实际组合）
        if main_tg and day_master_char:
            explanations.append(
                f"性格形成机制综合：日主{day_master}（{day_master_char}）与主导十神{main_tg}的组合，" +
                f"形成了您独特的性格特征。" +
                f"根据《渊海子平·论性情》，性格的形成是日主、十神、格局等多方面因素的综合，" +
                f"需要综合考虑才能准确判断。"
            )
        
        if not explanations:
            return "性格分析较为常规，无明显特殊机制需要深度解读。"
        
        return "。".join(explanations) + "。"
    
    def _generate_character_life_strategy(self, day_master: str, day_master_char: str,
                                          main_tg: str, ten_god_count: Dict[str, float],
                                          strength: str, month_pattern: str, strong: bool) -> Dict[str, str]:
        """
        生成性格人生策略建议 - 基于实际性格特征动态生成
        
        理论依据：
        - 《渊海子平·论性情》：不同性格特征的修炼建议
        - 《子平真诠·论格局》：格局对性格修炼的影响
        """
        strategy = {
            'character_password': '',  # 性格密码
            'cultivation_direction': '',  # 修炼方向
            'self_improvement': '',  # 自我提升
            'key_points': []  # 关键要点
        }
        
        # 1. 性格密码（基于日主和主导十神）
        tg_char_map = {
            '正官': '正直、负责、守规矩',
            '偏官': '果断、急躁、有魄力',
            '正财': '务实、节俭、稳重',
            '偏财': '豪爽、大方、灵活',
            '正印': '善良、仁慈、有文化',
            '偏印': '多疑、敏感、有才华',
            '食神': '温和、随和、有才艺',
            '伤官': '聪明、叛逆、有才华',
            '比肩': '独立、固执、有主见',
            '劫财': '冲动、竞争、有野心'
        }
        
        if main_tg:
            main_tg_count = ten_god_count.get(main_tg, 0)
            tg_char = tg_char_map.get(main_tg, '')
            strategy['character_password'] = (
                f"您的性格关键在于「发挥{main_tg}的优势」。" +
                f"主导十神{main_tg}（数量{main_tg_count:.1f}），" +
                f"性格特征为{tg_char}。" +
                f"需发挥{main_tg}的正面特征，避免其负面特征。"
            )
        elif day_master_char:
            strategy['character_password'] = (
                f"您的性格关键在于「发挥日主{day_master}的优势」。" +
                f"日主{day_master}，性格特征为{day_master_char}。" +
                f"需发挥{day_master}的正面特征，避免其负面特征。"
            )
        else:
            strategy['character_password'] = (
                "您的性格关键在于「自我认知和提升」。" +
                "需深入了解自己的性格特点，发挥优势，克服劣势。"
            )
        
        # 2. 修炼方向（基于格局和身强身弱）
        if month_pattern and '伤官配印' in month_pattern:
            strategy['cultivation_direction'] = (
                "伤官配印格，需平衡才华与理性。" +
                "避免过度张扬才华（伤官过旺），也避免过度保守（印星过旺）。" +
                "保持开放心态，主动学习，融入能激发您活力的圈子。"
            )
        elif month_pattern and '食神制杀' in month_pattern:
            strategy['cultivation_direction'] = (
                "食神制杀格，需平衡温和与果断。" +
                "避免过度温和（食神过旺），也避免过度果断（七杀过旺）。" +
                "保持权威和魄力，但也要注意温和待人。"
            )
        elif month_pattern and '正官格' in month_pattern:
            strategy['cultivation_direction'] = (
                "正官格，需发挥正直和负责的优势。" +
                "保持守规矩和责任感，但也要注意灵活性，避免过于刻板。"
            )
        elif main_tg == '伤官':
            strategy['cultivation_direction'] = (
                "伤官主导，需发挥聪明和才华的优势。" +
                "避免过度叛逆和冲动，通过理性思考来发挥才华。"
            )
        elif main_tg == '正印' or main_tg == '偏印':
            strategy['cultivation_direction'] = (
                f"{main_tg}主导，需发挥学识和思考的优势。" +
                ("避免过度思虑和多疑，保持开放心态。" if main_tg == '偏印' else "避免过度保守，保持灵活性。")
            )
        elif strong:
            strategy['cultivation_direction'] = (
                "身强，需发挥外向和主动的优势。" +
                "避免过度自信和冲动，保持谦逊和理性。"
            )
        else:
            strategy['cultivation_direction'] = (
                "身弱，需发挥谨慎和细致的优势。" +
                "避免过度依赖和被动，培养独立和自信。"
            )
        
        # 3. 自我提升（基于实际性格特征）
        improvement_items = []
        
        if main_tg == '伤官':
            improvement_items.append("伤官主导，需注意控制叛逆和冲动，通过理性思考来发挥才华")
        elif main_tg == '偏官':
            improvement_items.append("偏官主导，需注意控制急躁和冲动，保持冷静和理性")
        elif main_tg == '比肩' or main_tg == '劫财':
            improvement_items.append(f"{main_tg}主导，需注意控制固执和冲动，保持开放和灵活")
        elif main_tg == '偏印':
            improvement_items.append("偏印主导，需注意控制多疑和敏感，保持信任和开放")
        elif main_tg == '正印':
            improvement_items.append("正印主导，需注意控制过度保守，保持创新和灵活")
        
        if month_pattern and '伤官配印' in month_pattern:
            improvement_items.append("伤官配印格，需平衡才华与理性，避免过度张扬或过度保守")
        
        if strong:
            improvement_items.append("身强，需注意控制自信和冲动，保持谦逊和理性")
        else:
            improvement_items.append("身弱，需注意培养独立和自信，避免过度依赖")
        
        if not improvement_items:
            improvement_items.append("保持开放心态，主动学习，不断提升自己")
        
        strategy['self_improvement'] = "；".join(improvement_items) + "。"
        
        # 4. 关键要点（基于实际性格特征）
        if main_tg:
            strategy['key_points'].append(f"{main_tg}主导，需发挥其正面特征，避免负面特征")
        
        if month_pattern and '伤官配印' in month_pattern:
            strategy['key_points'].append("伤官配印格，需平衡才华与理性")
        
        if strong:
            strategy['key_points'].append("身强，需注意控制自信和冲动，保持谦逊和理性")
        else:
            strategy['key_points'].append("身弱，需注意培养独立和自信，避免过度依赖")
        
        if not strategy['key_points']:
            strategy['key_points'].append("保持开放心态，主动学习，不断提升自己")
        
        return strategy
    
    def _analyze_caiku(self, day_master: str, pillars: Dict, total_wealth: float) -> Dict:
        """
        财库分析 - 基于《渊海子平·论财库》《三命通会·财库论》
        
        ✅ 修复：使用通用公式计算财库，不再硬编码
        
        理论依据：
        - 财库 = 财星的墓库（十二长生的墓位），不是日主的墓库
        - 财星 = 日主五行所克之五行（我克者为财）
        - 计算公式：
          1. 根据日主五行，使用五行相克关系确定财星五行
          2. 根据财星五行，使用十二长生墓位确定财库地支
        
        - 坐财库：日支为财库
        - 开库时机：
          - 冲库：财库被冲开（如未库遇丑冲，戌库遇辰冲）
          - 刑库：财库被刑开
          - 合库：合也可能引动财库（六合或三合），尤其是合成日主喜用的五行局，以较为和缓的方式引动财库，带来机遇
            - 六合引动：如未库遇午年（午未合），较为和缓的方式引动财库
            - 三合引动：如未库遇卯年或亥年（亥卯未三合木局），合成喜用的木局，引动力更强
          - 大运流年引出财库
        """
        from ..core.utils import get_wealth_tomb_zhi
        
        day_zhi = pillars['day'][1]
        
        # ✅ 修复：使用通用公式计算财库，不再硬编码
        caiku_zhi = get_wealth_tomb_zhi(day_master)
        
        # 检查是否有财库
        caiku_exists = False
        caiku_positions = []
        if caiku_zhi:
            for pos, (gan, zhi) in pillars.items():
                if zhi == caiku_zhi:
                    caiku_exists = True
                    caiku_positions.append(pos)
        
        # 检查是否坐财库（日支为财库）
        zuo_caiku = (day_zhi == caiku_zhi) if caiku_zhi else False
        
        # 开库时机分析
        caiku_open_timing = []
        caiku_open_years = []  # ✅ 新增：具体开库年份列表
        if caiku_zhi:
            # 确定冲库的地支
            chong_map = {
                '辰': '戌', '戌': '辰',
                '丑': '未', '未': '丑'
            }
            chong_zhi = chong_map.get(caiku_zhi, None)
            
            if chong_zhi:
                # ✅ 新增：计算具体开库年份（未来20年）
                open_years = self._calculate_open_years(chong_zhi, caiku_zhi, years_ahead=20)
                if open_years:
                    year_list = [f"{y['year']}年（{y['ganzhi']}年）" for y in open_years[:5]]  # 显示前5个
                    if len(open_years) > 5:
                        year_list.append(f"等共{len(open_years)}个年份")
                    year_str = '、'.join(year_list)
                    caiku_open_timing.append(f'冲库：{caiku_zhi}库遇{chong_zhi}冲可开库')
                    caiku_open_timing.append(f'冲库年份：{year_str}')
                    caiku_open_years.extend(open_years)
                else:
                    caiku_open_timing.append(f'冲库：{caiku_zhi}库遇{chong_zhi}冲可开库')
                    caiku_open_timing.append(f'建议：大运或流年地支为{chong_zhi}时，{caiku_zhi}库被冲开，财运大增')
            
            # 刑库
            xing_map = {
                '辰': '自刑',
                '戌': '自刑',
                '丑': '戌丑未三刑',
                '未': '戌丑未三刑'
            }
            xing_info = xing_map.get(caiku_zhi, '')
            if xing_info:
                # ✅ 新增：计算刑库年份
                if xing_info == '自刑':
                    # 自刑：辰辰自刑、戌戌自刑
                    xing_years = self._calculate_open_years(caiku_zhi, caiku_zhi, years_ahead=20, xing_type='自刑')
                else:
                    # 三刑：需要计算戌、丑、未三个地支的年份
                    xing_zhi_list = ['戌', '丑', '未'] if caiku_zhi in ['丑', '未'] else []
                    xing_years = []
                    for xz in xing_zhi_list:
                        if xz != caiku_zhi:  # 排除财库本身
                            years_tmp = self._calculate_open_years(xz, caiku_zhi, years_ahead=20, xing_type='三刑')
                            xing_years.extend(years_tmp)
                    # 去重
                    seen = set()
                    xing_years = [y for y in xing_years if not (y['year'] in seen or seen.add(y['year']))]
                
                if xing_years:
                    year_list = [f"{y['year']}年（{y['ganzhi']}年）" for y in xing_years[:5]]
                    if len(xing_years) > 5:
                        year_list.append(f"等共{len(xing_years)}个年份")
                    year_str = '、'.join(year_list)
                    caiku_open_timing.append(f'刑库：{xing_info}亦可开库')
                    caiku_open_timing.append(f'刑库年份：{year_str}')
                    caiku_open_years.extend(xing_years)
                else:
                    caiku_open_timing.append(f'刑库：{xing_info}亦可开库')
            
            # ✅ 新增：合库引动分析（基于《渊海子平·论财库》《三命通会·财库论》）
            # 理论依据：合也可能引动财库，尤其是合成日主喜用的五行局，以较为和缓的方式引动财库，带来机遇
            from ..core.constants import DIZHI_LIUHE, DIZHI_SANHE
            
            # 1. 六合引动财库（较为和缓的方式）
            liuhe_zhi_list = []
            for zhi_pair, hua_wx in DIZHI_LIUHE.items():
                if caiku_zhi in zhi_pair:
                    # 找到与财库六合的地支
                    other_zhi = zhi_pair.replace(caiku_zhi, '')
                    liuhe_zhi_list.append(other_zhi)
                    # 说明：六合引动财库，较为和缓的方式，带来机遇
                    he_description = f'六合引动：{caiku_zhi}库遇{other_zhi}六合（{hua_wx}局），以较为和缓的方式引动财库，带来机遇'
                    caiku_open_timing.append(he_description)
            
            # 计算六合年份
            if liuhe_zhi_list:
                liuhe_years = []
                for lh_zhi in liuhe_zhi_list:
                    years_tmp = self._calculate_open_years(lh_zhi, caiku_zhi, years_ahead=20, xing_type='六合')
                    liuhe_years.extend(years_tmp)
                # 去重
                seen = set()
                liuhe_years = [y for y in liuhe_years if not (y['year'] in seen or seen.add(y['year']))]
                
                if liuhe_years:
                    year_list = [f"{y['year']}年（{y['ganzhi']}年）" for y in liuhe_years[:5]]
                    if len(liuhe_years) > 5:
                        year_list.append(f"等共{len(liuhe_years)}个年份")
                    year_str = '、'.join(year_list)
                    caiku_open_timing.append(f'六合年份：{year_str}')
                    caiku_open_years.extend(liuhe_years)
            
            # 2. 三合引动财库（更强大的引动力）
            # 查找包含财库的三合局
            sanhe_zhi_list = []
            for sanhe_branches, sanhe_wx in DIZHI_SANHE.items():
                if caiku_zhi in sanhe_branches:
                    # 找到与财库三合的其他地支
                    other_branches = [z for z in sanhe_branches if z != caiku_zhi]
                    sanhe_zhi_list.extend(other_branches)
                    # 说明：三合引动财库，合成喜用的五行局，引动力更强
                    # 例如：未库遇到卯年或亥年，形成亥卯未三合木局
                    sanhe_description = f'三合引动：{caiku_zhi}库遇{other_branches[0]}年或{other_branches[1]}年，形成{"/".join(sanhe_branches)}三合{sanhe_wx}局，引动财库，尤其是合成您喜用的{sanhe_wx}局，引动力更强'
                    caiku_open_timing.append(sanhe_description)
            
            # 计算三合年份
            if sanhe_zhi_list:
                sanhe_years = []
                for sh_zhi in sanhe_zhi_list:
                    years_tmp = self._calculate_open_years(sh_zhi, caiku_zhi, years_ahead=20, xing_type='三合')
                    sanhe_years.extend(years_tmp)
                # 去重
                seen = set()
                sanhe_years = [y for y in sanhe_years if not (y['year'] in seen or seen.add(y['year']))]
                
                if sanhe_years:
                    year_list = [f"{y['year']}年（{y['ganzhi']}年）" for y in sanhe_years[:5]]
                    if len(sanhe_years) > 5:
                        year_list.append(f"等共{len(sanhe_years)}个年份")
                    year_str = '、'.join(year_list)
                    caiku_open_timing.append(f'三合年份：{year_str}')
                    caiku_open_years.extend(sanhe_years)
        
        # ✅ 修复：优先判断日坐财库的情况，给出更详细的描述
        if zuo_caiku:
            # 日坐财库是非常利财的特殊组合，优先判断
            if caiku_exists and total_wealth > 0:
                description = f'【日坐财库】命局有财库（{caiku_zhi}库），且日支坐财库（{caiku_zhi}），财库贴身，这是非常利财的特殊组合。传统命理："日坐财库，无人不富"。且有财星，财库可用，开库时财运显著，财富积累能力极强。'
            elif caiku_exists and total_wealth == 0:
                description = f'【日坐财库】命局有财库（{caiku_zhi}库），且日支坐财库（{caiku_zhi}），财库贴身，这是非常利财的特殊组合。传统命理："日坐财库，无人不富"。虽无明财星，但需大运流年引出，开库时财运显著。'
            else:
                description = f'【日坐财库】命局有财库（{caiku_zhi}库），且日支坐财库（{caiku_zhi}），财库贴身，这是非常利财的特殊组合。传统命理："日坐财库，无人不富"。开库时财运显著，财富积累能力极强。'
        elif caiku_exists and total_wealth > 0:
            description = f'命局有财库（{caiku_zhi}库），且有财星，财库可用'
        elif caiku_exists and total_wealth == 0:
            description = f'命局有财库（{caiku_zhi}库），但无明财星，需大运流年引出'
        elif not caiku_exists and total_wealth > 0:
            description = f'命局无财库，但有财星，财星无库可藏'
        else:
            description = f'命局无财库，且无财星'
        
        return {
            'caiku_exists': caiku_exists,
            'caiku_zhi': caiku_zhi,
            'caiku_positions': caiku_positions,
            'zuo_caiku': zuo_caiku,
            'caiku_open_timing': caiku_open_timing,
            'caiku_open_years': caiku_open_years,  # ✅ 新增：具体开库年份列表
            'description': description
        }
    
    def _calculate_open_years(self, target_zhi: str, caiku_zhi: str, years_ahead: int = 20, xing_type: str = '') -> List[Dict]:
        """
        计算开库年份（冲库或刑库）
        
        Args:
            target_zhi: 目标地支（冲库时的冲库地支，或刑库时的刑库地支）
            caiku_zhi: 财库地支
            years_ahead: 计算未来多少年（默认20年）
            xing_type: 类型（'冲库'或'自刑'或'三刑'）
        
        Returns:
            开库年份列表，每个元素包含：year, ganzhi, type, description
        """
        from datetime import datetime
        from ..core.constants import TIANGAN_LIST, DIZHI_LIST
        
        current_year = datetime.now().year
        open_years = []
        
        # 年份转干支函数（使用1984年甲子年作为基准）
        def year_to_ganzhi(year: int) -> tuple:
            offset = year - 1984  # 1984年是甲子年
            gan = TIANGAN_LIST[offset % 10]
            zhi = DIZHI_LIST[offset % 12]
            return gan, zhi
        
        for i in range(years_ahead):
            year = current_year + i
            gan, zhi = year_to_ganzhi(year)
            
            # 检查是否是目标年份（冲库或刑库）
            if zhi == target_zhi:
                type_name = xing_type if xing_type else '冲库'
                description = f'{year}年（{gan}{zhi}年）{"冲" if not xing_type else "刑"}开{caiku_zhi}库'
                open_years.append({
                    'year': year,
                    'ganzhi': f"{gan}{zhi}",
                    'type': type_name,
                    'description': description
                })
        
        return open_years
