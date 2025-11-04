#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
起名分析界面 - 移动端
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp


class NamingScreen(MDScreen):
    """起名分析界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'naming'
        self.analysis_mode = 'analyze'  # 'analyze' 或 'suggest'
        self.build_ui()
    
    def build_ui(self):
        """构建UI界面"""
        layout = MDBoxLayout(
            orientation='vertical',
            padding=10,
            spacing=10
        )
        
        # 标题
        title = MDLabel(
            text="起名分析",
            halign="center",
            theme_text_color="Primary",
            font_style="H4",
            size_hint_y=None,
            height=dp(48)
        )
        layout.add_widget(title)
        
        # 模式选择
        mode_card = MDCard(
            size_hint_y=None,
            padding=15,
            spacing=10
        )
        mode_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint_y=None,
            height=dp(48)
        )
        
        self.analyze_btn = MDRaisedButton(
            text="姓名分析",
            size_hint_x=0.5
        )
        self.analyze_btn.bind(on_press=lambda x: self.set_mode('analyze'))
        mode_layout.add_widget(self.analyze_btn)
        
        self.suggest_btn = MDFlatButton(
            text="起名建议",
            size_hint_x=0.5
        )
        self.suggest_btn.bind(on_press=lambda x: self.set_mode('suggest'))
        mode_layout.add_widget(self.suggest_btn)
        
        mode_card.add_widget(mode_layout)
        layout.add_widget(mode_card)
        
        # 输入表单区域
        scroll = MDScrollView()
        self.form_container = MDBoxLayout(
            orientation='vertical',
            spacing=15,
            adaptive_height=True,
            padding=10
        )
        scroll.add_widget(self.form_container)
        layout.add_widget(scroll)
        
        # 构建分析表单
        self.build_analyze_form()
        
        # 分析按钮
        analyze_btn = MDRaisedButton(
            text="开始分析",
            size_hint_y=None,
            height=dp(48)
        )
        analyze_btn.bind(on_press=self.analyze_naming)
        layout.add_widget(analyze_btn)
        
        # 结果显示区域
        result_scroll = MDScrollView()
        self.result_container = MDBoxLayout(
            orientation='vertical',
            spacing=15,
            adaptive_height=True,
            padding=10
        )
        result_scroll.add_widget(self.result_container)
        layout.add_widget(result_scroll)
        
        # 返回按钮
        back_btn = MDFlatButton(
            text="返回",
            size_hint_y=None,
            height=dp(48)
        )
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def set_mode(self, mode):
        """设置分析模式"""
        self.analysis_mode = mode
        if mode == 'analyze':
            self.analyze_btn.md_bg_color = self.theme_cls.primary_color
            self.suggest_btn.md_bg_color = [0, 0, 0, 0]
        else:
            self.suggest_btn.md_bg_color = self.theme_cls.primary_color
            self.analyze_btn.md_bg_color = [0, 0, 0, 0]
        
        # 重建表单
        self.form_container.clear_widgets()
        if mode == 'analyze':
            self.build_analyze_form()
        else:
            self.build_suggest_form()
    
    def build_analyze_form(self):
        """构建姓名分析表单"""
        # 提示
        tip = MDLabel(
            text="提示：姓名分析需要先计算八字，请先在'八字算命'中计算",
            theme_text_color="Secondary",
            font_style="Body2",
            size_hint_y=None,
            height=dp(60)
        )
        self.form_container.add_widget(tip)
        
        # 姓氏
        self.surname = MDTextField(
            hint_text="姓氏",
            size_hint_y=None,
            height=dp(48)
        )
        self.form_container.add_widget(self.surname)
        
        # 名字
        self.given_name = MDTextField(
            hint_text="名字（不含姓氏）",
            size_hint_y=None,
            height=dp(48)
        )
        self.form_container.add_widget(self.given_name)
    
    def build_suggest_form(self):
        """构建起名建议表单"""
        # 提示
        tip = MDLabel(
            text="提示：起名建议需要先计算八字，请先在'八字算命'中计算",
            theme_text_color="Secondary",
            font_style="Body2",
            size_hint_y=None,
            height=dp(60)
        )
        self.form_container.add_widget(tip)
        
        # 姓氏
        self.suggest_surname = MDTextField(
            hint_text="姓氏",
            size_hint_y=None,
            height=dp(48)
        )
        self.form_container.add_widget(self.suggest_surname)
    
    def analyze_naming(self, instance):
        """执行起名分析"""
        try:
            # 检查是否有八字结果
            app = self.get_running_app()
            if not hasattr(app, 'current_bazi_result') or not app.current_bazi_result:
                self.show_error("请先在'八字算命'中计算八字")
                return
            
            # 清空之前的结果
            self.result_container.clear_widgets()
            
            from mobile_app.services.naming_service import NamingService
            service = NamingService()
            
            if self.analysis_mode == 'analyze':
                # 姓名分析
                surname = self.surname.text or ""
                given_name = self.given_name.text or ""
                
                if not surname or not given_name:
                    self.show_error("请填写完整的姓名")
                    return
                
                gender = app.current_bazi_result.get('gender', '男')
                result = service.analyze_name(
                    surname, given_name, app.current_bazi_result, gender
                )
            else:
                # 起名建议
                surname = self.suggest_surname.text or ""
                
                if not surname:
                    self.show_error("请填写姓氏")
                    return
                
                gender = app.current_bazi_result.get('gender', '男')
                result = service.suggest_names(
                    surname, app.current_bazi_result, gender
                )
            
            if result.get('success'):
                self.display_result(result['data'])
            else:
                self.show_error(result.get('error', '分析失败'))
                
        except Exception as e:
            self.show_error(f"分析出错：{str(e)}")
    
    def display_result(self, data):
        """显示分析结果"""
        card = MDCard(
            size_hint_y=None,
            padding=15,
            spacing=10
        )
        card_layout = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            adaptive_height=True
        )
        
        title = MDLabel(
            text="【分析结果】",
            theme_text_color="Primary",
            font_style="H6",
            size_hint_y=None,
            height=dp(30)
        )
        card_layout.add_widget(title)
        
        if self.analysis_mode == 'analyze':
            analysis_text = data.get('analysis', '')
        else:
            analysis_text = data.get('suggestions', '')
        
        content = MDLabel(
            text=analysis_text,
            theme_text_color="Secondary",
            font_style="Body1",
            size_hint_y=None,
            height=dp(len(analysis_text.split('\n')) * 30)
        )
        card_layout.add_widget(content)
        card.add_widget(card_layout)
        self.result_container.add_widget(card)
    
    def show_error(self, message):
        """显示错误信息"""
        self.result_container.clear_widgets()
        error_card = MDCard(
            size_hint_y=None,
            height=dp(100),
            padding=15
        )
        error_label = MDLabel(
            text=message,
            halign="center",
            theme_text_color="Error",
            font_style="Body1"
        )
        error_card.add_widget(error_label)
        self.result_container.add_widget(error_card)
    
    def go_back(self, instance):
        """返回主界面"""
        if hasattr(self, 'manager') and self.manager:
            self.manager.current = 'home'

