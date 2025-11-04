#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据持久化工具 - 移动端
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


class StorageManager:
    """存储管理器"""
    
    def __init__(self, app_name='bagua_clock_mobile'):
        """初始化存储管理器"""
        # 根据平台选择存储路径
        from kivy.utils import platform
        
        if platform == 'android':
            # Android使用应用数据目录
            from android.storage import primary_external_storage_path
            base_path = Path(primary_external_storage_path()) / app_name
        else:
            # 其他平台使用用户目录
            base_path = Path.home() / f'.{app_name}'
        
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # 数据文件路径
        self.history_file = self.base_path / 'history.json'
        self.settings_file = self.base_path / 'settings.json'
        self.results_file = self.base_path / 'results.json'
    
    def save_bazi_result(self, result: Dict[str, Any], name: Optional[str] = None) -> bool:
        """
        保存八字计算结果
        
        Args:
            result: 八字计算结果
            name: 保存的名称（可选）
        
        Returns:
            是否保存成功
        """
        try:
            # 加载现有结果
            results = self.load_all_results()
            
            # 创建新记录
            record = {
                'id': str(datetime.now().timestamp()),
                'timestamp': datetime.now().isoformat(),
                'name': name or result.get('name', '未命名'),
                'data': result
            }
            
            results.append(record)
            
            # 只保留最近100条记录
            if len(results) > 100:
                results = results[-100:]
            
            # 保存
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存结果失败：{e}")
            return False
    
    def load_all_results(self) -> List[Dict[str, Any]]:
        """加载所有保存的结果"""
        try:
            if self.results_file.exists():
                with open(self.results_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def get_result_by_id(self, result_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取结果"""
        results = self.load_all_results()
        for result in results:
            if result.get('id') == result_id:
                return result
        return None
    
    def delete_result(self, result_id: str) -> bool:
        """删除指定结果"""
        try:
            results = self.load_all_results()
            results = [r for r in results if r.get('id') != result_id]
            
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"删除结果失败：{e}")
            return False
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """保存设置"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存设置失败：{e}")
            return False
    
    def load_settings(self) -> Dict[str, Any]:
        """加载设置"""
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {
            'dark_mode': True,
            'auto_save': True,
            'notifications': True
        }
    
    def clear_all_data(self) -> bool:
        """清除所有数据"""
        try:
            if self.results_file.exists():
                self.results_file.unlink()
            if self.history_file.exists():
                self.history_file.unlink()
            return True
        except Exception as e:
            print(f"清除数据失败：{e}")
            return False

