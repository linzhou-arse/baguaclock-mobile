#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地命理分析引擎 - 完全本地化实现
基于传统命理学理论，不依赖任何外部API
包含：五行分析、十神分析、格局判断、用神分析、大运流年等
"""

class LocalMingliAnalyzer:
    """本地命理分析器 - 纯本地规则引擎"""
    
    def __init__(self):
        """初始化命理分析器"""
        # 天干列表
        self.tiangan_list = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        
        # ... existing code ...
        self.tiangan_wuxing = {
            '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
            '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'
        }

        # 初始化基础神煞系统
        self.init_basic_shensha()
        
        # 天干阴阳属性（参《渊海子平·阴阳章》）
        self.tiangan_yinyang = {
            '甲': '阳', '乙': '阴', '丙': '阳', '丁': '阴', '戊': '阳',
            '己': '阴', '庚': '阳', '辛': '阴', '壬': '阳', '癸': '阴'
        }
        
        # 地支五行属性（参《三命通会·地支司令》）
        self.dizhi_wuxing = {
            '子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土', '巳': '火',
            '午': '火', '未': '土', '申': '金', '酉': '金', '戌': '土', '亥': '水'
        }
        
        # 地支藏干（参《三命通会·藏干篇》）
        self.dizhi_canggan = {
            '子': ['癸'],
            '丑': ['己', '癸', '辛'],
            '寅': ['甲', '丙', '戊'],
            '卯': ['乙'],
            '辰': ['戊', '乙', '癸'],
            '巳': ['丙', '戊', '庚'],
            '午': ['丁', '己'],
            '未': ['己', '丁', '乙'],
            '申': ['庚', '壬', '戊'],
            '酉': ['辛'],
            '戌': ['戊', '辛', '丁'],
            '亥': ['壬', '甲']
        }
        # 藏干权重以本气/中气/余气为 0.6/0.3/0.1（参《子平真诠》多数学者注释）
        self.canggan_weight_map = {
            1: [1.0],
            2: [0.7, 0.3],
            3: [0.6, 0.3, 0.1]
        }
        # 禄位、羊刃位（参《三命通会·禄命篇》《渊海子平·禄刃歌》）
        self.lu_branch_map = {
            '甲': '寅', '乙': '卯', '丙': '巳', '丁': '午',
            '戊': '巳', '己': '午', '庚': '申', '辛': '酉',
            '壬': '亥', '癸': '子'
        }
        self.yangren_branch_map = {
            '甲': '卯', '乙': '寅', '丙': '午', '丁': '巳',
            '戊': '午', '己': '巳', '庚': '酉', '辛': '申',
            '壬': '子', '癸': '亥'
        }
        
        # 五行生克关系（参《滴天髓·五行章》）
        self.wuxing_sheng = {
            '木': '火', '火': '土', '土': '金', '金': '水', '水': '木'
        }
        self.wuxing_ke = {
            '木': '土', '火': '金', '土': '水', '金': '木', '水': '火'
        }
        
        # 十神关系表（参《渊海子平·十神章》）
        self.shishen_rules = {
            '同': {'阳阳': '比肩', '阴阴': '比肩', '阳阴': '劫财', '阴阳': '劫财'},
            '生我': {'阳阳': '偏印', '阴阴': '偏印', '阳阴': '正印', '阴阳': '正印'},
            '我生': {'阳阳': '食神', '阴阴': '食神', '阳阴': '伤官', '阴阳': '伤官'},
            '克我': {'阳阳': '偏官', '阴阴': '偏官', '阳阴': '正官', '阴阳': '正官'},
            '我克': {'阳阳': '偏财', '阴阴': '偏财', '阳阴': '正财', '阴阳': '正财'}
        }
    
    def analyze_bazi(self, pillars, gender='男', birth_info=None):
        """
        完整的八字分析
        pillars: {'year': '甲子', 'month': '丙寅', 'day': '戊辰', 'hour': '庚申'}
        返回详细的命理分析报告
        """
        try:
            # 解析四柱
            year_gan, year_zhi = pillars['year'][0], pillars['year'][1]
            month_gan, month_zhi = pillars['month'][0], pillars['month'][1]
            day_gan, day_zhi = pillars['day'][0], pillars['day'][1]
            hour_gan, hour_zhi = pillars['hour'][0], pillars['hour'][1]
            
            day_master = day_gan  # 日主
            
            # 1. 五行分析
            wuxing_analysis = self.analyze_wuxing(pillars)
            
            # 2. 十神分析
            shishen_analysis = self.analyze_shishen(day_master, pillars)
            
            # 3. 格局分析
            geju_analysis = self.analyze_geju(day_master, pillars, shishen_analysis)
            
            # 4. 旺衰分析
            wangshuai_analysis = self.analyze_wangshuai(day_master, month_zhi, pillars)
            
            # 5. 用神分析
            yongshen_analysis = self.analyze_yongshen(day_master, wuxing_analysis, wangshuai_analysis)
            
            # 6. 性格分析
            character_analysis = self.analyze_character(day_master, shishen_analysis, geju_analysis)
            
            # 7. 事业财运分析
            career_wealth = self.analyze_career_wealth(shishen_analysis, geju_analysis, gender)
            
            # 8. 六亲分析
            sixqin = self.analyze_sixqin(shishen_analysis, pillars, day_master, gender, wangshuai_analysis)
            
            # 9. 婚姻感情分析
            marriage = self.analyze_marriage(shishen_analysis, day_master, gender, pillars, wangshuai_analysis, birth_info)
            
            # 10. 健康分析
            health = self.analyze_health(wuxing_analysis, day_master)
            
            # 11. 大运分析
            dayun = self.analyze_dayun(day_master, gender, birth_info)
            
            # 12. 五行补救分析
            wuxing_remedy = self.analyze_wuxing_remedy(wuxing_analysis, yongshen_analysis)
            
            # 13. 需要在build_report中检验是否不会重複输出财運信息
            # (analyze_detailed_wealth的功能丂经整合到analyze_career_wealth)
            
            # 组装完整报告
            report = self.build_report(
                pillars, day_master, gender,
                wuxing_analysis, shishen_analysis, geju_analysis,
                wangshuai_analysis, yongshen_analysis,
                character_analysis, career_wealth, sixqin, marriage, health, dayun, wuxing_remedy
            )
            
            # 返回包含local_analysis_text的字典，供显示层调用
            return {
                'local_analysis_text': report,
                'pillars': pillars,
                'day_master': day_master,
                'gender': gender,
                'wuxing_analysis': wuxing_analysis,
                'shishen_analysis': shishen_analysis,
                'geju_analysis': geju_analysis,
                'wangshuai_analysis': wangshuai_analysis,
                'yongshen_analysis': yongshen_analysis,
                'character_analysis': character_analysis,
                'career_wealth': career_wealth,
                'sixqin': sixqin,
                'marriage': marriage,
                'health': health,
                'dayun': dayun,
                'wuxing_remedy': wuxing_remedy
            }
            
        except Exception as e:
            return f"命理分析失败：{str(e)}"
    
    def analyze_wuxing(self, pillars):
        """五行分析（参照干支权重推算）"""
        wuxing_count = {'木': 0.0, '火': 0.0, '土': 0.0, '金': 0.0, '水': 0.0}
        
        # 统计天干与地支藏干权重
        for pos in ['year', 'month', 'day', 'hour']:
            gan = pillars[pos][0]
            zhi = pillars[pos][1]
            wuxing_count[self.tiangan_wuxing[gan]] += 1.0  # 天干均记 1 分
            
            hidden_list = self.dizhi_canggan.get(zhi, [])
            weights = self.canggan_weight_map.get(len(hidden_list), [1.0])
            for idx, hidden_gan in enumerate(hidden_list):
                weight = weights[idx] if idx < len(weights) else weights[-1]
                wuxing_count[self.tiangan_wuxing[hidden_gan]] += weight
        
        total = sum(wuxing_count.values())
        wuxing_percent = {k: round(v / total * 100, 1) for k, v in wuxing_count.items()} if total else {k: 0 for k in wuxing_count}
        
        missing = [k for k, v in wuxing_count.items() if v == 0]
        strong = [k for k, v in wuxing_percent.items() if v >= 30]
        weak = [k for k, v in wuxing_percent.items() if 0 < v < 10]
        
        return {
            'count': wuxing_count,
            'percent': wuxing_percent,
            'missing': missing,
            'strong': strong,
            'weak': weak,
            'summary': self.wuxing_summary(wuxing_count, missing, strong, weak)
        }
    
    def wuxing_summary(self, count, missing, strong, weak):
        """五行总结（含干支权重）"""
        summary_parts = ["五行分布（含藏干权重）："]
        for wx, num in count.items():
            summary_parts.append(f"{wx}{round(num, 1)}")
        summary = " ".join(summary_parts)
        
        if missing:
            summary += f"\n五行缺{','.join(missing)}"
        if strong:
            summary += f"\n五行{','.join(strong)}偏旺"
        if weak:
            summary += f"\n五行{','.join(weak)}偏弱"
        
        return summary
    
    def analyze_shishen(self, day_master, pillars):
        """十神分析"""
        shishen_result = {}
        day_wuxing = self.tiangan_wuxing[day_master]
        day_yinyang = self.tiangan_yinyang[day_master]
        
        for pos in ['year', 'month', 'day', 'hour']:
            if pos == 'day':
                continue  # 日柱不计算十神
            
            gan = pillars[pos][0]
            gan_wuxing = self.tiangan_wuxing[gan]
            gan_yinyang = self.tiangan_yinyang[gan]
            
            # 判断五行关系
            if gan_wuxing == day_wuxing:
                relation = '同'
            elif self.wuxing_sheng.get(gan_wuxing) == day_wuxing:
                relation = '生我'
            elif self.wuxing_sheng.get(day_wuxing) == gan_wuxing:
                relation = '我生'
            elif self.wuxing_ke.get(gan_wuxing) == day_wuxing:
                relation = '克我'
            elif self.wuxing_ke.get(day_wuxing) == gan_wuxing:
                relation = '我克'
            else:
                relation = '同'
            
            # 判断阴阳关系
            if day_yinyang == gan_yinyang:
                yinyang_relation = '阳阳' if day_yinyang == '阳' else '阴阴'
            else:
                yinyang_relation = '阳阴' if day_yinyang == '阳' else '阴阳'
            
            # 获取十神
            shishen = self.shishen_rules[relation][yinyang_relation]
            shishen_result[pos] = {
                'gan': gan,
                'shishen': shishen,
                'wuxing': gan_wuxing
            }
        
        # 统计十神数量
        shishen_count = {}
        for pos_data in shishen_result.values():
            ss = pos_data['shishen']
            shishen_count[ss] = shishen_count.get(ss, 0) + 1
        
        return {
            'detail': shishen_result,
            'count': shishen_count,
            'summary': self.shishen_summary(shishen_count)
        }
    
    def shishen_summary(self, count):
        """十神总结"""
        if not count:
            return "十神分布均衡"
        
        summary = "十神：" + "、".join([f"{k}{v}个" for k, v in count.items()])
        return summary
    
    def analyze_geju(self, day_master, pillars, shishen_analysis):
        """
        格局分析 - 基于《子平真诠》《神峰通考》
        包含格局真假判断和特殊格局识别
        """
        shishen_count = shishen_analysis['count']
        month_shishen = shishen_analysis['detail'].get('month', {}).get('shishen', '')

        # 1. 首先检查特殊格局（从格、化格等）
        special_geju = self._check_special_patterns(day_master, pillars, shishen_analysis)
        if special_geju['is_special']:
            return {
                'type': special_geju['type'],
                'description': special_geju['description'],
                'month_shishen': month_shishen,
                'is_true_geju': True,
                'geju_level': '特殊格局'
            }

        # 2. 判断正格格局
        geju_info = self._judge_normal_geju(day_master, pillars, shishen_analysis)

        # 3. 格局真假判断
        geju_truth = self._judge_geju_truth(day_master, pillars, geju_info)

        # 4. 格局清浊判断
        geju_quality = self._judge_geju_quality(pillars, geju_info)

        # 5. 组合格局描述
        final_type = geju_info['type']
        final_desc = geju_info['description']

        # 添加真假清浊信息
        if not geju_truth['is_true']:
            final_type += "（假格）"
            final_desc += f"；{geju_truth['reason']}"
        else:
            final_type += "（真格）"

        if geju_quality['level'] == '浊':
            final_desc += f"；格局偏浊，{geju_quality['reason']}"
        elif geju_quality['level'] == '清':
            final_desc += "；格局清纯"

        return {
            'type': final_type,
            'pattern_type': final_type,  # ✅ 修复：添加兼容字段名
            'pattern': final_type,  # ✅ 修复：添加兼容字段名
            'description': final_desc,
            'summary': final_desc,  # ✅ 修复：添加兼容字段名
            'month_shishen': month_shishen,
            'is_true_geju': geju_truth['is_true'],
            'geju_level': geju_quality['level'],
            # ========== P1-3修复：格局三关评分 ==========
            'huwei_guan_score': geju_truth['score'] if 'score' in geju_truth else 85,  # 护卫关（真假判断）
            'zhenhua_guan_score': geju_truth['score'] if 'score' in geju_truth else 85,  # 真假关
            'qingchun_guan_score': geju_quality['score'] if 'score' in geju_quality else 70  # 清纯关
        }

    def _check_special_patterns(self, day_master, pillars, shishen_analysis):
        """检查特殊格局（从格、化格等）"""
        day_wuxing = self.tiangan_wuxing[day_master]
        shishen_count = shishen_analysis['count']

        # 检查从格
        cong_info = self._check_cong_ge(day_master, pillars, shishen_analysis)
        if cong_info['is_cong']:
            return {
                'is_special': True,
                'type': cong_info['type'],
                'description': cong_info['description']
            }

        # 检查化格
        hua_info = self._check_hua_ge(day_master, pillars, shishen_analysis)
        if hua_info['is_hua']:
            return {
                'is_special': True,
                'type': hua_info['type'],
                'description': hua_info['description']
            }

        return {'is_special': False}

    def _check_cong_ge(self, day_master, pillars, shishen_analysis, level=None):
        """检查从格（从财、从官、从儿等）"""
        day_wuxing = self.tiangan_wuxing[day_master]

        # 统计生扶日主的力量
        support_power = 0
        weaken_power = 0

        for pos in ['year', 'month', 'day', 'hour']:
            gan = pillars[pos][0]
            zhi = pillars[pos][1]

            gan_wuxing = self.tiangan_wuxing[gan]
            zhi_wuxing = self.dizhi_wuxing[zhi]

            # 统计生扶力量（印、比劫）
            if gan_wuxing == day_wuxing:
                support_power += 10
            elif self.wuxing_sheng.get(gan_wuxing) == day_wuxing:
                support_power += 8

            if zhi_wuxing == day_wuxing:
                support_power += 6
            elif self.wuxing_sheng.get(zhi_wuxing) == day_wuxing:
                support_power += 5

            # 统计克泄耗力量（官杀、财、食伤）
            if self.wuxing_ke.get(gan_wuxing) == day_wuxing:
                weaken_power += 8
            elif self.wuxing_sheng.get(day_wuxing) == gan_wuxing:
                weaken_power += 7
            elif self.wuxing_ke.get(day_wuxing) == gan_wuxing:
                weaken_power += 6

            if self.wuxing_ke.get(zhi_wuxing) == day_wuxing:
                weaken_power += 5
            elif self.wuxing_sheng.get(day_wuxing) == zhi_wuxing:
                weaken_power += 4
            elif self.wuxing_ke.get(day_wuxing) == zhi_wuxing:
                weaken_power += 3

        # 判断是否为从格
        if support_power < 10 and weaken_power > 30:
            # 身弱，旺官杀或财星，可成从格
            shishen_count = shishen_analysis['count']

            if shishen_count.get('正官', 0) + shishen_count.get('偏官', 0) >= 2:
                return {
                    'is_cong': True,
                    'type': '从官格',
                    'description': '日主极弱，官杀极旺，弃命从官，宜武职或执法'
                }
            elif shishen_count.get('正财', 0) + shishen_count.get('偏财', 0) >= 2:
                return {
                    'is_cong': True,
                    'type': '从财格',
                    'description': '日主极弱，财星极旺，弃命从财，宜经商或理财'
                }
            elif shishen_count.get('食神', 0) + shishen_count.get('伤官', 0) >= 2:
                return {
                    'is_cong': True,
                    'type': '从儿格',
                    'description': '日主极弱，食伤极旺，弃命从儿，宜技艺或创造'
                }

        return {'is_cong': False}

    def _check_hua_ge(self, day_master, pillars, shishen_analysis):
        """检查化格（甲己化土、乙庚化金等）"""
        # 简化版化格判断
        year_gan = pillars['year'][0]
        month_gan = pillars['month'][0]
        day_gan = pillars['day'][0]  # 即日主
        hour_gan = pillars['hour'][0]

        # 检查是否有合化条件
        hua_pairs = {
            ('甲', '己'): '土',
            ('乙', '庚'): '金',
            ('丙', '辛'): '水',
            ('丁', '壬'): '木',
            ('戊', '癸'): '火'
        }

        # 检查日主与其他天干能否合化
        for other_gan in [year_gan, month_gan, hour_gan]:
            for (gan1, gan2), element in hua_pairs.items():
                if (day_gan == gan1 and other_gan == gan2) or (day_gan == gan2 and other_gan == gan1):
                    # 检查化神是否得时得地（简化判断）
                    month_zhi = pillars['month'][1]
                    month_element = self.dizhi_wuxing[month_zhi]

                    if month_element == element or self.wuxing_sheng.get(month_element) == element:
                        return {
                            'is_hua': True,
                            'type': f'{gan1}{gan2}化{element}格',
                            'description': f'日主与{other_gan}合化，得月令相扶，化格成真'
                        }

        return {'is_hua': False}

    def _judge_normal_geju(self, day_master, pillars, shishen_analysis):
        """判断正格格局"""
        shishen_count = shishen_analysis['count']
        month_shishen = shishen_analysis['detail'].get('month', {}).get('shishen', '')

        geju_type = "普通格局"
        geju_desc = ""

        # 以月令为主判断格局（《子平真诠》月令为提纲）
        if month_shishen in ['正官', '偏官']:
            geju_type = "官杀格"
            geju_desc = "月令透官杀，以官杀为用神，宜从政或管理"
        elif month_shishen in ['正财', '偏财']:
            # ========== 关键修复：区分财格 vs 伤官格 ==========
            # 原则：伤官生财优先于纯财格判断
            # 依据《子平真诠》《滴天髓》：伤官是食神别名，生财更有力
            shiyinshang = shishen_count.get('食神', 0) + shishen_count.get('伤官', 0)
            
            if shiyinshang >= 1:
                # 伤官格（伤官生财）：月令财星基础上，有伤官出现
                # 特征：伤官出众，秋冬生人尤其好
                # 含义：借伤官之力生财，财源更丰富
                geju_type = "伤官格"
                geju_desc = "月令透伤官，伤官生财格，以伤官生财为用，宜技艺和商贸"
            else:
                # 纯财格：仅有月令财星，无伤官辅助
                # 特征：财源来自正常经营
                # 含义：以财为主，稳健理财
                geju_type = "财格"
                geju_desc = "月令透财星，以财为用神，宜经商或理财"
        elif month_shishen in ['正印', '偏印']:
            geju_type = "印格"
            geju_desc = "月令透印星，以印为用神，宜文化教育"
        elif month_shishen in ['食神', '伤官']:
            geju_type = "食伤格"
            geju_desc = "月令透食伤，以食伤为用神，宜技艺创作"
        elif month_shishen in ['比肩', '劫财']:
            geju_type = "比劫格"
            geju_desc = "月令透比劫，以比劫为用神，宜合作共事"

        # 添加组合信息
        if shishen_count.get('正官', 0) + shishen_count.get('偏官', 0) >= 2:
            geju_type += "（官杀混杂）"
            geju_desc += "；官杀并见，需清其混杂"

        if shishen_count.get('正财', 0) + shishen_count.get('偏财', 0) >= 2:
            geju_desc += "；财星多见，财运较佳但需防财多身弱"

        # 检查是否有财官双美
        if (shishen_count.get('正官', 0) + shishen_count.get('偏官', 0) >= 1 and
            shishen_count.get('正财', 0) + shishen_count.get('偏财', 0) >= 1):
            geju_type = "财官格"
            geju_desc = "财官双美，宜仕途经商并举"

        return {
            'type': geju_type,
            'description': geju_desc,
            'main_shishen': month_shishen
        }

    def _judge_geju_truth(self, day_master, pillars, geju_info):
        """
        判断格局真假（《子平真诠》格局真理论）
        真格判定标准：
        1. 月令未被冲克
        2. 格局主用神有根
        3. 优先类需要有力推动
        """
        month_branch = pillars['month'][1]
        main_shishen = geju_info.get('main_shishen', '')
        
        is_true = True
        reason = "格局真实"
        score = 85  # 真格基础分数
        
        # ========== 检查一：月令是否被冲克 ==========
        # 冲瑸关系：子午冲、丑未冲、寥丑冲、卑于冲
        chong_pairs = [('子', '午'), ('午', '子'), ('丑', '未'), ('未', '丑'),
                      ('寥', '丑'), ('丑', '寥'), ('卑', '于'), ('于', '卑')]
        
        for pos in ['year', 'day', 'hour']:
            if pillars[pos][1] != month_branch and (month_branch, pillars[pos][1]) in chong_pairs:
                is_true = False
                reason = "月令被冲，格局不真"
                score = 45  # 被冲的格局贫弱
                break
        
        # ========== 检查二：主用神是否有根 ==========
        if is_true and main_shishen:
            has_root = False
            
            # 检查外三柱是否有根
            for pos in ['year', 'month', 'hour']:
                gan = pillars[pos][0]
                zhi = pillars[pos][1]
                # 检查天乾是否是主用神
                from classic_analyzer.shishen_tables import get_ten_god_from_table
                try:
                    if get_ten_god_from_table(day_master, gan) == main_shishen:
                        has_root = True
                        break
                except:
                    # fallback：直接检查五行
                    if main_shishen in ['正官', '偏官'] and self.tiangan_wuxing[gan] in ['金', '土']:
                        has_root = True
                        break
                    elif main_shishen in ['正财', '偏财'] and day_master != gan:
                        has_root = True
                        break
            
            if not has_root:
                is_true = False
                reason = "格局主用神无根，力量不足"
                score = 50  # 有根提上分数
        
        return {
            'is_true': is_true,
            'reason': reason,
            'score': score  # 新增：真假判断的评分
        }

    def _judge_geju_quality(self, pillars, geju_info):
        """
        判断格局清浊（《子平真诠》清浊论）
        清浊判定标准：
        1. 清格：地支三合或不有冲克——，提高端帅人员
        2. 浊格：有冲宁、三一——（刀斧斗剑）、猪厉三合（无情之合）
        3. 中——：其他情况
        """
        # 检查地支冲克情况
        all_branches = [pillars[pos][1] for pos in ['year', 'month', 'day', 'hour']]
        
        # 冲柬关系
        chong_pairs = [('子', '午'), ('午', '子'), ('丑', '未'), ('未', '丑'),
                      ('卯', '酉'), ('酉', '卯'), ('寅', '申'), ('申', '寅'), ('巳', '亥'), ('亥', '巳')]
        
        # 客柳关系（三一——）
        kehan_pairs = [('子', '丑'), ('十', '该'), ('卡', '上'),
                      ('卓', '下')]
        
        # 合关系：三合、六一合
        he_triples = [('子', '辉', '毛'), ('丑', '守', '未'),
                     ('宣', '阿', '丑'), ('卓', '午', '帅')]
        
        conflicts = 0
        kehan = 0
        triple_he = 0
        
        # 检查冲克
        for i, b1 in enumerate(all_branches):
            for b2 in all_branches[i+1:]:
                if (b1, b2) in chong_pairs or (b2, b1) in chong_pairs:
                    conflicts += 1
        
        # 检查客柳（三一——）——最憎，表一人惠惧整日精
        for i, b1 in enumerate(all_branches):
            for b2 in all_branches[i+1:]:
                if (b1, b2) in kehan_pairs or (b2, b1) in kehan_pairs:
                    kehan += 1
        
        # 检查三合——表示一人娘沉然，也是有祸的
        for triple in he_triples:
            count = sum(1 for b in all_branches if b in triple)
            if count == 3:
                triple_he += 1
        
        # ========== 清浊判定逻辑 ==========
        level = '中'
        reason = ''
        score = 70  # 基础中格分
        
        if kehan >= 2:
            # ——客柳——————最憎！！！
            level = '浊'
            reason = '客柳——————一人惠惧整日'
            score = 30
        elif conflicts >= 2:
            # ——冲——————也是有祸，但不如客柳严重
            level = '浊'
            reason = '冲——————一人凯江不不骨'
            score = 45
        elif triple_he >= 1:
            # ——三合——也是不清的
            level = '浊'
            reason = '三合——————一人娘沉然'
            score = 50
        else:
            # 清格：没有冲克冲、客柳、三合
            level = '清'
            reason = '清————————绵阳贵气'
            score = 85
        
        return {
            'level': level,
            'reason': reason,
            'score': score  # 新增：清浊判定的评分
        }
    
    def _detect_special_geju(self, day_master, pillars, shishen_analysis):
        """检测常见特殊格局（禄格、羊刃格、财官双美等）"""
        result = {'type': '', 'description': ''}
        month_branch = pillars['month'][1]
        lu_branch = self.lu_branch_map.get(day_master)
        ren_branch = self.yangren_branch_map.get(day_master)
        
        # 禄格：月令得禄且天干透禄（《三命通会·禄命篇》）
        if lu_branch and month_branch == lu_branch:
            for pos in ['year', 'month', 'day', 'hour']:
                if pillars[pos][0] == day_master:
                    result['type'] = "禄格"
                    result['description'] = "月令得禄，天干复透，主科名仕途"
                    break
        
        # 羊刃格：月令为羊刃（《渊海子平·禄刃歌》）
        if not result['type'] and ren_branch and month_branch == ren_branch:
            result['type'] = "羊刃格"
            result['description'] = "月令坐羊刃，性格刚烈，宜武职或自由行业"
        
        # 财官双美：财星、官星数量均衡（《子平真诠·格局评注》）
        shishen_count = shishen_analysis['count']
        if shishen_count.get('正官', 0) + shishen_count.get('偏官', 0) >= 1 \
                and shishen_count.get('正财', 0) + shishen_count.get('偏财', 0) >= 1:
            desc = "财官双美，宜仕途经商并举"
            if result['description']:
                result['description'] += "；" + desc
            else:
                result['description'] = desc
            if not result['type']:
                result['type'] = "财官双美"
        
        return result
    
    def analyze_wangshuai(self, day_master, month_zhi, pillars):
        """旺衰分析"""
        # 简化版：根据月令判断旺衰
        day_wuxing = self.tiangan_wuxing[day_master]
        month_wuxing = self.dizhi_wuxing[month_zhi]
        
        strength = 50  # 基础分数
        
        # 月令得令
        if month_wuxing == day_wuxing:
            strength += 30
            status = "得令"
        elif self.wuxing_sheng.get(month_wuxing) == day_wuxing:
            strength += 20
            status = "得生"
        elif self.wuxing_ke.get(month_wuxing) == day_wuxing:
            strength -= 20
            status = "受克"
        else:
            status = "平"
        
        # 根据同类五行数量调整
        same_count = 0
        for pos in ['year', 'month', 'day', 'hour']:
            gan = pillars[pos][0]
            if self.tiangan_wuxing[gan] == day_wuxing:
                same_count += 1
        
        strength += (same_count - 1) * 10
        
        # 判断旺衰等级
        if strength >= 80:
            level = "太旺"
        elif strength >= 60:
            level = "偏旺"
        elif strength >= 40:
            level = "中和"
        elif strength >= 20:
            level = "偏弱"
        else:
            level = "太弱"
        
        # ✅ 修复：计算身强身弱比例（用于更准确的判断）
        strength_ratio = strength / 100.0 if strength > 0 else 0.0
        
        return {
            'strength': strength,
            'level': level,
            'strength_level': level,  # ✅ 修复：添加兼容字段名
            'strength_ratio': strength_ratio,  # ✅ 修复：添加身强身弱比例
            'ratio': strength_ratio,  # ✅ 修复：添加兼容字段名
            'status': status,
            'description': f"日主{day_master}({day_wuxing})在{month_zhi}月{status}，身{level}"
        }
    
    def analyze_yongshen(self, day_master, wuxing_analysis, wangshuai_analysis):
        """
        用神分析 - 基于《滴天髓》《穷通宝鉴》调候用神理论
        结合身旺身弱与调候需求综合判断用神
        """
        day_wuxing = self.tiangan_wuxing[day_master]
        strength = wangshuai_analysis['strength']

        # 1. 首先考虑调候用神（最优先）
        tiaohou_yongshen = self._get_tiaohou_yongshen(day_master, wuxing_analysis)

        # 2. 然后考虑身旺身弱的平衡用神
        if strength >= 60:
            # 身旺，需要克泄耗
            balance_yongshen = [
                self.wuxing_ke[day_wuxing],  # 克我者（官杀）
                self.wuxing_sheng.get(day_wuxing),  # 我生者（食伤）
            ]
            yongshen_type = "身旺宜克泄"
            balance_advice = "身旺旺相，宜克泄耗以平衡"
        else:
            # 身弱，需要生扶
            # 找生我者
            sheng_wo = None
            for wx, sheng in self.wuxing_sheng.items():
                if sheng == day_wuxing:
                    sheng_wo = wx
                    break

            balance_yongshen = [
                sheng_wo,  # 生我者（印）
                day_wuxing,  # 同类（比劫）
            ]
            yongshen_type = "身弱宜生扶"
            balance_advice = "身弱衰微，宜生扶助以助身"

        # 3. 综合判断：调候优先，兼顾平衡
        final_yongshen = tiaohou_yongshen['wuxing'] if tiaohou_yongshen['wuxing'] else balance_yongshen

        # 4. 过滤None值和重复
        final_yongshen = list(set([wx for wx in final_yongshen if wx]))

        # 5. 构建完整分析
        if tiaohou_yongshen['wuxing']:
            # 有调候用神，优先考虑调候
            description = f"调候用神：{','.join(tiaohou_yongshen['wuxing'])}，{tiaohou_yongshen['reason']}"
            description += f"；{balance_advice}"
            advice = f"首选{','.join(tiaohou_yongshen['wuxing'])}调候，兼顾{','.join(balance_yongshen)}平衡"
        else:
            # 无明显调候需求，按平衡选
            description = f"平衡用神：{','.join(final_yongshen)}，{balance_advice}"
            advice = f"宜用{','.join(final_yongshen)}{yongshen_type}"

        return {
            'wuxing': final_yongshen,
            'type': yongshen_type,
            'advice': advice,
            'description': description,
            'tiaohou': tiaohou_yongshen,
            'balance': {
                'wuxing': balance_yongshen,
                'type': yongshen_type
            }
        }

    def _get_tiaohou_yongshen(self, day_master, wuxing_analysis):
        """
        获取调候用神 - 基于《穷通宝鉴》调候理论
        调候用神主要用于调节命局的寒暖燥湿
        """
        day_wuxing = self.tiangan_wuxing[day_master]
        wuxing_count = wuxing_analysis['count']
        strong = wuxing_analysis['strong']
        weak = wuxing_analysis['weak']

        # 调候原则（简化版）
        # 1. 调节五行过旺过弱
        # 2. 调节寒暖燥湿
        # 3. 特殊情况的调候需求

        tiaohou_wuxing = []
        reason = ""

        # 五行强弱调候
        if strong:
            # 有过旺五行，需要克泄耗
            for strong_wuxing in strong:
                ke_wuxing = self.wuxing_ke.get(strong_wuxing)
                if ke_wuxing and ke_wuxing not in tiaohou_wuxing:
                    tiaohou_wuxing.append(ke_wuxing)
                    reason += f"过旺{strong_wuxing}宜{ke_wuxing}制；"

                sheng_wuxing = None
                for wx, sheng in self.wuxing_sheng.items():
                    if wx == strong_wuxing:
                        sheng_wuxing = sheng
                        break
                if sheng_wuxing and sheng_wuxing not in tiaohou_wuxing:
                    tiaohou_wuxing.append(sheng_wuxing)
                    reason += f"过旺{strong_wuxing}宜{sheng_wuxing}泄；"

        if weak:
            # 有过弱五行，需要生扶
            for weak_wuxing in weak:
                sheng_wuxing = None
                for wx, sheng in self.wuxing_sheng.items():
                    if sheng == weak_wuxing:
                        sheng_wuxing = wx
                        break
                if sheng_wuxing and sheng_wuxing not in tiaohou_wuxing:
                    tiaohou_wuxing.append(sheng_wuxing)
                    reason += f"过弱{weak_wuxing}宜{sheng_wuxing}补；"

                tonglei_wuxing = weak_wuxing
                if tonglei_wuxing not in tiaohou_wuxing:
                    tiaohou_wuxing.append(tonglei_wuxing)
                    reason += f"过弱{weak_wuxing}宜同类助；"

        # 特殊调候需求（基于日主五行）
        special_tiaohou = self._get_special_tiaohou(day_wuxing)
        if special_tiaohou['wuxing']:
            tiaohou_wuxing.extend([wx for wx in special_tiaohou['wuxing'] if wx not in tiaohou_wuxing])
            reason += special_tiaohou['reason']

        # 去重
        tiaohou_wuxing = list(set(tiaohou_wuxing))

        if not tiaohou_wuxing:
            return {
                'wuxing': [],
                'reason': "命局相对平衡，无特殊调候需求"
            }

        return {
            'wuxing': tiaohou_wuxing,
            'reason': reason.rstrip('；')
        }

    def _get_special_tiaohou(self, day_wuxing):
        """
        获取特殊调候需求 - 基于日主五行的特殊需求
        参考《穷通宝鉴》各日主调候法
        """
        special_map = {
            '甲': {
                'wuxing': ['水', '土'],
                'reason': "甲木参天，赖水滋养，土培根"
            },
            '乙': {
                'wuxing': ['火', '水'],
                'reason': "乙木花草，宜火暖，水润"
            },
            '丙': {
                'wuxing': ['水', '木'],
                'reason': "丙火太阳，赖水济，木生"
            },
            '丁': {
                'wuxing': ['木', '金'],
                'reason': "丁火灯烛，需木添，金助"
            },
            '戊': {
                'wuxing': ['火', '木'],
                'reason': "戊土高山，宜火暖，木疏"
            },
            '己': {
                'wuxing': ['火', '土'],
                'reason': "己土田园，需火照，土助"
            },
            '庚': {
                'wuxing': ['火', '土'],
                'reason': "庚金顽铁，宜火炼，土生"
            },
            '辛': {
                'wuxing': ['土', '水'],
                'reason': "辛金珠玉，赖土养，水洗"
            },
            '壬': {
                'wuxing': ['土', '木'],
                'reason': "壬水江河，需土堤，木引"
            },
            '癸': {
                'wuxing': ['土', '金'],
                'reason': "癸水雨露，要土承，金生"
            }
        }

        return special_map.get(day_wuxing, {'wuxing': [], 'reason': ""})

    def init_basic_shensha(self):
        """初始化基础神煞系统 - 基于《渊海子平》神煞章"""

        # 天乙贵人（最重要的吉神，逢凶化吉）
        self.tianyi_guiren = {
            '甲': ['丑', '未'], '戊': ['丑', '未'],
            '乙': ['子', '申'], '己': ['子', '申'],
            '丙': ['亥', '酉'], '丁': ['亥', '酉'],
            '庚': ['丑', '未'], '辛': ['寅', '午'],
            '壬': ['卯', '巳'], '癸': ['卯', '巳']
        }

        # 文昌贵人（利学业功名）
        self.wenchang_guiren = {
            '甲': '巳', '乙': '午', '丙': '申', '丁': '酉',
            '戊': '申', '己': '酉', '庚': '亥', '辛': '子',
            '壬': '寅', '癸': '卯'
        }

        # 驿马星（主动、变动、出行）
        self.yima = {
            '申': ['寅', '午', '戌'],  # 申子辰马在寅
            '子': ['寅', '午', '戌'],  # 申子辰马在寅
            '辰': ['寅', '午', '戌'],  # 申子辰马在寅
            '寅': ['巳', '酉', '丑'],  # 寅午戌马在巳
            '午': ['巳', '酉', '丑'],  # 寅午戌马在巳
            '戌': ['巳', '酉', '丑'],  # 寅午戌马在巳
            '巳': ['亥', '卯', '未'],  # 巳酉丑马在亥
            '酉': ['亥', '卯', '未'],  # 巳酉丑马在亥
            '丑': ['亥', '卯', '未'],  # 巳酉丑马在亥
            '亥': ['申', '子', '辰'],  # 亥卯未马在巳
            '卯': ['申', '子', '辰'],  # 亥卯未马在巳
            '未': ['申', '子', '辰'],  # 亥卯未马在巳
        }

        # 桃花星（感情、魅力）
        self.taohua = {
            '申': ['酉'],  # 申子辰见酉为桃花
            '子': ['酉'],  # 申子辰见酉为桃花
            '辰': ['酉'],  # 申子辰见酉为桃花
            '寅': ['卯'],  # 寅午戌见卯为桃花
            '午': ['卯'],  # 寅午戌见卯为桃花
            '戌': ['卯'],  # 寅午戌见卯为桃花
            '巳': ['午'],  # 巳酉丑见午为桃花
            '酉': ['午'],  # 巳酉丑见午为桃花
            '丑': ['午'],  # 巳酉丑见午为桃花
            '亥': ['子'],  # 亥卯未见子为桃花
            '卯': ['子'],  # 亥卯未见子为桃花
            '未': ['子'],  # 亥卯未见子为桃花
        }

        # 华盖星（艺术、宗教、孤独）
        self.huagai = {
            '申': ['辰'],  # 申子辰见辰为华盖
            '子': ['辰'],  # 申子辰见辰为华盖
            '辰': ['辰'],  # 申子辰见辰为华盖
            '寅': ['戌'],  # 寅午戌见戌为华盖
            '午': ['戌'],  # 寅午戌见戌为华盖
            '戌': ['戌'],  # 寅午戌见戌为华盖
            '巳': ['丑'],  # 巳酉丑见丑为华盖
            '酉': ['丑'],  # 巳酉丑见丑为华盖
            '丑': ['丑'],  # 巳酉丑见丑为华盖
            '亥': ['未'],  # 亥卯未见未为华盖
            '卯': ['未'],  # 亥卯未见未为华盖
            '未': ['未'],  # 亥卯未见未为华盖
        }

    def analyze_shensha(self, day_master, pillars):
        """
        神煞分析 - 基于《渊海子平》神煞章
        分析主要吉凶神煞
        """
        day_gan = pillars['day'][0]
        year_zhi = pillars['year'][1]
        month_zhi = pillars['month'][1]
        day_zhi = pillars['day'][1]
        hour_zhi = pillars['hour'][1]

        all_zhi = [year_zhi, month_zhi, day_zhi, hour_zhi]
        shensha_result = {
            '吉神': [],
            '凶神': [],
            '桃花': [],
            '贵人': [],
            '总结': ''
        }

        # 1. 天乙贵人（最高吉神）
        tianyi_list = self.tianyi_guiren.get(day_gan, [])
        for zhi in all_zhi:
            if zhi in tianyi_list:
                location = self._get_zhi_position(zhi, pillars)
                shensha_result['贵人'].append(f"天乙贵人在{location}")
                shensha_result['吉神'].append(f"天乙贵人{location}，逢凶化吉，得贵人相助")

        # 2. 文昌贵人（利学业）
        wenchang_zhi = self.wenchang_guiren.get(day_gan)
        if wenchang_zhi and wenchang_zhi in all_zhi:
            location = self._get_zhi_position(wenchang_zhi, pillars)
            shensha_result['吉神'].append(f"文昌贵人{location}，利学业功名，聪明智慧")

        # 3. 驿马星（主动变动）
        day_branch_group = self._get_sanhema_group(day_zhi)
        if day_branch_group:
            yima_list = self.yima.get(day_zhi, [])
            for zhi in all_zhi:
                if zhi in yima_list:
                    location = self._get_zhi_position(zhi, pillars)
                    shensha_result['吉神'].append(f"驿马星{location}，主变动、出行、事业有变动之象")
                    break

        # 4. 桃花星（感情魅力）
        day_branch_group = self._get_sanhema_group(day_zhi)
        if day_branch_group:
            taohua_list = self.taohua.get(day_zhi, [])
            for zhi in all_zhi:
                if zhi in taohua_list and zhi != day_zhi:
                    location = self._get_zhi_position(zhi, pillars)
                    shensha_result['桃花'].append(f"桃花{location}，主感情魅力，异性缘佳")
                    break

        # 5. 华盖星（艺术宗教）
        day_branch_group = self._get_sanhema_group(day_zhi)
        if day_branch_group:
            huagai_list = self.huagai.get(day_zhi, [])
            for zhi in all_zhi:
                if zhi in huagai_list:
                    location = self._get_zhi_position(zhi, pillars)
                    shensha_result['吉神'].append(f"华盖{location}，主艺术才华，宗教缘分，性格略带孤独")
                    break

        # 6. 生成总结
        summary_parts = []
        if shensha_result['贵人']:
            summary_parts.append(f"贵人助力：{len(shensha_result['贵人'])}位")
        if shensha_result['桃花']:
            summary_parts.append(f"桃花遇缘：{len(shensha_result['桃花'])}个")
        if not shensha_result['吉神'] and not shensha_result['桃花']:
            summary_parts.append("神煞平和，命局稳健")

        shensha_result['总结'] = "；".join(summary_parts) if summary_parts else "神煞分布均衡"

        return shensha_result

    def _get_sanhema_group(self, zhi):
        """获取地支所属三合局"""
        groups = {
            '申': '申子辰', '子': '申子辰', '辰': '申子辰',
            '寅': '寅午戌', '午': '寅午戌', '戌': '寅午戌',
            '巳': '巳酉丑', '酉': '巳酉丑', '丑': '巳酉丑',
            '亥': '亥卯未', '卯': '亥卯未', '未': '亥卯未'
        }
        return groups.get(zhi)

    def _get_zhi_position(self, zhi, pillars):
        """获取地支所在位置"""
        for pos in ['year', 'month', 'day', 'hour']:
            if pillars[pos][1] == zhi:
                pos_name = {'year': '年支', 'month': '月支', 'day': '日支', 'hour': '时支'}
                return pos_name[pos]
        return "未知位置"
    
    def analyze_character(self, day_master, shishen_analysis, geju_analysis):
        """性格分析"""
        day_wuxing = self.tiangan_wuxing[day_master]
        shishen_count = shishen_analysis['count']
        
        # 基于日主五行的性格特点
        wuxing_character = {
            '木': "仁慈正直，积极进取，有同情心，喜欢帮助他人，但有时过于理想化",
            '火': "热情开朗，积极乐观，有领导才能，但有时急躁冲动",
            '土': "诚实守信，稳重踏实，有责任心，但有时过于保守",
            '金': "果断坚毅，重视原则，有正义感，但有时过于严格",
            '水': "聪明灵活，善于变通，有智慧，但有时过于圆滑"
        }
        
        base_character = wuxing_character.get(day_wuxing, "性格特点待分析")
        
        # 基于十神的性格补充
        character_details = []
        
        if shishen_count.get('比肩', 0) + shishen_count.get('劫财', 0) >= 2:
            character_details.append("独立自主，有主见，重视朋友")
        
        if shishen_count.get('食神', 0) + shishen_count.get('伤官', 0) >= 2:
            character_details.append("思维活跃，富有创造力，表达能力强")
        
        if shishen_count.get('正财', 0) + shishen_count.get('偏财', 0) >= 2:
            character_details.append("务实理性，善于理财，注重物质")
        
        if shishen_count.get('正官', 0) + shishen_count.get('偏官', 0) >= 2:
            character_details.append("有责任感，遵守规则，适合管理")
        
        if shishen_count.get('正印', 0) + shishen_count.get('偏印', 0) >= 2:
            character_details.append("好学上进，重视精神，有文化修养")
        
        return {
            'base': base_character,
            'details': character_details,
            'summary': base_character + ("；" + "；".join(character_details) if character_details else "")
        }
    
    def analyze_career_wealth(self, shishen_analysis, geju_analysis, gender):
        """
        事业财运分析 - 基于《渊海子平》《滴天髓》经典理论
        重新设计财运评分体系，考虑格局、身旺身弱、财星有根无根等因素
        """
        shishen_count = shishen_analysis['count']
        geju_type = geju_analysis['type']

        career_advice = []
        wealth_analysis = []

        # 1. 基于格局的事业建议（保持原有正确内容）
        if '官杀' in geju_type:
            career_advice.append("适合公职、管理、执法类工作")
            if shishen_count.get('正官', 0) >= 1:
                career_advice.append("可从事政府机关、国企等体制内管理岗位")
        if '财格' in geju_type or '财官双美' in geju_type:
            career_advice.append("适合商业、金融、贸易类工作")
            wealth_analysis.append("财格成真，利于经营理财")
        if '印格' in geju_type:
            career_advice.append("适合文化、教育、科研类工作")
        if '食伤格' in geju_type:
            career_advice.append("适合技术、创意、传媒等需要表达创作的行业")
        if '禄格' in geju_type:
            career_advice.append("可掌实权，适合担任关键岗位")
            wealth_analysis.append("禄位临身，名利双收")
        if '从财格' in geju_type:
            career_advice.append("宜专注商业经营，投资理财")
            wealth_analysis.append("从财格，弃命从财，财运亨通")
        if '从官格' in geju_type:
            career_advice.append("宜从政、军警、法律等")
            wealth_analysis.append("从官格，官旺为用，仕途有望")

        # 2. 经典财运评分体系
        wealth_score = self._calculate_classic_wealth_score(shishen_analysis, geju_analysis)

        # 3. 财运等级判断（按经典理论调整）
        wealth_level = self._judge_wealth_level(wealth_score, shishen_analysis, geju_analysis)

        # 4. 财运详细分析
        wealth_detail = self._analyze_wealth_details(shishen_analysis, geju_analysis, gender)

        # 5. 组合建议
        final_advice = career_advice + [f"财运等级：{wealth_level}"] + wealth_analysis + wealth_detail

        return {
            'advice': final_advice,
            'wealth_level': wealth_level,
            'wealth_score': wealth_score,
            'summary': "\n".join(final_advice)
        }

    def _calculate_classic_wealth_score(self, shishen_analysis, geju_analysis):
        """
        计算经典财运评分 - 基于《渊海子平》《滴天髓》
        评分标准：
        1. 财星数量和质量（最重要）
        2. 官星护财能力
        3. 食伤生财辅助
        4. 比劫竞争压力
        5. 格局对财运的放大或削弱
        """
        shishen_count = shishen_analysis['count']
        geju_type = geju_analysis['type']

        # 基础分数：50分（代表"普通")
        wealth_score = 50.0

        # ========== 核心因素1：财星识别（占比40%） ==========
        zheng_cai = shishen_count.get('正财', 0)  # 正财：稳定收入
        pian_cai = shishen_count.get('偏财', 0)  # 偏财：机遇收入
        total_cai = zheng_cai + pian_cai

        if total_cai == 0:
            # ✅ 修复：无财星时，根据其他因素细化评分，避免所有人都是25.0
            # 基础分数：25分（无财星）
            wealth_score = 25.0
            
            # 即使无财星，也要考虑其他因素：
            # 1. 食伤生财潜力（虽然没有财星，但食伤可以生财）
            shiyinshang = shishen_count.get('食神', 0) + shishen_count.get('伤官', 0)
            if shiyinshang >= 2:
                wealth_score += 8.0  # 食伤多，有生财潜力
            elif shiyinshang == 1:
                wealth_score += 4.0
            
            # 2. 格局加成（特殊格局即使无财星也有财运）
            if '从财格' in geju_type:
                wealth_score += 15.0  # 从财格即使无财星也有财运
            elif '从官格' in geju_type:
                wealth_score += 10.0  # 从官格，官能生财
            elif '财官格' in geju_type or '财格' in geju_type:
                wealth_score += 5.0  # 财格即使无财星也有一定财运
            
            # 3. 比劫影响（比劫多会降低财运）
            bijie = shishen_count.get('比肩', 0) + shishen_count.get('劫财', 0)
            if bijie >= 3:
                wealth_score -= 5.0  # 比劫过多，即使无财星也会被争夺资源
            elif bijie >= 2:
                wealth_score -= 3.0
            
            # 确保最低分不低于20分
            wealth_score = max(20.0, wealth_score)
        elif total_cai == 1:
            # 单财星：稳定但有限
            if zheng_cai == 1:
                wealth_score += 20.0  # 正财稳定
            else:
                wealth_score += 15.0  # 偏财机遇
        elif total_cai >= 2:
            # 多财星：机遇丰富
            wealth_score += 25.0 + (total_cai - 2) * 5.0  # 每增加一个财星+5分

        # ========== 核心因素2：官星护财能力（占比25%） ==========
        guan_sha = shishen_count.get('正官', 0) + shishen_count.get('偏官', 0)
        if guan_sha >= 1 and total_cai >= 1:
            # 官星护财：保护财富
            wealth_score += 12.0
        elif guan_sha == 0 and total_cai >= 1:
            # 无官护财：财富易失
            wealth_score -= 8.0

        # ========== 核心因素3：食伤生财辅助（占比20%） ==========
        shiyinshang = shishen_count.get('食神', 0) + shishen_count.get('伤官', 0)
        if shiyinshang >= 1 and total_cai >= 1:
            # 食伤生财：财源充足
            wealth_score += 10.0
        elif shiyinshang >= 2 and total_cai >= 1:
            # 食伤多：生财能力强
            wealth_score += 5.0

        # ========== 核心因素4：比劫竞争（占比15%） ==========
        bijie = shishen_count.get('比肩', 0) + shishen_count.get('劫财', 0)
        if bijie >= 1 and total_cai >= 1:
            # 比劫夺财：竞争压力大
            wealth_score -= bijie * 6.0
        elif bijie >= 2:
            # 比劫过多：财星易被夺
            wealth_score = max(20.0, wealth_score - 20.0)  # 至少保留20分

        # ========== 额外因素：印星耗财（可选）==========
        yin_shen = shishen_count.get('正印', 0) + shishen_count.get('偏印', 0)
        if yin_shen >= 2 and total_cai >= 1:
            # 印多耗财：削弱财运
            wealth_score -= 5.0

        # ========== 格局放大或削弱系数 ==========
        if '从财格' in geju_type and total_cai >= 1:
            # 从财格：财运最佳
            wealth_score = min(95.0, wealth_score + 30.0)
        elif '财格' in geju_type and '（真格）' in geju_type and total_cai >= 1:
            # 财格成真：财运优良
            wealth_score += 20.0
        elif '财格' in geju_type and '（假格）' in geju_type:
            # 财格不真：削弱效果
            wealth_score -= 10.0
        elif '财官双美' in geju_type and total_cai >= 1:
            # 财官双美：名利双收
            wealth_score += 15.0

        # ========== 最终约束 ==========
        # 确保分数在合理范围（10-100分）
        return max(10.0, min(100.0, wealth_score))

    def _judge_wealth_level(self, wealth_score, shishen_analysis, geju_analysis):
        """
        判断财运等级 - 按经典理论划分，综合考虑多个因素
        等级：巨富、大富、中富、小富、普通、偏弱
        """
        shishen_count = shishen_analysis['count']
        geju_type = geju_analysis['type']
        total_cai = shishen_count.get('正财', 0) + shishen_count.get('偏财', 0)

        # 基础等级判断
        if wealth_score >= 90:
            level = "巨富"
        elif wealth_score >= 75:
            level = "大富"
        elif wealth_score >= 60:
            level = "中富"
        elif wealth_score >= 45:
            level = "小富"
        elif wealth_score >= 30:
            level = "普通"
        else:
            level = "偏弱"

        # 特殊格局强化或削弱
        if '从财格' in geju_type and total_cai >= 1 and wealth_score >= 70:
            level = "巨富"  # 从财格更容易致富
        elif '财格' in geju_type and '（真格）' in geju_type and total_cai >= 1:
            # 财格成真进一步提升
            if level == "中富":
                level = "大富"
            elif level == "小富":
                level = "中富"
        elif '财格' in geju_type and '（假格）' in geju_type:
            # 财格不真降低一档
            if level == "中富":
                level = "小富"
            elif level == "大富":
                level = "中富"
            else:
                level = "普通"
        elif '财官双美' in geju_type and total_cai >= 1:
            # 财官双美可提升效果
            if level == "小富":
                level = "中富"
            elif level == "普通":
                level = "小富"
        
        # 无财星的硬性限制
        if total_cai == 0:
            if level != "普通" and level != "偏弱":
                level = "普通"  # 无财星最多普通

        return level

    def _analyze_wealth_details(self, shishen_analysis, geju_analysis, gender):
        """财运详细分析"""
        shishen_count = shishen_analysis['count']
        geju_type = geju_analysis['type']
        details = []

        # 男命女命财运差异
        if gender == '男':
            if shishen_count.get('正财', 0) >= 1:
                details.append("男命正财为妻，妻贤家旺")
            if shishen_count.get('偏财', 0) >= 1:
                details.append("男命偏财为机遇，宜把握商机")
        else:
            if shishen_count.get('正官', 0) >= 1:
                details.append("女命官星为夫，夫荣妻贵")
            if shishen_count.get('食神', 0) >= 1:
                details.append("女命食神生财，宜发挥才华")

        # 财运建议
        total_cai = shishen_count.get('正财', 0) + shishen_count.get('偏财', 0)
        bijie = shishen_count.get('比肩', 0) + shishen_count.get('劫财', 0)

        if total_cai >= 1 and bijie >= 2:
            details.append("财星被比劫争夺，理财需谨慎")
        elif total_cai >= 1 and bijie == 0:
            details.append("财星清纯，财运稳定")
        elif total_cai == 0:
            details.append("命局无财星，宜靠技艺谋生")

        return details
    
    def analyze_sixqin(self, shishen_analysis, pillars, day_master, gender, wangshuai_analysis=None):
        """
        六亲分析 - 基于《渊海子平·六亲章》《三命通会·六亲论》
        包含：父串、母串、兄弟、子女
        """
        try:
            # 1. 父串分析
            father_info = self._analyze_father(shishen_analysis, pillars)
            
            # 2. 母串分析
            mother_info = self._analyze_mother(shishen_analysis, pillars)
            
            # 3. 兄弟姐妹分析
            siblings_info = self._analyze_siblings(shishen_analysis, day_master, pillars)
            
            # 4. 子女分析
            children_info = self._analyze_children(shishen_analysis, wangshuai_analysis)
            
            # 5. 格式化输出
            detailed_report = self._format_sixqin_report(
                father_info, mother_info, siblings_info, children_info
            )
            
            return {
                'father': father_info,
                'mother': mother_info,
                'siblings': siblings_info,
                'children': children_info,
                'summary': detailed_report
            }
        except Exception as e:
            return {'error': f'六亲分析异常：{str(e)}'}
    
    def _analyze_father(self, shishen_analysis, pillars):
        """
        父串分析 - 地位：年柱、正官为父
        """
        shishen_count = shishen_analysis['count']
        shishen_detail = shishen_analysis.get('detail', {})
        year_zhi = pillars.get('year', ['', ''])[1]
        
        # 识别正官
        guan_count = shishen_count.get('正官', 0)
        pian_guan = shishen_count.get('偏官', 0)
        
        father_info = {
            'existence': '',
            'health': '',
            'longevity': '',
            'relationship': '',
            'profession': ''
        }
        
        if guan_count == 0 and pian_guan == 0:
            # 无官星
            father_info['existence'] = '无'
            father_info['health'] = '难以判断'
            father_info['relationship'] = '缘分较淡'
        elif guan_count >= 1:
            # 正官为主
            father_info['existence'] = '有'
            father_info['profession'] = '公职、管理、仕途'
            father_info['health'] = '身体较好'
            father_info['longevity'] = '中等或较长'
            father_info['relationship'] = '事业心重、严肃'
        elif pian_guan >= 1:
            # 偏官为主
            father_info['existence'] = '有'
            father_info['profession'] = '自营、技薉、其他'
            father_info['health'] = '性情较强'
            father_info['longevity'] = '中等'
            father_info['relationship'] = '性格粗粝、脾气急'
        
        return father_info
    
    def _analyze_mother(self, shishen_analysis, pillars):
        """
        母串分析 - 地位：月柱、正印为母
        """
        shishen_count = shishen_analysis['count']
        shishen_detail = shishen_analysis.get('detail', {})
        
        yin_count = shishen_count.get('正印', 0)
        pian_yin = shishen_count.get('偏印', 0)
        shi_shang = shishen_count.get('食神', 0) + shishen_count.get('伤官', 0)
        
        mother_info = {
            'character': '',
            'health': '',
            'relationship': '',
            'is_stepmother': False,
            'advice': ''
        }
        
        if yin_count == 0 and pian_yin == 0:
            # 无印星
            mother_info['character'] = '与母缘较淡'
            mother_info['relationship'] = '缘分较淡或不在'
            mother_info['health'] = '无母或继母'
        elif yin_count >= 1 and pian_yin == 0:
            # 正印为主，无偏印盖
            mother_info['is_stepmother'] = False
            mother_info['character'] = '母临温柔贤涯，支持子女'
            if shi_shang >= 1:
                mother_info['character'] += '，但管整严格'
            mother_info['health'] = '母亲身体需上'
            mother_info['relationship'] = '亲情深厚，母子亲密'
        elif pian_yin >= 1:
            # 偏印是判正印
            if yin_count >= 1:
                mother_info['is_stepmother'] = True
                mother_info['character'] = '父亲夹手或有继母'
            else:
                mother_info['is_stepmother'] = True
                mother_info['character'] = '继母或养母，需尊敬'
            mother_info['health'] = '缘份平常'
            mother_info['relationship'] = '缘较淡或不在'
        
        return mother_info
    
    def _analyze_siblings(self, shishen_analysis, day_master, pillars):
        """
        兄弟姐妹分析 - 比肩为你或上一辈，劫财为缘人或下一辈
        """
        shishen_count = shishen_analysis['count']
        shishen_detail = shishen_analysis.get('detail', {})
        day_yinyang = self.tiangan_yinyang.get(day_master, '阳')
        
        bijie = shishen_count.get('比肩', 0) + shishen_count.get('劫财', 0)
        
        siblings_info = {
            'count': bijie,
            'siblings': [],
            'relationship': '不迟'
        }
        
        if bijie == 0:
            siblings_info['relationship'] = '此年不现或分长'
            siblings_info['note'] = '不一定没有兄弟，需看大运'
        else:
            # 统计男女数量
            bijie_list = []
            for position in ['year', 'month', 'hour']:
                if position in shishen_detail:
                    ten_god = shishen_detail[position].get('shishen', '')
                    gan = shishen_detail[position].get('gan', '')
                    gan_yinyang = self.tiangan_yinyang.get(gan, '阳')
                    
                    if ten_god == '比肩':
                        gender = '男' if gan_yinyang == '阳' else '女'
                        strength = '缘深' if self.wuxing_sheng.get(self.tiangan_wuxing[gan]) == self.tiangan_wuxing[day_master] else '一般'
                        bijie_list.append({
                            'type': '比肩',
                            'gender': gender,
                            'strength': strength,
                            'name': '哥哥' if gender == '男' else '姊姊'
                        })
                    elif ten_god == '劫财':
                        gender = '男' if gan_yinyang != day_yinyang else '女'
                        strength = '一般'
                        bijie_list.append({
                            'type': '劫财',
                            'gender': gender,
                            'strength': strength,
                            'name': '弟弟' if gender == '男' else '妹妹'
                        })
            
            siblings_info['siblings'] = bijie_list
            
            if bijie >= 2:
                siblings_info['relationship'] = '养弟姐会有不和，或早早分好'
            else:
                siblings_info['relationship'] = '养弟姐友好，有弇佐力'
        
        return siblings_info
    
    def _analyze_children(self, shishen_analysis, wangshuai_analysis):
        """
        子女分析 - 食神为有福之子，伤官为聚聚作事
        """
        shishen_count = shishen_analysis['count']
        
        shi_shen = shishen_count.get('食神', 0)
        shang_guan = shishen_count.get('伤官', 0)
        total_children = shi_shen + shang_guan
        
        children_info = {
            'count': total_children,
            'children': [],
            'overall': ''
        }
        
        if total_children == 0:
            children_info['overall'] = '缘分较淡，或子女较晨'
            children_info['note'] = '不一定无子，需看大运'
        else:
            # 子女特征
            for i in range(shi_shen):
                children_info['children'].append({
                    'order': f'长子' if i == 0 else f'次子' if i == 1 else f'三子',
                    'type': '食神',
                    'character': '聪慧伶俐，前程佳'
                })
            
            for i in range(shang_guan):
                order = shi_shen + i
                children_info['children'].append({
                    'order': f'长子' if order == 0 else f'次子' if order == 1 else f'三子',
                    'type': '伤官',
                    'character': '聪颖好动，前程有成'
                })
            
            strength = wangshuai_analysis.get('level', '中') if wangshuai_analysis else '中'
            if strength == '弱' and total_children >= 2:
                children_info['overall'] = f'预计{total_children}个子女，但身弱需补。子女是否克绳，所需强身'
            else:
                children_info['overall'] = f'预计{total_children}个子女，聪慧伶俐，前程光明'

        return children_info
    
    def _format_sixqin_report(self, father_info, mother_info, siblings_info, children_info):
        """
        格式化六亲分析报告
        """
        father_exist = '有' if father_info.get('existence') else '无'
        mother_exist = '有' if mother_info.get('existence') else '无'
        siblings_count = siblings_info.get('count', 0)
        children_count = children_info.get('count', 0)
        
        report = f"""
