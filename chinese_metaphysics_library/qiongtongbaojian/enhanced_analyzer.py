"""
《穷通宝鉴》深度增强分析器
基于原文的详细论述，提供更精准的命理分析
"""

from typing import Dict, List, Tuple
from ..core.base_analyzer import BaseAnalyzer
from ..core.data_structures import BaziData, AnalysisResult, AnalysisConfig
from ..core.utils import create_analysis_result, get_wuxing_by_tiangan, get_ten_god
from ..core.constants import DIZHI_CANGGAN


class EnhancedQiongtongAnalyzer(BaseAnalyzer):
    """
    《穷通宝鉴》深度增强分析器
    
    核心改进：
    1. 基于原文的详细论述
    2. 多层次判断（大贵、小贵、平人、贫贱）
    3. 特殊组合识别
    4. 具体案例参考
    """
    
    def __init__(self, config: AnalysisConfig = None):
        super().__init__("穷通宝鉴深度分析器", "穷通宝鉴", config)
        
        # 九月辛金的详细规则（基于原文）
        self.XIN_JIU_YUE_RULES = {
            'primary_yongshen': ['壬', '甲'],  # 先壬后甲
            'secondary_yongshen': ['癸'],  # 癸水也可用
            'xishen': ['癸'],  # 喜神
            'jishen': ['戊', '己'],  # 忌神：土多埋金
            'bing': '火土',  # 病：火土为病
            'yao': '水木',  # 药：水木为药
            
            # 层次判断规则（基于原文）
            'levels': {
                '桃洞之仙': {
                    'condition': lambda p: self._check_both_transparent(p, '壬', '甲'),
                    'score': 95,
                    'description': '壬甲两透，桃洞之仙，大富大贵'
                },
                '异途之仕': {
                    'condition': lambda p: self._check_pattern_1(p),  # 甲透壬藏，戊在支内
                    'score': 75,
                    'description': '甲透壬藏，戊在支内，异途之仕'
                },
                '富而可求': {
                    'condition': lambda p: self._check_ren_present(p),  # 一壬出，洗土助甲
                    'score': 70,
                    'description': '一壬出，洗土助甲，虽不发达，富而可求'
                },
                '略贵': {
                    'condition': lambda p: self._check_bing_xin(p),  # 土多无壬甲，时月多透丙辛
                    'score': 65,
                    'description': '土多无壬甲，时月多透丙辛者，略贵'
                },
                '平人': {
                    'condition': lambda p: self._check_ren_jia_cang(p),  # 壬透甲藏
                    'score': 55,
                    'description': '壬透甲藏，平人'
                },
                '常人': {
                    'condition': lambda p: self._check_mu_duo_tu_hou(p),  # 木多土厚，无水
                    'score': 45,
                    'description': '木多土厚，无水者常人'
                },
                '浊富': {
                    'condition': lambda p: self._check_ji_duo(p),  # 己透无壬有癸，己多
                    'score': 60,
                    'description': '己透无壬有癸，亦能滋生金力，衣衿之贵，但恐己多，不免浊富'
                }
            }
        }
    
    def analyze(self, bazi_data: BaziData) -> AnalysisResult:
        """
        深度分析
        """
        month_branch = bazi_data.get_month_branch()
        day_master = bazi_data.get_day_master()
        pillars = bazi_data.get_pillars()
        
        # 只处理辛金戌月（九月辛金）
        if day_master == '辛' and month_branch == '戌':
            return self._analyze_xin_jiuyue(bazi_data, pillars)
        else:
            # 其他组合使用基础分析
            return self._analyze_basic(bazi_data)
    
    def _analyze_xin_jiuyue(self, bazi_data: BaziData, pillars: Dict) -> AnalysisResult:
        """
        九月辛金的深度分析（基于《穷通宝鉴》原文）
        """
        # 提取天干
        year_gan = pillars['year'][0]
        month_gan = pillars['month'][0]
        day_gan = pillars['day'][0]
        hour_gan = pillars['hour'][0]
        
        # 提取地支
        year_zhi = pillars['year'][1]
        month_zhi = pillars['month'][1]
        day_zhi = pillars['day'][1]
        hour_zhi = pillars['hour'][1]
        
        # 层次判断
        level_result = self._judge_level_xin_jiuyue(pillars)
        
        # 用神检查
        yongshen_check = self._check_yongshen_xin_jiuyue(pillars)
        
        # 病药分析
        bing_yao = self._analyze_bing_yao(pillars)
        
        # 生成描述
        description = self._generate_description_xin_jiuyue(
            level_result, yongshen_check, bing_yao
        )
        
        # 生成建议
        advice = self._generate_advice_xin_jiuyue(
            level_result, yongshen_check, bing_yao
        )
        
        return create_analysis_result(
            analyzer_name=self.name,
            book_name=self.book_name,
            analysis_type="调候用神深度分析",
            level=level_result['level_name'],
            score=level_result['score'],
            description=description,
            details={
                'season': '秋',
                'temperature': '燥',
                'yongshen': ['壬', '甲'],
                'xishen': ['癸'],
                'jishen': ['戊', '己'],
                'bing': '火土',
                'yao': '水木',
                'level_detail': level_result,
                'yongshen_check': yongshen_check,
                'bing_yao': bing_yao,
                'original_text': '九月辛金，成土司令，母旺子相，须甲疏土，壬泄旺金，先壬後甲，壬甲两透，桃洞之仙...'
            },
            advice=advice
        )
    
    def _judge_level_xin_jiuyue(self, pillars: Dict) -> Dict:
        """
        判断九月辛金的层次
        """
        rules = self.XIN_JIU_YUE_RULES['levels']
        
        # 按优先级检查
        for level_name in ['桃洞之仙', '异途之仕', '富而可求', '略贵', '浊富', '平人', '常人']:
            rule = rules[level_name]
            if rule['condition'](pillars):
                return {
                    'level_name': level_name,
                    'score': rule['score'],
                    'description': rule['description']
                }
        
        # 默认
        return {
            'level_name': '平常',
            'score': 50,
            'description': '未符合特定格局'
        }
    
    def _check_both_transparent(self, pillars: Dict, gan1: str, gan2: str) -> bool:
        """检查两个天干是否都透出"""
        all_gans = [pillars['year'][0], pillars['month'][0], pillars['hour'][0]]
        return gan1 in all_gans and gan2 in all_gans
    
    def _check_pattern_1(self, pillars: Dict) -> bool:
        """甲透壬藏，戊在支内"""
        all_gans = [pillars['year'][0], pillars['month'][0], pillars['hour'][0]]
        all_zhis = [pillars['year'][1], pillars['month'][1], pillars['day'][1], pillars['hour'][1]]
        
        # 甲透出
        jia_transparent = '甲' in all_gans
        
        # 壬藏（在地支藏干中）
        ren_hidden = self._check_in_canggan(pillars, '壬')
        
        # 戊在支内
        wu_in_zhi = '戊' in [cg for zhi in all_zhis for cg, _ in DIZHI_CANGGAN.get(zhi, [])]
        
        return jia_transparent and ren_hidden and wu_in_zhi
    
    def _check_ren_present(self, pillars: Dict) -> bool:
        """一壬出"""
        all_gans = [pillars['year'][0], pillars['month'][0], pillars['hour'][0]]
        return '壬' in all_gans
    
    def _check_bing_xin(self, pillars: Dict) -> bool:
        """土多无壬甲，时月多透丙辛"""
        all_gans = [pillars['year'][0], pillars['month'][0], pillars['hour'][0]]
        
        # 无壬甲
        no_ren_jia = '壬' not in all_gans and '甲' not in all_gans
        
        # 时月多透丙辛
        month_hour_gans = [pillars['month'][0], pillars['hour'][0]]
        bing_xin_count = month_hour_gans.count('丙') + month_hour_gans.count('辛')
        
        return no_ren_jia and bing_xin_count >= 2
    
    def _check_ren_jia_cang(self, pillars: Dict) -> bool:
        """壬透甲藏"""
        all_gans = [pillars['year'][0], pillars['month'][0], pillars['hour'][0]]
        
        ren_transparent = '壬' in all_gans
        jia_hidden = self._check_in_canggan(pillars, '甲')
        
        return ren_transparent and jia_hidden and '甲' not in all_gans
    
    def _check_mu_duo_tu_hou(self, pillars: Dict) -> bool:
        """木多土厚，无水"""
        all_gans = [pillars['year'][0], pillars['month'][0], pillars['hour'][0]]
        
        # 统计木和土
        mu_count = sum(1 for gan in all_gans if get_wuxing_by_tiangan(gan) == '木')
        tu_count = sum(1 for gan in all_gans if get_wuxing_by_tiangan(gan) == '土')
        
        # 无水
        no_water = not any(get_wuxing_by_tiangan(gan) == '水' for gan in all_gans)
        
        return mu_count >= 2 and tu_count >= 2 and no_water
    
    def _check_ji_duo(self, pillars: Dict) -> bool:
        """己透无壬有癸，己多"""
        all_gans = [pillars['year'][0], pillars['month'][0], pillars['hour'][0]]
        
        ji_transparent = '己' in all_gans
        no_ren = '壬' not in all_gans
        has_gui = '癸' in all_gans
        ji_count = all_gans.count('己')
        
        return ji_transparent and no_ren and has_gui and ji_count >= 2
    
    def _check_in_canggan(self, pillars: Dict, gan: str) -> bool:
        """检查天干是否在地支藏干中"""
        all_zhis = [pillars['year'][1], pillars['month'][1], pillars['day'][1], pillars['hour'][1]]
        
        for zhi in all_zhis:
            canggan_list = DIZHI_CANGGAN.get(zhi, [])
            for cg, _ in canggan_list:
                if cg == gan:
                    return True
        return False
    
    def _check_yongshen_xin_jiuyue(self, pillars: Dict) -> Dict:
        """检查用神是否出现"""
        all_gans = [pillars['year'][0], pillars['month'][0], pillars['hour'][0]]
        
        ren_present = '壬' in all_gans
        jia_present = '甲' in all_gans
        gui_present = '癸' in all_gans
        
        return {
            'ren_present': ren_present,
            'jia_present': jia_present,
            'gui_present': gui_present,
            'both_present': ren_present and jia_present
        }
    
    def _analyze_bing_yao(self, pillars: Dict) -> Dict:
        """分析病药"""
        all_gans = [pillars['year'][0], pillars['month'][0], pillars['hour'][0]]
        
        # 病：火土
        huo_count = sum(1 for gan in all_gans if get_wuxing_by_tiangan(gan) == '火')
        tu_count = sum(1 for gan in all_gans if get_wuxing_by_tiangan(gan) == '土')
        
        # 药：水木
        shui_count = sum(1 for gan in all_gans if get_wuxing_by_tiangan(gan) == '水')
        mu_count = sum(1 for gan in all_gans if get_wuxing_by_tiangan(gan) == '木')
        
        return {
            'bing': {
                'huo': huo_count,
                'tu': tu_count,
                'total': huo_count + tu_count
            },
            'yao': {
                'shui': shui_count,
                'mu': mu_count,
                'total': shui_count + mu_count
            }
        }
    
    def _generate_description_xin_jiuyue(self, level_result: Dict, yongshen_check: Dict, bing_yao: Dict) -> str:
        """生成描述"""
        desc = f"九月辛金，成土司令，母旺子相。{level_result['description']}。"
        
        if yongshen_check['both_present']:
            desc += "壬甲两透，水木为药，火土之病得解。"
        elif yongshen_check['ren_present']:
            desc += "壬水出干，淘洗埋金之土。"
        elif yongshen_check['jia_present']:
            desc += "甲木出干，疏土有力。"
        else:
            desc += "壬甲不现，土重埋金，格局受损。"
        
        return desc
    
    def _generate_advice_xin_jiuyue(self, level_result: Dict, yongshen_check: Dict, bing_yao: Dict) -> str:
        """生成建议"""
        advice = "九月辛金，火土为病，水木为药。"
        
        if not yongshen_check['both_present']:
            advice += "宜补水木，以疏土淘金。"
        
        if bing_yao['bing']['total'] > bing_yao['yao']['total']:
            advice += "病重药轻，需加强水木之力。"
        
        return advice
    
    def _analyze_basic(self, bazi_data: BaziData) -> AnalysisResult:
        """基础分析（其他组合）"""
        # 这里可以调用原有的分析器
        return create_analysis_result(
            analyzer_name=self.name,
            book_name=self.book_name,
            analysis_type="调候用神分析",
            level="中平",
            score=60.0,
            description="基础调候分析",
            details={},
            advice="根据季节调候"
        )

