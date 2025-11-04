#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统设置界面 - 移动端
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.switch import MDSwitch
from kivymd.uix.list import MDList, OneLineListItem
from kivy.metrics import dp
import json
from pathlib import Path


class SettingsScreen(MDScreen):
    """系统设置界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'settings'
        self.settings_file = Path.home() / '.bagua_clock_mobile' / 'settings.json'
        self.settings = self.load_settings()
        self.build_ui()
    
    def load_settings(self):
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
    
    def save_settings(self):
        """保存设置"""
        try:
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存设置失败：{e}")
    
    def build_ui(self):
        """构建UI界面"""
        layout = MDBoxLayout(
            orientation='vertical',
            padding=20,
            spacing=20
        )
        
        # 标题
        title = MDLabel(
            text="系统设置",
            halign="center",
            theme_text_color="Primary",
            font_style="H4",
            size_hint_y=None,
            height=dp(48)
        )
        layout.add_widget(title)
        
        # 设置列表
        settings_card = MDCard(
            padding=15
        )
        settings_list = MDList()
        
        # 暗色模式
        dark_item = OneLineListItem(
            text="暗色模式"
        )
        dark_switch = MDSwitch(
            active=self.settings.get('dark_mode', True)
        )
        dark_switch.bind(active=self.on_dark_mode_changed)
        dark_item.add_widget(dark_switch)
        settings_list.add_widget(dark_item)
        
        # 自动保存
        auto_save_item = OneLineListItem(
            text="自动保存结果"
        )
        auto_save_switch = MDSwitch(
            active=self.settings.get('auto_save', True)
        )
        auto_save_switch.bind(active=self.on_auto_save_changed)
        auto_save_item.add_widget(auto_save_switch)
        settings_list.add_widget(auto_save_item)
        
        # 通知
        notify_item = OneLineListItem(
            text="启用通知"
        )
        notify_switch = MDSwitch(
            active=self.settings.get('notifications', True)
        )
        notify_switch.bind(active=self.on_notifications_changed)
        notify_item.add_widget(notify_switch)
        settings_list.add_widget(notify_item)
        
        settings_card.add_widget(settings_list)
        layout.add_widget(settings_card)
        
        # 关于信息
        about_card = MDCard(
            size_hint_y=None,
            height=dp(150),
            padding=15
        )
        about_layout = MDBoxLayout(
            orientation='vertical',
            spacing=10
        )
        about_title = MDLabel(
            text="关于",
            theme_text_color="Primary",
            font_style="H6"
        )
        about_text = MDLabel(
            text="八卦时钟 V2.0.0\n传统命理分析系统移动版",
            theme_text_color="Secondary",
            font_style="Body2"
        )
        about_layout.add_widget(about_title)
        about_layout.add_widget(about_text)
        about_card.add_widget(about_layout)
        layout.add_widget(about_card)
        
        # 返回按钮
        back_btn = MDFlatButton(
            text="返回",
            size_hint_y=None,
            height=dp(48)
        )
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def on_dark_mode_changed(self, instance, value):
        """暗色模式切换"""
        self.settings['dark_mode'] = value
        self.save_settings()
        # 更新应用主题
        app = self.get_running_app()
        if app:
            app.theme_cls.theme_style = "Dark" if value else "Light"
    
    def on_auto_save_changed(self, instance, value):
        """自动保存切换"""
        self.settings['auto_save'] = value
        self.save_settings()
    
    def on_notifications_changed(self, instance, value):
        """通知开关切换"""
        self.settings['notifications'] = value
        self.save_settings()
    
    def go_back(self, instance):
        """返回主界面"""
        if hasattr(self, 'manager') and self.manager:
            self.manager.current = 'home'

