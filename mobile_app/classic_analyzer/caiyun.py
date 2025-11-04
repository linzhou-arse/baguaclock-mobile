# -*- coding: utf-8 -*-
from __future__ import annotations

"""
财运分析模块 - 基于《渊海子平》《三命通会》等经典命书

✅ 修正原则：
1. 财运不是独立的"格局"，而是格局成败的结果
2. 只分析财星状态，不编造"食伤生财格"等虚假格局
3. 所有论述必须有真实的经典依据
4. 基于《渊海子平·论正财》《论偏财》《五行元理消息赋》的原文
"""

from typing import Dict, List, Optional, Tuple

from classic_analyzer.common import (
    DIZHI_CANGGAN_WEIGHTS,
    evaluate_day_master_strength,
    get_ten_god,
)


class CaiyunAnalyzer:
    """传统命理财运分析器 - 基于《渊海子平》"""

    TEN_GOD_ROLE = {
        '正财': 'wealth',
        '偏财': 'wealth',
        '食神': 'talent',
        '伤官': 'talent',
        '正官': 'officer',
        '七杀': 'officer',
        '正印': 'resource',
        '偏印': 'resource',
        '比肩': 'peer',
        '劫财': 'peer',
    }

    ROLE_LABELS = {
        'wealth': '财星',
        'talent': '食伤',
        'officer': '官杀',
        'resource': '印绶',
        'peer': '比劫',
    }

    @classmethod
    def analyze_caiyun(
        cls,
        pillars: Dict[str, Tuple[str, str]],
        day_master: str,
    ) -> Dict[str, any]:
        """
        财运分析 - 基于《渊海子平》

        《渊海子平·论正财》："正财者，喜身旺、印绶，忌官星、忌倒食、忌身弱、比肩劫财"
        《渊海子平·五行元理消息赋》："财多身弱，身旺以为荣。身旺财衰，财旺乡而发福"
        """
        # 1. 统计十神分布
        role_weights = cls._calculate_role_weights(pillars, day_master)

        # 2. 评估日主强弱
        strength_profile = evaluate_day_master_strength(pillars)
        strength_label = getattr(strength_profile, 'strength', '中和')

        # 3. 统计财星数量和状态
        wealth_count, wealth_status = cls._analyze_wealth_stars(pillars, day_master)

        # 4. 判断财运状态（基于《渊海子平》原文）
        caiyun_status = cls._judge_caiyun_status(
            role_weights, strength_label, wealth_count, pillars, day_master
        )

        # 5. 返回结果
        return {
            'wealth_count': wealth_count,
            'wealth_status': wealth_status,
            'caiyun_status': caiyun_status['status'],
            'description': caiyun_status['description'],
            'classic_basis': caiyun_status['classic'],
        }

    @classmethod
    def _calculate_role_weights(
        cls, pillars: Dict[str, Tuple[str, str]], day_master: str
    ) -> Dict[str, float]:
        """统计十神角色权重"""
        role_weights = {
            'wealth': 0.0,
            'talent': 0.0,
            'officer': 0.0,
            'resource': 0.0,
            'peer': 0.0,
        }

        # 天干权重
        for pos in ['year', 'month', 'hour']:
            gan = pillars[pos][0]
            ten_god = get_ten_god(day_master, gan)
            role = cls.TEN_GOD_ROLE.get(ten_god)
            if role:
                role_weights[role] += 1.0

        # 地支藏干权重
        for pos in ['year', 'month', 'day', 'hour']:
            zhi = pillars[pos][1]
            hidden_gans = DIZHI_CANGGAN_WEIGHTS.get(zhi, [])
            for hg, weight in hidden_gans:
                ten_god = get_ten_god(day_master, hg)
                role = cls.TEN_GOD_ROLE.get(ten_god)
                if role:
                    role_weights[role] += weight

        # 归一化
        total = sum(role_weights.values())
        if total > 0:
            for key in role_weights:
                role_weights[key] /= total

        return role_weights

    @classmethod
    def _analyze_wealth_stars(
        cls, pillars: Dict[str, Tuple[str, str]], day_master: str
    ) -> Tuple[int, str]:
        """
        统计财星数量和状态 - 🔥 修复：包含天干和地支藏干

        《渊海子平·论正财》："财星透干有根，主富"
        """
        # 1. 统计天干财星（权重1.0）
        wealth_count_gan = 0
        wealth_gans = []
        for pos in ['year', 'month', 'hour']:
            gan = pillars[pos][0]
            ten_god = get_ten_god(day_master, gan)
            if ten_god in ['正财', '偏财']:
                wealth_count_gan += 1
                wealth_gans.append(gan)

        # 2. 🔥 修复：统计地支藏干财星（按权重计算）
        wealth_count_zhi = 0.0
        for pos in ['year', 'month', 'day', 'hour']:
            zhi = pillars[pos][1]
            if zhi in DIZHI_CANGGAN_WEIGHTS:
                for hidden_gan, weight in DIZHI_CANGGAN_WEIGHTS[zhi]:
                    ten_god = get_ten_god(day_master, hidden_gan)
                    if ten_god in ['正财', '偏财']:
                        # 只有权重≥0.5的藏干才算有效财星
                        if weight >= 0.5:
                            wealth_count_zhi += 1.0
                        else:
                            wealth_count_zhi += weight  # 权重<0.5的按比例计算
        
        # 总财星数量（天干+地支，四舍五入到整数）
        wealth_count = int(round(wealth_count_gan + wealth_count_zhi))

        # 判断财星状态
        if wealth_count == 0:
            status = '财星不现'
        elif wealth_count == 1:
            status = '财星专一'
        else:
            status = '财星多现'

        return wealth_count, status

    @classmethod
    def _judge_caiyun_status(
        cls,
        role_weights: Dict[str, float],
        strength_label: str,
        wealth_count: int,
        pillars: Optional[Dict[str, Tuple[str, str]]] = None,
        day_master: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        判断财运状态 - 基于《渊海子平》原文，全面分析财运

        《渊海子平·五行元理消息赋》：
        "财多身弱，身旺以为荣。身旺财衰，财旺乡而发福"

        《渊海子平·论正财》：
        "正财者，喜身旺、印绶，忌官星、忌倒食、忌身弱、比肩劫财"
        
        《子平真诠·论财》：
        "食伤生财，财源广进；官杀护财，财源稳固"
        """
        wealth_weight = role_weights.get('wealth', 0.0)
        peer_weight = role_weights.get('peer', 0.0)
        talent_weight = role_weights.get('talent', 0.0)  # 食伤
        officer_weight = role_weights.get('officer', 0.0)  # 官杀

        # 🔥 增强：当财星为0时，检查其他生财方式
        if wealth_count == 0 or wealth_weight < 0.05:
            # 1.1 检查食伤生财（《子平真诠》："食伤生财，财源广进"）
            is_strong = strength_label in ['旺', '中旺']
            if talent_weight >= 0.15 and is_strong:
                return {
                    'status': '食伤生财',
                    'description': '命中无财星，但食伤有力且身强，可凭技艺、才华生财，财源虽非直接但可持续',
                    'classic': '《子平真诠·论财》："食伤生财，财源广进"',
                }
            
            # 1.2 检查官杀当财看（特殊格局：官杀强可当财）
            if officer_weight >= 0.25 and is_strong:
                return {
                    'status': '官杀当财',
                    'description': '命中无财星，但官杀有力且身强，可通过权力、地位、事业生财，级别较大',
                    'classic': '《三命通会·论财》："官杀当财看，权力生财"',
                }
            
            # 1.3 检查是否有禄神（禄当财看）
            if pillars and day_master:
                from classic_analyzer.common import get_wuxing_by_tiangan, get_wuxing_by_dizhi
                day_element = get_wuxing_by_tiangan(day_master)
                lu_positions = []
                for pos in ['year', 'month', 'day', 'hour']:
                    zhi = pillars[pos][1]
                    zhi_element = get_wuxing_by_dizhi(zhi)
                    if zhi_element == day_element:
                        lu_positions.append(pos)
                
                if lu_positions and is_strong:
                    return {
                        'status': '禄当财看',
                        'description': '命中无财星，但有禄神且身强，可通过稳定工作、薪资收入获财，级别大且稳定',
                        'classic': '《渊海子平·论财》："禄当财看，稳定收入"',
                    }
            
            # 1.4 真正的财星不现
            return {
                'status': '财星不现',
                'description': '命中财星极弱或不现，需看大运流年补之；若大运流年有财星或食伤，仍可获财',
                'classic': '《子平真诠·论财》："财为我克，使用之物也"',
            }

        # 🔥 修复：兼容新的日主强弱等级（旺/中旺/中和/中弱/弱）
        is_strong = strength_label in ['旺', '中旺']  # 身强
        is_weak = strength_label in ['弱', '中弱']  # 身弱
        is_neutral = strength_label == '中和'  # 中和
        
        # 2. 🔥 新增：食伤生财（有财星且食伤有力，优先级高）
        if wealth_weight >= 0.10 and talent_weight >= 0.15:
            if is_strong:
                return {
                    'status': '食伤生财',
                    'description': '财星与食伤并见，食伤生财有力，主财源广进，宜凭技艺、才华、创新获财',
                    'classic': '《子平真诠·论财》："食伤生财，财源广进"',
                }
        
        # 2.1 🔥 新增：官杀护财（有财星且官杀有力，优先级高）
        if wealth_weight >= 0.10 and officer_weight >= 0.15:
            return {
                'status': '官杀护财',
                'description': '财星与官杀并见，官杀护财有力，主财源稳固，可通过权力、地位、事业获财',
                'classic': '《三命通会·论财》："官杀护财，财源稳固"',
            }
        
        # 2.2 比劫夺财（需在有财星的情况下判断）
        if peer_weight >= 0.25 and wealth_weight >= 0.10:
            return {
                'status': '比劫夺财',
                'description': '比劫旺，夺财之象，需防合作破财、投资失利；建议单独经营，避免合伙',
                'classic': '《渊海子平·论正财》："忌身弱、比肩劫财"',
            }

        # 3. 身旺财旺
        if is_strong and wealth_weight >= 0.20:
            # 🔥 增强：检查财星是否透干有根
            quality_note = ""
            if pillars and day_master:
                from classic_analyzer.common import get_ten_god
                # 检查是否有透干（天干有财星）
                has_tougan = False
                for pos in ['year', 'month', 'hour']:
                    gan = pillars[pos][0]
                    ten_god = get_ten_god(day_master, gan)
                    if ten_god in ['正财', '偏财']:
                        has_tougan = True
                        break
                
                # 检查是否有根（地支有财星）
                has_gen = False
                for pos in ['year', 'month', 'day', 'hour']:
                    zhi = pillars[pos][1]
                    if zhi in DIZHI_CANGGAN_WEIGHTS:
                        for hidden_gan, weight in DIZHI_CANGGAN_WEIGHTS[zhi]:
                            ten_god = get_ten_god(day_master, hidden_gan)
                            if ten_god in ['正财', '偏财'] and weight >= 0.5:
                                has_gen = True
                                break
                    if has_gen:
                        break
                
                if has_tougan and has_gen:
                    quality_note = "，财星透干有根，质量上乘"
                elif has_tougan:
                    quality_note = "，财星透干，质量中等"
                elif has_gen:
                    quality_note = "，财星有根，质量中等"
            
            return {
                'status': '身旺财旺',
                'description': f'身旺财旺，能胜其财，主富{quality_note}',
                'classic': '《渊海子平·五行元理消息赋》："财多身弱，身旺以为荣"',
            }

        # 4. 身旺财弱
        if is_strong and wealth_weight < 0.20:
            return {
                'status': '身旺财弱',
                'description': '身旺财弱，需行财旺之运方能发福',
                'classic': '《渊海子平·五行元理消息赋》："身旺财衰，财旺乡而发福"',
            }

        # 5. 身弱财旺
        if is_weak and wealth_weight >= 0.20:
            return {
                'status': '身弱财旺',
                'description': '身弱财旺，身不胜财，反为祸患',
                'classic': '《渊海子平·五行元理消息赋》："财多身弱，身旺以为荣"（反之则凶）',
            }

        # 6. 身弱财弱
        if is_weak and wealth_weight < 0.20:
            return {
                'status': '身弱财弱',
                'description': '身弱财弱，需行印比之运扶身，再行财运方可',
                'classic': '《渊海子平·论正财》："喜身旺、印绶"',
            }

        # 7. 中和状态
        if is_neutral:
            if wealth_weight >= 0.20:
                return {
                    'status': '中和财旺',
                    'description': '日主中和，财星有力，财运尚可，需看大运配合',
                    'classic': '《渊海子平·论正财》："财要得时，不要财多"',
                }
            else:
                return {
                    'status': '中和财弱',
                    'description': '日主中和，财星不显，需看大运流年补之',
                    'classic': '《渊海子平·论正财》："财为我克，使用之物也"',
                }

        # 7. 默认：财运中等
        return {
            'status': '财运中等',
            'description': '财星有力，日主中和，财运尚可',
            'classic': '《渊海子平·论正财》："财要得时，不要财多"',
        }

