#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
扩展分析器 - 添加缺失的功能
基于《三命通会》《渊海子平》

功能：
1. 八字硬不硬（身旺身弱）
2. 犯不犯太岁
3. 牢狱之灾
4. 破财预测
5. 意外预测
"""

from typing import Dict, Any, List, Tuple
from ..core.base_analyzer import BaseAnalyzer
from ..core.data_structures import BaziData, AnalysisResult
from ..core.constants import (
    DIZHI_CANGGAN, TIANGAN_WUXING, DIZHI_WUXING,
    WUXING_SHENG_MAP, WUXING_KE_MAP
)
from ..core.utils import get_ten_god, create_analysis_result


class ExtendedAnalyzer(BaseAnalyzer):
    """
    扩展分析器
    """

    def __init__(self):
        super().__init__(name="扩展分析器", book_name="《三命通会》《渊海子平》")

    def analyze(self, bazi_data: BaziData) -> AnalysisResult:
        """
        执行扩展分析
        """
        pillars = bazi_data.get_pillars()
        day_master = bazi_data.get_day_master()
        birth_year = bazi_data.birth_year

        # 1. 八字硬不硬（身旺身弱）
        strength_analysis = self._analyze_strength(pillars, day_master)

        # 2. 犯不犯太岁
        taisui_analysis = self._analyze_taisui(pillars, birth_year)

        # 3. 牢狱之灾
        prison_analysis = self._analyze_prison_risk(pillars, day_master)

        # 4. 破财预测
        wealth_loss_analysis = self._analyze_wealth_loss(pillars, day_master)

        # 5. 意外预测
        accident_analysis = self._analyze_accident_risk(pillars, day_master)

        # 生成描述
        description = f"身旺身弱：{strength_analysis.get('level', '未知')}；"
        description += f"犯太岁：{taisui_analysis.get('result', '未知')}；"
        description += f"牢狱风险：{prison_analysis.get('risk_level', '未知')}；"
        description += f"破财风险：{wealth_loss_analysis.get('risk_level', '未知')}；"
        description += f"意外风险：{accident_analysis.get('risk_level', '未知')}"

        # 生成建议
        advice = f"身旺身弱建议：{strength_analysis.get('description', '')}；"
        advice += f"犯太岁建议：{taisui_analysis.get('advice', '')}；"
        advice += f"牢狱建议：{prison_analysis.get('advice', '')}；"
        advice += f"破财建议：{wealth_loss_analysis.get('advice', '')}；"
        advice += f"意外建议：{accident_analysis.get('advice', '')}"

        return create_analysis_result(
            analyzer_name=self.name,
            book_name=self.book_name,
            analysis_type="扩展分析",
            level="",
            score=0,
            description=description,
            details={
                'strength': strength_analysis,
                'taisui': taisui_analysis,
                'prison_risk': prison_analysis,
                'wealth_loss': wealth_loss_analysis,
                'accident_risk': accident_analysis
            },
            advice=advice
        )

    def _analyze_strength(self, pillars: Dict, day_master: str) -> Dict[str, Any]:
        """
        分析八字硬不硬（身旺身弱）

        理论依据：《三命通会》
        - 身旺：日主得令、得地、得生、得助
        - 身弱：日主失令、失地、失生、失助
        """
        day_wuxing = TIANGAN_WUXING[day_master]
        month_zhi = pillars['month'][1]

        # 1. 得令：月令是否生扶日主
        month_wuxing = DIZHI_WUXING[month_zhi]
        deling = False
        deling_score = 0

        # 月令生日主
        if WUXING_SHENG_MAP.get(month_wuxing) == day_wuxing:
            deling = True
            deling_score = 40  # 得令最重要
        # 月令与日主同五行
        elif month_wuxing == day_wuxing:
            deling = True
            deling_score = 30
        # 月令被日主所生（泄气）
        elif WUXING_SHENG_MAP.get(day_wuxing) == month_wuxing:
            deling_score = -20
        # 月令克日主
        elif WUXING_KE_MAP.get(month_wuxing) == day_wuxing:
            deling_score = -30

        # 2. 得地：地支是否有根
        # ✅ 修复：根据《三命通会》，只要有根就算得地，根气强弱只影响分数
        dedi = False
        dedi_score = 0
        root_count = 0

        for pos, (gan, zhi) in pillars.items():
            # ✅ 修复：日支也应该计算根气（日支是日主的根基，最重要）
            # 检查地支藏干
            for canggan, weight in DIZHI_CANGGAN.get(zhi, []):
                cg_wuxing = TIANGAN_WUXING[canggan]
                # 同五行为根（权重>=0.3的藏干才算根）
                if cg_wuxing == day_wuxing and weight >= 0.3:
                    # 日支的根气权重更高（因为日支是日主的根基）
                    if pos == 'day':
                        root_count += weight * 1.5  # 日支根气权重提高50%
                    else:
                        root_count += weight

        # ✅ 修复：只要有根（root_count >= 0.3）就算得地，只是强弱不同
        if root_count >= 1.0:
            dedi = True
            dedi_score = 20  # 强根
        elif root_count >= 0.5:
            dedi = True
            dedi_score = 10  # 中等根
        elif root_count >= 0.3:
            dedi = True
            dedi_score = 5   # 弱根，但有根就算得地

        # 3. 得生：天干是否有印星生扶
        desheng = False
        desheng_score = 0

        for pos, (gan, zhi) in pillars.items():
            if pos == 'day':
                continue
            ten_god = get_ten_god(day_master, gan)
            if ten_god in ['正印', '偏印']:
                desheng = True
                desheng_score += 15

        # 4. 得助：天干是否有比劫帮身
        dezhu = False
        dezhu_score = 0

        for pos, (gan, zhi) in pillars.items():
            if pos == 'day':
                continue
            ten_god = get_ten_god(day_master, gan)
            if ten_god in ['比肩', '劫财']:
                dezhu = True
                dezhu_score += 10

        # 综合评分
        total_score = deling_score + dedi_score + desheng_score + dezhu_score

        # 判断身旺身弱
        if total_score >= 40:
            strength_level = '身旺'
            strength_desc = '日主强旺，能任财官，喜行财官运'
        elif total_score >= 20:
            strength_level = '身中和'
            strength_desc = '日主中和，不强不弱，运行平稳'
        elif total_score >= 0:
            strength_level = '身稍弱'
            strength_desc = '日主稍弱，需印比扶助，忌财官太重'
        else:
            strength_level = '身弱'
            strength_desc = '日主衰弱，难任财官，喜行印比运'

        return {
            'level': strength_level,
            'score': total_score,
            'description': strength_desc,
            'deling': deling,
            'deling_score': deling_score,
            'dedi': dedi,
            'dedi_score': dedi_score,
            'root_count': root_count,
            'desheng': desheng,
            'desheng_score': desheng_score,
            'dezhu': dezhu,
            'dezhu_score': dezhu_score,
            'details': {
                '得令': f"{'是' if deling else '否'}（{deling_score}分）",
                '得地': self._format_dedi_detail(dedi, dedi_score, root_count),
                '得生': f"{'是' if desheng else '否'}（{desheng_score}分）",
                '得助': f"{'是' if dezhu else '否'}（{dezhu_score}分）"
            }
        }
    
    def _format_dedi_detail(self, dedi: bool, dedi_score: int, root_count: float) -> str:
        """
        格式化得地详情显示
        """
        if not dedi:
            return f"否（{dedi_score}分，根气{root_count:.1f}）"
        
        # 根据根气强弱标注
        if root_count >= 1.0:
            root_level = "强根"
        elif root_count >= 0.5:
            root_level = "中等根"
        else:
            root_level = "弱根"
        
        return f"是（{dedi_score}分，根气{root_count:.1f}，{root_level}）"

    def _analyze_taisui(self, pillars: Dict, birth_year: int) -> Dict[str, Any]:
        """
        分析犯不犯太岁

        理论依据：《渊海子平》
        "犯岁君者，其年必主凶丧、剋妻妾及破财是非、犯上之悔"
        """
        # 获取当前年份（2025年）
        current_year = 2025
        year_gan = pillars['year'][0]
        year_zhi = pillars['year'][1]

        # 计算当前太岁（2025年为乙巳年）
        # 这里简化处理，实际应该根据当前年份计算
        current_taisui_gan = '乙'
        current_taisui_zhi = '巳'

        # 判断是否犯太岁
        fan_taisui = False
        fan_type = []

        # 1. 值太岁（本命年）
        if year_zhi == current_taisui_zhi:
            fan_taisui = True
            fan_type.append('值太岁（本命年）')

        # 2. 冲太岁
        chong_map = {
            '子': '午', '午': '子',
            '丑': '未', '未': '丑',
            '寅': '申', '申': '寅',
            '卯': '酉', '酉': '卯',
            '辰': '戌', '戌': '辰',
            '巳': '亥', '亥': '巳'
        }
        if year_zhi == chong_map.get(current_taisui_zhi):
            fan_taisui = True
            fan_type.append('冲太岁')

        # 3. 刑太岁
        xing_map = {
            '子': ['卯'], '卯': ['子'],
            '寅': ['巳'], '巳': ['申'], '申': ['寅'],
            '丑': ['戌'], '戌': ['未'], '未': ['丑'],
            '辰': ['辰'], '午': ['午'], '酉': ['酉'], '亥': ['亥']
        }
        if year_zhi in xing_map.get(current_taisui_zhi, []):
            fan_taisui = True
            fan_type.append('刑太岁')

        # 4. 害太岁
        hai_map = {
            '子': '未', '未': '子',
            '丑': '午', '午': '丑',
            '寅': '巳', '巳': '寅',
            '卯': '辰', '辰': '卯',
            '申': '亥', '亥': '申',
            '酉': '戌', '戌': '酉'
        }
        if year_zhi == hai_map.get(current_taisui_zhi):
            fan_taisui = True
            fan_type.append('害太岁')

        # 5. 破太岁
        po_map = {
            '子': '酉', '酉': '子',
            '丑': '辰', '辰': '丑',
            '寅': '亥', '亥': '寅',
            '卯': '午', '午': '卯',
            '巳': '申', '申': '巳',
            '未': '戌', '戌': '未'
        }
        if year_zhi == po_map.get(current_taisui_zhi):
            fan_taisui = True
            fan_type.append('破太岁')

        if fan_taisui:
            result = '犯太岁'
            description = f"2025年（乙巳年）{', '.join(fan_type)}，需谨慎行事，避免冲动"
            advice = "犯太岁之年，宜守不宜攻，避免大的变动，可佩戴化太岁符或拜太岁化解"
        else:
            result = '不犯太岁'
            description = f"2025年（乙巳年）不犯太岁，运势平稳"
            advice = "不犯太岁，可正常发展，但仍需谨慎行事"

        return {
            'result': result,
            'fan_taisui': fan_taisui,
            'fan_type': fan_type,
            'current_year': current_year,
            'current_taisui': f"{current_taisui_gan}{current_taisui_zhi}",
            'year_pillar': f"{year_gan}{year_zhi}",
            'description': description,
            'advice': advice
        }

    def _analyze_prison_risk(self, pillars: Dict, day_master: str) -> Dict[str, Any]:
        """
        分析牢狱之灾

        理论依据：《三命通会》
        - 官杀混杂，身弱无制
        - 伤官见官，为祸百端
        - 羊刃冲刑，刑狱之灾
        """
        risk_level = '无'
        risk_score = 0
        risk_factors = []

        # 统计十神
        ten_god_count = {}
        for pos, (gan, zhi) in pillars.items():
            ten_god = get_ten_god(day_master, gan)
            ten_god_count[ten_god] = ten_god_count.get(ten_god, 0) + 1

        # 1. 官杀混杂
        zhengguan_count = ten_god_count.get('正官', 0)
        qisha_count = ten_god_count.get('七杀', 0)

        if zhengguan_count >= 1 and qisha_count >= 1:
            risk_score += 20
            risk_factors.append('官杀混杂（正官与七杀并见）')

        # 2. 伤官见官
        shangguan_count = ten_god_count.get('伤官', 0)

        if shangguan_count >= 1 and zhengguan_count >= 1:
            risk_score += 30
            risk_factors.append('伤官见官（为祸百端）')

        # 3. 七杀无制
        shishen_count = ten_god_count.get('食神', 0)

        if qisha_count >= 2 and shishen_count == 0 and shangguan_count == 0:
            risk_score += 25
            risk_factors.append('七杀无制（杀重无制）')

        # 4. 羊刃冲刑
        # 检查刑冲，并显示具体组合
        xing_details = []
        chong_details = []
        xingchong_combinations = []  # 新增：存储具体的刑冲组合

        zhis = [pillars[pos][1] for pos in ['year', 'month', 'day', 'hour']]

        # 检查六冲
        chong_pairs = [
            ('子', '午'), ('丑', '未'), ('寅', '申'),
            ('卯', '酉'), ('辰', '戌'), ('巳', '亥')
        ]
        for z1, z2 in chong_pairs:
            if z1 in zhis and z2 in zhis:
                chong_detail = f'{z1}冲{z2}'
                chong_details.append(chong_detail)
                xingchong_combinations.append(chong_detail)  # 保存具体组合

        # 检查三刑
        # 注意：寅巳申三刑为无恩之刑，丑戌未三刑为恃势之刑（《三命通会》标准分类）
        if set(['寅', '巳', '申']).issubset(set(zhis)):
            xing_detail = '寅巳申三刑（无恩之刑）'
            xing_details.append(xing_detail)
            xingchong_combinations.append(xing_detail)  # 保存具体组合
        if set(['丑', '戌', '未']).issubset(set(zhis)):
            xing_detail = '丑戌未三刑（恃势之刑）'
            xing_details.append(xing_detail)
            xingchong_combinations.append(xing_detail)  # 保存具体组合
        if '子' in zhis and '卯' in zhis:
            xing_detail = '子卯相刑（无礼之刑）'
            xing_details.append(xing_detail)
            xingchong_combinations.append(xing_detail)  # 保存具体组合

        if xing_details or chong_details:
            risk_score += 15
            # 不再在risk_factors中重复显示刑冲组合（已在xingchong_combinations中单独显示）

        # 判断风险等级
        if risk_score >= 50:
            risk_level = '高风险'
            description = '命局有牢狱之灾的征兆，需特别谨慎，遵纪守法'
        elif risk_score >= 30:
            risk_level = '中等风险'
            description = '命局有一定风险，需注意避免官非诉讼'
        elif risk_score >= 15:
            risk_level = '低风险'
            description = '命局有轻微风险，平时注意即可'
        else:
            risk_level = '无风险'
            description = '命局无明显牢狱之灾征兆'

        # 计算具体风险年份
        specific_years = []
        if risk_score > 0 and (xing_details or chong_details):
            import datetime
            current_year = datetime.datetime.now().year

            for year in range(current_year, current_year + 11):
                year_zhi = self._get_year_zhi(year)
                risk_reasons = []

                # 检查是否逢冲
                if chong_details:
                    zhis = [pillars[pos][1] for pos in ['year', 'month', 'day', 'hour']]
                    chong_pairs = [
                        ('子', '午'), ('丑', '未'), ('寅', '申'),
                        ('卯', '酉'), ('辰', '戌'), ('巳', '亥')
                    ]
                    for z1, z2 in chong_pairs:
                        if z1 in zhis and year_zhi == z2:
                            # 流年冲命局中的z1
                            risk_reasons.append(f'逢冲（{year_zhi}冲命局{z1}）')
                            break
                        elif z2 in zhis and year_zhi == z1:
                            # 流年冲命局中的z2
                            risk_reasons.append(f'逢冲（{year_zhi}冲命局{z2}）')
                            break

                # 检查是否逢刑
                if xing_details:
                    zhis = [pillars[pos][1] for pos in ['year', 'month', 'day', 'hour']]
                    if set(['寅', '巳', '申']).issubset(set(zhis)) and year_zhi in ['寅', '巳', '申']:
                        risk_reasons.append('逢刑（寅巳申三刑）')
                    elif set(['丑', '戌', '未']).issubset(set(zhis)) and year_zhi in ['丑', '戌', '未']:
                        risk_reasons.append('逢刑（丑戌未三刑）')
                    elif '子' in zhis and '卯' in zhis and year_zhi in ['子', '卯']:
                        risk_reasons.append('逢刑（子卯相刑）')

                if risk_reasons:
                    specific_years.append(f"{year}年（{' '.join(risk_reasons)}）")

        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'xingchong_combinations': xingchong_combinations,  # 新增：具体的刑冲组合列表
            'specific_years': specific_years,  # 新增：具体年份列表
            'description': description,
            'advice': '遵纪守法，避免冲动行事，远离是非之地' if risk_score > 0 else '无需特别担心'
        }

    def _analyze_wealth_loss(self, pillars: Dict, day_master: str) -> Dict[str, Any]:
        """
        分析破财预测

        理论依据：《渊海子平》
        "犯岁君者，其年必主凶丧、剋妻妾及破财是非"
        "财多身弱，反受其累"
        """
        risk_level = '无'
        risk_score = 0
        risk_factors = []
        risk_years = []

        # 统计财星
        cai_count = 0.0
        for pos, (gan, zhi) in pillars.items():
            ten_god = get_ten_god(day_master, gan)
            if ten_god in ['正财', '偏财']:
                cai_count += 1.0

            # 地支藏干
            for canggan, weight in DIZHI_CANGGAN.get(pillars[pos][1], []):
                tg = get_ten_god(day_master, canggan)
                if tg in ['正财', '偏财']:
                    cai_count += weight

        # 统计比劫
        bijie_count = 0.0
        for pos, (gan, zhi) in pillars.items():
            ten_god = get_ten_god(day_master, gan)
            if ten_god in ['比肩', '劫财']:
                bijie_count += 1.0

        # 1. 财多身弱
        # 简化判断：财星多于2个，且无比劫帮身
        if cai_count >= 2.0 and bijie_count == 0:
            risk_score += 30
            risk_factors.append('财多身弱（财星过多，难以驾驭）')

        # 2. 比劫夺财
        if bijie_count >= 2:
            risk_score += 25
            risk_factors.append('比劫夺财（兄弟朋友分夺财物）')

        # 3. 财星被冲克
        # 检查冲，并显示具体组合
        zhis = [pillars[pos][1] for pos in ['year', 'month', 'day', 'hour']]
        chong_pairs = [
            ('子', '午'), ('丑', '未'), ('寅', '申'),
            ('卯', '酉'), ('辰', '戌'), ('巳', '亥')
        ]
        chong_details = []
        for z1, z2 in chong_pairs:
            if z1 in zhis and z2 in zhis:
                chong_details.append(f'{z1}冲{z2}')

        if chong_details:
            risk_score += 15
            # 不再在risk_factors中重复显示冲组合（已在chong_combinations中单独显示）
            # 风险因素中只保留解释性说明
            risk_factors.append('财库受冲，易有破耗')

        # 判断风险等级
        if risk_score >= 50:
            risk_level = '高风险'
            description = '命局有破财征兆，需谨慎理财，避免投资风险'
        elif risk_score >= 30:
            risk_level = '中等风险'
            description = '命局有一定破财风险，需注意财务管理'
        elif risk_score >= 15:
            risk_level = '低风险'
            description = '命局有轻微破财风险，平时注意即可'
        else:
            risk_level = '无风险'
            description = '命局无明显破财征兆'

        # 预测破财时间（计算具体年份）
        specific_years = []
        if risk_score > 0:
            import datetime
            current_year = datetime.datetime.now().year

            # 计算未来10年的破财风险年份
            for year in range(current_year, current_year + 11):
                year_zhi = self._get_year_zhi(year)
                risk_reasons = []

                # 检查是否逢冲（财库受冲）
                if chong_details:
                    zhis = [pillars[pos][1] for pos in ['year', 'month', 'day', 'hour']]
                    chong_pairs = [
                        ('子', '午'), ('丑', '未'), ('寅', '申'),
                        ('卯', '酉'), ('辰', '戌'), ('巳', '亥')
                    ]
                    for z1, z2 in chong_pairs:
                        if z1 in zhis and year_zhi == z2:
                            # 流年冲命局中的z1（财库受冲）
                            risk_reasons.append(f'财库受冲（{year_zhi}冲命局{z1}）')
                            break
                        elif z2 in zhis and year_zhi == z1:
                            # 流年冲命局中的z2（财库受冲）
                            risk_reasons.append(f'财库受冲（{year_zhi}冲命局{z2}）')
                            break

                if risk_reasons:
                    specific_years.append(f"{year}年（{' '.join(risk_reasons)}）")

            # 如果没有具体年份，显示一般性建议
            if not specific_years:
                risk_years.append('比劫运（兄弟朋友分财）')
                risk_years.append('财星太旺运（财多身弱）')

        # 新增：提取具体的刑冲组合（用于显示）
        chong_combinations = []
        if chong_details:
            chong_combinations = chong_details.copy()

        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'risk_years': risk_years,
            'chong_combinations': chong_combinations,  # 新增：具体的冲组合
            'specific_years': specific_years,  # 新增：具体年份列表
            'description': description,
            'advice': '谨慎理财，避免借贷，远离赌博，不做担保' if risk_score > 0 else '财运平稳，正常理财即可'
        }

    def _analyze_accident_risk(self, pillars: Dict, day_master: str) -> Dict[str, Any]:
        """
        分析意外预测

        理论依据：《三命通会》
        - 羊刃冲刑，血光之灾
        - 七杀无制，意外伤灾
        - 金神入火乡，血光之灾
        """
        risk_level = '无'
        risk_score = 0
        risk_factors = []
        caution_years = []

        # 1. 羊刃冲刑
        zhis = [pillars[pos][1] for pos in ['year', 'month', 'day', 'hour']]
        xingchong_combinations = []  # 新增：存储具体的刑冲组合
        risk_types = []  # 新增：存储具体的风险类型

        # 检查六冲
        chong_pairs = [
            ('子', '午'), ('丑', '未'), ('寅', '申'),
            ('卯', '酉'), ('辰', '戌'), ('巳', '亥')
        ]
        has_chong = False
        for z1, z2 in chong_pairs:
            if z1 in zhis and z2 in zhis:
                has_chong = True
                risk_score += 20
                chong_detail = f'{z1}冲{z2}'
                # 不再在risk_factors中重复显示刑冲组合（已在xingchong_combinations中单独显示）
                xingchong_combinations.append(chong_detail)  # 保存具体组合
                risk_types.append('交通意外')  # 冲主交通意外
                risk_types.append('跌打损伤')  # 冲主跌打损伤
                break

        # 检查三刑
        # 注意：寅巳申三刑为无恩之刑，丑戌未三刑为恃势之刑（《三命通会》标准分类）
        has_xing = False
        if set(['寅', '巳', '申']).issubset(set(zhis)):
            has_xing = True
            risk_score += 25
            xing_detail = '寅巳申三刑（无恩之刑）'
            # 不再在risk_factors中重复显示刑冲组合（已在xingchong_combinations中单独显示）
            xingchong_combinations.append(xing_detail)  # 保存具体组合
            risk_types.append('血光之灾')  # 三刑主血光
            risk_types.append('手术外伤')  # 三刑主手术外伤
        elif set(['丑', '戌', '未']).issubset(set(zhis)):
            has_xing = True
            risk_score += 25
            xing_detail = '丑戌未三刑（恃势之刑）'
            # 不再在risk_factors中重复显示刑冲组合（已在xingchong_combinations中单独显示）
            xingchong_combinations.append(xing_detail)  # 保存具体组合
            risk_types.append('意外伤害')  # 三刑主意外
            risk_types.append('跌打损伤')  # 三刑主跌打
        elif zhis.count('子') >= 1 and zhis.count('卯') >= 1:
            has_xing = True
            risk_score += 20
            xing_detail = '子卯相刑（无礼之刑）'
            # 不再在risk_factors中重复显示刑冲组合（已在xingchong_combinations中单独显示）
            xingchong_combinations.append(xing_detail)  # 保存具体组合
            risk_types.append('口舌是非')  # 子卯刑主口舌

        # 2. 七杀无制
        ten_god_count = {}
        for pos, (gan, zhi) in pillars.items():
            ten_god = get_ten_god(day_master, gan)
            ten_god_count[ten_god] = ten_god_count.get(ten_god, 0) + 1

        qisha_count = ten_god_count.get('七杀', 0)
        shishen_count = ten_god_count.get('食神', 0)
        shangguan_count = ten_god_count.get('伤官', 0)

        if qisha_count >= 2 and shishen_count == 0 and shangguan_count == 0:
            risk_score += 20
            risk_factors.append('七杀无制（杀重无制，易有意外伤灾）')
            risk_types.append('意外伤灾')  # 七杀无制主意外
            risk_types.append('突发疾病')  # 七杀主突发

        # 3. 羊刃
        # 简化判断：日主的羊刃
        yangbian_map = {
            '甲': '卯', '乙': '寅',
            '丙': '午', '丁': '巳',
            '戊': '午', '己': '巳',
            '庚': '酉', '辛': '申',
            '壬': '子', '癸': '亥'
        }
        yangbian_zhi = yangbian_map.get(day_master)
        if yangbian_zhi and yangbian_zhi in zhis:
            risk_score += 15
            risk_factors.append(f'命带羊刃（{yangbian_zhi}，易有血光之灾）')
            risk_types.append('血光之灾')  # 羊刃主血光
            risk_types.append('手术外伤')  # 羊刃主手术

        # 判断风险等级
        if risk_score >= 50:
            risk_level = '高风险'
            description = '命局有意外伤灾征兆，需特别小心，避免危险场所'
        elif risk_score >= 30:
            risk_level = '中等风险'
            description = '命局有一定意外风险，需注意安全'
        elif risk_score >= 15:
            risk_level = '低风险'
            description = '命局有轻微意外风险，平时注意即可'
        else:
            risk_level = '无风险'
            description = '命局无明显意外伤灾征兆'

        # 预测需要小心的时间（计算具体年份）
        specific_years = []
        if risk_score > 0:
            # 计算未来10年的风险年份
            import datetime
            current_year = datetime.datetime.now().year

            for year in range(current_year, current_year + 11):
                year_zhi = self._get_year_zhi(year)
                risk_reasons = []
                year_risk_types = []  # 该年份的风险类型

                # 检查是否逢冲
                if has_chong:
                    for z1, z2 in chong_pairs:
                        if z1 in zhis and year_zhi == z2:
                            # 流年冲命局中的z1
                            risk_reasons.append(f'逢冲（{year_zhi}冲命局{z1}）')
                            year_risk_types.append('交通意外')
                            year_risk_types.append('跌打损伤')
                            break
                        elif z2 in zhis and year_zhi == z1:
                            # 流年冲命局中的z2
                            risk_reasons.append(f'逢冲（{year_zhi}冲命局{z2}）')
                            year_risk_types.append('交通意外')
                            year_risk_types.append('跌打损伤')
                            break

                # 检查是否逢刑
                if has_xing:
                    # 检查三刑
                    if set(['寅', '巳', '申']).issubset(set(zhis)) and year_zhi in ['寅', '巳', '申']:
                        risk_reasons.append('逢刑（寅巳申三刑）')
                        year_risk_types.append('血光之灾')
                        year_risk_types.append('手术外伤')
                    elif set(['丑', '戌', '未']).issubset(set(zhis)) and year_zhi in ['丑', '戌', '未']:
                        risk_reasons.append('逢刑（丑戌未三刑）')
                        year_risk_types.append('意外伤害')
                        year_risk_types.append('跌打损伤')
                    elif '子' in zhis and '卯' in zhis and year_zhi in ['子', '卯']:
                        risk_reasons.append('逢刑（子卯相刑）')
                        year_risk_types.append('口舌是非')

                # 检查七杀旺年
                if qisha_count >= 2:
                    # 简化：如果流年地支与命局地支有特殊关系，可能引动七杀
                    year_risk_types.append('意外伤灾')
                    year_risk_types.append('突发疾病')

                if risk_reasons:
                    # 去重风险类型
                    unique_risk_types = list(dict.fromkeys(year_risk_types))
                    risk_types_str = '、'.join(unique_risk_types) if unique_risk_types else ''
                    if risk_types_str:
                        specific_years.append(f"{year}年（{' '.join(risk_reasons)}，风险类型：{risk_types_str}）")
                    else:
                        specific_years.append(f"{year}年（{' '.join(risk_reasons)}）")

            # 如果没有具体年份，显示一般性建议
            if not specific_years:
                if has_chong:
                    caution_years.append('逢冲之年（与命局地支相冲的年份）')
                if has_xing:
                    caution_years.append('逢刑之年（与命局地支相刑的年份）')
                if qisha_count > 0:
                    caution_years.append('七杀旺年（杀气重的年份）')

        # 去重风险类型
        unique_risk_types = list(dict.fromkeys(risk_types))

        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'risk_factors': risk_factors,
            'xingchong_combinations': xingchong_combinations,  # 新增：具体的刑冲组合
            'risk_types': unique_risk_types,  # 新增：具体的风险类型列表
            'caution_years': caution_years,
            'specific_years': specific_years,  # 新增：具体年份列表（包含风险类型）
            'description': description,
            'advice': '注意交通安全，避免危险运动，远离是非之地，不去危险场所' if risk_score > 0 else '平时注意安全即可'
        }

    def _get_year_zhi(self, year: int) -> str:
        """
        计算年份的地支

        理论依据：
        - 1924年为甲子年（地支为子）
        - 地支12年一循环
        """
        dizhi_list = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        offset = (year - 1924) % 12
        return dizhi_list[offset]

