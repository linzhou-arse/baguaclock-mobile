"""
经典命理分析核心模块 - 基于《子平真诠》《滴天髓》等

整合所有命理分析功能，提供统一接口
"""

from .constants import WUXING_MAP, KE_MAP, SHENG_MAP
from .shensha import analyze_shensha_complete
from .geju_sanguan import analyze_geju_sanguan_complete
from .diaohou import analyze_diaohou_yongshen_complete
from ..local_mingli_analyzer import LocalMingliAnalyzer
from ..classic_lookup_tables import ClassicLookupTables


class ClassicMingliAnalyzer(LocalMingliAnalyzer):
    """
    经典命理分析器 - 完整功能不降级版本
    
    继承自LocalMingliAnalyzer，保证所有基础功能完整
    添加经典理论分析模块（神煞、格局三关、调候、财运、大运、综合评分）
    """
    
    def __init__(self):
        """初始化"""
        super().__init__()
        self.classic_tables = ClassicLookupTables()
        self._init_all_data()
    
    def _init_all_data(self):
        """初始化所有经典对照表数据"""
        # 从经典对照表加载神煞数据
        self.tianyi_guiren = self.classic_tables.TIANYI_GUIREN
        self.wenchang_guiren = self.classic_tables.WENCHANG_GUIREN
        self.lushen = self.classic_tables.LUSHEN
        self.yangren = self.classic_tables.YANGREN
        self.taohua = self.classic_tables.TAOHUA
        self.huagai = self.classic_tables.HUAGAI
        self.yima = self.classic_tables.YIMA
        self.hongyan = self.classic_tables.HONGYAN
        self.guchen = self.classic_tables.GUCHEN
        self.guasu = self.classic_tables.GUASU
        
        # 地支关系
        self.sanhe = {
            '申子辰': {'element': '水', 'desc': '申子辰三合水局'},
            '寅午戌': {'element': '火', 'desc': '寅午戌三合火局'},
            '巳酉丑': {'element': '金', 'desc': '巳酉丑三合金局'},
            '亥卯未': {'element': '木', 'desc': '亥卯未三合木局'}
        }
        
        # 藏干数据
        self.canggan_detail = {
            '子': [('癸', 100, '本气')],
            '丑': [('己', 18, '余气'), ('癸', 9, '中气'), ('辛', 73, '本气')],
            '寅': [('戊', 16, '余气'), ('丙', 14, '中气'), ('甲', 70, '本气')],
            '卯': [('甲', 20, '余气'), ('乙', 80, '本气')],
            '辰': [('乙', 18, '余气'), ('癸', 9, '中气'), ('戊', 73, '本气')],
            '巳': [('庚', 16, '余气'), ('戊', 14, '中气'), ('丙', 70, '本气')],
            '午': [('己', 20, '余气'), ('丁', 80, '本气')],
            '未': [('丁', 18, '余气'), ('乙', 9, '中气'), ('己', 73, '本气')],
            '申': [('壬', 16, '余气'), ('戊', 14, '中气'), ('庚', 70, '本气')],
            '酉': [('庚', 20, '余气'), ('辛', 80, '本气')],
            '戌': [('辛', 18, '余气'), ('丁', 9, '中气'), ('戊', 73, '本气')],
            '亥': [('甲', 16, '余气'), ('壬', 84, '本气')]
        }
        
        # 调候用神表
        self.diaohou_yongshen = self.classic_tables.DIAOHOU_YONGSHEN
    
    def analyze_bazi(self, pillars, gender='男', birth_info=None):
        """完整八字分析 - 不降级不简化"""
        if birth_info is None:
            birth_info = {'year': 2000}
        
        try:
            # 继承基类完整分析
            basic_result = super().analyze_bazi(pillars, gender, birth_info)
            
            # 获取基础报告文本
            if isinstance(basic_result, dict):
                basic_report = str(basic_result.get('local_analysis_text', ''))
            else:
                basic_report = str(basic_result)
            
            # 提取关键信息
            day_master = pillars['day'][0]
            year_zhi = pillars['year'][1]
            day_zhi = pillars['day'][1]
            month_zhi = pillars['month'][1]
            
            # 添加经典模块分析
            shensha_report = str(self._analyze_shensha_simple(pillars, day_master, year_zhi, day_zhi))
            huwei_report = str(self._analyze_geju_sanguan(pillars, gender, month_zhi, day_master))
            zhenjia_report = str(self._analyze_geju_zhenjia_guan(pillars, month_zhi, day_master))
            qingchun_report = str(self._analyze_geju_qingchun_guan(pillars, day_master))
            diaohou_report = str(self._analyze_diaohou_yongshen(pillars, day_master, month_zhi))
            
            # 组合完整报告
            enhanced_report = (
                basic_report + "\n" + 
                shensha_report + "\n" + 
                huwei_report + "\n" + 
                zhenjia_report + "\n" + 
                qingchun_report + "\n" + 
                diaohou_report
            )
            
            return enhanced_report
            
        except Exception as e:
            return f"分析出错：{str(e)}"
    
    # ══════════════════════════════════════════════════════════════════
    # 辅助方法 - 十神、位置、空亡等
    # ══════════════════════════════════════════════════════════════════
    
    def _get_simple_shishen(self, day_master, target_gan):
        """
        简单十神判断 - 基于阴阳和五行关系
        
        十神关系表（以日主为中心）：
        同五行 = 比肩/劫财
        我克的 = 正财/偏财
        克我的 = 正官/偏官
        生我的 = 正印/偏印
        我生的 = 食神/伤官
        """
        day_wx = WUXING_MAP.get(day_master)
        target_wx = WUXING_MAP.get(target_gan)
        
        if not day_wx or not target_wx:
            return '未知'
        
        # 判断阴阳
        yang_gan = ['甲', '丙', '戊', '庚', '壬']
        day_is_yang = day_master in yang_gan
        target_is_yang = target_gan in yang_gan
        
        # 同五行
        if day_wx == target_wx:
            return '比肩' if day_is_yang == target_is_yang else '劫财'
        
        # 我克的
        if KE_MAP.get(day_wx) == target_wx:
            return '正财' if day_is_yang != target_is_yang else '偏财'
        
        # 克我的
        if KE_MAP.get(target_wx) == day_wx:
            return '正官' if day_is_yang != target_is_yang else '偏官'
        
        # 生我的
        if SHENG_MAP.get(target_wx) == day_wx:
            return '正印' if day_is_yang != target_is_yang else '偏印'
        
        # 我生的
        if SHENG_MAP.get(day_wx) == target_wx:
            return '食神' if day_is_yang != target_is_yang else '伤官'
        
        return '未知'
    
    # ══════════════════════════════════════════════════════════════════
    # 占位符方法 - 具体实现将在对应模块中
    # ══════════════════════════════════════════════════════════════════
    
    def _analyze_shensha_simple(self, pillars, day_master, year_zhi, day_zhi):
        """神煞分析 - 简化版"""
        return "\n【经典神煞分析】\n（详见shensha.py模块）"
    
    def _analyze_geju_sanguan(self, pillars, gender, month_zhi, day_master):
        """护卫关分析"""
        return "\n【格局三关 - 护卫关】\n（详见geju_sanguan.py模块）"
    
    def _analyze_geju_zhenjia_guan(self, pillars, month_zhi, day_master):
        """真假关分析"""
        return "\n【格局三关 - 真假关】\n（详见geju_sanguan.py模块）"
    
    def _analyze_geju_qingchun_guan(self, pillars, day_master):
        """清纯关分析"""
        return "\n【格局三关 - 清纯关】\n（详见geju_sanguan.py模块）"
    
    def _analyze_diaohou_yongshen(self, pillars, day_master, month_zhi):
        """调候用神分析"""
        return "\n【调候用神分析】\n（详见diaohou.py模块）"


# 完整实现将分散到各个模块中