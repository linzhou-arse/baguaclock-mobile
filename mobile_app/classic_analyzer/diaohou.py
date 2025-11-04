"""
调候用神分析模块 - 基于《子平真诠》《滴天髓》

理论依据：
调候用神是命理分析的核心。根据季节和八字特点，需要确定用神（扶助日主）
和忌神（克制日主）的配置。

调候原则：
1. 春季木旺：需要生火，不需要火来生土
2. 夏季火旺：需要调候，金来克火，水来泄火
3. 秋季金旺：需要生水，不需要水来润金
4. 冬季水旺：需要调候，火来克水，木来生火
5. 四季土旺：需要金生水或木来泄土

用神选择：
- 主用神：最核心的，必须有根
- 辅用神：配合主用神，不一定有根
- 俱全：主辅都有，最优

三要素判断日主强弱（《滴天髓》）：
1. 月令当令 (40%) - 月支是否当令
2. 天干透干 (40%) - 天干是否透出同五行
3. 地支根气 (20%) - 地支藏干中是否有同五行

根气判断（《子平真诠》）：
- 有根 = 在四柱中有同五行的地支藏干
- 地支藏干权重：本气(0.6-0.7)、中气(0.2-0.3)、余气(0.1)
"""

from .constants import WUXING_MAP, KE_MAP, SHENG_MAP, CANG_GAN_MAP


