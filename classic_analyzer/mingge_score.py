from __future__ import annotations

"""
\u547d\u683c\u7efc\u5408\u8bc4\u5206\u6a21\u5757\uff08\u53c2\u8003\u300a\u5b50\u5e73\u771f\u8be0\u300b\u300a\u7a77\u901a\u5b9d\u9274\u300b\u300a\u4e09\u547d\u901a\u4f1a\u300b\u300a\u6ef4\u5929\u9ad3\u300b\uff09

\u8bc4\u4f30\u903b\u8f91\uff1a
1. \u5148\u5224\u7ed3\u6784\uff08\u8eab\u5f3a/\u8eab\u5f31\u4e0e\u4e94\u884c\u5e03\u52bf\uff09\uff0c\u8861\u91cf\u6839\u6c14\u4e0e\u6cc4\u8017\u3002
2. \u518d\u770b\u7528\u795e\uff08\u8c03\u5019\u4e0e\u6276\u6291\uff09\uff0c\u786e\u8ba4\u6d41\u901a\u662f\u5426\u987a\u7545\u3002
3. \u7ed3\u5408\u8d22\u8fd0\u3001\u8fd0\u52bf\u3001\u795e\u715e\u7b49\u5ba2\u89c2\u6307\u6807\uff0c\u7efc\u5408\u6210\u6700\u7ec8\u8bc4\u5206\u3002
4. \u6240\u6709\u6743\u91cd\u968f\u547d\u5c40\u5e73\u8861\u5ea6\u4e0e\u5916\u90e8\u5f97\u5206\u52a8\u6001\u8c03\u6574\uff0c\u675c\u7edd\u786c\u7f16\u7801\u3002
"""

from typing import Dict, List, Optional

from classic_analyzer.common import (
    SHENG_MAP,
    SHENG_REVERSE,
    KE_MAP,
    KE_REVERSE,
    clamp_score,
)


