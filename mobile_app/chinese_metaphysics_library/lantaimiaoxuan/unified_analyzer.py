from typing import List, Dict, Tuple
from ..core.base_analyzer import BaseAnalyzer
from ..core.data_structures import BaziData, AnalysisResult, AnalysisConfig
from ..core.utils import create_analysis_result, get_wuxing_by_tiangan, get_wuxing_by_dizhi, get_ten_god
from ..core.constants import DIZHI_CANGGAN

class LantaimiaoxuanAnalyzer(BaseAnalyzer):
    """
    《兰台妙选》统一分析器
    核心理论：
    1. 特殊格局识别（魁罡、日禄、日德、金神等）
    2. 格局成立条件判断（魁罡忌财官，日禄喜财官等）
    3. 动态评分，不硬编码
    """

    def __init__(self, config: AnalysisConfig = None):
        super().__init__("兰台妙选统一分析器", "兰台妙选", config)

        # ✅ 完整的特殊格局定义（包含成立条件）
        self.SPECIAL_PATTERNS = {
            '魁罡': {
                'pillars': {('庚','辰'),('庚','戌'),('壬','辰'),('壬','戌')},
                'base_score': 70,
                'success_bonus': 15,
                'fail_penalty': -10,
                'success_condition': '无财官',  # 魁罡格忌见财官
                'description': '魁罡格，主聪慧果断，刚烈不屈'
            },
            '日禄': {
                'pillars': {('甲','寅'),('乙','卯'),('丙','巳'),('丁','午'),('庚','申'),('辛','酉'),('壬','亥'),('癸','子')},
                'base_score': 65,
                'success_bonus': 10,
                'fail_penalty': -5,
                'success_condition': '有财官',  # 日禄格喜见财官
                'description': '日禄格，主衣禄丰足，自立自强'
            },
            '日德': {
                'pillars': {('甲','寅'),('丙','辰'),('戊','辰'),('庚','辰'),('壬','戌')},
                'base_score': 66,
                'success_bonus': 12,
                'fail_penalty': -6,
                'success_condition': '无刑冲',  # 日德格忌刑冲
                'description': '日德格，主聪慧仁厚，德行高尚'
            },
            '金神': {
                'pillars': {('癸','巳'),('己','巳'),('乙','丑')},
                'base_score': 62,
                'success_bonus': 13,
                'fail_penalty': -8,
                'success_condition': '有火制',  # 金神格需火制
                'description': '金神格，主刚毅果敢，需火制方吉'
            },
            '六秀': {
                'pillars': {('丙','午'),('丁','未'),('戊','午'),('己','未'),('庚','辰'),('辛','巳')},
                'base_score': 68,
                'success_bonus': 11,
                'fail_penalty': -5,
                'success_condition': '无破损',
                'description': '六秀格，主聪明秀丽，才华横溢'
            },
            '福德': {
                'pillars': {('甲','子'),('乙','亥'),('丙','寅'),('丁','卯'),('戊','午'),('己','巳'),('庚','申'),('辛','酉'),('壬','子'),('癸','亥')},
                'base_score': 64,
                'success_bonus': 9,
                'fail_penalty': -4,
                'success_condition': '无破损',
                'description': '福德格，主福禄双全，平安顺遂'
            }
        }

    def analyze(self, bazi_data: BaziData) -> AnalysisResult:
        """
        特殊格局识别
        ✅ 已修复：
        1. 完善特殊格局判断条件（魁罡忌财官，日禄喜财官等）
        2. 动态评分，不再硬编码60分
        3. 增加更多特殊格局（金神、六秀、福德等）
        """
        pillars = bazi_data.get_pillars()
        day_gan, day_zhi = pillars['day']
        day_master = bazi_data.get_day_master()
        month_branch = bazi_data.get_month_branch()

        # 识别所有特殊格局
        identified_patterns = self._identify_special_patterns(day_gan, day_zhi, month_branch)

        # 判断格局成败
        pattern_results = []
        total_score = 0.0

        if identified_patterns:
            for pattern_name in identified_patterns:
                pattern_info = self.SPECIAL_PATTERNS[pattern_name]
                success, reason = self._check_pattern_success(pattern_name, pattern_info, pillars, day_master)

                if success:
                    pattern_score = pattern_info['base_score'] + pattern_info['success_bonus']
                    status = '成格'
                else:
                    pattern_score = pattern_info['base_score'] + pattern_info['fail_penalty']
                    status = '破格'

                total_score += pattern_score
                pattern_results.append({
                    'name': pattern_name,
                    'status': status,
                    'reason': reason,
                    'score': pattern_score,
                    'description': pattern_info['description']
                })

            # 多个格局取平均分
            score = total_score / len(identified_patterns)
        else:
            # 无特殊格局，基础分
            score = 55.0
            pattern_results.append({
                'name': '无特殊格局',
                'status': '平常',
                'reason': '日柱不符合特殊格局条件',
                'score': 55.0,
                'description': '普通命格，需看其他格局'
            })

        score = max(0.0, min(100.0, score))
        level = '大吉' if score >= 85 else ('吉' if score >= 70 else ('中平' if score >= 55 else ('凶' if score >= 40 else '大凶')))

        # 生成描述
        if identified_patterns:
            pattern_strs = []
            for result in pattern_results:
                pattern_strs.append(f"{result['name']}（{result['status']}）")
            description = f"特殊格局：{' + '.join(pattern_strs)}"
        else:
            description = "无特殊格局，普通命格"

        advice = self._generate_advice(pattern_results)

        return create_analysis_result(
            analyzer_name=self.name,
            book_name=self.book_name,
            analysis_type="特殊格局分析",
            level=level,
            score=score,
            description=description,
            details={
                'identified_patterns': identified_patterns,
                'pattern_results': pattern_results
            },
            advice=advice
        )

    def _identify_special_patterns(self, day_gan: str, day_zhi: str, month_branch: str) -> List[str]:
        """
        识别特殊格局
        ✅ 完整的格局识别逻辑
        """
        patterns = []
        day_pillar = (day_gan, day_zhi)

        # 检查所有日柱格局
        for pattern_name, pattern_info in self.SPECIAL_PATTERNS.items():
            if 'pillars' in pattern_info and day_pillar in pattern_info['pillars']:
                patterns.append(pattern_name)

        return patterns

    def _check_pattern_success(self, pattern_name: str, pattern_info: Dict,
                               pillars: Dict, day_master: str) -> Tuple[bool, str]:
        """
        检查格局是否成立
        ✅ 根据不同格局的成立条件判断
        """
        condition = pattern_info.get('success_condition', '')

        # 魁罡格：忌见财官
        if pattern_name == '魁罡':
            has_cai = self._has_cai_guan(pillars, day_master, check_type='财')
            has_guan = self._has_cai_guan(pillars, day_master, check_type='官')

            if has_cai or has_guan:
                return False, '见财官破格'
            else:
                return True, '无财官，格局成立'

        # 日禄格：喜见财官
        elif pattern_name == '日禄':
            has_cai = self._has_cai_guan(pillars, day_master, check_type='财')
            has_guan = self._has_cai_guan(pillars, day_master, check_type='官')

            if has_cai or has_guan:
                return True, '有财官，格局成立'
            else:
                return False, '无财官，格局不成'

        # 日德格：忌刑冲
        elif pattern_name == '日德':
            has_xing_chong = self._has_xing_chong(pillars)

            if has_xing_chong:
                return False, '有刑冲破格'
            else:
                return True, '无刑冲，格局成立'

        # 金神格：需火制
        elif pattern_name == '金神':
            has_fire = self._has_wuxing(pillars, '火')

            if has_fire:
                return True, '有火制，格局成立'
            else:
                return False, '无火制，格局不成'

        # 六秀格、福德格：无破损即可
        elif pattern_name in ('六秀', '福德'):
            has_damage = self._has_damage(pillars, day_master)

            if has_damage:
                return False, '有破损，格局不成'
            else:
                return True, '无破损，格局成立'

        # 默认：成立
        return True, '格局成立'

    def _has_cai_guan(self, pillars: Dict, day_master: str, check_type: str = '财') -> bool:
        """检查是否有财或官"""
        for pos, (gan, zhi) in pillars.items():
            if pos == 'day':
                continue

            ten_god = get_ten_god(day_master, gan)

            if check_type == '财':
                if ten_god in ('正财', '偏财'):
                    return True
            elif check_type == '官':
                if ten_god in ('正官', '偏官'):
                    return True

            # 检查藏干
            for canggan, w in DIZHI_CANGGAN.get(zhi, []):
                ten_god_cg = get_ten_god(day_master, canggan)
                if check_type == '财' and ten_god_cg in ('正财', '偏财'):
                    return True
                elif check_type == '官' and ten_god_cg in ('正官', '偏官'):
                    return True

        return False

    def _has_xing_chong(self, pillars: Dict) -> bool:
        """检查是否有刑冲（简化判断）"""
        # 地支六冲：子午、丑未、寅申、卯酉、辰戌、巳亥
        chong_pairs = [
            ('子', '午'), ('丑', '未'), ('寅', '申'),
            ('卯', '酉'), ('辰', '戌'), ('巳', '亥')
        ]

        branches = [pillars[pos][1] for pos in ['year', 'month', 'day', 'hour']]

        for b1, b2 in chong_pairs:
            if b1 in branches and b2 in branches:
                return True

        return False

    def _has_wuxing(self, pillars: Dict, wuxing: str) -> bool:
        """检查是否有某五行"""
        for pos, (gan, zhi) in pillars.items():
            if get_wuxing_by_tiangan(gan) == wuxing:
                return True

            # 检查藏干
            for canggan, w in DIZHI_CANGGAN.get(zhi, []):
                if get_wuxing_by_tiangan(canggan) == wuxing:
                    return True

        return False

    def _has_damage(self, pillars: Dict, day_master: str) -> bool:
        """检查是否有破损（简化：看是否有克日主的强势十神）"""
        damage_count = 0

        for pos, (gan, zhi) in pillars.items():
            if pos == 'day':
                continue

            ten_god = get_ten_god(day_master, gan)

            # 七杀、伤官视为破损
            if ten_god in ('偏官', '伤官'):
                damage_count += 1

        return damage_count >= 2  # 两个以上视为有破损

    def _generate_advice(self, pattern_results: List[Dict]) -> str:
        """
        生成建议
        ✅ 根据格局成败给出建议
        """
        if not pattern_results:
            return '无特殊格局，守常而行，亦可成就。'

        # 取第一个格局
        main_result = pattern_results[0]
        pattern_name = main_result['name']
        status = main_result['status']

        if pattern_name == '无特殊格局':
            return '无特殊格局，需看其他格局配合，宜中和为贵。'

        # 根据格局给建议
        advice_map = {
            '魁罡': {
                '成格': '魁罡格成，主聪慧果断，刚烈不屈，宜从事管理、军警、学术等工作，忌见财官破格。',
                '破格': '魁罡格破，见财官破格，宜修身养性，避免刚愎自用。'
            },
            '日禄': {
                '成格': '日禄格成，主衣禄丰足，自立自强，有财官相助更佳，宜稳健经营。',
                '破格': '日禄格破，无财官不成，宜自力更生，勤俭持家。'
            },
            '日德': {
                '成格': '日德格成，主聪慧仁厚，德行高尚，宜修德立业，从事教育、文化等工作。',
                '破格': '日德格破，有刑冲破格，宜谨慎行事，避免冲突。'
            },
            '金神': {
                '成格': '金神格成，有火制方吉，主刚毅果敢，宜从事武职、技术等工作。',
                '破格': '金神格破，无火制不成，宜修身养性，避免暴躁。'
            },
            '六秀': {
                '成格': '六秀格成，主聪明秀丽，才华横溢，宜从事文化、艺术等工作。',
                '破格': '六秀格破，有破损不成，宜修身养性，发挥才华。'
            },
            '福德': {
                '成格': '福德格成，主福禄双全，平安顺遂，宜守成发展。',
                '破格': '福德格破，有破损不成，宜谨慎行事，积德行善。'
            }
        }

        return advice_map.get(pattern_name, {}).get(status, '贵格宜修德立业，发挥优势。')
