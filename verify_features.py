# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, 'd:\\xianmuweijianjia\\py_suanming传统版')

from local_mingli_analyzer import LocalMingliAnalyzer

analyzer = LocalMingliAnalyzer()
test_pillars = {
    'year': '甲子',
    'month': '丙寅', 
    'day': '戊辰',
    'hour': '庚申'
}

result = analyzer.analyze_bazi(test_pillars, gender='男', birth_info={'year': 2000, 'month': 3, 'day': 15})

if isinstance(result, str):
    print("[OK] Full report generated")
    
    checks = [
        ('SixQin section', '【六、六亲信息】'),
        ('Marriage prediction', '【九、婚姻感情】'),
        ('Marriage age', '预测结婚年龄'),
        ('Auspicious months', '吉利结婚月份'),
    ]
    
    for name, keyword in checks:
        if keyword in result:
            print(f"[OK] {name}")
        else:
            print(f"[FAIL] {name}")
    
    print(f"[INFO] Report length: {len(result)} chars")
else:
    print(f"[FAIL] Analysis returned {type(result)}")
