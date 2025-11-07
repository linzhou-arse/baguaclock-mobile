#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
全面测试1950-2024年八字分析
每年生成一男一女，共150个测试案例
检查：硬编码、逻辑错误、思路错误、闰月处理等
"""

import sys
import io
import random
import json
from datetime import datetime
from lunar_python import Lunar, Solar

# 设置输出编码为UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 测试配置
START_YEAR = 1950
END_YEAR = 2024
TEST_CASES = []

def generate_test_cases():
    """生成测试案例"""
    print("="*80)
    print("生成测试案例（1950-2024年，每年一男一女）")
    print("="*80)
    
    cases = []
    
    for year in range(START_YEAR, END_YEAR + 1):
        # 随机选择月份和日期
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # 避免月末问题
        
        # 随机选择时辰
        hour_male = random.choice([1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23])
        hour_female = random.choice([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22])
        
        # 男性案例
        cases.append({
            'id': f"{year}_M",
            'name': f"测试{year}男",
            'gender': '男',
            'year': year,
            'month': month,
            'day': day,
            'hour': hour_male
        })
        
        # 女性案例
        cases.append({
            'id': f"{year}_F",
            'name': f"测试{year}女",
            'gender': '女',
            'year': year,
            'month': month,
            'day': day,
            'hour': hour_female
        })
    
    print(f"✅ 生成了 {len(cases)} 个测试案例")
    return cases

def check_lunar_conversion(case):
    """检查农历转换"""
    try:
        solar = Solar.fromYmdHms(case['year'], case['month'], case['day'], case['hour'], 0, 0)
        lunar = solar.getLunar()
        
        return {
            'success': True,
            'lunar_year': lunar.getYear(),
            'lunar_month': lunar.getMonth(),
            'lunar_day': lunar.getDay(),
            'is_leap': lunar.getMonth() < 0,  # 负数表示闰月
            'lunar_str': f"{lunar.getYearInChinese()}年{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def analyze_bazi(case):
    """分析八字（调用六书库）"""
    try:
        from sxtwl_adapter import compute_bazi_json, Rules, Location
        from chinese_metaphysics_library import UnifiedMetaphysicsAnalyzer
        from chinese_metaphysics_library.core.data_structures import BaziData

        # 计算八字
        bazi_json = compute_bazi_json(
            year=case['year'],
            month=case['month'],
            day=case['day'],
            hour=case['hour'],
            minute=0,
            second=0,
            tz_offset_hours=8.0,
            rules=Rules(use_true_solar_time=True),
            location=Location(lon=112.98, lat=28.2)
        )

        if not bazi_json or 'error' in bazi_json:
            return {
                'success': False,
                'error': bazi_json.get('error', '八字计算失败')
            }

        # 从sxtwl_json提取pillars
        pillars = bazi_json.get('pillars', {})
        if not pillars:
            return {
                'success': False,
                'error': 'pillars数据缺失'
            }

        # 构造BaziData
        bazi_data = BaziData(
            year=(pillars['year'][0], pillars['year'][1]),
            month=(pillars['month'][0], pillars['month'][1]),
            day=(pillars['day'][0], pillars['day'][1]),
            hour=(pillars['hour'][0], pillars['hour'][1]),
            birth_year=case['year'],
            birth_month=case['month'],
            birth_day=case['day'],
            birth_hour=case['hour'],
            gender=case['gender']
        )

        # 统一分析
        analyzer = UnifiedMetaphysicsAnalyzer()

        # 子平真诠分析
        zpzq_result = analyzer.analyzers['子平真诠'].analyze(bazi_data)
        pattern_info = zpzq_result.details.get('pattern_info', {})
        yongshen_info = zpzq_result.details.get('yongshen_info', {})

        # 渊海子平分析
        yhzp_result = analyzer.analyzers['渊海子平'].analyze(bazi_data)
        shishen_count = yhzp_result.details.get('shishen_count', {})

        # 格式化pillars
        pillars_str = f"{pillars['year'][0]}{pillars['year'][1]} {pillars['month'][0]}{pillars['month'][1]} {pillars['day'][0]}{pillars['day'][1]} {pillars['hour'][0]}{pillars['hour'][1]}"

        return {
            'success': True,
            'pillars': pillars_str,
            'day_master': pillars['day'][0],
            'pattern': pattern_info.get('pattern_type', '未知'),
            'pattern_status': pattern_info.get('pattern_status', '未知'),
            'huwei': pattern_info.get('huwei_description', ''),
            'yongshen': yongshen_info.get('yongshen', ''),
            'yongshen_wuxing': yongshen_info.get('yongshen_wuxing', []),
            'xishen_wuxing': yongshen_info.get('xishen_wuxing', []),
            'jishen_wuxing': yongshen_info.get('jishen_wuxing', []),
            'shishen_count': shishen_count
        }
    except Exception as e:
        import traceback
        return {
            'success': False,
            'error': f"{str(e)}\n{traceback.format_exc()}"
        }

def check_hardcoding(results):
    """检查硬编码问题"""
    issues = []
    
    # 检查1：相同的格局建议
    pattern_advice = {}
    for r in results:
        if r.get('analysis', {}).get('success'):
            pattern = r['analysis'].get('pattern', '')
            advice = r['analysis'].get('advice', '')
            
            if pattern not in pattern_advice:
                pattern_advice[pattern] = []
            pattern_advice[pattern].append(advice)
    
    # 检查是否所有相同格局的建议都一样
    for pattern, advices in pattern_advice.items():
        if len(set(advices)) == 1 and len(advices) > 5:
            issues.append({
                'type': '硬编码',
                'pattern': pattern,
                'issue': f'所有{pattern}的建议都相同',
                'advice': advices[0]
            })
    
    # 检查2：护卫关描述
    huwei_desc = {}
    for r in results:
        if r.get('analysis', {}).get('success'):
            huwei = r['analysis'].get('huwei', '')
            if huwei:
                huwei_desc[huwei] = huwei_desc.get(huwei, 0) + 1
    
    # 如果某个护卫关描述出现次数过多
    for desc, count in huwei_desc.items():
        if count > len(results) * 0.3:  # 超过30%
            issues.append({
                'type': '硬编码',
                'issue': f'护卫关描述"{desc}"出现{count}次（{count/len(results)*100:.1f}%）',
                'suspicious': True
            })
    
    return issues

def check_logic_errors(results):
    """检查逻辑错误"""
    issues = []
    
    for r in results:
        case = r['case']
        analysis = r.get('analysis', {})
        
        if not analysis.get('success'):
            continue
        
        # 检查1：伤官配印格但无印星
        pattern = analysis.get('pattern', '')
        shishen = analysis.get('shishen_count', {})
        
        if '伤官配印' in pattern:
            yin_count = shishen.get('正印', 0) + shishen.get('偏印', 0)
            if yin_count < 0.5:
                issues.append({
                    'type': '逻辑错误',
                    'case_id': case['id'],
                    'issue': f'格局是{pattern}，但印星只有{yin_count:.2f}',
                    'severity': '严重'
                })
        
        # 检查2：伤官格但有大量印星
        if pattern == '伤官格' and '配印' not in pattern:
            yin_count = shishen.get('正印', 0) + shishen.get('偏印', 0)
            if yin_count >= 2.0:
                issues.append({
                    'type': '逻辑错误',
                    'case_id': case['id'],
                    'issue': f'格局是{pattern}，但印星有{yin_count:.2f}（应该是伤官配印格）',
                    'severity': '严重'
                })
        
        # 检查3：用神和喜神矛盾
        yongshen = analysis.get('yongshen_wuxing', [])
        xishen = analysis.get('xishen_wuxing', [])
        jishen = analysis.get('jishen_wuxing', [])
        
        # 用神不应该在忌神中
        for ys in yongshen:
            if ys in jishen:
                issues.append({
                    'type': '逻辑错误',
                    'case_id': case['id'],
                    'issue': f'用神{ys}同时在忌神中',
                    'severity': '严重'
                })
    
    return issues

def check_leap_month(results):
    """检查闰月处理"""
    issues = []
    leap_cases = []
    
    for r in results:
        lunar = r.get('lunar', {})
        if lunar.get('is_leap'):
            leap_cases.append(r)
    
    print(f"\n找到 {len(leap_cases)} 个闰月案例")
    
    for r in leap_cases:
        case = r['case']
        lunar = r['lunar']
        analysis = r.get('analysis', {})
        
        # 检查闰月是否正确处理
        if not analysis.get('success'):
            issues.append({
                'type': '闰月处理',
                'case_id': case['id'],
                'issue': '闰月案例分析失败',
                'lunar': lunar.get('lunar_str', '')
            })
    
    return issues, leap_cases

def main():
    print("="*80)
    print("全面测试：1950-2024年八字分析")
    print("="*80)
    
    # 1. 生成测试案例
    test_cases = generate_test_cases()
    
    # 2. 测试农历转换
    print("\n" + "="*80)
    print("步骤1：测试农历转换")
    print("="*80)
    
    results = []
    conversion_errors = []
    
    for i, case in enumerate(test_cases):
        lunar_result = check_lunar_conversion(case)
        
        result = {
            'case': case,
            'lunar': lunar_result
        }
        
        if not lunar_result['success']:
            conversion_errors.append({
                'case_id': case['id'],
                'error': lunar_result['error']
            })
        
        results.append(result)
        
        if (i + 1) % 20 == 0:
            print(f"  已处理 {i + 1}/{len(test_cases)} 个案例...")
    
    print(f"✅ 农历转换完成")
    print(f"   成功：{len(results) - len(conversion_errors)} 个")
    print(f"   失败：{len(conversion_errors)} 个")
    
    if conversion_errors:
        print("\n❌ 农历转换错误：")
        for err in conversion_errors[:5]:  # 只显示前5个
            print(f"   {err['case_id']}: {err['error']}")
    
    # 3. 检查闰月处理
    print("\n" + "="*80)
    print("步骤2：检查闰月处理")
    print("="*80)
    
    leap_issues, leap_cases = check_leap_month(results)
    
    if leap_cases:
        print(f"✅ 找到 {len(leap_cases)} 个闰月案例")
        for lc in leap_cases[:3]:  # 显示前3个
            case = lc['case']
            lunar = lc['lunar']
            print(f"   {case['id']}: {case['year']}-{case['month']}-{case['day']} → {lunar.get('lunar_str', '')}")
    
    if leap_issues:
        print(f"\n❌ 闰月处理问题：{len(leap_issues)} 个")
        for issue in leap_issues[:5]:
            print(f"   {issue['case_id']}: {issue['issue']}")
    
    # 4. 运行八字分析测试（选择部分案例）
    print("\n" + "="*80)
    print("步骤3：运行八字分析测试（抽样测试）")
    print("="*80)

    # 选择测试案例：每10年抽取2个（1男1女）+ 所有闰月案例
    sample_cases = []

    # 每10年抽取
    for year in range(START_YEAR, END_YEAR + 1, 10):
        year_cases = [c for c in test_cases if c['year'] == year]
        sample_cases.extend(year_cases[:2])  # 取该年的男女各1个

    # 添加所有闰月案例
    for lc in leap_cases:
        if lc['case'] not in sample_cases:
            sample_cases.append(lc['case'])

    print(f"选择了 {len(sample_cases)} 个案例进行详细分析")
    print(f"  - 抽样案例：{len(sample_cases) - len(leap_cases)} 个")
    print(f"  - 闰月案例：{len(leap_cases)} 个")

    # 运行分析
    analysis_results = []
    analysis_errors = []

    for i, case in enumerate(sample_cases):
        print(f"\r  分析中... {i+1}/{len(sample_cases)}", end='')

        analysis = analyze_bazi(case)

        # 找到对应的lunar结果
        lunar_result = next((r['lunar'] for r in results if r['case']['id'] == case['id']), {})

        result = {
            'case': case,
            'lunar': lunar_result,
            'analysis': analysis
        }

        if not analysis['success']:
            analysis_errors.append({
                'case_id': case['id'],
                'error': analysis.get('error', '未知错误')
            })

        analysis_results.append(result)

    print(f"\n✅ 八字分析完成")
    print(f"   成功：{len(analysis_results) - len(analysis_errors)} 个")
    print(f"   失败：{len(analysis_errors)} 个")

    if analysis_errors:
        print(f"\n❌ 分析错误：")
        for err in analysis_errors[:5]:
            print(f"   {err['case_id']}: {err['error']}")

    # 5. 检查硬编码
    print("\n" + "="*80)
    print("步骤4：检查硬编码问题")
    print("="*80)

    hardcoding_issues = check_hardcoding(analysis_results)

    if hardcoding_issues:
        print(f"❌ 发现 {len(hardcoding_issues)} 个硬编码问题")
        for issue in hardcoding_issues:
            print(f"   类型：{issue['type']}")
            print(f"   问题：{issue['issue']}")
    else:
        print(f"✅ 未发现硬编码问题")

    # 6. 检查逻辑错误
    print("\n" + "="*80)
    print("步骤5：检查逻辑错误")
    print("="*80)

    logic_issues = check_logic_errors(analysis_results)

    if logic_issues:
        print(f"❌ 发现 {len(logic_issues)} 个逻辑错误")
        for issue in logic_issues[:10]:  # 显示前10个
            print(f"   案例：{issue['case_id']}")
            print(f"   问题：{issue['issue']}")
            print(f"   严重程度：{issue['severity']}")
            print()
    else:
        print(f"✅ 未发现逻辑错误")

    # 7. 生成测试报告
    print("\n" + "="*80)
    print("生成测试报告")
    print("="*80)

    report = {
        'test_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_cases': len(test_cases),
        'year_range': f"{START_YEAR}-{END_YEAR}",
        'conversion_success': len(results) - len(conversion_errors),
        'conversion_errors': len(conversion_errors),
        'leap_month_cases': len(leap_cases),
        'leap_month_issues': len(leap_issues),
        'analysis_sample_size': len(sample_cases),
        'analysis_success': len(analysis_results) - len(analysis_errors),
        'analysis_errors': len(analysis_errors),
        'hardcoding_issues': len(hardcoding_issues),
        'logic_issues': len(logic_issues),
        'test_cases': test_cases[:10],  # 保存前10个案例作为示例
        'leap_cases': [lc['case'] for lc in leap_cases[:5]],  # 保存前5个闰月案例
        'hardcoding_details': hardcoding_issues,
        'logic_details': logic_issues[:20]  # 保存前20个逻辑错误
    }

    # 保存报告
    with open('测试报告_完整分析.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"✅ 测试报告已保存：测试报告_完整分析.json")
    
    # 8. 总结
    print("\n" + "="*80)
    print("测试总结")
    print("="*80)

    print(f"\n📊 测试统计：")
    print(f"   总案例数：{len(test_cases)} 个")
    print(f"   年份范围：{START_YEAR}-{END_YEAR}")
    print(f"   男性案例：{len([c for c in test_cases if c['gender'] == '男'])} 个")
    print(f"   女性案例：{len([c for c in test_cases if c['gender'] == '女'])} 个")

    print(f"\n✅ 农历转换：")
    print(f"   成功：{len(results) - len(conversion_errors)} 个")
    print(f"   失败：{len(conversion_errors)} 个")
    print(f"   成功率：{(len(results) - len(conversion_errors)) / len(results) * 100:.1f}%")

    print(f"\n📅 闰月处理：")
    print(f"   闰月案例：{len(leap_cases)} 个")
    print(f"   处理问题：{len(leap_issues)} 个")

    print(f"\n🔍 八字分析（抽样）：")
    print(f"   抽样数量：{len(sample_cases)} 个")
    print(f"   分析成功：{len(analysis_results) - len(analysis_errors)} 个")
    print(f"   分析失败：{len(analysis_errors)} 个")
    print(f"   成功率：{(len(analysis_results) - len(analysis_errors)) / len(analysis_results) * 100:.1f}%")

    print(f"\n🔧 质量检查：")
    print(f"   硬编码问题：{len(hardcoding_issues)} 个")
    print(f"   逻辑错误：{len(logic_issues)} 个")

    # 评分
    total_score = 100
    if conversion_errors:
        total_score -= len(conversion_errors) / len(results) * 20
    if leap_issues:
        total_score -= len(leap_issues) / max(len(leap_cases), 1) * 15
    if analysis_errors:
        total_score -= len(analysis_errors) / len(analysis_results) * 25
    if hardcoding_issues:
        total_score -= min(len(hardcoding_issues) * 5, 20)
    if logic_issues:
        total_score -= min(len(logic_issues) * 2, 20)

    print(f"\n📈 总体评分：{total_score:.1f}/100")

    if total_score >= 90:
        print("   评级：优秀 ⭐⭐⭐⭐⭐")
    elif total_score >= 80:
        print("   评级：良好 ⭐⭐⭐⭐")
    elif total_score >= 70:
        print("   评级：中等 ⭐⭐⭐")
    elif total_score >= 60:
        print("   评级：及格 ⭐⭐")
    else:
        print("   评级：不及格 ⭐")

    print("\n" + "="*80)
    print("测试完成！")
    print("="*80)
    print(f"\n详细报告已保存：测试报告_完整分析.json")

    if hardcoding_issues or logic_issues:
        print(f"\n⚠️  发现问题，建议修复：")
        if hardcoding_issues:
            print(f"   - 硬编码问题：{len(hardcoding_issues)} 个")
        if logic_issues:
            print(f"   - 逻辑错误：{len(logic_issues)} 个")
    else:
        print(f"\n✅ 未发现硬编码和逻辑错误，系统运行良好！")

if __name__ == "__main__":
    main()

