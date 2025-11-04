# -*- coding: utf-8 -*-
"""
人生重大事件时间预测分析器 - 基于《三命通会》《渊海子平》等经典理论

功能：
1. 牢狱之灾时间预测
2. 破财时间预测
3. 意外事故时间预测
4. 官运时间预测

理论依据：
- 《三命通会·论三刑》：三刑主刑狱
- 《三命通会·论官符》：官符主官灾
- 《三命通会·论灾煞》：灾煞主血光横死
- 《渊海子平·论大运》：败财之地，主破财
"""

from typing import Dict, List, Tuple, Any, Optional
from chinese_metaphysics_library.core.data_structures import BaziData
from chinese_metaphysics_library.core.utils import get_ten_god, get_wuxing_by_tiangan, get_wuxing_by_dizhi
from chinese_metaphysics_library.core.constants import WUXING_KE_MAP


class LifeEventTimeAnalyzer:
    """人生重大事件时间预测分析器"""
    
    def __init__(self):
        pass
    
    def analyze_disaster_timing(self, 
                                bazi_data: BaziData,
                                dayun_list: List[Tuple[str, str, int, int]],
                                liunian_list: List[Tuple[str, str, int]]) -> Dict[str, Any]:
        """
        分析重大灾祸时间（牢狱之灾、意外事故）
        
        参数：
        - bazi_data: 八字数据
        - dayun_list: 大运列表 [(天干, 地支, 起始年龄, 结束年龄), ...]
        - liunian_list: 流年列表 [(天干, 地支, 年份), ...]
        
        返回：
        {
            'laoyu_risk': [...],  # 牢狱风险时段
            'yiwai_risk': [...],  # 意外风险时段
            'summary': '...'      # 总体评估
        }
        """
        pillars = bazi_data.get_pillars()
        day_master = bazi_data.get_day_master()
        
        # 1. 分析命局中的凶煞
        try:
            from chinese_metaphysics_library.santonghui.shensha_analyzer import ShenshaAnalyzer
            shensha_analyzer = ShenshaAnalyzer()
            xiong_shen = shensha_analyzer._analyze_xiong_shen(bazi_data)
        except Exception as e:
            # 如果导入失败，使用简化判断
            xiong_shen = []
        
        # 获取凶煞名称
        xiong_shen_names = {shen.get('name', '') for shen in xiong_shen}
        
        # 2. 分析大运中的风险时段
        laoyu_risk = []  # 牢狱风险
        yiwai_risk = []  # 意外风险
        
        for gan, zhi, start_age, end_age in dayun_list:
            risk_level = 0
            risk_reasons = []
            
            # 检查大运是否引动凶煞
            # 2.1 检查三刑
            if any(name in xiong_shen_names for name in ['无恩之刑', '无礼之刑', '恃势之刑', '自刑']):
                # 检查大运地支是否参与三刑
                if self._is_sanxing_in_dayun(zhi, pillars):
                    risk_level += 15
                    risk_reasons.append('大运引动三刑')
            
            # 2.2 检查官符煞
            if '官符煞' in xiong_shen_names:
                if self._is_guanfu_in_dayun(zhi, pillars):
                    risk_level += 12
                    risk_reasons.append('大运遇官符煞')
            
            # 2.3 检查勾绞煞
            if any(name in xiong_shen_names for name in ['勾煞', '绞煞']):
                if self._is_goujiao_in_dayun(zhi, pillars, bazi_data):
                    risk_level += 10
                    risk_reasons.append('大运遇勾绞煞')
            
            # 2.4 检查灾煞
            if '灾煞' in xiong_shen_names:
                if self._is_zhaisha_in_dayun(zhi, pillars):
                    risk_level += 12
                    risk_reasons.append('大运遇灾煞')
                    yiwai_risk.append({
                        'type': '意外',
                        'period': f'{start_age}-{end_age}岁',
                        'dayun': f'{gan}{zhi}',
                        'level': '高' if risk_level >= 20 else '中',
                        'reason': '；'.join(risk_reasons),
                        'advice': '需格外小心，避免高风险活动，注意交通安全'
                    })
            
            # 2.5 检查羊刃
            if '羊刃' in xiong_shen_names:
                yangren_zhi = self._get_yangren_zhi(day_master)
                if zhi == yangren_zhi:
                    risk_level += 8
                    risk_reasons.append('大运遇羊刃')
                    yiwai_risk.append({
                        'type': '意外',
                        'period': f'{start_age}-{end_age}岁',
                        'dayun': f'{gan}{zhi}',
                        'level': '中',
                        'reason': '大运遇羊刃，主血光之灾',
                        'advice': '需注意安全，避免争斗，注意健康'
                    })
            
            # 判断牢狱风险
            if risk_level >= 15:
                laoyu_risk.append({
                    'type': '牢狱',
                    'period': f'{start_age}-{end_age}岁',
                    'dayun': f'{gan}{zhi}',
                    'level': '高' if risk_level >= 25 else '中',
                    'reason': '；'.join(risk_reasons),
                    'advice': '需循法守序，避免违法行为，谨慎处理法律事务'
                })
        
        # 3. 分析流年中的风险年份
        laoyu_years = []
        yiwai_years = []
        
        for gan, zhi, year in liunian_list:
            # 检查流年是否与命局三刑
            if self._is_sanxing_in_liunian(gan, zhi, pillars, day_master):
                laoyu_years.append({
                    'year': year,
                    'ganzhi': f'{gan}{zhi}',
                    'reason': '流年与命局三刑',
                    'level': '中'
                })
            
            # 检查流年是否引动灾煞
            if self._is_zhaisha_in_liunian(zhi, pillars):
                yiwai_years.append({
                    'year': year,
                    'ganzhi': f'{gan}{zhi}',
                    'reason': '流年遇灾煞',
                    'level': '高',
                    'advice': '需格外小心，避免高风险活动'
                })
        
        return {
            'laoyu_risk': laoyu_risk,
            'yiwai_risk': yiwai_risk,
            'laoyu_years': laoyu_years,
            'yiwai_years': yiwai_years,
            'summary': self._generate_disaster_summary(laoyu_risk, yiwai_risk, laoyu_years, yiwai_years)
        }
    
    def analyze_wealth_timing(self,
                              bazi_data: BaziData,
                              dayun_list: List[Tuple[str, str, int, int]],
                              liunian_list: List[Tuple[str, str, int]]) -> Dict[str, Any]:
        """
        分析破财时间
        
        理论依据：
        - 《渊海子平》："且如甲乙得寅卯运，名曰劫财败财，主剋父母及剋妻、破财争斗之事"
        - "财行得地则发，行败财之地必死"
        """
        pillars = bazi_data.get_pillars()
        day_master = bazi_data.get_day_master()
        
        # 1. 统计财星和比劫
        from chinese_metaphysics_library.core.utils import get_ten_god
        
        # 获取财星五行
        day_wuxing = get_wuxing_by_tiangan(day_master)
        # 我克者为财（使用常量）
        wealth_wuxing = WUXING_KE_MAP.get(day_wuxing, '')
        
        # 我同者为比劫
        wuxing_same_map = {
            '木': '木', '土': '土', '水': '水',
            '火': '火', '金': '金'
        }
        bijie_wuxing = wuxing_same_map.get(day_wuxing, '')
        
        # 2. 分析大运中的破财风险
        pocai_risk = []
        
        for gan, zhi, start_age, end_age in dayun_list:
            gan_wx = get_wuxing_by_tiangan(gan)
            zhi_wx = get_wuxing_by_dizhi(zhi)
            dayun_ten_god = get_ten_god(day_master, gan)
            
            risk_level = 0
            risk_reasons = []
            
            # 2.1 检查比劫大运（败财运）
            if dayun_ten_god in ['比肩', '劫财']:
                risk_level += 15
                risk_reasons.append(f'{dayun_ten_god}大运，比劫夺财')
            
            # 2.2 检查财星被克
            if gan_wx == wealth_wuxing or zhi_wx == wealth_wuxing:
                # 财星大运，但需检查是否有比劫来夺
                # 这里简化处理：如果命局比劫重，财星大运也可能被夺
                pass
            
            # 2.3 检查财破印（印重时，财破印反而好，但需具体情况分析）
            
            if risk_level >= 10:
                pocai_risk.append({
                    'type': '破财',
                    'period': f'{start_age}-{end_age}岁',
                    'dayun': f'{gan}{zhi}',
                    'level': '高' if risk_level >= 20 else '中',
                    'reason': '；'.join(risk_reasons),
                    'advice': '需谨慎投资，避免合伙，注意理财，避免大额支出'
                })
        
        # 3. 分析流年中的破财年份
        pocai_years = []
        
        for gan, zhi, year in liunian_list:
            liunian_ten_god = get_ten_god(day_master, gan)
            
            if liunian_ten_god in ['比肩', '劫财']:
                pocai_years.append({
                    'year': year,
                    'ganzhi': f'{gan}{zhi}',
                    'reason': f'流年{liunian_ten_god}，比劫夺财',
                    'level': '中',
                    'advice': '需谨慎理财，避免大额投资'
                })
        
        return {
            'pocai_risk': pocai_risk,
            'pocai_years': pocai_years,
            'summary': self._generate_wealth_summary(pocai_risk, pocai_years)
        }
    
    def analyze_official_timing(self,
                                bazi_data: BaziData,
                                dayun_list: List[Tuple[str, str, int, int]],
                                liunian_list: List[Tuple[str, str, int]]) -> Dict[str, Any]:
        """
        分析官运时间
        
        理论依据：
        - 《三命通会》："有官喜财运，财生官"
        - "有七杀喜食伤运，食伤制杀"
        - "官欲运生"
        """
        pillars = bazi_data.get_pillars()
        day_master = bazi_data.get_day_master()
        
        # 1. 分析命局中的官星
        official_stars = {'正官': [], '偏官': [], '七杀': []}
        for pos, (gan, zhi) in pillars.items():
            ten_god = get_ten_god(day_master, gan)
            if ten_god in ['正官', '偏官', '七杀']:
                official_stars[ten_god].append(pos)
        
        # 2. 分析大运中的官运时机
        guanyun_opportunities = []
        
        for gan, zhi, start_age, end_age in dayun_list:
            gan_ten_god = get_ten_god(day_master, gan)
            
            opportunity_level = 0
            opportunity_reasons = []
            
            # 2.1 检查官印相生
            if gan_ten_god == '正官':
                # 检查是否有印星（简化：检查地支是否有印星）
                # 这里需要更复杂的判断，简化处理
                opportunity_level += 15
                opportunity_reasons.append('正官大运，官印相生')
            
            # 2.2 检查财生官
            if gan_ten_god in ['正财', '偏财']:
                if len(official_stars['正官']) > 0 or len(official_stars['偏官']) > 0:
                    opportunity_level += 12
                    opportunity_reasons.append('财生官，财运助官运')
            
            # 2.3 检查食伤制杀
            if gan_ten_god in ['食神', '伤官']:
                if len(official_stars['七杀']) > 0:
                    opportunity_level += 15
                    opportunity_reasons.append('食伤制杀，英雄独压万人')
            
            if opportunity_level >= 10:
                guanyun_opportunities.append({
                    'type': '官运',
                    'period': f'{start_age}-{end_age}岁',
                    'dayun': f'{gan}{zhi}',
                    'level': '高' if opportunity_level >= 20 else '中',
                    'reason': '；'.join(opportunity_reasons),
                    'advice': '宜把握机遇，积极进取，注重能力提升和人际关系'
                })
        
        # 3. 分析流年中的升官年份
        shengguan_years = []
        
        for gan, zhi, year in liunian_list:
            liunian_ten_god = get_ten_god(day_master, gan)
            
            if liunian_ten_god == '正官' and len(official_stars['正官']) > 0:
                shengguan_years.append({
                    'year': year,
                    'ganzhi': f'{gan}{zhi}',
                    'reason': '流年正官，官运提升',
                    'level': '中'
                })
        
        return {
            'guanyun_opportunities': guanyun_opportunities,
            'shengguan_years': shengguan_years,
            'summary': self._generate_official_summary(guanyun_opportunities, shengguan_years)
        }
    
    # ============ 辅助方法 ============
    
    def _is_sanxing_in_dayun(self, dayun_zhi: str, pillars: Dict) -> bool:
        """检查大运地支是否参与三刑"""
        all_branches = [pillars[pos][1] for pos in ['year', 'month', 'day', 'hour']]
        all_branches.append(dayun_zhi)
        
        # 检查三刑组合
        yinsi_shen = {'寅', '巳', '申'}
        chou_xu_wei = {'丑', '戌', '未'}
        
        yinsi_count = sum(1 for b in all_branches if b in yinsi_shen)
        chou_xu_wei_count = sum(1 for b in all_branches if b in chou_xu_wei)
        
        # 无恩之刑：至少3个
        if yinsi_count >= 3:
            return True
        
        # 恃势之刑：至少3个
        if chou_xu_wei_count >= 3:
            return True
        
        # 无礼之刑
        if '子' in all_branches and '卯' in all_branches:
            return True
        
        return False
    
    def _is_guanfu_in_dayun(self, dayun_zhi: str, pillars: Dict) -> bool:
        """检查大运是否遇官符"""
        year_branch = pillars['year'][1]
        dizhi_order = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        year_index = dizhi_order.index(year_branch)
        guanfu_index = (year_index + 5) % 12
        guanfu_branch = dizhi_order[guanfu_index]
        return dayun_zhi == guanfu_branch
    
    def _is_goujiao_in_dayun(self, dayun_zhi: str, pillars: Dict, bazi_data: BaziData) -> bool:
        """检查大运是否遇勾绞"""
        year_branch = pillars['year'][1]
        gender = bazi_data.gender  # 🔥 修复：直接使用gender属性，不使用get_gender()方法
        year_gan = pillars['year'][0]
        
        dizhi_order = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        year_index = dizhi_order.index(year_branch)
        
        yang_gan = {'甲', '丙', '戊', '庚', '壬'}
        is_yang_gan = year_gan in yang_gan
        
        if (is_yang_gan and gender == '男') or (not is_yang_gan and gender == '女'):
            gou_index = (year_index + 3) % 12
            jiao_index = (year_index - 3) % 12
            gou_branch = dizhi_order[gou_index]
            jiao_branch = dizhi_order[jiao_index]
        else:
            jiao_index = (year_index + 3) % 12
            gou_index = (year_index - 3) % 12
            gou_branch = dizhi_order[gou_index]
            jiao_branch = dizhi_order[jiao_index]
        
        return dayun_zhi in [gou_branch, jiao_branch]
    
    def _is_zhaisha_in_dayun(self, dayun_zhi: str, pillars: Dict) -> bool:
        """检查大运是否遇灾煞"""
        all_branches = [pillars[pos][1] for pos in ['year', 'month', 'day', 'hour']]
        
        sanhe_zhaisha_map = {
            ('申', '子', '辰'): '午',
            ('寅', '午', '戌'): '子',
            ('巳', '酉', '丑'): '卯',
            ('亥', '卯', '未'): '酉',
        }
        
        for sanhe_branches, zhaisha_branch in sanhe_zhaisha_map.items():
            sanhe_count = sum(1 for b in sanhe_branches if b in all_branches)
            if sanhe_count >= 3 and dayun_zhi == zhaisha_branch:
                return True
        
        return False
    
    def _get_yangren_zhi(self, day_master: str) -> str:
        """获取羊刃地支"""
        yangren_map = {
            '甲': '卯', '乙': '寅', '丙': '午', '丁': '巳',
            '戊': '午', '己': '巳', '庚': '酉', '辛': '申',
            '壬': '子', '癸': '亥'
        }
        return yangren_map.get(day_master, '')
    
    def _is_sanxing_in_liunian(self, liunian_gan: str, liunian_zhi: str,
                               pillars: Dict, day_master: str) -> bool:
        """检查流年是否与命局三刑"""
        all_branches = [pillars[pos][1] for pos in ['year', 'month', 'day', 'hour']]
        all_branches.append(liunian_zhi)
        
        yinsi_shen = {'寅', '巳', '申'}
        chou_xu_wei = {'丑', '戌', '未'}
        
        yinsi_count = sum(1 for b in all_branches if b in yinsi_shen)
        chou_xu_wei_count = sum(1 for b in all_branches if b in chou_xu_wei)
        
        if yinsi_count >= 3 or chou_xu_wei_count >= 3:
            return True
        
        if '子' in all_branches and '卯' in all_branches:
            return True
        
        return False
    
    def _is_zhaisha_in_liunian(self, liunian_zhi: str, pillars: Dict) -> bool:
        """检查流年是否遇灾煞"""
        all_branches = [pillars[pos][1] for pos in ['year', 'month', 'day', 'hour']]
        
        sanhe_zhaisha_map = {
            ('申', '子', '辰'): '午',
            ('寅', '午', '戌'): '子',
            ('巳', '酉', '丑'): '卯',
            ('亥', '卯', '未'): '酉',
        }
        
        for sanhe_branches, zhaisha_branch in sanhe_zhaisha_map.items():
            sanhe_count = sum(1 for b in sanhe_branches if b in all_branches)
            if sanhe_count >= 3 and liunian_zhi == zhaisha_branch:
                return True
        
        return False
    
    def _generate_disaster_summary(self, laoyu_risk, yiwai_risk, laoyu_years, yiwai_years) -> str:
        """生成灾祸总结"""
        summary_parts = []
        
        if laoyu_risk:
            high_risk = [r for r in laoyu_risk if r['level'] == '高']
            if high_risk:
                summary_parts.append(f"牢狱风险较高时段：{', '.join([r['period'] for r in high_risk])}")
        
        if yiwai_risk:
            high_risk = [r for r in yiwai_risk if r['level'] == '高']
            if high_risk:
                summary_parts.append(f"意外风险较高时段：{', '.join([r['period'] for r in high_risk])}")
        
        if laoyu_years:
            summary_parts.append(f"需注意的年份：{', '.join([str(y['year']) for y in laoyu_years])}")
        
        if yiwai_years:
            summary_parts.append(f"需格外小心的年份：{', '.join([str(y['year']) for y in yiwai_years])}")
        
        if not summary_parts:
            return "综合分析，命局相对平稳，无特别明显的牢狱和意外风险。"
        
        return "。".join(summary_parts) + "。建议在这些时段和年份，需格外谨慎，循法守序，注意安全。"
    
    def _generate_wealth_summary(self, pocai_risk, pocai_years) -> str:
        """生成破财总结"""
        summary_parts = []
        
        if pocai_risk:
            high_risk = [r for r in pocai_risk if r['level'] == '高']
            if high_risk:
                summary_parts.append(f"破财风险较高时段：{', '.join([r['period'] for r in high_risk])}")
        
        if pocai_years:
            summary_parts.append(f"需注意理财的年份：{', '.join([str(y['year']) for y in pocai_years])}")
        
        if not summary_parts:
            return "综合分析，财运相对平稳，无特别明显的破财风险。"
        
        return "。".join(summary_parts) + "。建议在这些时段和年份，需谨慎理财，避免大额投资和合伙。"
    
    def _generate_official_summary(self, guanyun_opportunities, shengguan_years) -> str:
        """生成官运总结"""
        summary_parts = []
        
        if guanyun_opportunities:
            high_opp = [o for o in guanyun_opportunities if o['level'] == '高']
            if high_opp:
                summary_parts.append(f"官运机会较好时段：{', '.join([o['period'] for o in high_opp])}")
        
        if shengguan_years:
            summary_parts.append(f"有望升官的年份：{', '.join([str(y['year']) for y in shengguan_years])}")
        
        if not summary_parts:
            return "综合分析，官运一般，需把握机遇，积极进取。"
        
        return "。".join(summary_parts) + "。建议在这些时段和年份，积极把握机遇，注重能力提升和人际关系。"
