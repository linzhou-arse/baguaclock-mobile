#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八卦时钟移动版 - Android & HarmonyOS 4.0+
使用KivyMD框架构建，支持触摸屏操作
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager

# 设置窗口大小（移动端全屏）
if platform == 'android':
    from android import mActivity
    Window.fullscreen = 'auto'
elif platform == 'win':
    # Windows测试模式
    Window.size = (360, 640)

# 导入业务逻辑模块（保持原有逻辑不变）
try:
    from sxtwl_adapter import compute_bazi_json, Rules, Location
    SXTWL_AVAILABLE = True
except ImportError:
    SXTWL_AVAILABLE = False

try:
    from local_mingli_analyzer_unified import UnifiedMingliAnalyzer
    LOCAL_ANALYZER_AVAILABLE = True
except ImportError:
    LOCAL_ANALYZER_AVAILABLE = False

try:
    from chinese_metaphysics_library import UnifiedMetaphysicsAnalyzer
    CML_UNIFIED_AVAILABLE = True
except Exception:
    CML_UNIFIED_AVAILABLE = False


class BaguaClockMobileApp(MDApp):
    """八卦时钟移动应用主类"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "八卦时钟 V2.0.0"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Amber"
        self.current_bazi_result = None
        self.current_analysis_result = None
        
        # 初始化存储管理器
        from mobile_app.utils.storage import StorageManager
        self.storage = StorageManager()
        
        # 加载设置
        settings = self.storage.load_settings()
        if settings.get('dark_mode', True):
            self.theme_cls.theme_style = "Dark"
        else:
            self.theme_cls.theme_style = "Light"
        
    def build(self):
        """构建应用界面"""
        # 加载KV文件
        kv_file = Path(__file__).parent / "bagua_clock_mobile.kv"
        if kv_file.exists():
            root = Builder.load_file(str(kv_file))
            # 确保有screen_manager
            if not hasattr(root, 'ids') or 'screen_manager' not in root.ids:
                # 如果没有screen_manager，创建一个
                sm = ScreenManager()
                # 导入并添加所有屏幕
                from mobile_app.screens.home_screen import HomeScreen
                from mobile_app.screens.bazi_screen import BaziScreen
                from mobile_app.screens.zeri_screen import ZeriScreen
                from mobile_app.screens.fengshui_screen import FengshuiScreen
                from mobile_app.screens.naming_screen import NamingScreen
                
                sm.add_widget(HomeScreen(name='home'))
                sm.add_widget(BaziScreen(name='bazi'))
                sm.add_widget(ZeriScreen(name='zeri'))
                sm.add_widget(FengshuiScreen(name='fengshui'))
                sm.add_widget(NamingScreen(name='naming'))
                return sm
            return root
        else:
            # 如果没有KV文件，使用代码构建
            sm = ScreenManager()
            from mobile_app.screens.home_screen import HomeScreen
            from mobile_app.screens.bazi_screen import BaziScreen
            from mobile_app.screens.zeri_screen import ZeriScreen
            from mobile_app.screens.fengshui_screen import FengshuiScreen
            from mobile_app.screens.naming_screen import NamingScreen
            
            sm.add_widget(HomeScreen(name='home'))
            sm.add_widget(BaziScreen(name='bazi'))
            sm.add_widget(ZeriScreen(name='zeri'))
            sm.add_widget(FengshuiScreen(name='fengshui'))
            sm.add_widget(NamingScreen(name='naming'))
            return sm
    
    
    def on_start(self):
        """应用启动时执行"""
        # 检查依赖模块
        self.check_dependencies()
        
    def check_dependencies(self):
        """检查必要的依赖模块"""
        missing = []
        if not SXTWL_AVAILABLE:
            missing.append("sxtwl_adapter")
        if not LOCAL_ANALYZER_AVAILABLE:
            missing.append("local_mingli_analyzer_unified")
        if not CML_UNIFIED_AVAILABLE:
            missing.append("chinese_metaphysics_library")
        
        if missing:
            from kivymd.uix.dialog import MDDialog
            dialog = MDDialog(
                text=f"缺少以下模块：{', '.join(missing)}\n部分功能可能无法使用。",
                buttons=[
                    MDRaisedButton(
                        text="确定",
                        on_press=lambda x: dialog.dismiss()
                    )
                ]
            )
            dialog.open()


def main():
    """主函数"""
    app = BaguaClockMobileApp()
    app.run()


if __name__ == '__main__':
    main()