👨 【父亲】
  存在状况：{father_exist}
  健康状态：{father_info.get('health', '未知')}
  寿长预期：{father_info.get('longevity', '未知')}
  事业特征：{father_info.get('profession', '未知')}
  父子关系：{father_info.get('relationship', '未知')}

👩 【母亲】
  性格特征：{mother_info.get('character', '未知')}
  健康状态：{mother_info.get('health', '未知')}
  母子关系：{mother_info.get('relationship', '未知')}
  特殊情况：{'继母' if mother_info.get('is_stepmother') else '亲母'}

👫 【兄弟姐妹】
  人数：{siblings_count}人
  关系和谐度：{siblings_info.get('relationship_harmony', '良好')}

👶 【子女】
  预计数量：{children_count}人
  性别特征：{children_info.get('gender_pattern', '未知')}
  整体评估：{children_info.get('overall', '未知')}

💝 【家庭建议】
- 孝敬父母，关心长辈
- 与兄妹融洽，相互帮助
- 子女教育用心，不可放任
"""
        
        return report
    
    def analyze_marriage(self, shishen_analysis, day_master, gender, pillars=None, wangshuai_analysis=None, birth_info=None):
        """
        婚姻感情分析 - 基于《渊海子平·六亲章》《三命通会·配偶宫理论》
        包含：婚姻质量、配偶特征、结婚时间预测
        """
        shishen_count = shishen_analysis['count']
        shishen_detail = shishen_analysis.get('detail', {})
        
        # 男命看财星，女命看官星
        if gender == '男':
            spouse_star = '财星'
            star_count = shishen_count.get('正财', 0) + shishen_count.get('偏财', 0)
            zheng_star = shishen_count.get('正财', 0)
            pian_star = shishen_count.get('偏财', 0)
        else:
            spouse_star = '官星'
            star_count = shishen_count.get('正官', 0) + shishen_count.get('偏官', 0)
            zheng_star = shishen_count.get('正官', 0)
            pian_star = shishen_count.get('偏官', 0)
        
        marriage_analysis = []
        
        if star_count == 0:
            # ✅ 修复：无配偶星时，根据其他因素细化判断，避免所有人都是"迟婚为宜"
            # 检查日支是否有配偶星（藏干）
            day_zhi = pillars.get('day', ['', ''])[1] if pillars else ''
            has_spouse_in_day_zhi = False
            
            if day_zhi and day_zhi in self.dizhi_canggan:
                hidden_list = self.dizhi_canggan[day_zhi]
                for hidden_gan in hidden_list:
                    hidden_wuxing = self.tiangan_wuxing.get(hidden_gan, '')
                    day_wuxing = self.tiangan_wuxing[day_master]
                    
                    # 判断是否为配偶星
                    if gender == '男':
                        # 男命看财星（我克者）
                        if self.wuxing_ke.get(day_wuxing) == hidden_wuxing:
                            has_spouse_in_day_zhi = True
                            break
                    else:
                        # 女命看官星（克我者）
                        if self.wuxing_ke.get(hidden_wuxing) == day_wuxing:
                            has_spouse_in_day_zhi = True
                            break
            
            # 根据情况判断
            if has_spouse_in_day_zhi:
                marriage_analysis.append(f"{spouse_star}藏于日支，婚姻缘分较晚但稳定")
                marriage_quality = "晚婚稳定"  # ✅ 与"迟婚为宜"区分
            elif shishen_count.get('比肩', 0) + shishen_count.get('劫财', 0) >= 2:
                marriage_analysis.append(f"{spouse_star}不现，比劫多见，婚姻缘分较晚")
                marriage_quality = "较晚婚"  # ✅ 与"迟婚为宜"区分
            else:
                marriage_analysis.append(f"{spouse_star}不现，婚姻缘分较晚")
                marriage_quality = "迟婚为宜"
        elif star_count == 1:
            if zheng_star == 1:
                marriage_analysis.append(f"{spouse_star}专一，婚姻美满")
                marriage_quality = "良好"
            else:
                marriage_analysis.append(f"{spouse_star}偏显，感情波折")
                marriage_quality = "需注意"
        else:
            marriage_analysis.append(f"{spouse_star}多现，感情复杂")
            marriage_quality = "需谨慎"
        
        # 其他影响因素
        if shishen_count.get('比肩', 0) + shishen_count.get('劫财', 0) >= 2:
            if gender == '男':
                marriage_analysis.append("比劫多见，需防夺妻之虞")
        
        if shishen_count.get('伤官', 0) >= 1 and gender == '女':
            marriage_analysis.append("伤官见官，婚姻需谨慎经营")
        
        # 添加结婚时间预测（如果有完整信息）
        marriage_timing = None
        if pillars and birth_info:
            marriage_timing = self._predict_marriage_timing(
                day_master, gender, shishen_detail, pillars, 
                wangshuai_analysis, shishen_count, birth_info
            )
        
        return {
            'quality': marriage_quality,
            'analysis': marriage_analysis,
            'summary': "；".join(marriage_analysis),
            'timing': marriage_timing
        }
    
    def _predict_marriage_timing(self, day_master, gender, shishen_detail, pillars, wangshuai_analysis, shishen_count, birth_info):
        """
        结婚时间预测 - 基于《三命通会·配偶宫理论》《子平真诠·论配偶》
        返回：{
            'marriage_age_range': (最早年龄, 最晚年龄),
            'predicted_years': [预测结婚年份列表],
            'auspicious_months': [吉利月份],
            'spouse_characteristics': 配偶特征描述,
            'marriage_quality': 婚姻质量评估
        }
        """
        try:
            # 1. 识别配偶星透干情况
            spouse_transparency, spouse_gan = self._identify_spouse_transparency(
                shishen_detail, gender
            )
            
            # 2. 计算基础婚龄
            bijie_count = shishen_count.get('比肩', 0) + shishen_count.get('劫财', 0)
            base_age, age_range = self._calculate_marriage_age_range(
                spouse_transparency, wangshuai_analysis, bijie_count, gender
            )
            
            # 3. 判断具体结婚年份
            birth_year = birth_info.get('year', 0)
            if birth_year > 0:
                predicted_years = self._predict_marriage_years(birth_year, age_range)
            else:
                predicted_years = []
            
            # 4. 判断吉利结婚月份
            auspicious_months = self._find_auspicious_months(spouse_gan, day_master)
            
            # 5. 预测配偶特征
            spouse_chars = self._predict_spouse_characteristics(
                spouse_transparency, gender, shishen_count, pillars
            )
            
            return {
                'spouse_star_transparency': spouse_transparency,
                'marriage_age_range': age_range,
                'predicted_years': predicted_years,
                'auspicious_months': auspicious_months,
                'spouse_characteristics': spouse_chars,
                'detailed_prediction': self._format_marriage_prediction(
                    age_range, predicted_years, auspicious_months, spouse_chars
                )
            }
        except Exception as e:
            return {'error': f'结婚时间预测异常：{str(e)}'}
    
    def _identify_spouse_transparency(self, shishen_detail, gender):
        """
        识别配偶星的透干位置和天干
        颗戕顺序：正配偶星 > 偶配偶星
        返回：(透干位置, 天干), 如 ('月干', '丁')
        """
        # 先找正配偶星（正财/正官）
        for position in ['month', 'year', 'hour']:
            if position in shishen_detail:
                ten_god = shishen_detail[position].get('shishen', '')
                spouse_check = ('正财' if gender == '男' else '正官')
                if ten_god == spouse_check:
                    gan = shishen_detail[position].get('gan', '')
                    return (f'{position}干', gan)
        
        # 如果没找到正配偶星，再找偶配偶星（偏财/偏官）
        for position in ['month', 'year', 'hour']:
            if position in shishen_detail:
                ten_god = shishen_detail[position].get('shishen', '')
                if gender == '男' and ten_god == '偏财':
                    gan = shishen_detail[position].get('gan', '')
                    return (f'{position}干', gan)
                elif gender == '女' and ten_god == '偏官':
                    gan = shishen_detail[position].get('gan', '')
                    return (f'{position}干', gan)
        
        return ('无', '')
    
    def _calculate_marriage_age_range(self, spouse_transparency, wangshuai_analysis, bijie_count, gender):
        """
        计算结婚年龄范围
        基于透干情况和调整因素
        """
        # 基础年龄（基于透干位置）
        base_ages = {
            '月干': 20,   # 月干透出 - 早婚
            '年干': 24,   # 年干透出 - 常婚
            '时干': 26,   # 时干透出 - 稍晚
            '无': 30      # 完全不现 - 晚婚
        }
        
        base_age = base_ages.get(spouse_transparency, 24)
        
        # 调整因素1：日主强弱
        strength = wangshuai_analysis.get('level', '中') if wangshuai_analysis else '中'
        if strength == '旺':
            base_age -= 2  # 身旺能承财/官，婚期偏早
        elif strength == '弱':
            base_age += 2  # 身弱难承，婚期偏晚
        
        # 调整因素2：比劫影响
        if bijie_count >= 2:
            base_age += 3  # 比劫多争夺配偶，婚期推迟
        
        # 形成年龄范围（±3年）
        age_range = (base_age - 2, base_age + 3)
        
        return base_age, age_range
    
    def _predict_marriage_years(self, birth_year, age_range):
        """
        根据年龄范围计算预测结婚年份
        """
        min_age, max_age = age_range
        current_year = 2025
        current_age = current_year - birth_year
        
        # 如果整整年龄已过，与其收集未来年份范围
        if current_age >= max_age:
            return []  # 已经过了予测婚龄
        
        # 计算有效的结婚年份
        if current_age < min_age:
            # 还没有数到最早年龄
            start_year = birth_year + min_age
        else:
            # 已经过了最早年龄，今年可以
            start_year = current_year
        
        end_year = birth_year + max_age
        predicted_years = list(range(start_year, end_year + 1))
        
        return predicted_years[:6]  # 最多显示6年
    
    def _find_auspicious_months(self, spouse_gan, day_master):
        """
        判断吉利结婚月份
        基于配偶星天干对应的月份
        """
        # 天干与月份对应（参《穷通宝鉴》择日部分）
        gan_to_month = {
            '甲': 3, '乙': 4,
            '丙': 5, '丁': 6,
            '戊': 5, '己': 6,
            '庚': 9, '辛': 10,
            '壬': 11, '癸': 12
        }
        
        auspicious_months = []
        
        if spouse_gan:
            primary_month = gan_to_month.get(spouse_gan)
            if primary_month:
                auspicious_months.append({
                    'month': primary_month,
                    'reason': f'配偶星{spouse_gan}对应农历{primary_month}月',
                    'auspicious_level': '★★★★★'
                })
        
        # 添加备选月份
        if spouse_gan and spouse_gan in ['甲', '乙']:  # 木
            auspicious_months.append({
                'month': 2,
                'reason': '初春木气旺，婚配吉利',
                'auspicious_level': '★★★★'
            })
        
        return auspicious_months
    
    def _predict_spouse_characteristics(self, spouse_transparency, gender, shishen_count, pillars):
        """
        预测配偶特征：性格、财富、年龄等
        """
        characteristics = []
        
        # 性格特征
        if gender == '男':
            zheng = shishen_count.get('正财', 0)
            pian = shishen_count.get('偏财', 0)
            if zheng >= 1:
                characteristics.append('性格温柔贤淑，内向低调')
            if pian >= 1:
                characteristics.append('性格外向独立，主动积极')
        else:
            zheng = shishen_count.get('正官', 0)
            pian = shishen_count.get('偏官', 0)
            if zheng >= 1:
                characteristics.append('丈夫温文尔雅，有教养')
            if pian >= 1:
                characteristics.append('丈夫性格强势，能力较强')
        
        # 财富水平
        characteristics.append('经济条件中等以上，生活较为稳定')
        
        # 年龄关系
        characteristics.append('年龄相近或略有差异')
        
        return characteristics
    
    def _format_marriage_prediction(self, age_range, predicted_years, auspicious_months, spouse_chars):
        """
        格式化结婚时间预测报告
        """
        min_age, max_age = age_range
        report = f"""
