"""
经典命理分析器 - 模块化结构
基于《渊海子平》《三命通会》《子平真诠》《滴天髓》《穷通宝鉴》等经典著作

核心原则：
- 完全基于经典著作，不做假
- 严格查表不推算
- 功能完整不降级
- 每个模块独立完整

模块结构：
- core.py - 核心类和框架
- shensha.py - 神煞分析（独立模块）
- geju_sanguan.py - 格局三关（独立模块）
- diaohou.py - 调候用神（独立模块）
- caiyun.py - 财运分析（完整实现）
- dayun.py - 大运分析（完整实现）
- mingge_score.py - 综合评分（完整实现）
"""

# 模块化导入
from . import caiyun, dayun, shensha, mingge_score
from . import geju_analyzer, yongshen_analyzer, wuxing_analyzer, tiaohou_analyzer
from . import caiyun_classic
from .common import compute_wuxing_distribution

__version__ = '1.0.0-modular'
__all__ = [
    'caiyun', 'dayun', 'shensha', 'mingge_score',
    'geju_analyzer', 'yongshen_analyzer', 'wuxing_analyzer', 'tiaohou_analyzer',
    'caiyun_classic', 'compute_wuxing_distribution'
]
