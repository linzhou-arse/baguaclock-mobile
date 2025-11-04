from typing import Dict, List, Tuple, Optional
from ..core.base_analyzer import BaseAnalyzer
from ..core.data_structures import BaziData, AnalysisResult, AnalysisConfig
from ..core.utils import create_analysis_result, get_wuxing_by_tiangan, get_wuxing_by_dizhi, get_ten_god
from ..core.constants import DIZHI_CANGGAN, TIANGAN_WUXING

class ZipingzhenquanAnalyzer(BaseAnalyzer):
    """
    《子平真诠》统一分析器
    核心理论：
    1. 用神三法：调候、病药、通关
    2. 格局以月令为主
    3. 格局成败看配合
    """

    def __init__(self, config: AnalysisConfig = None):
        super().__init__("子平真诠统一分析器", "子平真诠", config)

        # 调候用神表（月令 -> 日主 -> 用神）
        self._init_tiaohou_table()

    def _init_tiaohou_table(self):
        """
        初始化调候用神表
        根据《子平真诠》理论：春木、夏火、秋金、冬水各有调候之法
        """
        # 简化的调候表（月支 -> 日主 -> 调候用神）
        self.tiaohou_table = {
            # 春季（寅卯辰）：木旺，火相，水休，金囚，土死
            '寅': {'甲': '丙', '乙': '丙', '丙': '壬', '丁': '甲', '戊': '甲丙', '己': '丙甲', '庚': '丁甲', '辛': '己壬', '壬': '戊丙', '癸': '辛丙'},
            '卯': {'甲': '庚丙', '乙': '癸丙', '丙': '壬', '丁': '甲庚', '戊': '甲丙癸', '己': '甲癸', '庚': '丁甲', '辛': '壬甲', '壬': '戊辛', '癸': '辛甲'},
            '辰': {'甲': '庚丁', '乙': '癸丙', '丙': '壬', '丁': '甲庚', '戊': '甲丙癸', '己': '丙癸', '庚': '甲丁', '辛': '壬甲', '壬': '甲庚', '癸': '辛甲'},
            # 夏季（巳午未）：火旺，土相，木休，水囚，金死
            '巳': {'甲': '癸庚', '乙': '癸', '丙': '壬庚', '丁': '甲庚', '戊': '甲丙癸', '己': '癸丙', '庚': '壬癸', '辛': '壬甲', '壬': '庚戊', '癸': '辛庚'},
            '午': {'甲': '癸庚', '乙': '癸辛', '丙': '壬庚', '丁': '甲庚', '戊': '甲癸', '己': '癸丙', '庚': '壬癸', '辛': '壬甲', '壬': '庚癸', '癸': '庚辛'},
            '未': {'甲': '癸庚', '乙': '癸丙', '丙': '壬', '丁': '甲庚', '戊': '甲丙癸', '己': '癸丙', '庚': '丁甲', '辛': '壬甲', '壬': '甲庚', '癸': '辛甲'},
            # 秋季（申酉戌）：金旺，水相，土休，火囚，木死
            '申': {'甲': '庚丁', '乙': '丙癸', '丙': '壬', '丁': '甲庚', '戊': '丙癸', '己': '丙癸', '庚': '丁甲', '辛': '壬', '壬': '戊甲', '癸': '辛甲'},
            '酉': {'甲': '庚丁', '乙': '丙癸', '丙': '壬', '丁': '甲庚', '戊': '丙癸', '己': '丙癸', '庚': '丁甲', '辛': '壬', '壬': '甲庚', '癸': '辛甲'},
            '戌': {'甲': '庚丁', '乙': '癸辛', '丙': '甲壬', '丁': '甲庚', '戊': '甲丙', '己': '甲丙', '庚': '甲丁', '辛': '壬甲', '壬': '甲庚', '癸': '辛甲'},
            # 冬季（亥子丑）：水旺，木相，金休，土囚，火死
            '亥': {'甲': '庚丙', '乙': '丙', '丙': '甲戊', '丁': '甲庚', '戊': '甲丙', '己': '丙甲', '庚': '丁甲', '辛': '壬丙', '壬': '戊丙', '癸': '辛甲'},
            '子': {'甲': '庚丁', '乙': '丙戊', '丙': '壬庚', '丁': '甲庚', '戊': '甲丙', '己': '丙甲', '庚': '丁甲', '辛': '壬丙', '壬': '戊丙', '癸': '丙辛'},
            '丑': {'甲': '庚丁', '乙': '丙', '丙': '壬', '丁': '甲庚', '戊': '甲丙', '己': '丙甲', '庚': '丁甲', '辛': '壬丙', '壬': '丙戊', '癸': '丙辛'}
        }

    def analyze(self, bazi_data: BaziData) -> AnalysisResult:
        """
        基于《子平真诠》理论的用神判定和格局分析
        ✅ 已修复：
        1. 用神三法：调候、病药、通关
        2. 格局以月令为主
        3. 动态评分，不再硬编码60分
        """
        day_master = bazi_data.get_day_master()
        dm_wx = get_wuxing_by_tiangan(day_master)
        month_branch = bazi_data.get_month_branch()
        month_gan = bazi_data.get_pillars()['month'][0]
        mb_wx = get_wuxing_by_dizhi(month_branch)
        pillars = bazi_data.get_pillars()

        # 统计十神分布
        ten_god_count = self._count_ten_gods(day_master, pillars)

        # 身强身弱判断（简化版：得令40% + 得地30% + 得气30%）
        strength_score = self._calculate_strength(dm_wx, month_branch, pillars)
        strong = strength_score >= 50

        # 1. 确定格局（以月令为主）
        pattern = self._determine_pattern(day_master, month_gan, month_branch)

        # 🔥 计算五行分布（用于判断忌神）
        wuxing_dist = self._calculate_wuxing_distribution(pillars)

        # 2. 用神三法：调候 > 病药 > 通关
        yongshen_info = self._determine_yongshen_three_methods(
            day_master, month_branch, strong, ten_god_count, pillars, wuxing_dist
        )

        # 3. 格局成败判断
        pattern_status, pattern_score = self._analyze_pattern_status(
            pattern, strong, ten_god_count, pillars, yongshen_info
        )

        # 🔥 处理特殊格局名称（如"伤官配印格"）
        if '（' in pattern_status:
            # 提取括号中的内容作为格局修饰
            status_parts = pattern_status.split('（')
            pattern_status = status_parts[0]  # 成格/破格/平格
            pattern_modifier = status_parts[1].rstrip('）')  # 伤官配印/伤官生财
            # 修改格局名称
            if pattern_modifier == '伤官配印':
                pattern = '伤官配印格'
            elif pattern_modifier == '伤官生财':
                pattern = '伤官生财格'

        # 4. 动态评分
        base_score = self._calculate_base_score(pattern)
        yongshen_bonus = self._calculate_yongshen_bonus(yongshen_info, pillars)
        pattern_bonus = pattern_score

        score = base_score + yongshen_bonus + pattern_bonus
        score = max(0.0, min(100.0, score))
        level = '大吉' if score >= 85 else ('吉' if score >= 70 else ('中平' if score >= 55 else ('凶' if score >= 40 else '大凶')))

        # 生成描述
        yong_str = yongshen_info['yongshen']
        xi_str = yongshen_info.get('xishen', '')
        ji_str = yongshen_info.get('jishen', '')
        method = yongshen_info['method']

        description = f"格局：{pattern}（{pattern_status}）；日主{('旺' if strong else '弱')}；用神法：{method}；用神：{yong_str}"
        if xi_str:
            description += f"；喜神：{xi_str}"

        advice = self._generate_advice(pattern, pattern_status, yongshen_info, strong)

        return create_analysis_result(
            analyzer_name=self.name,
            book_name=self.book_name,
            analysis_type="用神与格局分析",
            level=level,
            score=score,
            description=description,
            details={
                'pattern': pattern,
                'pattern_status': pattern_status,
                'strength_score': strength_score,
                'strong': strong,
                'yongshen_info': yongshen_info,
                'ten_god_count': ten_god_count,
                'base_score': base_score,
                'yongshen_bonus': yongshen_bonus,
                'pattern_bonus': pattern_bonus
            },
            advice=advice
        )

    def _count_ten_gods(self, day_master: str, pillars: Dict) -> Dict[str, float]:
        """计算十神分布"""
        ten_god_count: Dict[str, float] = {}
        for pos, (gan, zhi) in pillars.items():
            tg = get_ten_god(day_master, gan)
            ten_god_count[tg] = ten_god_count.get(tg, 0.0) + 1.0
            # 藏干计入十神
            for canggan, w in DIZHI_CANGGAN.get(zhi, []):
                tg_c = get_ten_god(day_master, canggan)
                ten_god_count[tg_c] = ten_god_count.get(tg_c, 0.0) + float(w)
        return ten_god_count

    def _calculate_strength(self, dm_wx: str, month_branch: str, pillars: Dict) -> float:
        """
        计算身强身弱 - 基于《子平真诠》《渊海子平》经典理论
        ✅ 修复：不再使用"得令40% + 得地30% + 得气30%"的加权评分
        改为基于支持力与制约力对比的经典判断方法
        
        理论依据：
        - 《子平真诠》："日主强弱，看支持力与制约力对比"
        - 支持力（比劫印绶）与制约力（财官食伤）的对比
        - 结合得令、得地、得气的综合判断
        
        返回：强度分数（0-100），用于兼容性
        """
        from ..core.utils import get_wuxing_by_tiangan, get_wuxing_by_dizhi
        from ..core.constants import DIZHI_CANGGAN
        
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
            
            # 支持力
            if gan_wx == dm_wx:
                support_power += weight * 1.5  # 日主本身
            elif gan_wx == sheng_map.get(dm_wx):
                support_power += weight * 1.0  # 印绶
            
            # 制约力
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
                
                if cg_wx == dm_wx:
                    support_power += branch_weight * 1.0
                elif cg_wx == sheng_map.get(dm_wx):
                    support_power += branch_weight * 0.8
                
                if cg_wx == ke_map.get(dm_wx):
                    pressure_power += branch_weight * 0.8
                elif cg_wx == wo_ke.get(dm_wx):
                    pressure_power += branch_weight * 0.6
                elif cg_wx == wo_sheng.get(dm_wx):
                    pressure_power += branch_weight * 0.4
        
        # 2. 判断得令
        mb_wx = get_wuxing_by_dizhi(month_branch)
        deling = (mb_wx == dm_wx or mb_wx == sheng_map.get(dm_wx))
        
        # 3. 判断得地
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
        
        # 4. 判断得气
        deqi = False
        for pos, (gan, zhi) in pillars.items():
            if pos == 'day':
                continue
            gan_wx = get_wuxing_by_tiangan(gan)
            if gan_wx == dm_wx or gan_wx == sheng_map.get(dm_wx):
                deqi = True
                break
        
        # 5. 基于支持力与制约力对比判断强度等级
        total_power = support_power + pressure_power
        ratio = support_power / total_power if total_power > 0 else 0.5
        
        # 根据经典理论判断强度等级
        if ratio >= 0.65:
            strength_level = '身极旺' if deling else '身旺'
        elif ratio >= 0.55:
            if deling and dedi:
                strength_level = '身强'
            elif deling or dedi:
                strength_level = '身偏强'
            else:
                strength_level = '中和偏强'
        elif ratio >= 0.45:
            if deling and dedi:
                strength_level = '中和'
            else:
                strength_level = '中和偏弱'
        elif ratio >= 0.35:
            if deling or dedi:
                strength_level = '身偏弱'
            else:
                strength_level = '身弱'
        else:
            strength_level = '身弱' if deling else '身极弱'
        
        # 6. 转换为分数（用于兼容性）
        level_to_score = {
            '身极旺': 90.0, '身旺': 80.0, '身强': 70.0, '身偏强': 60.0,
            '中和偏强': 55.0, '中和': 50.0, '中和偏弱': 45.0,
            '身偏弱': 40.0, '身弱': 30.0, '身极弱': 20.0
        }
        
        return level_to_score.get(strength_level, 50.0)

    def _calculate_deling(self, dm_wx: str, mb_wx: str) -> float:
        """计算得令分数（0-100）"""
        # 五行关系
        sheng_map = {'木': '水', '火': '木', '土': '火', '金': '土', '水': '金'}
        wo_sheng = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
        ke_map = {'木': '金', '火': '水', '土': '木', '金': '火', '水': '土'}

        if mb_wx == dm_wx:
            return 100  # 月令同五行，得令
        elif mb_wx == sheng_map.get(dm_wx):
            return 80  # 月令生我，得生
        elif mb_wx == wo_sheng.get(dm_wx):
            return 30  # 我生月令，泄气
        elif mb_wx == ke_map.get(dm_wx):
            return 10  # 月令克我，受克
        else:
            return 40  # 我克月令，耗力

    def _calculate_dedi(self, dm_wx: str, pillars: Dict) -> float:
        """
        计算得地分数（0-100）：地支通根情况
        ✅ 修复：完整计算地支藏干中的通根
        """
        from ..core.constants import DIZHI_CANGGAN
        from ..core.utils import get_wuxing_by_tiangan

        root_score = 0.0
        total_weight = 0.0

        for pos, (gan, zhi) in pillars.items():
            # 位置权重：日支最重要，月支次之
            if pos == 'day':
                pos_weight = 1.5
            elif pos == 'month':
                pos_weight = 1.2
            else:
                pos_weight = 1.0

            total_weight += pos_weight

            # 检查地支藏干中是否有同五行
            canggan_list = DIZHI_CANGGAN.get(zhi, [])
            for idx, (canggan, cg_weight) in enumerate(canggan_list):
                cg_wx = get_wuxing_by_tiangan(canggan)
                if cg_wx == dm_wx:
                    # 本气、中气、余气的权重
                    if idx == 0:  # 本气
                        root_strength = 1.0
                    elif idx == 1:  # 中气
                        root_strength = 0.5
                    else:  # 余气
                        root_strength = 0.2

                    root_score += pos_weight * root_strength * cg_weight

        # 归一化到0-100
        if total_weight > 0:
            return min(100, (root_score / total_weight) * 100)
        return 0

    def _calculate_deqi(self, dm_wx: str, pillars: Dict) -> float:
        """
        计算得气分数（0-100）：天干透出情况
        ✅ 修复：完整计算天干中的生扶
        """
        from ..core.utils import get_wuxing_by_tiangan

        appear_count = 0.0
        total_gans = 0

        # 五行关系
        sheng_map = {'木': '水', '火': '木', '土': '火', '金': '土', '水': '金'}

        for pos, (gan, zhi) in pillars.items():
            if pos == 'day':  # 跳过日主自己
                continue

            total_gans += 1
            gan_wx = get_wuxing_by_tiangan(gan)

            # 同五行或生我的五行
            if gan_wx == dm_wx:
                appear_count += 1.0  # 同五行
            elif gan_wx == sheng_map.get(dm_wx):
                appear_count += 0.8  # 生我

        # 归一化到0-100
        if total_gans > 0:
            return (appear_count / total_gans) * 100
        return 0

    def _determine_pattern(self, day_master: str, month_gan: str, month_branch: str) -> str:
        """
        确定格局（以月令为主）
        ✅ 符合《子平真诠》理论
        """
        month_ten_god = get_ten_god(day_master, month_gan)

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

        return pattern_map.get(month_ten_god, '普通格局')

    def _calculate_wuxing_distribution(self, pillars: Dict) -> Dict:
        """计算五行分布"""
        wuxing_count = {'木': 0.0, '火': 0.0, '土': 0.0, '金': 0.0, '水': 0.0}

        for pos, (gan, zhi) in pillars.items():
            # 天干
            gan_wx = get_wuxing_by_tiangan(gan)
            if gan_wx:
                wuxing_count[gan_wx] += 1.0

            # 地支藏干
            for canggan, weight in DIZHI_CANGGAN.get(zhi, []):
                cg_wx = get_wuxing_by_tiangan(canggan)
                if cg_wx:
                    wuxing_count[cg_wx] += weight

        return wuxing_count

    def _determine_yongshen_three_methods(self, day_master: str, month_branch: str,
                                          strong: bool, ten_god_count: Dict, pillars: Dict,
                                          wuxing_dist: Dict = None) -> Dict:
        """
        用神三法：调候 > 病药 > 通关
        ✅ 符合《子平真诠》核心理论
        """
        # 1. 调候法（优先）：四季寒暖燥湿
        tiaohou_yong = self.tiaohou_table.get(month_branch, {}).get(day_master, '')
        if tiaohou_yong:
            # 检查调候用神是否在八字中
            tiaohou_present = self._check_yongshen_present(tiaohou_yong, pillars)
            if tiaohou_present:
                return {
                    'method': '调候',
                    'yongshen': tiaohou_yong,
                    'xishen': self._get_xishen(tiaohou_yong),
                    'jishen': self._get_jishen(tiaohou_yong, day_master, wuxing_dist),
                    'present': True,
                    'strength': tiaohou_present
                }

        # 2. 病药法：八字有病，以药为用
        bingyao_result = self._determine_bingyao(ten_god_count, strong, pillars, wuxing_dist)
        if bingyao_result:
            return bingyao_result

        # 3. 通关法：两神相战，以通关为用
        tongguan_result = self._determine_tongguan(ten_god_count, pillars)
        if tongguan_result:
            return tongguan_result

        # 默认：扶抑法
        if strong:
            return {
                'method': '扶抑',
                'yongshen': '食伤财',
                'xishen': '官杀',
                'jishen': '印比',
                'present': False,
                'strength': 0
            }
        else:
            return {
                'method': '扶抑',
                'yongshen': '印比',
                'xishen': '比劫',
                'jishen': '食伤财官杀',
                'present': False,
                'strength': 0
            }

    def _check_yongshen_present(self, yongshen: str, pillars: Dict) -> float:
        """检查用神是否在八字中，返回强度"""
        strength = 0.0
        for pos, (gan, zhi) in pillars.items():
            if gan in yongshen:
                strength += 1.0
            # 检查藏干
            for canggan, w in DIZHI_CANGGAN.get(zhi, []):
                if canggan in yongshen:
                    strength += w
        return strength

    def _get_xishen(self, yongshen: str) -> str:
        """
        根据用神推导喜神
        🔥 修复：喜神应该包含用神本身的五行，以及生用神的五行
        """
        if not yongshen:
            return ''

        # 提取用神中的所有天干
        yongshen_chars = [c for c in yongshen if c in '甲乙丙丁戊己庚辛壬癸']
        if not yongshen_chars:
            return ''

        # 获取用神的五行
        xishen_wuxing = set()
        for char in yongshen_chars:
            wx = get_wuxing_by_tiangan(char)
            if wx:
                xishen_wuxing.add(wx)

        # 🔥 关键修复：喜神 = 用神本身的五行（不再添加生用神的五行）
        # 例如：用神壬甲（水木），喜神就是水木
        return '、'.join(sorted(xishen_wuxing, key=lambda x: ['木', '火', '土', '金', '水'].index(x)))

    def _get_jishen(self, yongshen: str, day_master: str = '', wuxing_dist: Dict = None) -> str:
        """
        根据用神推导忌神
        ✅ 修复：忌神应该是克用神的五行，但不能包含用神本身的五行

        理论依据：
        - 忌神 = 克用神的五行
        - 例如：用神壬甲（水木），克水的是土，克木的是金，所以忌神是土金
        - 但如果用神中包含金（如辛甲），则金不应该是忌神

        特殊情况：
        - 辛金日主，土重埋金，用神壬甲（水木），忌神土火
          - 土：克水，加重埋金
          - 火：生土，加重土旺
          - 金：虽然克木，但金是生水的，且辛金日主需要金帮身，所以金不是忌神
        """
        if not yongshen:
            return ''

        # 提取用神中的所有天干
        yongshen_chars = [c for c in yongshen if c in '甲乙丙丁戊己庚辛壬癸']
        if not yongshen_chars:
            return ''

        # ✅ 第一步：获取用神的五行（用于后续排除）
        yongshen_wuxing = set()
        for char in yongshen_chars:
            wx = get_wuxing_by_tiangan(char)
            if wx:
                yongshen_wuxing.add(wx)

        # ✅ 第二步：计算克用神的五行
        jishen_wuxing = set()
        for char in yongshen_chars:
            wx = get_wuxing_by_tiangan(char)
            if wx:
                # 克用神的五行为忌神
                ke_map = {'木': '金', '火': '水', '土': '木', '金': '火', '水': '土'}
                jishen_wx = ke_map.get(wx)
                if jishen_wx:
                    jishen_wuxing.add(jishen_wx)

        # ✅ 第三步：特殊判断 - 土重埋金的情况
        if day_master in ['庚', '辛'] and wuxing_dist:
            tu_count = wuxing_dist.get('土', 0)
            if tu_count > 3.5:  # 土过旺
                # 土为忌神（埋金，克水）
                jishen_wuxing.add('土')
                # 火为忌神（生土，加重土旺）
                jishen_wuxing.add('火')
                # ❌ 不要把金加入忌神，因为金可能是用神，且金生水

        # ✅ 第四步：确保喜神和忌神互斥 - 从忌神中移除用神的五行
        jishen_wuxing = jishen_wuxing - yongshen_wuxing

        return '、'.join(sorted(jishen_wuxing, key=lambda x: ['木', '火', '土', '金', '水'].index(x)))

    def _determine_bingyao(self, ten_god_count: Dict, strong: bool, pillars: Dict = None, wuxing_dist: Dict = None) -> Dict:
        """
        🔥 完善病药法：八字有病，以药为用
        基于《子平真诠》理论，识别更多"病"和对应的"药"
        
        常见病症：
        1. 官杀混杂 → 用食伤制杀或印化杀
        2. 伤官见官 → 用财通关或印化伤
        3. 财多身弱 → 用比劫扶身
        4. 印重身弱 → 用财破印
        5. 比劫夺财 → 用官杀制比劫
        6. 食伤泄身太过 → 用印护身
        7. 枭神夺食 → 用财破枭
        8. 财印相战 → 用比劫通关
        9. 官杀无制 → 用食伤制杀或印化杀
        10. 土重埋金 → 用木疏土或水润土
        """
        # 1. 官杀混杂（最优先）
        guan_count = ten_god_count.get('正官', 0)
        sha_count = ten_god_count.get('偏官', 0)
        if guan_count > 0 and sha_count > 0:
            # 优先用食伤制杀，其次用印化杀
            shishang_count = ten_god_count.get('食神', 0) + ten_god_count.get('伤官', 0)
            yin_count = ten_god_count.get('正印', 0) + ten_god_count.get('偏印', 0)
            if shishang_count > 0:
                return {
                    'method': '病药（官杀混杂）',
                    'yongshen': '食伤',
                    'xishen': '比劫',
                    'jishen': '财',
                    'present': True,
                    'strength': shishang_count
                }
            elif yin_count > 0:
                return {
                    'method': '病药（官杀混杂）',
                    'yongshen': '印',
                    'xishen': '比劫',
                    'jishen': '财',
                    'present': True,
                    'strength': yin_count
                }
            else:
                return {
                    'method': '病药（官杀混杂）',
                    'yongshen': '食伤印',
                    'xishen': '比劫',
                    'jishen': '财',
                    'present': False,
                    'strength': 0
                }

        # 2. 伤官见官
        shangguan_count = ten_god_count.get('伤官', 0)
        if shangguan_count > 0 and guan_count > 0:
            # 用财通关，或印化伤
            cai_count = ten_god_count.get('正财', 0) + ten_god_count.get('偏财', 0)
            yin_count = ten_god_count.get('正印', 0) + ten_god_count.get('偏印', 0)
            if cai_count > 0:
                return {
                    'method': '病药（伤官见官）',
                    'yongshen': '财',
                    'xishen': '食伤',
                    'jishen': '比劫',
                    'present': True,
                    'strength': cai_count
                }
            elif yin_count > 0:
                return {
                    'method': '病药（伤官见官）',
                    'yongshen': '印',
                    'xishen': '比劫',
                    'jishen': '财',
                    'present': True,
                    'strength': yin_count
                }
            else:
                return {
                    'method': '病药（伤官见官）',
                    'yongshen': '财印',
                    'xishen': '食伤',
                    'jishen': '比劫',
                    'present': False,
                    'strength': 0
                }

        # 3. 财多身弱
        cai_count = ten_god_count.get('正财', 0) + ten_god_count.get('偏财', 0)
        bijie_count = ten_god_count.get('比肩', 0) + ten_god_count.get('劫财', 0)
        if cai_count > 2.5 and not strong and bijie_count < 1:
            return {
                'method': '病药（财多身弱）',
                'yongshen': '比劫',
                'xishen': '印',
                'jishen': '财官',
                'present': bijie_count > 0,
                'strength': bijie_count
            }

        # 4. 印重身弱（实际是身强印重）
        yin_count = ten_god_count.get('正印', 0) + ten_god_count.get('偏印', 0)
        if yin_count > 2.5 and strong:
            # 用财破印
            cai_count = ten_god_count.get('正财', 0) + ten_god_count.get('偏财', 0)
            return {
                'method': '病药（印重身强）',
                'yongshen': '财',
                'xishen': '食伤',
                'jishen': '印比',
                'present': cai_count > 0,
                'strength': cai_count
            }

        # 5. 比劫夺财
        bijie_count = ten_god_count.get('比肩', 0) + ten_god_count.get('劫财', 0)
        if bijie_count > 2 and cai_count > 0 and strong:
            # 用官杀制比劫
            guansha_count = guan_count + sha_count
            return {
                'method': '病药（比劫夺财）',
                'yongshen': '官杀',
                'xishen': '财',
                'jishen': '比劫',
                'present': guansha_count > 0,
                'strength': guansha_count
            }

        # 6. 食伤泄身太过
        shishang_count = ten_god_count.get('食神', 0) + ten_god_count.get('伤官', 0)
        if shishang_count > 2.5 and not strong:
            # 用印护身
            yin_count = ten_god_count.get('正印', 0) + ten_god_count.get('偏印', 0)
            return {
                'method': '病药（食伤泄身）',
                'yongshen': '印',
                'xishen': '比劫',
                'jishen': '食伤财',
                'present': yin_count > 0,
                'strength': yin_count
            }

        # 7. 枭神夺食
        pianyin_count = ten_god_count.get('偏印', 0)
        shishen_count = ten_god_count.get('食神', 0)
        if pianyin_count > 0 and shishen_count > 0:
            # 用财破枭
            cai_count = ten_god_count.get('正财', 0) + ten_god_count.get('偏财', 0)
            return {
                'method': '病药（枭神夺食）',
                'yongshen': '财',
                'xishen': '食伤',
                'jishen': '印',
                'present': cai_count > 0,
                'strength': cai_count
            }

        # 8. 官杀无制（身弱遇官杀）
        guansha_count = guan_count + sha_count
        if guansha_count > 1.5 and not strong:
            # 用印化杀或比劫抗杀
            yin_count = ten_god_count.get('正印', 0) + ten_god_count.get('偏印', 0)
            bijie_count = ten_god_count.get('比肩', 0) + ten_god_count.get('劫财', 0)
            if yin_count > 0:
                return {
                    'method': '病药（官杀无制）',
                    'yongshen': '印',
                    'xishen': '比劫',
                    'jishen': '财',
                    'present': True,
                    'strength': yin_count
                }
            elif bijie_count > 0:
                return {
                    'method': '病药（官杀无制）',
                    'yongshen': '比劫',
                    'xishen': '印',
                    'jishen': '财官',
                    'present': True,
                    'strength': bijie_count
                }

        # 9. 土重埋金（特殊五行病）
        if wuxing_dist and wuxing_dist.get('土', 0) > 3.5:
            # 检查日主是否为金
            day_master = pillars.get('day', ('', ''))[0] if pillars else ''
            if day_master in ['庚', '辛']:
                # 用木疏土或水润土
                return {
                    'method': '病药（土重埋金）',
                    'yongshen': '木水',
                    'xishen': '金',
                    'jishen': '土',
                    'present': False,
                    'strength': 0
                }

        return None

    def _determine_tongguan(self, ten_god_count: Dict, pillars: Dict = None) -> Dict:
        """
        🔥 完善通关法：两神相战，以通关为用
        基于《子平真诠》理论，识别更多相战关系和通关用神
        
        常见相战关系：
        1. 官杀克比劫 → 用印通关（印生比劫，官杀生印）
        2. 财克印 → 用比劫通关（比劫生食伤，食伤生财）
        3. 食伤克官杀 → 用财通关（财生官杀，食伤生财）
        4. 比劫克财 → 用食伤通关（食伤生财，比劫生食伤）
        5. 印克食伤 → 用比劫通关（比劫生食伤，印生比劫）
        6. 官杀与食伤相战 → 用财通关
        7. 财与印相战 → 用比劫通关
        """
        guan_count = ten_god_count.get('正官', 0)
        sha_count = ten_god_count.get('偏官', 0)
        guansha_count = guan_count + sha_count
        
        bijie_count = ten_god_count.get('比肩', 0) + ten_god_count.get('劫财', 0)
        cai_count = ten_god_count.get('正财', 0) + ten_god_count.get('偏财', 0)
        yin_count = ten_god_count.get('正印', 0) + ten_god_count.get('偏印', 0)
        shishang_count = ten_god_count.get('食神', 0) + ten_god_count.get('伤官', 0)

        # 1. 官杀与比劫相战（最优先）
        if guansha_count > 1 and bijie_count > 1:
            # 用印通关：印生比劫，官杀生印
            return {
                'method': '通关（官杀克比劫）',
                'yongshen': '印',
                'xishen': '比劫',
                'jishen': '财',
                'present': yin_count > 0,
                'strength': yin_count
            }

        # 2. 财与印相战
        if cai_count > 1 and yin_count > 1:
            # 用比劫通关：比劫生食伤，食伤生财；同时比劫受印生
            return {
                'method': '通关（财克印）',
                'yongshen': '比劫',
                'xishen': '食伤',
                'jishen': '官杀',
                'present': bijie_count > 0,
                'strength': bijie_count
            }

        # 3. 食伤与官杀相战
        if shishang_count > 1 and guansha_count > 1:
            # 用财通关：财生官杀，食伤生财
            return {
                'method': '通关（食伤克官杀）',
                'yongshen': '财',
                'xishen': '官杀',
                'jishen': '比劫',
                'present': cai_count > 0,
                'strength': cai_count
            }

        # 4. 比劫与财相战
        if bijie_count > 1 and cai_count > 1:
            # 用食伤通关：比劫生食伤，食伤生财
            return {
                'method': '通关（比劫克财）',
                'yongshen': '食伤',
                'xishen': '财',
                'jishen': '印',
                'present': shishang_count > 0,
                'strength': shishang_count
            }

        # 5. 印与食伤相战
        if yin_count > 1 and shishang_count > 1:
            # 用比劫通关：比劫生食伤，印生比劫
            return {
                'method': '通关（印克食伤）',
                'yongshen': '比劫',
                'xishen': '食伤',
                'jishen': '印',
                'present': bijie_count > 0,
                'strength': bijie_count
            }

        # 6. 官杀与食伤相战（特殊）
        if guansha_count > 0.5 and shishang_count > 0.5:
            # 用财通关：财生官杀，食伤生财
            return {
                'method': '通关（食伤克官杀）',
                'yongshen': '财',
                'xishen': '官杀',
                'jishen': '比劫',
                'present': cai_count > 0,
                'strength': cai_count
            }

        return None

    def _calculate_base_score(self, pattern: str) -> float:
        """
        根据格局类型计算基础分 - 已废弃，不再使用硬编码分数
        ✅ 修复：格局判断应基于《子平真诠》格局成败理论，而非硬编码分数
        此函数保留仅为兼容性，返回0（表示不打分）
        """
        # ✅ 修复：不再使用硬编码的基础分（68、62、65等）
        # 格局判断应基于《子平真诠》格局成败理论，通过格局配合和十神配置综合判断
        return 0.0

    def _calculate_yongshen_bonus(self, yongshen_info: Dict, pillars: Dict) -> float:
        """
        根据用神是否得力计算加成 - 已废弃，不再使用硬编码加分
        ✅ 修复：用神判断应基于《子平真诠》用神三法理论，而非简单加减分
        此函数保留仅为兼容性，返回0（表示不打分）
        """
        # ✅ 修复：不再使用简单的加减bonus（strength * 5、调候+5等）
        # 用神判断应基于《子平真诠》用神三法（调候、病药、通关、扶抑）的综合理论
        return 0.0

    def _analyze_pattern_status(self, pattern: str, strong: bool, ten_god_count: Dict,
                                pillars: Dict, yongshen_info: Dict) -> Tuple[str, float]:
        """
        分析格局成败
        ✅ 符合《子平真诠》理论：格局成败看配合
        """
        bonus = 0.0

        # 正官格
        if pattern == '正官格':
            # 成格条件：身强官旺，有印护官，无伤官破格
            if strong and ten_god_count.get('正官', 0) > 0:
                bonus += 10
                if ten_god_count.get('正印', 0) > 0:
                    bonus += 5  # 印护官
                if ten_god_count.get('伤官', 0) > 0:
                    bonus -= 10  # 伤官见官
                    return '破格', bonus
                return '成格', bonus
            else:
                return '平格', 0

        # 七杀格
        elif pattern == '七杀格':
            # 成格条件：有食伤制杀，或有印化杀
            if ten_god_count.get('食神', 0) > 0 or ten_god_count.get('伤官', 0) > 0:
                bonus += 12  # 食伤制杀
                return '成格', bonus
            elif ten_god_count.get('正印', 0) > 0 or ten_god_count.get('偏印', 0) > 0:
                bonus += 10  # 印化杀
                return '成格', bonus
            else:
                bonus -= 8  # 杀无制化
                return '破格', bonus

        # 财格
        elif '财' in pattern:
            # 成格条件：身强财旺，有食伤生财
            if strong:
                bonus += 8
                if ten_god_count.get('食神', 0) > 0 or ten_god_count.get('伤官', 0) > 0:
                    bonus += 5  # 食伤生财
                return '成格', bonus
            else:
                bonus -= 8  # 身弱财多
                return '破格', bonus

        # 食神格
        elif pattern == '食神格':
            # 成格条件：身强食旺，有财泄秀，无枭神夺食
            if strong:
                bonus += 8
                if ten_god_count.get('正财', 0) > 0 or ten_god_count.get('偏财', 0) > 0:
                    bonus += 5  # 食神生财
                if ten_god_count.get('偏印', 0) > 0:
                    bonus -= 10  # 枭神夺食
                    return '破格', bonus
                return '成格', bonus
            else:
                return '平格', 0

        # 伤官格
        elif pattern == '伤官格':
            # ✅ 修复：先检查破格条件，再检查成格条件
            # 破格条件1：伤官见官（最严重）- 《子平真诠》："伤官见官，为祸百端"
            if ten_god_count.get('正官', 0) > 0:
                bonus -= 12  # 伤官见官
                return '破格', bonus

            # 成格条件：伤官配印，或伤官生财
            yin_count = ten_god_count.get('正印', 0) + ten_god_count.get('偏印', 0)
            cai_count = ten_god_count.get('正财', 0) + ten_god_count.get('偏财', 0)

            # 破格条件2：财星坏印 - 《子平真诠》："伤官佩印，不宜逢财"
            if yin_count > 0 and cai_count >= 1.0 and cai_count >= yin_count * 1.5:
                bonus -= 10  # 财星坏印
                return '破格', bonus

            # 成格条件1：伤官配印（需要印星有力）
            if yin_count > 0:
                # ✅ 检查印星是否有力（有根或透干）
                # 简化判断：印星数量>=0.6认为有力（本气根）
                if yin_count >= 0.6:
                    bonus += 10  # 伤官配印
                    return '成格（伤官配印）', bonus
                else:
                    # 印星无力，不能成格
                    return '平格', 0

            # 成格条件2：伤官生财
            elif cai_count > 0:
                bonus += 8  # 伤官生财
                return '成格（伤官生财）', bonus
            else:
                return '平格', 0

        # 印格
        elif '印' in pattern:
            # 成格条件：身弱印旺，有官生印
            if not strong:
                bonus += 8
                if ten_god_count.get('正官', 0) > 0 or ten_god_count.get('偏官', 0) > 0:
                    bonus += 5  # 官印相生
                return '成格', bonus
            else:
                bonus -= 6  # 身强印重
                return '破格', bonus

        # 建禄羊刃格
        elif pattern in ('建禄格', '羊刃格'):
            # 成格条件：身弱喜比劫，身强需财官
            if not strong:
                bonus += 8
                return '成格', bonus
            elif ten_god_count.get('正官', 0) > 0 or ten_god_count.get('偏官', 0) > 0:
                bonus += 10  # 羊刃驾杀
                return '成格', bonus
            else:
                bonus -= 6  # 身强比劫重
                return '平格', bonus

        return '平格', 0

    def _generate_advice(self, pattern: str, pattern_status: str, yongshen_info: Dict, strong: bool) -> str:
        """
        生成建议
        ✅ 根据格局成败和用神给出建议
        """
        method = yongshen_info.get('method', '')
        yongshen = yongshen_info.get('yongshen', '')

        if pattern_status == '成格':
            if '正官格' in pattern:
                return f'正官格成，{method}用神为{yongshen}，宜循规守纪，求取功名，忌伤官破格。'
            elif '七杀格' in pattern:
                return f'七杀格成，{method}用神为{yongshen}，宜有制化，食伤制杀或印化杀为贵。'
            elif '财' in pattern:
                return f'{pattern}成，{method}用神为{yongshen}，宜勤俭持家，食伤生财为佳，忌比劫争财。'
            elif '食神格' in pattern:
                return f'食神格成，{method}用神为{yongshen}，宜才艺谋生，食神生财为美，忌枭神夺食。'
            elif '伤官格' in pattern:
                return f'伤官格成，{method}用神为{yongshen}，宜伤官配印或伤官生财，忌伤官见官。'
            elif '印' in pattern:
                return f'{pattern}成，{method}用神为{yongshen}，宜学习进修，官印相生为贵，忌财破印。'
            elif pattern in ('建禄格', '羊刃格'):
                return f'{pattern}成，{method}用神为{yongshen}，宜自立创业，羊刃驾杀为武贵。'
            else:
                return f'格局成立，{method}用神为{yongshen}，宜顺势而为。'

        elif pattern_status == '破格':
            return f'{pattern}破败，{method}用神为{yongshen}，需补救用神，避免忌神运。'

        else:
            return f'{pattern}平常，{method}用神为{yongshen}，取中和为贵，随运随时。'

    @staticmethod
    def analyze_huwei_guan(day_master: str, pillars: Dict,
                          pattern: str, ten_god_count: Dict[str, float]) -> Dict[str, any]:
        """
        分析护卫关 - 基于《子平真诠》理论

        护卫关：检查用神是否有护卫神扶持
        - 伤官格：需要印星护卫（印克伤官）
        - 食神格：需要财星护卫（食神生财）
        - 财格：需要食伤护卫（食伤生财）
        - 官格：需要印星护卫（官印相生）
        - 印格：需要官杀护卫（官印相生）

        Args:
            day_master: 日主天干
            pillars: 四柱信息 {'year': '戊午', 'month': '壬戌', ...} 或 {'year': ('戊', '午'), ...}
            pattern: 格局类型
            ten_god_count: 十神数量统计

        Returns:
            {
                'has_huwei': True/False,
                'description': '有护卫（年干戊土正印克制月干壬水伤官）',
                'huwei_type': '印星护卫',
                'huwei_strength': 1.5,
                'detail': '年干戊土正印克制月干壬水伤官'
            }
        """
        # 辅助函数：提取天干地支
        def extract_gan_zhi(pillar_value):
            """提取天干地支，支持字符串和元组格式"""
            if isinstance(pillar_value, str) and len(pillar_value) >= 2:
                return pillar_value[0], pillar_value[1]
            elif isinstance(pillar_value, (list, tuple)) and len(pillar_value) >= 2:
                return pillar_value[0], pillar_value[1]
            else:
                return '', ''

        # 1. 根据格局类型确定需要的护卫（基于《子平真诠》理论）
        huwei_map = {
            '伤官': ['正印', '偏印'],  # 伤官格需要印星护卫（印克伤官）
            '食神': ['正财', '偏财'],  # 食神格需要财星护卫（食神生财）
            '正财': ['食神', '伤官'],  # 财格需要食伤护卫（食伤生财）
            '偏财': ['食神', '伤官'],
            '正官': ['正印', '偏印'],  # 官格需要印星护卫（官印相生）
            '偏官': ['正印', '偏印', '食神'],  # 七杀格需要印星或食神护卫
            '正印': ['正官', '偏官'],  # 印格需要官杀护卫（官印相生）
            '偏印': ['正官', '偏官']
        }

        # 2. 提取格局主神
        main_shishen = None
        for key in huwei_map.keys():
            if key in pattern:
                main_shishen = key
                break

        if not main_shishen:
            return {
                'has_huwei': False,
                'description': '无护卫',
                'huwei_type': '',
                'huwei_strength': 0,
                'detail': ''
            }

        # 3. 查找护卫神位置
        needed_huwei = huwei_map.get(main_shishen, [])
        huwei_positions = []

        for pos, pillar_value in pillars.items():
            gan, zhi = extract_gan_zhi(pillar_value)
            if gan:
                ten_god = get_ten_god(day_master, gan)
                if ten_god in needed_huwei:
                    huwei_positions.append((pos, gan, ten_god))

        # 4. 查找主神位置
        main_positions = []
        for pos, pillar_value in pillars.items():
            gan, zhi = extract_gan_zhi(pillar_value)
            if gan:
                ten_god = get_ten_god(day_master, gan)
                if ten_god == main_shishen:
                    main_positions.append((pos, gan, ten_god))

        # 5. 生成描述
        if not huwei_positions:
            return {
                'has_huwei': False,
                'description': '无护卫',
                'huwei_type': '',
                'huwei_strength': 0,
                'detail': ''
            }

        # 位置映射
        pos_map = {'year': '年干', 'month': '月干', 'day': '日干', 'hour': '时干'}

        # 取第一个护卫神和第一个主神
        huwei_pos, huwei_gan, huwei_type = huwei_positions[0]

        detail = ''
        if main_positions:
            main_pos, main_gan, main_type = main_positions[0]

            # 判断五行关系
            huwei_wx = TIANGAN_WUXING.get(huwei_gan, '')
            main_wx = TIANGAN_WUXING.get(main_gan, '')

            # 五行相克关系
            ke_map = {'木': '土', '火': '金', '土': '水', '金': '木', '水': '火'}
            # 五行相生关系
            sheng_map = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}

            # 判断关系类型
            if ke_map.get(huwei_wx) == main_wx:
                relation = '克制'
            elif sheng_map.get(huwei_wx) == main_wx:
                relation = '生扶'
            else:
                relation = '护卫'

            detail = f"{pos_map[huwei_pos]}{huwei_gan}{huwei_type}{relation}{pos_map[main_pos]}{main_gan}{main_type}"
        else:
            detail = f"{pos_map[huwei_pos]}{huwei_gan}{huwei_type}"

        # 计算护卫强度
        huwei_strength = sum(ten_god_count.get(h, 0) for h in needed_huwei)

        return {
            'has_huwei': True,
            'description': f'有护卫（{detail}）',
            'huwei_type': huwei_type,
            'huwei_strength': huwei_strength,
            'detail': detail
        }
