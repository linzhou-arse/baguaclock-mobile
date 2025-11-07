#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
格局分析器 - Geju Analyzer
========================

基于《三命通会·格局篇》的格局分析
"""

from __future__ import annotations
from typing import Dict, List, Any, Tuple
import time

from ..core.base_analyzer import BaseAnalyzer
from ..core.data_structures import BaziData, AnalysisResult, AnalysisConfig
from ..core.utils import get_ten_god, create_analysis_result, get_wuxing_by_tiangan, get_wuxing_by_dizhi
from ..core.constants import DIZHI_CANGGAN


class GejuAnalyzer(BaseAnalyzer):
    """格局分析器 - 基于《三命通会·格局篇》"""
    
    def __init__(self, config: AnalysisConfig = None):
        super().__init__("格局分析器", "三命通会", config)
    
    def analyze(self, bazi_data: BaziData) -> AnalysisResult:
        """
        执行格局分析（十神主导+月令取用的基础版）
        ✅ 已修复：消除硬编码60分，根据格局质量动态评分
        """
        start_time = time.time()

        try:
            pillars = bazi_data.get_pillars()
            day_master = bazi_data.get_day_master()
            month_branch = bazi_data.get_month_branch()

            ten_gods_count, ten_gods_positions = self._count_ten_gods(day_master, pillars)
            month_strength = self._estimate_day_master_strength(day_master, month_branch)
            
            # 🔥 新增：先检查特殊格局（优先级高于普通格局）
            special_geju = self._check_special_patterns(bazi_data, ten_gods_count)
            if special_geju:
                geju_type = special_geju['type']
                base_score = special_geju['base_score']
                level_delta = special_geju['bonus']
            else:
                # 普通格局分析
                main_pattern = self._determine_main_pattern(ten_gods_count)
                geju_type, base_score, level_delta = self._refine_pattern_with_strength(
                    main_pattern, month_strength, ten_gods_count
                )

            # ✅ 动态基础分：根据格局类型
            score = base_score + level_delta
            score = max(0.0, min(100.0, score))
            level = self._score_to_level(score)

            analysis_time = (time.time() - start_time) * 1000

            details = {
                'ten_gods_count': ten_gods_count,
                'ten_gods_positions': ten_gods_positions,
                'month_strength': month_strength,
                'main_pattern': main_pattern,
                'geju_type': geju_type,
                'base_score': base_score,
                'level_delta': level_delta
            }

            description = f"主导十神：{main_pattern}；日主{month_strength}；格局：{geju_type}"

            advice = self._generate_advice(geju_type, month_strength)

            return create_analysis_result(
                analyzer_name=self.name,
                book_name=self.book_name,
                analysis_type="格局分析",
                level=level,
                score=score,
                description=description,
                details=details,
                advice=advice,
                analysis_time=analysis_time
            )

        except Exception as e:
            raise Exception(f"格局分析失败: {e}")

    def _count_ten_gods(self, day_master: str, pillars: Dict[str, Tuple[str, str]]) -> Tuple[Dict[str, int], Dict[str, List[str]]]:
        counts: Dict[str, int] = {}
        positions: Dict[str, List[str]] = {}
        for pillar, (gan, zhi) in pillars.items():
            tg = get_ten_god(day_master, gan)
            counts[tg] = counts.get(tg, 0) + 1
            positions.setdefault(tg, []).append(pillar)
        return counts, positions

    def _estimate_day_master_strength(self, day_master: str, month_branch: str) -> str:
        dm_wx = get_wuxing_by_tiangan(day_master)
        mb_wx = get_wuxing_by_dizhi(month_branch)
        # 生我五行
        sheng_map = {'木': '水', '火': '木', '土': '火', '金': '土', '水': '金'}
        # 我生五行
        wo_sheng = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        if mb_wx == dm_wx:
            return '得令偏旺'
        elif mb_wx == sheng_map.get(dm_wx):
            return '得生偏旺'
        elif wo_sheng.get(dm_wx) == mb_wx:
            return '泄气偏弱'
        else:
            return '平衡或偏弱'

    def _determine_main_pattern(self, counts: Dict[str, int]) -> str:
        groups = {
            '官杀': counts.get('正官', 0) + counts.get('偏官', 0),
            '财星': counts.get('正财', 0) + counts.get('偏财', 0),
            '食伤': counts.get('食神', 0) + counts.get('伤官', 0),
            '印星': counts.get('正印', 0) + counts.get('偏印', 0),
            '比劫': counts.get('比肩', 0) + counts.get('劫财', 0)
        }
        main = max(groups.items(), key=lambda x: x[1])[0]
        return main

    def _refine_pattern_with_strength(self, main_pattern: str, strength: str, counts: Dict[str, int]) -> Tuple[str, float, float]:
        """
        根据格局和身强身弱判断格局质量
        ✅ 已修复：
        1. 修正bonus计算错误（bonus -= 6 if not strong else -2 改为 bonus -= (6 if not strong else 2)）
        2. 动态基础分，根据格局类型不同
        3. 返回三个值：格局类型、基础分、加成分
        """
        # 依据《三命通会》取用大意：
        # 官杀格：身强用官杀泄身，身弱忌官杀
        # 财格：身强用财，身弱忌财
        # 食伤格：身强可，身弱不宜过多泄气
        # 印格：身弱喜印，身强忌印太多
        # 比劫：身弱喜比劫扶身，身强忌比劫争财

        bonus = 0.0
        geju = main_pattern + '格'
        strong = ('旺' in strength)

        # ✅ 动态基础分：根据格局类型
        base_score_map = {
            '官杀': 65.0,  # 官杀格较贵
            '财星': 62.0,  # 财格较富
            '食伤': 58.0,  # 食伤格较灵活
            '印星': 60.0,  # 印格较稳
            '比劫': 55.0   # 比劫格较平
        }
        base_score = base_score_map.get(main_pattern, 60.0)

        # 官杀混杂判定
        if counts.get('正官', 0) > 0 and counts.get('偏官', 0) > 0:
            geju = '官杀混杂'
            # ✅ 修正：bonus -= (6 if not strong else 2)
            bonus -= (6 if not strong else 2)  # 身弱遇混杂更不利
            base_score = 52.0  # 官杀混杂基础分较低

        if main_pattern == '官杀':
            bonus += 8 if strong else -8
        elif main_pattern == '财星':
            bonus += 6 if strong else -6
        elif main_pattern == '食伤':
            bonus += 4 if strong else -4
        elif main_pattern == '印星':
            bonus += 8 if not strong else -4
        elif main_pattern == '比劫':
            bonus += 6 if not strong else -6

        # 组合加成：食伤生财、财生官、印绶护官
        if counts.get('食神', 0) + counts.get('伤官', 0) > 0 and counts.get('正财', 0) + counts.get('偏财', 0) > 0:
            bonus += 5  # 食伤生财，流通有情
        if counts.get('正财', 0) + counts.get('偏财', 0) > 0 and counts.get('正官', 0) + counts.get('偏官', 0) > 0:
            bonus += 5  # 财生官，富贵双全
        if counts.get('正印', 0) + counts.get('偏印', 0) > 0 and counts.get('正官', 0) + counts.get('偏官', 0) > 0:
            bonus += 4  # 印绶护官，官印相生

        # 从格基础识别：身极弱且比劫少，财/官/食伤某一类明显占优
        if not strong and counts.get('比肩', 0) + counts.get('劫财', 0) == 0:
            groups = {
                '从官': counts.get('正官', 0) + counts.get('偏官', 0),
                '从财': counts.get('正财', 0) + counts.get('偏财', 0),
                '从儿': counts.get('食神', 0) + counts.get('伤官', 0)
            }
            major, major_cnt = max(groups.items(), key=lambda x: x[1])
            if major_cnt >= 2:
                geju = major + '格'
                base_score = 68.0  # 从格成立，基础分较高
                bonus += 6  # 从格加成

        return geju, base_score, bonus

    def _score_to_level(self, score: float) -> str:
        if score >= 85:
            return '大吉'
        elif score >= 70:
            return '吉'
        elif score >= 55:
            return '中平'
        elif score >= 40:
            return '凶'
        return '大凶'

    def _generate_advice(self, geju_type: str, strength: str) -> str:
        if '官杀' in geju_type:
            return '官杀为用，宜循规避险；身弱者先扶身再用官杀。'
        if '财星' in geju_type:
            return '财为用神，宜理财务实；身弱者忌贪财，先固本。'
        if '食伤' in geju_type:
            return '食伤为用，宜才艺谋生；忌过度泄气，需有印化。'
        if '印星' in geju_type:
            return '印星为用，宜学习进修；身强忌印过多压抑。'
        if '比劫' in geju_type:
            return '比劫为用，宜团队协作；身强忌与人争锋。'
        return '综合衡量喜忌，取用以中和为先。'
    
    def _check_special_patterns(self, bazi_data: BaziData, ten_gods_count: Dict[str, int]) -> Dict[str, Any] | None:
        """
        🔥 新增：检查特殊格局
        按优先级检查：化气格 > 专旺格 > 从格 > 两神成象格 > 外格
        """
        pillars = bazi_data.get_pillars()
        day_master = bazi_data.get_day_master()
        
        # 1. 化气格（最高优先级）
        huaqi_result = self._check_huaqi_geju(pillars)
        if huaqi_result:
            return huaqi_result
        
        # 2. 专旺格
        zhuanwang_result = self._check_zhuanwang_geju(bazi_data, ten_gods_count)
        if zhuanwang_result:
            return zhuanwang_result
        
        # 3. 从格（增强版）
        cong_result = self._check_cong_geju_enhanced(bazi_data, ten_gods_count)
        if cong_result:
            return cong_result
        
        # 4. 两神成象格
        liangshen_result = self._check_liangshen_geju(bazi_data)
        if liangshen_result:
            return liangshen_result
        
        # 5. 外格
        waige_result = self._check_waige_geju(bazi_data, ten_gods_count)
        if waige_result:
            return waige_result
        
        return None
    
    def _check_huaqi_geju(self, pillars: Dict[str, Tuple[str, str]]) -> Dict[str, Any] | None:
        """
        化气格查法 - 基于《三命通会》理论
        《三命通会》："化气者，天干五合也。"
        
        化气格条件：
        1. 年月日天干出现五合（甲己、乙庚、丙辛、丁壬、戊癸）
        2. 化神当令（月支为化神）
        3. 日干被合
        """
        year_gan = pillars['year'][0]
        month_gan = pillars['month'][0]
        day_gan = pillars['day'][0]
        month_branch = pillars['month'][1]
        
        # 五合表
        wuhe_map = {
            '甲': '己', '己': '甲',  # 甲己化土
            '乙': '庚', '庚': '乙',  # 乙庚化金
            '丙': '辛', '辛': '丙',  # 丙辛化水
            '丁': '壬', '壬': '丁',  # 丁壬化木
            '戊': '癸', '癸': '戊'   # 戊癸化火
        }
        
        # 化神五行表（月支五行）
        huaqi_wuxing_map = {
            '甲己': '土', '乙庚': '金', '丙辛': '水', '丁壬': '木', '戊癸': '火'
        }
        
        # 检查日干是否被合
        if day_gan in wuhe_map:
            he_gan = wuhe_map[day_gan]
            # 检查年月日是否有合
            if (year_gan == he_gan or month_gan == he_gan):
                # 确定化神
                if day_gan < he_gan:
                    pair = day_gan + he_gan
                else:
                    pair = he_gan + day_gan
                
                huaqi_wx = huaqi_wuxing_map.get(pair)
                if huaqi_wx:
                    mb_wx = get_wuxing_by_dizhi(month_branch)
                    # 检查化神是否当令
                    if mb_wx == huaqi_wx:
                        geju_name_map = {
                            '甲己': '甲己化土格', '乙庚': '乙庚化金格',
                            '丙辛': '丙辛化水格', '丁壬': '丁壬化木格',
                            '戊癸': '戊癸化火格'
                        }
                        return {
                            'type': geju_name_map.get(pair, '化气格'),
                            'base_score': 72.0,
                            'bonus': 8.0
                        }
        
        return None
    
    def _check_zhuanwang_geju(self, bazi_data: BaziData, ten_gods_count: Dict[str, int]) -> Dict[str, Any] | None:
        """
        专旺格查法 - 基于《三命通会》理论
        《三命通会》："专旺者，一行独旺也。"
        
        专旺格类型：
        - 曲直格（木）：日主甲乙，四柱木多，无金克
        - 炎上格（火）：日主丙丁，四柱火多，无水克
        - 稼穑格（土）：日主戊己，四柱土多，无木克
        - 从革格（金）：日主庚辛，四柱金多，无火克
        - 润下格（水）：日主壬癸，四柱水多，无土克
        """
        pillars = bazi_data.get_pillars()
        day_master = bazi_data.get_day_master()
        dm_wx = get_wuxing_by_tiangan(day_master)
        
        # 统计五行分布
        wuxing_count = self._count_wuxing_distribution(pillars)
        
        # 专旺格判断条件：本行超过60%，克我五行少于10%
        if dm_wx == '木':
            if wuxing_count.get('木', 0) >= 0.6 and wuxing_count.get('金', 0) < 0.1:
                return {'type': '曲直格', 'base_score': 70.0, 'bonus': 6.0}
        elif dm_wx == '火':
            if wuxing_count.get('火', 0) >= 0.6 and wuxing_count.get('水', 0) < 0.1:
                return {'type': '炎上格', 'base_score': 70.0, 'bonus': 6.0}
        elif dm_wx == '土':
            if wuxing_count.get('土', 0) >= 0.6 and wuxing_count.get('木', 0) < 0.1:
                return {'type': '稼穑格', 'base_score': 70.0, 'bonus': 6.0}
        elif dm_wx == '金':
            if wuxing_count.get('金', 0) >= 0.6 and wuxing_count.get('火', 0) < 0.1:
                return {'type': '从革格', 'base_score': 70.0, 'bonus': 6.0}
        elif dm_wx == '水':
            if wuxing_count.get('水', 0) >= 0.6 and wuxing_count.get('土', 0) < 0.1:
                return {'type': '润下格', 'base_score': 70.0, 'bonus': 6.0}
        
        return None
    
    def _check_cong_geju_enhanced(self, bazi_data: BaziData, ten_gods_count: Dict[str, int]) -> Dict[str, Any] | None:
        """
        从格增强版查法 - 基于《三命通会》理论
        从格条件更严格：
        1. 日主极弱（比劫少或无）
        2. 某一行或某一十神明显占优
        3. 无生扶（印星少或无）
        """
        pillars = bazi_data.get_pillars()
        day_master = bazi_data.get_day_master()
        
        # 统计比劫和印星
        bijie_count = ten_gods_count.get('比肩', 0) + ten_gods_count.get('劫财', 0)
        yin_count = ten_gods_count.get('正印', 0) + ten_gods_count.get('偏印', 0)
        
        # 从格条件：比劫+印星总数 <= 1
        if bijie_count + yin_count <= 1:
            # 检查从官杀
            guansha_count = ten_gods_count.get('正官', 0) + ten_gods_count.get('偏官', 0)
            if guansha_count >= 2:
                return {'type': '从官格', 'base_score': 68.0, 'bonus': 6.0}
            
            # 检查从财
            cai_count = ten_gods_count.get('正财', 0) + ten_gods_count.get('偏财', 0)
            if cai_count >= 2:
                return {'type': '从财格', 'base_score': 68.0, 'bonus': 6.0}
            
            # 检查从儿（从食伤）
            shishang_count = ten_gods_count.get('食神', 0) + ten_gods_count.get('伤官', 0)
            if shishang_count >= 2:
                return {'type': '从儿格', 'base_score': 68.0, 'bonus': 6.0}
        
        return None
    
    def _check_liangshen_geju(self, bazi_data: BaziData) -> Dict[str, Any] | None:
        """
        两神成象格查法 - 基于《三命通会》理论
        《三命通会》："两神成象者，二行相生而成象也。"
        
        常见两神成象格：
        - 木火通明：木火相生
        - 金水相涵：金水相生
        - 土金相生：土金相生
        - 水火既济：水火相济
        """
        pillars = bazi_data.get_pillars()
        wuxing_count = self._count_wuxing_distribution(pillars)
        
        # 找出占比最高的两个五行
        sorted_wx = sorted(wuxing_count.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_wx) >= 2:
            wx1, count1 = sorted_wx[0]
            wx2, count2 = sorted_wx[1]
            
            # 两神成象条件：两个五行合计超过80%，其他五行少于20%
            if count1 + count2 >= 0.8:
                # 木火通明
                if (wx1 == '木' and wx2 == '火') or (wx1 == '火' and wx2 == '木'):
                    return {'type': '木火通明格', 'base_score': 75.0, 'bonus': 8.0}
                # 金水相涵
                elif (wx1 == '金' and wx2 == '水') or (wx1 == '水' and wx2 == '金'):
                    return {'type': '金水相涵格', 'base_score': 75.0, 'bonus': 8.0}
                # 土金相生
                elif (wx1 == '土' and wx2 == '金') or (wx1 == '金' and wx2 == '土'):
                    return {'type': '土金相生格', 'base_score': 73.0, 'bonus': 7.0}
        
        return None
    
    def _check_waige_geju(self, bazi_data: BaziData, ten_gods_count: Dict[str, int]) -> Dict[str, Any] | None:
        """
        外格查法 - 基于《三命通会》理论
        外格包括：金神格、魁罡格、日德格、日贵格等
        """
        pillars = bazi_data.get_pillars()
        day_master = bazi_data.get_day_master()
        day_branch = pillars['day'][1]
        
        # 魁罡格：日柱为庚戌、戊戌、壬辰、庚辰
        if (day_master == '庚' and day_branch == '戌') or \
           (day_master == '戊' and day_branch == '戌') or \
           (day_master == '壬' and day_branch == '辰') or \
           (day_master == '庚' and day_branch == '辰'):
            return {'type': '魁罡格', 'base_score': 66.0, 'bonus': 5.0}
        
        # 金神格：日柱为乙丑、己巳、癸酉，且时柱为金
        if (day_master == '乙' and day_branch == '丑') or \
           (day_master == '己' and day_branch == '巳') or \
           (day_master == '癸' and day_branch == '酉'):
            hour_branch = pillars['hour'][1]
            hour_wx = get_wuxing_by_dizhi(hour_branch)
            if hour_wx == '金':
                return {'type': '金神格', 'base_score': 67.0, 'bonus': 5.0}
        
        return None
    
    def _count_wuxing_distribution(self, pillars: Dict[str, Tuple[str, str]]) -> Dict[str, float]:
        """
        统计五行分布（归一化到0-1）
        """
        wuxing_count = {'木': 0, '火': 0, '土': 0, '金': 0, '水': 0}
        total = 0
        
        for pillar, (gan, zhi) in pillars.items():
            # 天干五行
            gan_wx = get_wuxing_by_tiangan(gan)
            wuxing_count[gan_wx] += 1
            total += 1
            
            # 地支五行（主气）
            zhi_wx = get_wuxing_by_dizhi(zhi)
            wuxing_count[zhi_wx] += 1
            total += 1
            
            # 地支藏干五行
            canggan_list = DIZHI_CANGGAN.get(zhi, [])
            for cg in canggan_list:
                cg_wx = get_wuxing_by_tiangan(cg)
                wuxing_count[cg_wx] += 0.3  # 藏干权重0.3
                total += 0.3
        
        # 归一化
        if total > 0:
            return {wx: count / total for wx, count in wuxing_count.items()}
        return wuxing_count
