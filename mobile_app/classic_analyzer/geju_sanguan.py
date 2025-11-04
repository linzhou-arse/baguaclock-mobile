"""
格局三关分析模块 - 基于《子平真诠》《滴天髓》

理论依据：
命格的成立与否取决于三关的成立情况：

1. 护卫关：用神是否有护卫神扶持
   ├─ 用神得生扶 → 成立
   ├─ 用神被克泄 → 不成立
   └─ 用神独立无依 → 勉强成立

2. 真假关：用神是否有强根且无伤
   ├─ 用神有强根、无刑冲 → 真格局
   ├─ 用神有根、略有损伤 → 假格局
   └─ 用神无根或受重伤 → 不成立

3. 清纯关：十神搭配是否清纯专一
   ├─ 十神清纯、五行流通 → 成立
   ├─ 十神基本清纯、略有混杂 → 勉强成立
   └─ 十神混杂、五行失衡 → 不成立
"""

from .constants import WUXING_MAP, KE_MAP, SHENG_MAP, HE_MAP, XING_PAIRS, CHONG_PAIRS, SAN_HE_GROUPS, LIU_HE_PAIRS


class GejuSanguanAnalyzer:
    """
    格局三关分析器 - 完整基于《子平真诠》《滴天髓》
    """
    
    # ══════════════════════════════════════════════════════════════════
    # 格局三关分析主方法
    # ══════════════════════════════════════════════════════════════════
    
    @staticmethod
    def analyze_geju_sanguan(pillars):
        """
        分析格局三关 - 基于《子平真诠》《滴天髓》
        
        Args:
            pillars: dict - 四柱信息
        
        Returns:
            dict - 格局三关分析结果
            {
                'hu_wei_guan': {...},    # 护卫关
                'zhen_jia_guan': {...},  # 真假关
                'qing_chun_guan': {...}, # 清纯关
                'overall_level': '成立', # 整体判断
                'score': 75,
                'analysis': '...'
            }
        """
        
        # 第一步：判断护卫关
        hu_wei_result = GejuSanguanAnalyzer._judge_hu_wei_guan(pillars)
        
        # 第二步：判断真假关
        zhen_jia_result = GejuSanguanAnalyzer._judge_zhen_jia_guan(pillars)
        
        # 第三步：判断清纯关
        qing_chun_result = GejuSanguanAnalyzer._judge_qing_chun_guan(pillars)
        
        # 第四步：综合三关判断
        overall = GejuSanguanAnalyzer._judge_overall_level(
            hu_wei_result, zhen_jia_result, qing_chun_result
        )
        
        return {
            'hu_wei_guan': hu_wei_result,
            'zhen_jia_guan': zhen_jia_result,
            'qing_chun_guan': qing_chun_result,
            'overall_level': overall['level'],
            'overall_guan_count': overall['guan_count'],
            'score': overall['score'],
            'analysis': overall['analysis'],
            'classic_text': '《子平真诠》：格局成立须三关俱成'
        }
    
    @staticmethod
    def _judge_hu_wei_guan(pillars):
        """
        判断护卫关 - 用神是否有护卫神扶持
        
        规则：根据日主强弱确定用神，检查用神是否得到生扶
        - 用神得生扶 → 成立
        - 用神被克泄 → 不成立
        - 用神独立无依 → 勉强成立
        """
        
        day_gan = pillars['day'][0]
        day_wx = WUXING_MAP.get(day_gan)
        
        # 简化的判断：检查日主周围是否有生扶
        all_gan = [pillars['year'][0], pillars['month'][0], 
                   pillars['day'][0], pillars['hour'][0]]
        
        # 统计生扶日主的五行数量
        sheng_fu_count = 0
        ke_xie_count = 0
        
        for gan in all_gan:
            if gan != day_gan:  # 不计算日主自己
                gan_wx = WUXING_MAP.get(gan)
                if gan_wx:
                    # 检查是否生扶日主
                    if SHENG_MAP.get(gan_wx) == day_wx:
                        sheng_fu_count += 1
                    # 检查是否克泄日主
                    elif KE_MAP.get(gan_wx) == day_wx:
                        ke_xie_count += 1
        
        if sheng_fu_count > ke_xie_count:
            return {
                'name': '护卫关',
                'description': '用神得生扶，护卫有力',
                'status': '成立',
                'level': '护卫有力',
                'analysis': '日主得生扶，格局稳固，成就较大'
            }
        elif ke_xie_count > sheng_fu_count:
            return {
                'name': '护卫关',
                'description': '用神被克泄，护卫无力',
                'status': '不成立',
                'level': '护卫无力',
                'analysis': '日主受克泄，格局不稳，难以成就'
            }
        else:
            return {
                'name': '护卫关',
                'description': '用神独立无依，护卫一般',
                'status': '勉强成立',
                'level': '护卫一般',
                'analysis': '日主无明显生扶克泄，格局一般，需后天补足'
            }

    @staticmethod
    def _judge_zhen_jia_guan(pillars):
        """
        判断真假关 - 用神是否有强根且无伤
        
        规则：检查用神在四柱中是否有根，是否受刑冲破害
        - 用神有强根、无刑冲 → 真格局
        - 用神有根、略有损伤 → 假格局
        - 用神无根或受重伤 → 不成立
        """
        
        day_gan = pillars['day'][0]
        day_wx = WUXING_MAP.get(day_gan)
        
        # 确定用神（简化处理，实际应结合调候用神分析）
        if day_wx:
            # 日主旺时，用神为克泄耗（官杀、财、食伤）
            # 日主弱时，用神为生扶（印、比劫）
            # 这里简化处理，以官杀为例
            yong_shen_wx = KE_MAP.get(day_wx)
            
            # 检查用神是否有根
            all_symbols = []
            for pos in ['year', 'month', 'day', 'hour']:
                all_symbols.append(pillars[pos][0])  # 天干
                all_symbols.append(pillars[pos][1])  # 地支
            
            # 统计用神在四柱中的出现次数
            yong_shen_count = 0
            for symbol in all_symbols:
                symbol_wx = WUXING_MAP.get(symbol)
                if symbol_wx == yong_shen_wx:
                    yong_shen_count += 1
            
            # 检查是否有刑冲破害（简化处理）
            has_xing_chong = False
            zhi_list = [pillars['year'][1], pillars['month'][1], 
                       pillars['day'][1], pillars['hour'][1]]
            
            # 刑：子刑卯、卯刑子；寅刑巳、巳刑申、申刑寅；丑刑戌、戌刑未、未刑丑
            xing_pairs = [
                ['子', '卯'], ['寅', '巳'], ['巳', '申'], ['申', '寅'],
                ['丑', '戌'], ['戌', '未'], ['未', '丑']
            ]
            
            # 冲：子午冲、丑未冲、寅申冲、卯酉冲、辰戌冲、巳亥冲
            chong_pairs = [
                ['子', '午'], ['丑', '未'], ['寅', '申'], 
                ['卯', '酉'], ['辰', '戌'], ['巳', '亥']
            ]
            
            # 检查刑
            for pair in xing_pairs:
                if all(zhi in zhi_list for zhi in pair):
                    has_xing_chong = True
                    break
            
            # 检查冲
            if not has_xing_chong:
                for pair in chong_pairs:
                    if all(zhi in zhi_list for zhi in pair):
                        has_xing_chong = True
                        break
            
            if yong_shen_count >= 2 and not has_xing_chong:
                return {
                    'name': '真假关',
                    'description': '用神有强根、无刑冲，真格局',
                    'status': '成立',
                    'level': '真格局',
                    'analysis': '用神得地有力、无刑冲破害，格局真纯，成就较大'
                }
            elif yong_shen_count >= 1:
                if has_xing_chong:
                    return {
                        'name': '真假关',
                        'description': '用神有根但受损伤，假格局',
                        'status': '勉强成立',
                        'level': '假格局',
                        'analysis': '用神虽有根但受刑冲，格局欠纯，需后天补足'
                    }
                else:
                    return {
                        'name': '真假关',
                        'description': '用神有根无损伤，真格局',
                        'status': '成立',
                        'level': '真格局',
                        'analysis': '用神得地、无刑冲破害，格局真纯，成就较大'
                    }
            else:
                return {
                    'name': '真假关',
                    'description': '用神无根或受重伤，不成立',
                    'status': '不成立',
                    'level': '无根格局',
                    'analysis': '用神无根或受重伤，格局不成立，难以成就'
                }
        else:
            return {
                'name': '真假关',
                'description': '无法确定用神',
                'status': '不成立',
                'level': '无法判断',
                'analysis': '日主五行不明，无法判断格局真假'
            }

    @staticmethod
    def _judge_qing_chun_guan(pillars):
        """
        判断清纯关 - 十神搭配是否清纯专一
        
        规则：十神清纯、五行流通为成立
        - 十神清纯、五行流通 → 成立
        - 十神基本清纯、略有混杂 → 勉强成立
        - 十神混杂、五行失衡 → 不成立
        """
        
        # 这里需要结合十神分析，简化处理
        all_gan = [pillars['year'][0], pillars['month'][0], 
                   pillars['day'][0], pillars['hour'][0]]
        all_zhi = [pillars['year'][1], pillars['month'][1], 
                   pillars['day'][1], pillars['hour'][1]]
        
        all_symbols = all_gan + all_zhi
        
        # 统计五行分布
        wuxing_count = {'木': 0, '火': 0, '土': 0, '金': 0, '水': 0}
        for symbol in all_symbols:
            wx = WUXING_MAP.get(symbol)
            if wx:
                wuxing_count[wx] += 1
        
        # 检查五行分布的均衡性
        distributed = [count for count in wuxing_count.values() if count > 0]
        max_count = max(wuxing_count.values())
        min_count = min([count for count in wuxing_count.values() if count > 0])
        
        # 检查是否有明显的五行偏枯
        has_pian_ku = max_count - min_count >= 4
        
        # 检查相生链条（简化处理）
        sheng_chain_length = 0
        wuxing_list = ['木', '火', '土', '金', '水']
        for i in range(len(wuxing_list)):
            current = wuxing_list[i]
            next_wx = wuxing_list[(i + 1) % len(wuxing_list)]
            if wuxing_count[current] > 0 and wuxing_count[next_wx] > 0:
                sheng_chain_length += 1
        
        if not has_pian_ku and sheng_chain_length >= 3:
            # 五行相对均衡且相生链条完整
            return {
                'name': '清纯关',
                'description': '十神清纯、五行流通，清纯成立',
                'status': '成立',
                'level': '清纯',
                'analysis': '五行分布均衡、相生流通，格局清纯，成就较大'
            }
        elif not has_pian_ku or sheng_chain_length >= 2:
            # 五行基本均衡或相生链条基本完整
            return {
                'name': '清纯关',
                'description': '十神基本清纯、五行基本流通，清纯勉强成立',
                'status': '勉强成立',
                'level': '基本清纯',
                'analysis': '五行分布基本均衡、相生链条基本完整，格局较为清纯'
            }
        else:
            # 五行严重失衡或相生链条不完整
            return {
                'name': '清纯关',
                'description': '十神混杂、五行失衡，清纯不成立',
                'status': '不成立',
                'level': '混杂',
                'analysis': '五行分布失衡、相生链条不完整，格局混杂，成就有限'
            }

    @staticmethod
    def _judge_overall_level(hu_wei_result, zhen_jia_result, qing_chun_result):
        """
        综合三关进行整体判断
        
        规则：
        - 三关都成立 → 成立 (90+分)
        - 两关成立 → 基本成立 (70-89分)
        - 一关成立 → 勉强成立 (50-69分)
        - 都不成立 → 不成立 (0-49分)
        """
        
        guan_count = 0
        if hu_wei_result['status'] == '成立':
            guan_count += 1
        if zhen_jia_result['status'] in ['成立', '勉强成立']:
            guan_count += 1
        if qing_chun_result['status'] in ['成立', '勉强成立']:
            guan_count += 1
        
        if guan_count == 3:
            return {
                'level': '成立',
                'guan_count': 3,
                'score': 90,
                'analysis': '三关俱成，格局成立，成就大'
            }
        elif guan_count == 2:
            return {
                'level': '基本成立',
                'guan_count': 2,
                'score': 75,
                'analysis': '两关成立，格局基本成立，成就中等'
            }
        elif guan_count == 1:
            return {
                'level': '勉强成立',
                'guan_count': 1,
                'score': 55,
                'analysis': '仅一关成立，格局勉强成立，需后天补足'
            }
        else:
            return {
                'level': '不成立',
                'guan_count': 0,
                'score': 30,
                'analysis': '三关都不成立，格局破败，难以成就'
            }


def analyze_geju_sanguan_complete(pillars):
    """
    完整的格局三关分析函数
    
    理论依据：《子平真诠》《滴天髓》
    """
    return GejuSanguanAnalyzer.analyze_geju_sanguan(pillars)