📅 【结婚时间预测】

💍 预测结婚年龄：{min_age}-{max_age}岁

📆 最可能的结婚年份：
   {', '.join(map(str, predicted_years)) if predicted_years else '需要出生年份计算'}

🎉 吉利结婚月份："""
        
        for month_info in auspicious_months:
            report += f"\n   农历{month_info['month']}月 {month_info['auspicious_level']} - {month_info['reason']}"
        
        report += f"\n\n💑 配偶特征预测："
        for char in spouse_chars:
            report += f"\n   • {char}"
        
        report += "\n\n💝 婚姻建议：\n   按预测年份积极把握机会，吉利月份更宜办理婚事"
        
        return report
    
    def analyze_health(self, wuxing_analysis, day_master):
        """健康分析"""
        missing = wuxing_analysis['missing']
        strong = wuxing_analysis['strong']
        
        # 五行与健康的对应关系
        wuxing_health = {
            '木': '肝胆、神经系统',
            '火': '心脏、血液循环',
            '土': '脾胃、消化系统',
            '金': '肺、呼吸系统',
            '水': '肾脏、生殖系统'
        }
        
        health_advice = []
        
        # 缺失五行的健康提示
        for wx in missing:
            organ = wuxing_health.get(wx, '未知')
            health_advice.append(f"五行缺{wx}，注意{organ}保养")
        
        # 过旺五行的健康提示
        for wx in strong:
            organ = wuxing_health.get(wx, '未知')
            health_advice.append(f"五行{wx}过旺，{organ}需防过亢")
        
        if not health_advice:
            health_advice.append("五行平衡，体质较好")
        
        # ✅ 修复：添加健康风险等级
        risk_level = ""
        if len(missing) >= 2:
            risk_level = "中等风险"  # 缺2个以上五行
        elif len(missing) == 1:
            risk_level = "低风险"  # 缺1个五行
        elif len(strong) >= 2:
            risk_level = "中等风险"  # 2个以上五行过旺
        elif len(strong) == 1:
            risk_level = "低风险"  # 1个五行过旺
        else:
            risk_level = "无风险"  # 五行平衡
        
        return {
            'advice': health_advice,
            'summary': "；".join(health_advice),
            'risk_level': risk_level,  # ✅ 修复：添加风险等级
            'level': risk_level  # ✅ 修复：添加兼容字段名
        }
    
    def analyze_wuxing_remedy(self, wuxing_analysis, yongshen_analysis):
        """
        五行补救方案 - 基于《穷通宝鉴》《滴天髓》
        包含颜色、方位、食物、配饰等生活化建议
        """
        missing_wuxing = wuxing_analysis.get('missing', [])
        weak_wuxing = wuxing_analysis.get('weak', [])
        yongshen = yongshen_analysis.get('yongshen', '')
        
        # 五行补救信息映射
        wuxing_remedy_map = {
            '木': {
                'colors': ['绿色', '青色', '翠色'],
                'positions': ['东方', '东北方'],
                'foods': ['绿叶蔬菜', '青笋', '草莓', '猕猴桃'],
                'accessories': ['玉佩', '木质饰品', '绿碧玺', '绿幽灵'],
                'professions': ['林业', '园艺', '医学', '教育']
            },
            '火': {
                'colors': ['红色', '紫色', '橙色'],
                'positions': ['南方', '东南方'],
                'foods': ['红枣', '山楂', '苹果', '胡萝卜'],
                'accessories': ['红玛瑙', '红宝石', '红珊瑚', '火晶'],
                'professions': ['餐饮', '娱乐', '电力', '传媒']
            },
            '土': {
                'colors': ['黄色', '褐色', '米色'],
                'positions': ['中央', '西南方'],
                'foods': ['黄豆', '玉米', '地瓜', '蜂蜜'],
                'accessories': ['黄水晶', '陶瓷', '琥珀', '黄玉'],
                'professions': ['房地产', '农业', '矿业', '建筑']
            },
            '金': {
                'colors': ['白色', '银色', '金色'],
                'positions': ['西方', '西北方'],
                'foods': ['银耳', '白萝卜', '豆腐', '牛奶'],
                'accessories': ['白水晶', '金饰', '银饰', '金属饰品'],
                'professions': ['金融', '机械', '精密', '手术']
            },
            '水': {
                'colors': ['黑色', '蓝色', '深蓝色'],
                'positions': ['北方', '西北方'],
                'foods': ['黑芝麻', '黑木耳', '海带', '鱼类'],
                'accessories': ['黑曜石', '蓝宝石', '黑玛瑙', '青金石'],
                'professions': ['航海', '贸易', '旅游', '运输']
            }
        }
        
        # 旺衰五行补救建议
        remedy_advice = []
        
        # 缺失五行补救
        if missing_wuxing:
            remedy_advice.append(f"\n【缺失五行补救】")
            for wx in missing_wuxing:
                remedy_info = wuxing_remedy_map.get(wx, {})
                colors = '、'.join(remedy_info.get('colors', []))
                positions = '、'.join(remedy_info.get('positions', []))
                foods = '、'.join(remedy_info.get('foods', []))
                accessories = '、'.join(remedy_info.get('accessories', []))
                
                remedy_advice.append(f"  • {wx}缺失：")
                remedy_advice.append(f"    颜色补救：穿着{colors}的衣服")
                remedy_advice.append(f"    方位补救：住家或办公室朝向{positions}")
                remedy_advice.append(f"    食疗补救：常食{foods}")
                remedy_advice.append(f"    佩饰补救：佩戴{accessories}")
        
        # 偏弱五行补救
        if weak_wuxing:
            remedy_advice.append(f"\n【偏弱五行补强】")
            for wx in weak_wuxing:
                remedy_info = wuxing_remedy_map.get(wx, {})
                colors = '、'.join(remedy_info.get('colors', []))
                foods = '、'.join(remedy_info.get('foods', []))
                
                remedy_advice.append(f"  • {wx}偏弱：多接触{colors}环境，增加食用{foods}")
        
        # 用神补强建议
        if yongshen and yongshen in wuxing_remedy_map:
            remedy_advice.append(f"\n【用神{yongshen}补强（重点）】")
            remedy_info = wuxing_remedy_map.get(yongshen, {})
            colors = '、'.join(remedy_info.get('colors', []))
            positions = '、'.join(remedy_info.get('positions', []))
            accessories = '、'.join(remedy_info.get('accessories', []))
            professions = '、'.join(remedy_info.get('professions', []))
            
            remedy_advice.append(f"  用神为{yongshen}，建议：")
            remedy_advice.append(f"  1. 颜色调整：日常穿着以{colors}为主")
            remedy_advice.append(f"  2. 方位调整：卧室、办公室朝向{positions}")
            remedy_advice.append(f"  3. 配饰建议：佩戴{accessories}")
            remedy_advice.append(f"  4. 职业选择：宜从事{professions}等行业")
        
        if not remedy_advice:
            remedy_advice.append("五行平衡，无需特别补救")
        
        return {
            'missing': missing_wuxing,
            'weak': weak_wuxing,
            'yongshen': yongshen,
            'advice': remedy_advice,
            'summary': "\n".join(remedy_advice)
        }
    
    def analyze_dayun(self, day_master, gender, birth_info):
        """
        大运分析 - 基于《三命通会》经典算法
        包含起运年龄计算、阴阳顺逆排列、10步完整大运
        """
        if not birth_info:
            return {
                'info': "大运分析需要完整的出生时间信息",
                'advice': "请提供出生年月日时以计算准确的大运"
            }

        birth_year = birth_info.get('year', 0)
        birth_month = birth_info.get('month', 0)
        birth_day = birth_info.get('day', 0)

        if birth_year == 0 or birth_month == 0:
            return {
               'info': "大运分析需要准确的出生年月",
                'advice': "请提供准确的出生年月以计算大运"
            }

        try:
            # 1. 计算起运年龄
            qiyun_age = self.calculate_qiyun_age(birth_year, birth_month, birth_day, gender)

            # 2. 判断顺逆（基于年干阴阳和性别）
            year_gan = birth_info.get('year_gan', '')
            if not year_gan:
                # 如果没有提供年干，尝试从pillars获取
                year_gan = day_master  # 备用
            
            is_yang_year = year_gan in ['甲', '丙', '戊', '庚', '壬']
            if gender == '男':
                shun_ni = '顺行' if is_yang_year else '逆行'
            else:
                shun_ni = '逆行' if is_yang_year else '顺行'

            # 3. 获取月柱干支（起始大运）
            month_gan = birth_info.get('month_gan', '')
            month_zhi = birth_info.get('month_zhi', '')
            
            # ✅ 修复：如果没有提供月柱，尝试从pillars获取
            if not month_gan or not month_zhi:
                # 尝试从birth_info中获取完整四柱
                if 'pillars' in birth_info:
                    pillars = birth_info['pillars']
                    if isinstance(pillars, dict) and 'month' in pillars:
                        month_pillar = pillars['month']
                        if isinstance(month_pillar, (list, tuple)) and len(month_pillar) >= 2:
                            month_gan = month_pillar[0]
                            month_zhi = month_pillar[1]
            
            # 如果仍然没有，使用默认值
            if month_gan not in self.tiangan_list:
                month_gan = '丙'  # 默认值
            if month_zhi not in self.dizhi_list:
                month_zhi = '寅'  # 默认值
            
            # ✅ 修复：计算10步完整大运（包含天干地支）
            gan_index = self.tiangan_list.index(month_gan)
            zhi_index = self.dizhi_list.index(month_zhi)
            direction = 1 if shun_ni == '顺行' else -1
            dayun_list = []
            
            for step in range(10):  # 完整10步
                # 从月柱顺逆推算（第1步大运是月柱的下/上一个干支）
                offset = (step + 1) * direction
                gan_idx = (gan_index + offset) % 10
                zhi_idx = (zhi_index + offset) % 12
                
                gan = self.tiangan_list[gan_idx]
                zhi = self.dizhi_list[zhi_idx]
                ganzhi = gan + zhi
                
                start_age = qiyun_age + step * 10
                end_age = start_age + 9
                
                dayun_list.append({
                    'step': step + 1,
                    'gan': gan,
                    'zhi': zhi,
                    'ganzhi': ganzhi,  # ✅ 修复：添加完整干支
                    'start_age': start_age,
                    'end_age': end_age,
                    'age_range': f"{start_age}-{end_age}岁"
                })

            # 5. 确定当前大运
            current_year = 2025
            current_age = current_year - birth_year
            current_dayun = None
            dayun_info = ""
            
            if current_age < qiyun_age:
                dayun_info = f"未起运（{current_age}岁），将于{qiyun_age}岁起运"
            else:
                for dayun in dayun_list:
                    if dayun['start_age'] <= current_age <= dayun['end_age']:
                        current_dayun = dayun
                        ganzhi = dayun.get('ganzhi', dayun.get('gan', ''))
                        dayun_info = f"当前行第{dayun['step']}步大运（{ganzhi}，{dayun['start_age']}-{dayun['end_age']}岁）"
                        break
                
                if not current_dayun:
                    dayun_info = f"已超过预设大运范围，当前{current_age}岁"

            return {
                'info': dayun_info,
                'qiyun_age': qiyun_age,
                'qiyun_shun_ni': shun_ni,
                'current_age': current_age,
                'current_dayun': current_dayun,
                'dayun_list': dayun_list,
                'advice': "大运十年一变，宜结合用神分析大运吉凶"
            }

        except Exception as e:
            return {
                'info': f"大运计算异常：{str(e)}",
                'advice': "请检查出生时间是否准确"
            }

    def calculate_qiyun_age(self, birth_year, birth_month, birth_day, gender):
        """
        计算起运年龄 - 基于《三命通会》起运法
        算法：阳男阴女顺行，阴男阳女逆行
        """
        # 简化版起运计算（实际需要精确节气）
        # 这里使用按月计算的方法

        # 基础起运年龄（一般1-8岁起运）
        base_age = 3

        # 根据出生月份调整
        month_adjust = {
            1: 1.5, 2: 2.0, 3: 2.5, 4: 3.0,
            5: 3.5, 6: 4.0, 7: 3.5, 8: 3.0,
            9: 2.5, 10: 2.0, 11: 1.5, 12: 1.0
        }

        qiyun_age = base_age + month_adjust.get(birth_month, 3.0)

        # 确保在合理范围内（1-8岁）
        return max(1.0, min(8.0, qiyun_age))

    def calculate_dayun_list(self, day_master, gender, qiyun_age, current_age, month_gan=None, month_zhi=None, year_gan=None):
        """
        计算大运列表 - 按经典顺逆排大运（修复硬编码问题）
        返回格式：[{step: 1, ganzhi: '甲子', age_range: '3-12岁', start_age: 3, end_age: 12}]
        """
        dayun_list = []

        # 天干地支顺序
        gan_order = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        zhi_order = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

        # ✅ 修复：如果没有提供月柱，使用默认值（但会打印警告）
        if not month_gan or not month_zhi:
            print(f"⚠️ calculate_dayun_list: 缺少月柱信息，使用默认值")
            month_gan = month_gan or '丙'
            month_zhi = month_zhi or '寅'
        
        # ✅ 修复：判断顺逆（基于年干阴阳和性别）
        if not year_gan:
            # 如果没有年干，尝试从日主推断（不够准确，但比硬编码好）
            year_gan = day_master
            print(f"⚠️ calculate_dayun_list: 缺少年干信息，使用日主{day_master}作为推断")
        
        is_yang_year = year_gan in ['甲', '丙', '戊', '庚', '壬']
        if gender == '男':
            shun_ni = '顺行' if is_yang_year else '逆行'
        else:
            shun_ni = '逆行' if is_yang_year else '顺行'
        
        direction = 1 if shun_ni == '顺行' else -1
        
        # ✅ 修复：从月柱干支开始推算大运（顺行：月柱后一位起；逆行：月柱前一位起）
        gan_index = gan_order.index(month_gan) if month_gan in gan_order else 2
        zhi_index = zhi_order.index(month_zhi) if month_zhi in zhi_order else 2
        
        # 计算10步大运
        for step in range(10):
            # 从月柱顺逆推算（第1步大运是月柱的下/上一个干支）
            offset = (step + 1) * direction
            gan_idx = (gan_index + offset) % 10
            zhi_idx = (zhi_index + offset) % 12
            
            gan = gan_order[gan_idx]
            zhi = zhi_order[zhi_idx]
            ganzhi = gan + zhi
            
            start_age = int(qiyun_age + step * 10)
            end_age = start_age + 9
            
            dayun_list.append({
                'step': step + 1,
                'ganzhi': ganzhi,
                'gan': gan,
                'zhi': zhi,
                'age_range': f'{start_age}-{end_age}岁',
                'start_age': start_age,
                'end_age': end_age
            })

        # 计算当前应该显示的大运
        for dayun in dayun_list:
            if current_age >= dayun['start_age'] and current_age <= dayun['end_age']:
                dayun['current'] = True
                break

        return dayun_list
    
    def build_report(self, pillars, day_master, gender, wuxing_analysis,
                     shishen_analysis, geju_analysis, wangshuai_analysis,
                     yongshen_analysis, character_analysis, career_wealth,
                     sixqin, marriage, health, dayun, wuxing_remedy=None,
                     detailed_wealth=None):
        """构建完整的命理分析报告"""

        # 添加神煞分析
        shensha_analysis = self.analyze_shensha(day_master, pillars)
        
        # 构建大运列表显示
        dayun_list = dayun.get('dayun_list', [])
        if dayun_list:
            dayun_list_display = "\n".join([
                f"  第{d['step']}步大运：{d['gan']}运（{d['start_age']}-{d['end_age']}岁）"
                for d in dayun_list
            ])
        else:
            dayun_list_display = "  暂无大运排列（未起运或数据不足）"
        
        # 构建起运信息
        qiyun_info = f"第{dayun.get('qiyun_age', '待算')}岁起运（{dayun.get('qiyun_shun_ni', '顺/逆')}行）"

        # 获取财运详细预测（如果提供）
        detailed_wealth_text = ""
        if detailed_wealth:
            detailed_wealth_text = self._format_detailed_wealth_report(detailed_wealth)

        report = f"""
