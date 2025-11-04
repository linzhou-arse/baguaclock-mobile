#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主界面 - 移动端
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.gridlayout import MDGridLayout
from kivy.clock import Clock
from kivy.metrics import dp
from datetime import datetime


class HomeScreen(MDScreen):
    """主界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'home'
        self.build_ui()
        # 启动时间更新
        Clock.schedule_interval(self.update_time, 1)
    
    def build_ui(self):
        """构建UI界面"""
        layout = MDBoxLayout(
            orientation='vertical',
            padding=20,
            spacing=20
        )
        
        # 标题
        title = MDLabel(
            text="八卦时钟 V2.0.0",
            halign="center",
            theme_text_color="Primary",
            font_style="H4",
            size_hint_y=None,
            height=dp(48)
        )
        layout.add_widget(title)
        
        # 八卦时钟显示区域
        clock_card = MDCard(
            size_hint_y=None,
            height=dp(300),
            padding=15,
            spacing=10
        )
        
        clock_layout = MDBoxLayout(
            orientation='vertical',
            spacing=10
        )
        
        clock_label = MDLabel(
            text="当前时辰",
            halign="center",
            theme_text_color="Primary",
            font_style="H6",
            size_hint_y=None,
            height=dp(40)
        )
        
        self.time_label = MDLabel(
            text="加载中...",
            halign="center",
            theme_text_color="Secondary",
            font_style="Body1",
            size_hint_y=None,
            height=dp(60)
        )
        
        clock_layout.add_widget(clock_label)
        clock_layout.add_widget(self.time_label)
        clock_card.add_widget(clock_layout)
        layout.add_widget(clock_card)
        
        # 功能按钮区域
        btn_layout = MDBoxLayout(
            orientation='vertical',
            spacing=10
        )
        
        btn_bazi = MDRaisedButton(
            text="八字算命",
            size_hint_y=None,
            height=dp(60)
        )
        btn_bazi.bind(on_press=self.show_bazi)
        btn_layout.add_widget(btn_bazi)
        
        btn_zeri = MDRaisedButton(
            text="择日分析",
            size_hint_y=None,
            height=dp(60)
        )
        btn_zeri.bind(on_press=self.show_zeri)
        btn_layout.add_widget(btn_zeri)
        
        btn_fengshui = MDRaisedButton(
            text="风水分析",
            size_hint_y=None,
            height=dp(60)
        )
        btn_fengshui.bind(on_press=self.show_fengshui)
        btn_layout.add_widget(btn_fengshui)
        
        btn_naming = MDRaisedButton(
            text="起名分析",
            size_hint_y=None,
            height=dp(60)
        )
        btn_naming.bind(on_press=self.show_naming)
        btn_layout.add_widget(btn_naming)
        
        layout.add_widget(btn_layout)
        
        self.add_widget(layout)
    
    def update_time(self, dt):
        """更新时间显示"""
        now = datetime.now()
        time_str = now.strftime("%Y年%m月%d日 %H:%M:%S")
        self.time_label.text = time_str
    
    def show_bazi(self, instance):
        """显示八字算命界面"""
        if hasattr(self, 'manager') and self.manager:
            self.manager.current = 'bazi'
    
    def show_zeri(self, instance):
        """显示择日分析界面"""
        if hasattr(self, 'manager') and self.manager:
            self.manager.current = 'zeri'
    
    def show_fengshui(self, instance):
        """显示风水分析界面"""
        if hasattr(self, 'manager') and self.manager:
            self.manager.current = 'fengshui'
    
    def show_naming(self, instance):
        """显示起名分析界面"""
        if hasattr(self, 'manager') and self.manager:
            self.manager.current = 'naming'

