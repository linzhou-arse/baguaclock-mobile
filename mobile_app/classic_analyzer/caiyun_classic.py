#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, List, Tuple, Optional
from .constants import WUXING_MAP, KE_MAP, SHENG_MAP, CANG_GAN_MAP

class ClassicCaiyunAnalyzer:
    
    @staticmethod
    def analyze_classic_caiyun(pillars: Dict[str, Tuple[str, str]], day_master: str) -> Dict[str, object]:
        # Delegate to new implementation
        from .caiyun import CaiyunAnalyzer
        # Allow list/tuple as pillar values
        norm = {k: (v[0], v[1]) if isinstance(v, (list, tuple)) and len(v) >= 2 else v for k, v in pillars.items()}
        return CaiyunAnalyzer.analyze_caiyun(norm, day_master)


def analyze_classic_caiyun_complete(pillars: Dict[str, Tuple[str, str]], day_master: str) -> Dict[str, object]:
    return ClassicCaiyunAnalyzer.analyze_classic_caiyun(pillars, day_master)