╔══════════════════════════════════════════════════════════════════╗
║                    传统八字命理分析报告                           ║
║                  （本地算法 - 纯传统命理学）                      ║
╚══════════════════════════════════════════════════════════════════╝

【一、基础数据】
年柱：{pillars['year']}    月柱：{pillars['month']}    日柱：{pillars['day']}    时柱：{pillars['hour']}
日主：{day_master}（{self.tiangan_wuxing[day_master]}）    性别：{gender}

【二、五行分布】
{wuxing_analysis['summary']}
五行详情：木{wuxing_analysis['count']['木']:.1f} 火{wuxing_analysis['count']['火']:.1f} 土{wuxing_analysis['count']['土']:.1f} 金{wuxing_analysis['count']['金']:.1f} 水{wuxing_analysis['count']['水']:.1f}

【三、十神分析】
{shishen_analysis['summary']}
年干：{shishen_analysis['detail'].get('year', {}).get('shishen', '无')}
月干：{shishen_analysis['detail'].get('month', {}).get('shishen', '无')}
时干：{shishen_analysis['detail'].get('hour', {}).get('shishen', '无')}

【四、格局分析】
格局类型：{geju_analysis['type']}
格局说明：{geju_analysis['description']}

【五、日主强弱】
{wangshuai_analysis['description']}
旺衰等级：{wangshuai_analysis['level']}（强度：{wangshuai_analysis['strength']}）