class MinggeScoreAnalyzer:
    """\u547d\u683c\u7efc\u5408\u8bc4\u5206\u5668\u3002"""

    LEVEL_RULES = [
        {
            'name': '\u4e0a\u4e0a',
            'min_score': 88,
            'description': '\u683c\u5c40\u7eaf\u7cb9\uff0c\u8eab\u4e0e\u7528\u795e\u76f8\u5f97\u76ca\u5f70\uff0c\u8d22\u5b98\u5370\u4e09\u8005\u76f8\u4e92\u652f\u63f4\u3002',
            'advice': '\u7ef4\u6301\u6d41\u901a\uff0c\u5ba1\u614e\u6269\u5f20\uff0c\u53ef\u95ee\u9f0e\u9ad8\u4f4d\u3002',
        },
        {
            'name': '\u4e0a',
            'min_score': 78,
            'description': '\u547d\u5c40\u5e73\u8861\uff0c\u53d6\u7528\u5f97\u5f53\uff0c\u884c\u8fd0\u76f8\u968f\uff0c\u53ef\u671b\u4e8b\u4e1a\u5b8f\u5c55\u3002',
            'advice': '\u987a\u52bf\u6df1\u8015\u4e3b\u4e1a\uff0c\u4ee5\u7a33\u4e2d\u6c42\u8fdb\u4e3a\u5b9c\u3002',
        },
        {
            'name': '\u4e2d\u4e0a',
            'min_score': 68,
            'description': '\u5927\u4f53\u5e73\u8861\u4f46\u5076\u6709\u6ce2\u6298\uff0c\u9700\u5584\u7528\u8f85\u661f\u4ee5\u5b88\u6210\u3002',
            'advice': '\u9488\u5bf9\u77ed\u677f\u8865\u5f3a\uff0c\u53ef\u8003\u8651\u5b66\u4e60\u4e0e\u5408\u4f5c\u3002',
        },
        {
            'name': '\u4e2d',
            'min_score': 58,
            'description': '\u547d\u5c40\u6447\u6446\u672a\u5b9a\uff0c\u5b9c\u5bfb\u52a9\u529b\u4ee5\u7a33\u6b65\u524d\u884c\u3002',
            'advice': '\u91cd\u70b9\u4fee\u70bc\u5fc3\u6027\u4e0e\u8d44\u6e90\u6574\u5408\uff0c\u7f13\u6b65\u63a8\u8fdb\u3002',
        },
        {
            'name': '\u4e2d\u4e0b',
            'min_score': 48,
            'description': '\u7ed3\u6784\u5931\u8861\u6216\u884c\u8fd0\u4e0d\u6d4e\uff0c\u9700\u9632\u6ce2\u6298\u3002',
            'advice': '\u5b88\u6210\u7b2c\u4e00\uff0c\u51cf\u5c11\u5192\u9669\uff0c\u5148\u56fa\u6839\u57fa\u3002',
        },
        {
            'name': '\u4e0b',
            'min_score': 0,
            'description': '\u547d\u5c40\u4e4f\u529b\u4e14\u5916\u7f18\u591a\u9650\uff0c\u5b9c\u8c28\u614e\u81ea\u5b88\u3002',
            'advice': '\u4e13\u6ce8\u63d0\u5347\u81ea\u6211\uff0c\u7b49\u5f85\u8fd0\u52bf\u7ffb\u8f6c\u3002',
        },
    ]

    BASE_WEIGHTS = {
        'structure': 0.28,
        'use_god': 0.24,
        'wealth': 0.20,
        'luck': 0.18,
        'shensha': 0.10,
    }

    @classmethod
    def analyze_mingge_score(cls, analysis_results: Dict[str, Dict]) -> Dict[str, object]:
        """
        命格综合分析 - 基于《子平真诠》理论
        ✅ 修复：移除打分系统，改为格局成败判断

        传统命理不打分，只论格局成败、用神得失
        """
        # 1. 提取各模块的成败判断
        geju_result = analysis_results.get('geju', {})
        caiyun_result = analysis_results.get('caiyun', {})
        dayun_result = analysis_results.get('dayun', {})
        shensha_result = analysis_results.get('shensha', {})

        # 2. 判断格局成败
        geju_chengbai = geju_result.get('geju_chengbai', '未知')

        # 3. 判断用神得失（从大运喜忌判断）
        dayun_xiji = dayun_result.get('xiji', '未知')

        # 4. 判断财运格局
        caiyun_pattern = caiyun_result.get('pattern_name', '未知')
        caiyun_chengbai = caiyun_result.get('pattern_chengbai', '未知')

        # 5. 统计神煞吉凶
        jishen_count = len(shensha_result.get('jishen', []))
        xiongshen_count = len(shensha_result.get('xiongshen', []))

        # 6. 综合判断命格成败（不打分）
        chengbai_result = cls._judge_mingge_chengbai(
            geju_chengbai, dayun_xiji, caiyun_chengbai, jishen_count, xiongshen_count
        )

        return {
            'level': chengbai_result['level'],
            'detail': chengbai_result['detail'],
            'advice': chengbai_result['advice'],
            'classic_basis': chengbai_result['classic_basis'],

            # 各模块成败判断
            'geju_chengbai': geju_chengbai,
            'dayun_xiji': dayun_xiji,
            'caiyun_pattern': caiyun_pattern,
            'caiyun_chengbai': caiyun_chengbai,
            'jishen_count': jishen_count,
            'xiongshen_count': xiongshen_count,
        }

    @staticmethod
    def _extract_profile(analysis_results: Dict[str, Dict]) -> Dict[str, object]:
        candidates = [
            analysis_results.get('profile'),
            analysis_results.get('dayun', {}).get('profile'),
            analysis_results.get('structure', {}).get('profile'),
        ]
        for item in candidates:
            if isinstance(item, dict) and item:
                return item
        return {
            'strength': '\u5e73',
            'element': '\u6728',
            'support_power': 0.0,
            'pressure_power': 0.0,
            'distribution': {},
        }

    @classmethod
    def _calculate_section_weights(
        cls,
        profile: Dict[str, object],
        analysis_results: Dict[str, Dict],
    ) -> Dict[str, float]:
        weights = dict(cls.BASE_WEIGHTS)
        support = float(profile.get('support_power', 0.0))
        pressure = float(profile.get('pressure_power', 0.0))
        total = support + pressure or 1.0
        balance = (support - pressure) / total

        weights['structure'] += abs(balance) * 0.06

        diaohou_score = analysis_results.get('diaohou', {}).get('score')
        if diaohou_score is not None:
            weights['use_god'] += (diaohou_score - 60.0) / 500.0

        caiyun_score = analysis_results.get('caiyun', {}).get('score')
        if caiyun_score is not None:
            weights['wealth'] += (caiyun_score - 70.0) / 600.0

        dayun_score = cls._extract_dayun_score(analysis_results)
        if dayun_score is not None:
            weights['luck'] += (dayun_score - 70.0) / 600.0

        shensha_data = analysis_results.get('shensha', {})
        ji_count = shensha_data.get('ji_sha_count')
        xiong_count = shensha_data.get('xiong_sha_count')
        if isinstance(ji_count, (int, float)) and isinstance(xiong_count, (int, float)):
            weights['shensha'] += (ji_count - xiong_count) / 200.0

        for key in list(weights.keys()):
            if analysis_results.get(key) is None and key not in ('structure', 'use_god'):
                weights[key] *= 0.5

        total_weight = sum(weights.values()) or 1.0
        return {k: v / total_weight for k, v in weights.items()}

    @classmethod
    def _score_structure(
        cls,
        profile: Dict[str, object],
        analysis_results: Dict[str, Dict],
    ) -> Dict[str, object]:
        base = analysis_results.get('structure', {})
        if 'score' in base and 'detail' in base:
            return {'score': float(base['score']), 'detail': base['detail']}

        distribution = profile.get('distribution') or {}
        day_element = profile.get('element', '\u6728')
        resource = SHENG_REVERSE.get(day_element, '')
        drain = SHENG_MAP.get(day_element, '')
        wealth = KE_MAP.get(day_element, '')
        officer = KE_REVERSE.get(day_element, '')

        support = distribution.get(day_element, 0.0) + distribution.get(resource, 0.0)
        pressure = distribution.get(drain, 0.0) + distribution.get(wealth, 0.0) + distribution.get(officer, 0.0)
        total = support + pressure or 1.0
        balance_ratio = (support - pressure) / total

        score = 70.0 + balance_ratio * 20.0
        if abs(balance_ratio) < 0.1:
            score += 5.0

        score = clamp_score(score)
        detail = (
            f"\u7ed3\u6784\u5e73\u8861\u5ea6\uff1a\u652f\u6301{support:.2f} / \u538b\u529b{pressure:.2f}\uff0c\u5e73\u8861\u7cfb\u6570{balance_ratio:+.2f}\u3002"
        )
        return {'score': score, 'detail': detail}

    @classmethod
    def _score_use_god(
        cls,
        profile: Dict[str, object],
        analysis_results: Dict[str, Dict],
    ) -> Dict[str, object]:
        diaohou = analysis_results.get('diaohou', {})
        if 'score' in diaohou and 'detail' in diaohou:
            return {'score': float(diaohou['score']), 'detail': diaohou['detail']}

        caiyun_metrics = analysis_results.get('caiyun', {}).get('metrics', {})
        role_ratios = caiyun_metrics.get('role_ratios', {})
        strength = profile.get('strength', '\u5e73')

        if role_ratios:
            if strength == '\u65fa':
                useful = role_ratios.get('talent', 0.0) + role_ratios.get('wealth', 0.0) + role_ratios.get('officer', 0.0)
                burden = role_ratios.get('resource', 0.0) + role_ratios.get('peer', 0.0)
            else:
                useful = role_ratios.get('resource', 0.0) + role_ratios.get('officer', 0.0)
                burden = role_ratios.get('talent', 0.0)
            score = clamp_score(65.0 + (useful - burden) * 80.0)
            detail = (
                f"\u7528\u795e\u4fa7\u91cd\uff1a\u6709\u5229\u6bd4\u91cd{useful * 100:.1f}% \uff0c\u63a3\u8098\u5360\u6bd4{burden * 100:.1f}%\u3002"
            )
            return {'score': score, 'detail': detail}

        return {'score': 60.0, 'detail': '\u7f3a\u5c11\u8c03\u5019\u4fe1\u606f\uff0c\u6309\u5e73\u5747\u6c34\u5e73\u4f30\u8ba1\u3002'}

    @classmethod
    def _score_wealth(cls, analysis_results: Dict[str, Dict]) -> Dict[str, object]:
        caiyun = analysis_results.get('caiyun', {})
        if 'score' in caiyun and 'detail' in caiyun:
            return {'score': float(caiyun['score']), 'detail': caiyun['detail']}

        level = caiyun.get('level')
        mapping = {
            '\u5927\u5bcc': 90,
            '\u5bcc\u88d5': 80,
            '\u4e2d\u5e73': 65,
            '\u7a0d\u8584': 55,
            '\u7834\u8d22': 45,
        }
        score = mapping.get(level, 60)
        detail = caiyun.get('detail', '\u8d22\u8fd0\u8d44\u6599\u4e0d\u8db3\uff0c\u6309\u4fdd\u5b88\u503c\u4f30\u8ba1\u3002')
        return {'score': float(score), 'detail': detail}

    @classmethod
    def _extract_dayun_score(cls, analysis_results: Dict[str, Dict]) -> Optional[float]:
        dayun = analysis_results.get('dayun', {})
        if 'score' in dayun:
            return float(dayun['score'])
        jixiong = dayun.get('jixiong_info', {})
        if 'score' in jixiong:
            return float(jixiong['score'])
        return None

    @classmethod
    def _score_luck(
        cls,
        profile: Dict[str, object],
        analysis_results: Dict[str, Dict],
    ) -> Dict[str, object]:
        dayun = analysis_results.get('dayun', {})
        if 'score' in dayun and 'detail' in dayun:
            return {'score': float(dayun['score']), 'detail': dayun['detail']}

        jixiong = dayun.get('jixiong_info', {})
        if jixiong:
            score = float(jixiong.get('score', 60.0))
            detail = jixiong.get('detail', '\u8fd0\u52bf\u4fe1\u606f\u6309\u9ed8\u8ba4\u63a8\u65ad\u3002')
            return {'score': clamp_score(score), 'detail': detail}

        balance = float(profile.get('support_power', 0.0)) - float(profile.get('pressure_power', 0.0))
        score = clamp_score(62.0 + balance * 5.0)
        detail = f"\u4ee5\u8eab\u65fa\u8870\u4f30\u7b97\u8fd0\u52bf\uff0c\u5e73\u8861\u5dee\u503c{balance:+.2f}\u3002"
        return {'score': score, 'detail': detail}

    @classmethod
    def _score_shensha(cls, analysis_results: Dict[str, Dict]) -> Dict[str, object]:
        """神煞评分 - 按《三命通会·神煞篇》理论实现"""
        shensha = analysis_results.get('shensha', {})
        if 'score' in shensha and 'detail' in shensha:
            return {'score': float(shensha['score']), 'detail': shensha['detail']}

        ji_sha = shensha.get('ji_sha', []) or []
        xiong_sha = shensha.get('xiong_sha', []) or []
        
        # 按《三命通会》理论：吉煞有轻重，凶煞有化解
        ji_score = 0
        xiong_score = 0
        
        # 吉煞评分（按等级加权）
        for sha in ji_sha:
            level = sha.get('level', '小吉')
            if level == '大吉':
                ji_score += 15  # 天德、天乙等大吉煞
            elif level == '中吉':
                ji_score += 10  # 文昌、禄神等中吉煞
            else:
                ji_score += 5   # 其他小吉煞
        
        # 凶煞评分（按等级加权，但可化解）
        for sha in xiong_sha:
            level = sha.get('level', '小凶')
            if level == '大凶':
                xiong_score += 12  # 羊刃、空亡等大凶煞
            elif level == '中凶':
                xiong_score += 8   # 孤辰、寡宿等中凶煞
            else:
                xiong_score += 4   # 其他小凶煞
        
        # 基础分60分，吉煞加分，凶煞减分
        base_score = 60.0
        score = clamp_score(base_score + ji_score - xiong_score)
        
        # 生成详细说明
        ji_count = len(ji_sha)
        xiong_count = len(xiong_sha)
        detail_parts = [f"吉煞{ji_count}个(+{ji_score}分)"]
        if xiong_count > 0:
            detail_parts.append(f"凶煞{xiong_count}个(-{xiong_score}分)")
        detail_parts.append(f"按《三命通会》神煞理论评分")
        
        detail = "，".join(detail_parts)
        return {'score': score, 'detail': detail}

    @classmethod
    def _judge_mingge_chengbai(
        cls,
        geju_chengbai: str,
        dayun_xiji: str,
        caiyun_chengbai: str,
        jishen_count: int,
        xiongshen_count: int,
    ) -> Dict[str, str]:
        """
        判断命格成败 - 基于《子平真诠》理论
        ✅ 修复：不打分，只判断成败

        综合考虑：
        1. 格局成败（最重要）
        2. 大运喜忌（次重要）
        3. 财运格局
        4. 神煞吉凶
        """
        # 1. 格局成败是核心
        if geju_chengbai == '格局大成':
            if dayun_xiji in ['大喜', '小喜']:
                level = '格局大成'
                detail = f'格局大成，大运{dayun_xiji}，命格极佳。'
                advice = '维持流通，审慎扩张，可问鼎高位。'
                classic = '《子平真诠》：格局成立，用神有力，行运得地，格局大成。'
            else:
                level = '格局成立'
                detail = f'格局大成，但大运{dayun_xiji}，需待时机。'
                advice = '格局虽好，但大运不佳，宜守成待时。'
                classic = '《子平真诠》：格局成立，但行运不佳，需待时机。'

        elif geju_chengbai == '格局成立':
            if dayun_xiji in ['大喜', '小喜']:
                level = '格局成立'
                detail = f'格局成立，大运{dayun_xiji}，命局平衡。'
                advice = '顺势深耕主业，以稳中求进为宜。'
                classic = '《子平真诠》：格局成立，行运得地，可望事业宏展。'
            elif dayun_xiji == '平':
                level = '格局勉强'
                detail = f'格局成立，但大运{dayun_xiji}，平稳发展。'
                advice = '大体平衡但偶有波折，需善用辅星以守成。'
                classic = '《子平真诠》：格局成立，但行运平平，需稳步前行。'
            else:
                level = '格局勉强'
                detail = f'格局成立，但大运{dayun_xiji}，需防波折。'
                advice = '格局虽成，但大运不佳，需防波折。'
                classic = '《子平真诠》：格局成立，但行运不佳，需防波折。'

        elif geju_chengbai == '格局勉强':
            if dayun_xiji in ['大喜', '小喜']:
                level = '格局勉强'
                detail = f'格局勉强，但大运{dayun_xiji}，可借运势改善。'
                advice = '格局虽弱，但大运得力，可借运势改善。'
                classic = '《子平真诠》：格局勉强，但行运得地，可借运势改善。'
            else:
                level = '格局破败'
                detail = f'格局勉强，大运{dayun_xiji}，需谨慎自守。'
                advice = '守成第一，减少冒险，先固根基。'
                classic = '《子平真诠》：格局勉强，行运不佳，需谨慎自守。'

        else:  # 格局破败
            level = '格局破败'
            detail = f'格局破败，大运{dayun_xiji}，需等待运势翻转。'
            advice = '专注提升自我，等待运势翻转。'
            classic = '《子平真诠》：格局破败，需等待运势翻转。'

        # 2. 补充财运和神煞信息
        if caiyun_chengbai == '格局成立':
            detail += f' 财运{caiyun_chengbai}。'

        if jishen_count > xiongshen_count:
            detail += f' 吉神{jishen_count}项，凶神{xiongshen_count}项，吉多于凶。'
        elif xiongshen_count > jishen_count:
            detail += f' 吉神{jishen_count}项，凶神{xiongshen_count}项，凶多于吉。'

        return {
            'level': level,
            'detail': detail,
            'advice': advice,
            'classic_basis': classic,
        }

def analyze_mingge_complete(analysis_results: Dict[str, Dict]) -> Dict[str, object]:
    """\u517c\u5bb9\u65e7\u63a5\u53e3\u7684\u547d\u683c\u7efc\u5408\u5206\u6790\u51fd\u6570\u3002"""
    return MinggeScoreAnalyzer.analyze_mingge_score(analysis_results)
