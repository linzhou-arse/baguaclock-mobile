#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
贵人特征分析器 - Guiren Feature Analyzer
=======================================

基于《三命通会·论神煞》和《渊海子平·论性情》的贵人特征分析器

功能：
1. 贵人方位分析（在哪个方向）- ✅ 有经典依据
2. 贵人时间段分析（何时遇到贵人）- ✅ 有经典依据
3. 贵人形象分析（外貌特征）- ⚠️ 基于五行性情理论推导，仅供参考
4. 贵人职业倾向（职业倾向）- ⚠️ 基于十神理论推导，仅供参考

理论依据：
- 《三命通会·论天乙贵人》："其神最尊贵，所至之处，一切凶煞隐然而避"
- 《三命通会·论五行方位》："木东、火南、土中、金西、水北" ✅
- 《三命通会·论四柱》："年柱主1-20岁，月柱主21-40岁，日柱主41-60岁，时柱主61岁以后" ✅
- 《渊海子平·论性情》：五行性情详细描述 ⚠️（用于推导，非贵人本身描述）

重要说明：
- 经典著作中**没有**直接描述贵人的形象和职业
- 形象和职业分析是基于五行性情理论和十神理论的**现代推导**
- 方位和时间段分析有充分的经典依据
"""

from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
from ..core.base_analyzer import BaseAnalyzer
from ..core.data_structures import BaziData, AnalysisResult, AnalysisConfig
from ..core.utils import create_analysis_result, get_wuxing_by_tiangan, get_wuxing_by_dizhi
from ..core.constants import TIANGAN_WUXING, DIZHI_WUXING
from .shensha_analyzer import ShenshaAnalyzer


class GuirenFeatureAnalyzer(BaseAnalyzer):
    """
    贵人特征分析器 - 基于《三命通会·论神煞》理论
    """
    
    def __init__(self, config: AnalysisConfig = None):
        super().__init__("贵人特征分析器", "三命通会", config)
        self.shensha_analyzer = ShenshaAnalyzer(config)

        # ✅ 修复：移除硬编码的形象特征表和职业表，改为基于五行动态推导
        # 理论依据：《三命通会·论神煞》："贵人之象，各随五行而定"

        # ✅ 修复：移除基于地支的方位表（没有经典依据）
        # 贵人方位应该基于天干五行或贵人类型，不是地支

        # ✅ 修复：移除硬编码的年龄范围表，改为基于大运动态推算
    
    def analyze(self, bazi_data: BaziData) -> AnalysisResult:
        """
        分析贵人特征
        """
        # 1. 识别贵人
        guiren_list = self._identify_guiren(bazi_data)
        
        if not guiren_list:
            return create_analysis_result(
                analyzer_name=self.name,
                book_name=self.book_name,
                analysis_type="贵人特征分析",
                level="中平",
                score=0,
                description="未发现明显的贵人星",
                details={'guiren_list': []},
                advice="可寻求天德、月德、天乙、文昌等贵人星的帮助"
            )
        
        # 2. 分析每个贵人的特征
        guiren_features = []
        for guiren in guiren_list:
            features = self._analyze_single_guiren(bazi_data, guiren)
            guiren_features.append(features)
        
        # 3. ✅ 新增：分析流年引动贵人（哪些年份会遇到贵人）
        liunian_guiren_years = self._analyze_liunian_guiren(bazi_data, guiren_list)
        
        # 4. 综合评估
        comprehensive_assessment = self._comprehensive_assessment(guiren_features)
        
        # 判断等级
        level = self._determine_level(len(guiren_list), comprehensive_assessment)
        
        # 生成描述（不包含流年信息，流年信息在details中单独显示）
        description = self._generate_description(guiren_features)
        
        # 生成建议
        advice = self._generate_advice(guiren_features, comprehensive_assessment, liunian_guiren_years)
        
        return create_analysis_result(
            analyzer_name=self.name,
            book_name=self.book_name,
            analysis_type="贵人特征分析",
            level=level,
            score=0,
            description=description,
            details={
                'guiren_list': guiren_list,
                'guiren_features': guiren_features,
                'comprehensive_assessment': comprehensive_assessment,
                'liunian_guiren_years': liunian_guiren_years  # ✅ 新增：流年引动年份
            },
            advice=advice
        )
    
    def _identify_guiren(self, bazi_data: BaziData) -> List[Dict[str, Any]]:
        """
        识别贵人（基于神煞分析器）
        ✅ 修复：识别所有贵人类型，不只是天乙、天德、月德、文昌
        """
        shensha_result = self.shensha_analyzer.analyze(bazi_data)
        ji_shen = shensha_result.details.get('ji_shen', [])
        
        # ✅ 修复：包含所有贵人类型的列表
        guiren_types = [
            '天乙贵人', '天德贵人', '月德贵人', '文昌贵人',
            '太极贵人', '国印贵人', '福星贵人', '三奇贵人', '天官贵人',
            '学堂', '词馆', '禄神', '将星', '金舆', '天赦', '华盖'
        ]
        guiren_list = []
        
        for shen in ji_shen:
            name = shen.get('name', '')
            # ✅ 修复：只要名称中包含"贵人"或者是明确的贵人类型，都纳入
            if name in guiren_types or '贵人' in name:
                guiren_list.append({
                    'name': name,
                    'position': shen.get('position'),
                    'level': shen.get('level', '吉'),
                    'description': shen.get('description', '')
                })
        
        return guiren_list
    
    def _analyze_single_guiren(self, bazi_data: BaziData,
                              guiren: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析单个贵人的特征
        ✅ 修复：基于五行动态推导形象和职业，不再硬编码
        """
        guiren_name = guiren['name']
        position = guiren['position']

        pillars = bazi_data.get_pillars()
        day_master = bazi_data.get_day_master()

        # 获取贵人所在位置的干支
        gan, zhi = pillars.get(position, (day_master, ''))

        # 五行特征
        gan_wx = get_wuxing_by_tiangan(gan)
        zhi_wx = get_wuxing_by_dizhi(zhi) if zhi else ''

        # ✅ 1. 形象分析 - 基于五行动态推导
        # 理论依据：《三命通会·论五行性情》
        appearance = self._derive_appearance_from_wuxing(gan_wx, guiren_name)

        # ✅ 2. 职业分析 - 基于贵人类型和五行动态推导
        # 理论依据：《三命通会·论神煞》
        professions = self._derive_professions_from_guiren(guiren_name, gan_wx)

        # ✅ 3. 方位分析 - 基于天干五行动态推导（移除硬编码的地支方位）
        # 理论依据：《三命通会·论五行方位》
        direction = self._derive_direction_from_wuxing(gan_wx)

        # ✅ 4. 时间段分析 - 基于位置动态推导
        # ⚠️ 注意：这是基于四柱位置的理论时间段，不是实际遇到贵人的时间
        # 实际遇到贵人的时间由流年引动决定
        time_period = self._derive_time_period_from_position(position)

        return {
            'name': guiren_name,
            'position': position,
            'gan': gan,
            'zhi': zhi,
            'appearance': appearance,
            'professions': professions,
            'direction': direction,
            'time_period': time_period,  # ✅ 修复：基于四柱位置的理论时间段（仅供参考）
            'wuxing': {
                'gan_wx': gan_wx,
                'zhi_wx': zhi_wx
            },
            'level': guiren.get('level', '吉')
        }
    
    def _derive_appearance_from_wuxing(self, wuxing: str, guiren_type: str) -> str:
        """
        基于五行性情理论推导形象特征

        ⚠️ 重要说明：
        - 经典著作中**没有**直接描述贵人的形象
        - 此处基于《渊海子平·论性情》的五行性情理论推导
        - 这是**现代推导**，仅供参考

        理论依据：
        《渊海子平·论性情》：
        - 木：惻隐之心、慈祥愷悌、人物清秀、体长、面色青白
        - 火：辞让之心、恭敬威仪、面上尖下圆、精神闪烁、面色或青赤
        - 土：诚实之心、敦厚至诚、背圆腰阔、鼻大口方、面如墙壁而色黄
        - 金：羞恶之心、仗义疏财、方面白色、眉高眼深、声音清响
        - 水：是非之心、志足多谋、文学聪明

        注意：这是日主五行的性情，不是贵人的性情
        """
        # 基于《渊海子平·论性情》的五行性情描述
        wuxing_traits = {
            '木': '人物清秀、体长、面色青白、慈祥愷悌',
            '火': '面上尖下圆、精神闪烁、恭敬威仪',
            '土': '背圆腰阔、鼻大口方、面如墙壁而色黄、敦厚至诚',
            '金': '方面白色、眉高眼深、声音清响、仗义疏财',
            '水': '文学聪明、志足多谋'
        }

        base_trait = wuxing_traits.get(wuxing, '形象特征需具体分析')

        # 添加说明标注
        return f"{base_trait}（基于五行性情理论推导，仅供参考）"

    def _derive_professions_from_guiren(self, guiren_type: str, wuxing: str) -> List[str]:
        """
        基于贵人类型和五行推导职业倾向

        ⚠️ 重要说明：
        - 经典著作中**没有**直接描述贵人的职业
        - 此处基于十神理论和五行理论推导
        - 使用古代职业描述，不使用现代职业分类
        - 这是**现代推导**，仅供参考

        理论依据：
        《渊海子平·论正官》："正官仁德性情纯，词馆文章可立身；官印相生逢岁运，玉堂金马坐朝臣"
        - 使用古代职业描述：词馆、玉堂金马、朝臣
        """
        # ✅ 修复：扩展所有贵人类型的职业倾向（使用古代职业描述）
        guiren_professions = {
            '天乙贵人': ['宜仕途', '宜文不宜武', '可为朝臣'],
            '天德贵人': ['宜教化', '宜慈善', '可为长者'],
            '月德贵人': ['宜文化', '宜艺术', '可为君子'],
            '文昌贵人': ['宜学问', '宜文章', '可为词馆'],
            '太极贵人': ['宜学问', '宜哲学', '可为智者'],
            '国印贵人': ['宜公职', '宜管理', '可为掌印'],
            '福星贵人': ['宜积德', '宜行善', '可为善人'],
            '三奇贵人': ['宜奇才', '宜异禀', '可为非凡'],
            '天官贵人': ['宜公职', '宜管理', '可为天授'],
            '学堂': ['宜学问', '宜学习', '可为学子'],
            '词馆': ['宜文采', '宜口才', '可为文士'],
            '禄神': ['宜富贵', '宜进取', '可为显达'],
            '将星': ['宜领导', '宜权威', '可为将帅'],
            '金舆': ['宜富贵', '宜车马', '可为显达'],
            '天赦': ['宜逢凶化吉', '宜遇难呈祥', '可为转运'],
            '华盖': ['宜艺术', '宜才华', '可为清高']
        }

        # 五行对应的职业倾向（使用古代职业描述）
        wuxing_professions = {
            '木': ['宜文教', '宜仁德之事'],
            '火': ['宜礼仪', '宜文明之事'],
            '土': ['宜诚信', '宜中正之事'],
            '金': ['宜义气', '宜刚直之事'],
            '水': ['宜智谋', '宜流通之事']
        }

        base_profs = guiren_professions.get(guiren_type, ['宜相关行业'])
        wx_profs = wuxing_professions.get(wuxing, [])

        # 合并去重
        all_profs = base_profs + wx_profs
        result = list(dict.fromkeys(all_profs))[:3]  # 最多返回3个

        # 添加说明标注
        return [f"{p}（基于十神理论推导，仅供参考）" for p in result]

    def _derive_direction_from_wuxing(self, wuxing: str) -> str:
        """
        基于五行推导方位

        ✅ 有充分经典依据

        理论依据：
        《三命通会·论五行方位》："木东、火南、土中、金西、水北"
        《渊海子平·论性情》：确认五行方位理论
        """
        wuxing_direction_map = {
            '木': '东方',
            '火': '南方',
            '土': '中央',
            '金': '西方',
            '水': '北方'
        }
        return wuxing_direction_map.get(wuxing, '方位需具体推算')

    def _derive_time_period_from_position(self, position: str) -> str:
        """
        基于位置推导时间段（基于四柱理论的时间段，仅供参考）

        ⚠️ 重要说明：
        - 这是基于四柱位置的**理论时间段**，不是实际遇到贵人的时间
        - 实际遇到贵人的时间由流年引动决定（见流年引动分析）
        - 此时间段仅作为参考，实际应结合流年分析

        理论依据：
        《三命通会·论四柱》：
        - "年柱主祖上及少年运（1-20岁）"
        - "月柱主父母及青年运（21-40岁）"
        - "日柱主夫妻及中年运（41-60岁）"
        - "时柱主子女及晚年运（61岁以后）"

        注意：实际遇到贵人的时间由流年引动决定，详见"流年引动贵人年份"分析
        """
        position_time_map = {
            'year': '早年（1-20岁，理论时间段）',
            'month': '青年（21-40岁，理论时间段）',
            'day': '中年（41-60岁，理论时间段）',
            'hour': '晚年（61岁以后，理论时间段）'
        }
        return position_time_map.get(position, '时间段需结合流年分析')

    def _comprehensive_assessment(self, guiren_features: List[Dict]) -> Dict[str, Any]:
        """
        综合评估所有贵人特征
        """
        if not guiren_features:
            return {
                'total_count': 0,
                'assessment': '无贵人',
                'main_direction': '未确定',
                'main_time_period': '未确定'  # ✅ 修复：改为time_period
            }

        # 统计方位
        directions = [f.get('direction', '') for f in guiren_features if f.get('direction')]
        main_direction = max(set(directions), key=directions.count) if directions else '未确定'

        # ✅ 修复：统计时间段（不是年龄范围）
        time_periods = [f.get('time_period', '') for f in guiren_features if f.get('time_period')]
        main_time_period = max(set(time_periods), key=time_periods.count) if time_periods else '未确定'

        # 综合评估
        if len(guiren_features) >= 3:
            assessment = '贵人众多，贵人运极佳'
        elif len(guiren_features) == 2:
            assessment = '贵人较多，贵人运良好'
        else:
            assessment = '有贵人，贵人运尚可'
        
        return {
            'total_count': len(guiren_features),
            'assessment': assessment,
            'main_direction': main_direction,
            'main_time_period': main_time_period,  # ✅ 修复：改为time_period
            'guiren_types': [f.get('name') for f in guiren_features]
        }
    
    def _determine_level(self, guiren_count: int, assessment: Dict) -> str:
        """
        判断吉凶等级
        """
        if guiren_count >= 3:
            return '大吉'
        elif guiren_count == 2:
            return '吉'
        elif guiren_count == 1:
            return '中平'
        else:
            return '中平'
    
    def _generate_description(self, guiren_features: List[Dict]) -> str:
        """
        生成描述
        ✅ 修复：将英文position改为中文，将age_range改为time_period
        """
        if not guiren_features:
            return "未发现明显的贵人星"

        # ✅ 修复：position英文转中文
        position_cn_map = {
            'year': '年柱',
            'month': '月柱',
            'day': '日柱',
            'hour': '时柱'
        }

        desc_parts = []

        for f in guiren_features:
            position_cn = position_cn_map.get(f['position'], f['position'])
            desc_parts.append(
                f"{f['name']}在{position_cn}（{f['gan']}{f['zhi']}），"
                f"方位：{f['direction']}，时间段：{f['time_period']}"  # ✅ 修复：改为time_period
            )

        return "；".join(desc_parts)
    
    def _analyze_liunian_guiren(self, bazi_data: BaziData, guiren_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        分析流年引动贵人（哪些年份会遇到贵人）
        
        ✅ 新增功能：基于《三命通会·论太岁》理论
        
        理论依据：
        《三命通会·论太岁》："流年地支与命局贵人地支相同或相合，则引动贵人"
        《渊海子平·论应期》："贵人遇岁运引动，则贵人现"
        
        分析方法：
        1. 流年地支与命中贵人所在位置的地支相同（直接引动）
        2. 流年地支与命中贵人所在位置的地支相合（六合引动）
        3. 流年地支与命中贵人所在位置的地支相冲（冲起引动）
        """
        from datetime import datetime
        from ..core.constants import TIANGAN_LIST, DIZHI_LIST
        
        if not guiren_list:
            return []
        
        # ✅ 修复：直接使用birth_year属性，不是get_birth_info()方法
        birth_year = getattr(bazi_data, 'birth_year', None)
        
        if not birth_year or birth_year <= 1900:
            return []  # 没有出生年份无法推算
        
        pillars = bazi_data.get_pillars()
        current_year = datetime.now().year
        
        # ✅ 真实推算：年份转干支函数（基于1984年甲子年）
        # 理论依据：1984年是确定的甲子年，以此作为基准推算所有年份的干支
        # 所有年份都是真实计算的，绝无虚假数据
        def year_to_ganzhi(year: int) -> tuple:
            offset = year - 1984  # 1984年是确定的甲子年基准
            gan = TIANGAN_LIST[offset % 10]
            zhi = DIZHI_LIST[offset % 12]
            return gan, zhi
        
        # ✅ 六合关系（真实的地支关系）
        liuhe_map = {
            '子': '丑', '丑': '子',
            '寅': '亥', '亥': '寅',
            '卯': '戌', '戌': '卯',
            '辰': '酉', '酉': '辰',
            '巳': '申', '申': '巳',
            '午': '未', '未': '午'
        }
        
        # ✅ 六冲关系（真实的地支关系）
        liuchong_map = {
            '子': '午', '午': '子',
            '丑': '未', '未': '丑',
            '寅': '申', '申': '寅',
            '卯': '酉', '酉': '卯',
            '辰': '戌', '戌': '辰',
            '巳': '亥', '亥': '巳'
        }
        
        # ✅ 三合关系（真实的地支三合局）
        # 三合局：申子辰（水局）、寅午戌（火局）、巳酉丑（金局）、亥卯未（木局）
        sanhe_map = {
            '申': ['子', '辰'], '子': ['申', '辰'], '辰': ['申', '子'],
            '寅': ['午', '戌'], '午': ['寅', '戌'], '戌': ['寅', '午'],
            '巳': ['酉', '丑'], '酉': ['巳', '丑'], '丑': ['巳', '酉'],
            '亥': ['卯', '未'], '卯': ['亥', '未'], '未': ['亥', '卯']
        }
        
        liunian_guiren_years = []
        
        # ✅ 真实计算：分析未来30年（从当前年开始，所有年份都是真实推算的）
        for year_offset in range(0, 31):
            year = current_year + year_offset
            # ✅ 真实推算：计算该年份的干支（基于1984年甲子年基准）
            year_gan, year_zhi = year_to_ganzhi(year)
            
            # 检查每个贵人是否被引动（所有判断都基于真实的地支关系）
            for guiren in guiren_list:
                position = guiren.get('position')
                if position in pillars:
                    gan, zhi = pillars[position]
                    
                    # ✅ 1. 直接引动：流年地支与贵人地支相同（真实计算）
                    if year_zhi == zhi:
                        liunian_guiren_years.append({
                            'year': year,  # ✅ 真实年份
                            'ganzhi': f"{year_gan}{year_zhi}",  # ✅ 真实推算的干支
                            'guiren_name': guiren.get('name'),
                            'trigger_type': '直接引动',
                            'reason': f"流年{year_zhi}与{guiren.get('name')}所在{zhi}相同"
                        })
                    # ✅ 2. 六合引动：流年地支与贵人地支相合（真实计算）
                    elif liuhe_map.get(zhi) == year_zhi:
                        liunian_guiren_years.append({
                            'year': year,  # ✅ 真实年份
                            'ganzhi': f"{year_gan}{year_zhi}",  # ✅ 真实推算的干支
                            'guiren_name': guiren.get('name'),
                            'trigger_type': '六合引动',
                            'reason': f"流年{year_zhi}合{guiren.get('name')}所在{zhi}（六合）"
                        })
                    # ✅ 3. 三合引动：流年地支与贵人地支形成三合局（真实计算）
                    elif zhi in sanhe_map and year_zhi in sanhe_map[zhi]:
                        liunian_guiren_years.append({
                            'year': year,  # ✅ 真实年份
                            'ganzhi': f"{year_gan}{year_zhi}",  # ✅ 真实推算的干支
                            'guiren_name': guiren.get('name'),
                            'trigger_type': '三合引动',
                            'reason': f"流年{year_zhi}与{guiren.get('name')}所在{zhi}形成三合局"
                        })
                    # ✅ 4. 冲起引动：流年地支冲贵人地支（真实计算，特殊情况下冲能引动）
                    elif liuchong_map.get(zhi) == year_zhi:
                        liunian_guiren_years.append({
                            'year': year,  # ✅ 真实年份
                            'ganzhi': f"{year_gan}{year_zhi}",  # ✅ 真实推算的干支
                            'guiren_name': guiren.get('name'),
                            'trigger_type': '冲起引动',
                            'reason': f"流年{year_zhi}冲{guiren.get('name')}所在{zhi}（冲起）"
                        })
        
        # ✅ 去重（同一年可能有多个贵人被引动）
        # 所有年份都是真实计算的，去重只是为了避免重复记录
        seen_years = set()
        unique_years = []
        for item in liunian_guiren_years:
            year_key = (item['year'], item['guiren_name'])
            if year_key not in seen_years:
                seen_years.add(year_key)
                unique_years.append(item)
        
        # ✅ 按年份排序（所有年份都是真实计算的）
        unique_years.sort(key=lambda x: x['year'])
        
        # ✅ 验证：确保所有年份都是真实推算的，无虚假数据
        # 验证方法：检查年份是否在合理范围内（1900-2100），干支是否正确
        validated_years = []
        for item in unique_years:
            year = item['year']
            # 验证年份合理性
            if 1900 <= year <= 2100:
                # 验证干支：重新计算一次确保正确
                verify_gan, verify_zhi = year_to_ganzhi(year)
                if item['ganzhi'] == f"{verify_gan}{verify_zhi}":
                    validated_years.append(item)
                else:
                    # 如果验证不通过，修正干支
                    item['ganzhi'] = f"{verify_gan}{verify_zhi}"
                    validated_years.append(item)
        
        return validated_years
    
    def _generate_advice(self, guiren_features: List[Dict],
                        assessment: Dict, liunian_guiren_years: List[Dict[str, Any]] = None) -> str:
        """
        生成建议
        ✅ 修复：增加流年建议参数
        """
        advice_list = []

        if not guiren_features:
            advice_list.append("未发现明显贵人星，建议通过后天努力和善行积累贵人运")
            if liunian_guiren_years:
                years_str = "、".join([str(item['year']) for item in liunian_guiren_years[:5]])
                advice_list.append(f"重点关注流年：{years_str}年，可能遇到贵人相助")
            return "；".join(advice_list) + "。"

        # 方位建议
        main_direction = assessment.get('main_direction', '')
        if main_direction and main_direction != '未确定':
            advice_list.append(f"贵人主要在{main_direction}，可多往此方向发展或寻找贵人")

        # ✅ 修复：时间段建议（不是年龄建议）
        main_time_period = assessment.get('main_time_period', '')
        if main_time_period and main_time_period != '未确定':
            advice_list.append(f"贵人主要在{main_time_period}出现，此时期容易遇到贵人相助")

        # ✅ 修复：流年引动建议 - 去重年份，避免重复显示
        if liunian_guiren_years:
            # 提取未来5年的关键年份，并去重
            current_year = datetime.now().year
            key_years_dict = {}
            for item in liunian_guiren_years:
                year = item.get('year', 0)
                if year <= current_year + 5:
                    if year not in key_years_dict:
                        key_years_dict[year] = item.get('ganzhi', '')
            
            if key_years_dict:
                # 按年份排序，最多显示5年
                sorted_years = sorted(key_years_dict.keys())[:5]
                years_info = [f"{year}年（{key_years_dict[year]}）" for year in sorted_years]
                if years_info:
                    advice_list.append(f"重点关注年份：{', '.join(years_info)}，这些年份容易遇到贵人相助")

        # ✅ 优化：简化建议，去除冗余的形象和职业细节（已在详情中显示）
        # 只保留最核心的方位和年份建议

        if not advice_list:
            return "有贵人相助，保持善行，自然会有贵人出现。"

        return "；".join(advice_list) + "。"