【六、用神分析】
{yongshen_analysis['description']}
喜用建议：{yongshen_analysis['advice']}

【七、神煞分析】
{shensha_analysis['总结']}
{'; '.join(shensha_analysis['吉神']) if shensha_analysis['吉神'] else '无特殊神煞'}
{'; '.join(shensha_analysis['桃花']) if shensha_analysis['桃花'] else ''}

【八、性格特点】
{character_analysis['summary']}

【九、六亲分析】
{sixqin.get('summary', '')}

【十、事业财运】
财运等级：{career_wealth['wealth_level']}（财富评分：{career_wealth.get('wealth_score', '未计算'):.1f}）
事业建议：
{career_wealth['summary']}

【十一、财运详细预测】
{detailed_wealth_text if detailed_wealth_text else '财运分析数据不足'}

【十二、婚姻感情】
婚姻质量：{marriage['quality']}
感情分析：{marriage['summary']}
{marriage['timing']['detailed_prediction'] if marriage.get('timing') and 'detailed_prediction' in marriage['timing'] else ''}

【十三、健康提示】
{health['summary']}

【十四、五行补救】
{wuxing_remedy.get('summary', '五行平衡，无需特别补救') if wuxing_remedy else '五行平衡，无需特别补救'}

【十五、大运分析】
起运信息：{qiyun_info}
当前大运：{dayun['info']}

大运排列（10步）：
{dayun_list_display}

运势建议：{dayun['advice']}

════════════════════════════════════════════════════════════════════
注：本报告依据《渊海子平》《三命通会》《滴天髓》《子平真诠》《穷通宝鉴》
等传统命理著作所载原则编写，采用经典算法推演生成，仅供参考。
命运掌握在自己手中，后天努力同样重要。
════════════════════════════════════════════════════════════════════
"""

        return report.strip()

if __name__ == "__main__":
    analyzer = LocalMingliAnalyzer()
    
    # 测试用例
    test_pillars = {
        'year': '甲子',
        'month': '丙寅',
        'day': '戊辰',
        'hour': '庚申'
    }
    
    result = analyzer.analyze_bazi(test_pillars, gender='男', birth_info={'year': 1984})
    print(result)