class DiahouYongshenAnalyzer:
    """
    调候用神分析器 - 完整基于《子平真诠》《滴天髓》
    """
    
    # ══════════════════════════════════════════════════════════════════
    # 调候用神分析主方法
    # ══════════════════════════════════════════════════════════════════
    
    @staticmethod
    def analyze_diaohou_yongshen(pillars, birth_info):
        """
        分析调候用神 - 基于《子平真诠》《滴天髓》
        
        Args:
            pillars: dict - 四柱信息
            birth_info: dict - 出生信息
        
        Returns:
            dict - 调候用神分析结果
            {
                'season': '春季',
                'main_yongshen': '火',  # 主用神
                'fu_yongshen': '土',    # 辅用神
                'completeness': '俱全',  # 主辅配置
                'score': 80,
                'analysis': '...'
            }
        """
        
        # 第一步：判断季节
        month = birth_info.get('month', 1)
        season = DiahouYongshenAnalyzer._get_season(month)
        
        # 第二步：判断日主强弱
        day_gan = pillars['day'][0]
        day_zhi = pillars['day'][1]
        strength = DiahouYongshenAnalyzer._judge_strength(pillars, season)
        
        # 第三步：确定用神和忌神
        yongshen_info = DiahouYongshenAnalyzer._determine_yongshen(
            day_gan, strength, season
        )
        
        # 第四步：检查用神是否有根
        root_status = DiahouYongshenAnalyzer._check_root(
            yongshen_info, pillars
        )
        
        return {
            'season': season,
            'day_master': day_gan,
            'strength': strength,
            'main_yongshen': yongshen_info['main'],
            'fu_yongshen': yongshen_info['fu'],
            'main_root': root_status['main_root'],
            'fu_root': root_status['fu_root'],
            'completeness': root_status['completeness'],
            'score': root_status['score'],
            'analysis': root_status['analysis'],
            'classic_text': '《子平真诠》：调候得当，格局成立；《滴天髓》：用神有根，福泽深厚'
        }
    
    @staticmethod
    def _get_season(month):
        """
        根据月份判断季节
        
        春季（1-3月）、夏季（4-6月）、秋季（7-9月）、冬季（10-12月）
        """
        if month in [1, 2, 3]:
            return '春季'
        elif month in [4, 5, 6]:
            return '夏季'
        elif month in [7, 8, 9]:
            return '秋季'
        elif month in [10, 11, 12]:
            return '冬季'
        return '四季'
    
    @staticmethod
    def _judge_strength(pillars, season):
        """
        判断日主强弱 - 基于《滴天髓》三要素综合判断
        
        三要素：
        1. 月令当令 (40%) - 月支是否当令
        2. 天干透干 (40%) - 天干是否透出同五行
        3. 地支根气 (20%) - 地支藏干中是否有同五行
        
        综合评分 >= 0.5 = 旺，< 0.5 = 衰
        """
        day_gan = pillars['day'][0]
        day_wx = WUXING_MAP.get(day_gan)
        
        # 地支藏干表（带权重）
        # 根据《子平真诠》和《滴天髓》理论，采用本气/中气/余气权重比例
        cang_gan_map = {
            '子': [('癸', 1.0)],
            '丑': [('己', 0.6), ('癸', 0.3), ('辛', 0.1)],
            '寅': [('甲', 0.7), ('丙', 0.2), ('戊', 0.1)],
            '卯': [('乙', 1.0)],
            '辰': [('戊', 0.6), ('乙', 0.3), ('癸', 0.1)],
            '巳': [('丙', 0.7), ('戊', 0.2), ('庚', 0.1)],
            '午': [('丁', 0.7), ('己', 0.3)],
            '未': [('己', 0.6), ('丁', 0.3), ('乙', 0.1)],
            '申': [('庚', 0.7), ('壬', 0.2), ('戊', 0.1)],
            '酉': [('辛', 1.0)],
            '戌': [('戊', 0.6), ('辛', 0.3), ('丁', 0.1)],
            '亥': [('壬', 0.7), ('甲', 0.3)]
        }
        
        strength_score = 0.0
        
        # 1. 月令当令 (40%权重)
        month_zhi = pillars['month'][1]
        month_cang_gans = cang_gan_map.get(month_zhi, [])
        
        month_is_current = any(
            WUXING_MAP.get(cg) == day_wx 
            for cg, strength in month_cang_gans
        )
        strength_score += 0.4 * (1.0 if month_is_current else 0.0)
        
        # 2. 天干透干 (40%权重)
        all_gan = [pillars['year'][0], pillars['month'][0], pillars['day'][0], pillars['hour'][0]]
        gan_same_wx_count = sum(
            1 for gan in all_gan 
            if WUXING_MAP.get(gan) == day_wx
        )
        # 每透出一个同五行天干加0.1，最多0.4
        strength_score += min(0.4, gan_same_wx_count * 0.1)
        
        # 3. 地支根气 (20%权重)
        all_zhi = [pillars['year'][1], pillars['month'][1], pillars['day'][1], pillars['hour'][1]]
        root_strength = 0.0
        for zhi in all_zhi:
            cang_gans = cang_gan_map.get(zhi, [])
            for cang_gan, weight in cang_gans:
                if WUXING_MAP.get(cang_gan) == day_wx:
                    root_strength += weight
        # 根气权重最多0.2 (20%权重)
        strength_score += min(0.2, root_strength * 0.2)
        
        # 综合评分 >= 0.5 = 旺，< 0.5 = 衰
        if strength_score >= 0.5:
            return '旺'
        else:
            return '衰'
    
    @staticmethod
    def _determine_yongshen(day_gan, strength, season):
        """
        确定用神和忌神
        
        规则：根据日主强弱和季节确定调候方向
        """
        day_wx = WUXING_MAP.get(day_gan)
        
        # 克制关系
        ke_map = {
            '木': '土', '土': '水', '水': '火', '火': '金', '金': '木'
        }
        
        # 生助关系
        sheng_map = {
            '木': '火', '火': '土', '土': '金', '金': '水', '水': '木'
        }
        
        if strength == '旺':
            # 日主旺，需要克制或泻漏
            if day_wx:
                main_yongshen = ke_map.get(day_wx)
                ke_wx = ke_map.get(day_wx)
                fu_yongshen = sheng_map.get(ke_wx) if ke_wx else None
            else:
                main_yongshen = None
                fu_yongshen = None
        else:
            # 日主衰，需要帮助或生助
            if day_wx:
                main_yongshen = sheng_map.get(day_wx)
                sheng_wx = sheng_map.get(day_wx)
                fu_yongshen = sheng_map.get(sheng_wx) if sheng_wx else None
            else:
                main_yongshen = None
                fu_yongshen = None
        
        return {
            'main': main_yongshen,
            'fu': fu_yongshen,
            'strength': strength,
            'season': season
        }
    
    @staticmethod
    def _check_root(yongshen_info, pillars):
        """
        检查用神是否有根 - 需于干上或地支藏干
        
        有根 = 在四柱中有同五行的地支或藏干
        根据《子平真诠》理论，地支本气为根，中气为苗，余气为花
        """
        main_yongshen = yongshen_info['main']
        fu_yongshen = yongshen_info['fu']
        
        all_gan = [pillars['year'][0], pillars['month'][0], pillars['day'][0], pillars['hour'][0]]
        all_zhi = [pillars['year'][1], pillars['month'][1], pillars['day'][1], pillars['hour'][1]]
        
        def has_root_wx(yongshen_wx, all_gan, all_zhi):
            """检查特定五行是否有根"""
            # 检查干上
            for gan in all_gan:
                if WUXING_MAP.get(gan) == yongshen_wx:
                    return True
            # 检查地支藏干
            for zhi in all_zhi:
                # 检查藏干（严格按照《子平真诠》理论，地支本气才是真正的根）
                cang_gans = CANG_GAN_MAP.get(zhi, [])
                for cang_gan, weight in cang_gans:
                    if WUXING_MAP.get(cang_gan) == yongshen_wx:
                        # 根据《子平真诠》，只有本气(权重>=0.6)才算真正的根
                        if weight >= 0.6:
                            return True
                        # 中气(权重0.2-0.3)为苗，余气(权重0.1)为花，不算根
            return False
        
        # 检查主用神有根
        main_root = has_root_wx(main_yongshen, all_gan, all_zhi)
        
        # 检查辅用神有根
        fu_root = has_root_wx(fu_yongshen, all_gan, all_zhi) if fu_yongshen else False
        
        # 判断主辅配置完整度
        if main_root and fu_root:
            completeness = '俱全'
            score = 90
            analysis = f'主用神{main_yongshen}和辅用神{fu_yongshen}都有根，配置完善'
        elif main_root:
            completeness = '有主'
            score = 70
            analysis = f'主用神{main_yongshen}有根，辅用神{fu_yongshen}无根，配置基本'
        elif fu_root:
            completeness = '有辅'
            score = 50
            analysis = f'辅用神{fu_yongshen}有根，主用神{main_yongshen}无根，配置欠缺'
        else:
            completeness = '无根'
            score = 30
            analysis = f'主辅用神都无根，调候不利，需后天补救'
        
        return {
            'main_root': main_root,
            'fu_root': fu_root,
            'completeness': completeness,
            'score': score,
            'analysis': analysis
        }


def analyze_diaohou_yongshen_complete(pillars, birth_info):
    """
    完整的调候用神分析函数
    
    理论依据：《子平真诠》《滴天髓》
    """
    return DiahouYongshenAnalyzer.analyze_diaohou_yongshen(pillars, birth_info)
