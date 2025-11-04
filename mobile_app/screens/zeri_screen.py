#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
择日分析界面 - 移动端
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.segmentedbutton import MDSegmentedButton, MDSegmentedButtonItem
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.metrics import dp
from datetime import datetime, date, timedelta


class ZeriScreen(MDScreen):
    """择日分析界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'zeri'
        self.mode = 'general'  # 'general' 或 'bazi'
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
            text="择日分析",
            halign="center",
            theme_text_color="Primary",
            font_style="H4",
            size_hint_y=None,
            height=dp(48)
        )
        layout.add_widget(title)
        
        # 择日模式选择
        mode_card = MDCard(
            size_hint_y=None,
            padding=15,
            spacing=10
        )
        mode_layout = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            adaptive_height=True
        )
        
        mode_label = MDLabel(
            text="择日模式",
            theme_text_color="Primary",
            font_style="H6",
            size_hint_y=None,
            height=dp(30)
        )
        mode_layout.add_widget(mode_label)
        
        # 模式选择按钮
        btn_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint_y=None,
            height=dp(48)
        )
        
        self.general_btn = MDRaisedButton(
            text="黄道吉日",
            size_hint_x=0.5
        )
        self.general_btn.bind(on_press=lambda x: self.set_mode('general'))
        btn_layout.add_widget(self.general_btn)
        
        self.bazi_btn = MDFlatButton(
            text="八字择日",
            size_hint_x=0.5
        )
        self.bazi_btn.bind(on_press=lambda x: self.set_mode('bazi'))
        btn_layout.add_widget(self.bazi_btn)
        
        mode_layout.add_widget(btn_layout)
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
        
        # 构建通用输入表单
        self.build_general_form()
        
        # 分析按钮
        analyze_btn = MDRaisedButton(
            text="开始择日分析",
            size_hint_y=None,
            height=dp(48)
        )
        analyze_btn.bind(on_press=self.analyze_zeri)
        layout.add_widget(analyze_btn)
        
        # 结果显示区域
        self.result_scroll = MDScrollView()
        self.result_container = MDBoxLayout(
            orientation='vertical',
            spacing=15,
            adaptive_height=True,
            padding=10
        )
        self.result_scroll.add_widget(self.result_container)
        layout.add_widget(self.result_scroll)
        
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
        """设置择日模式"""
        self.mode = mode
        if mode == 'general':
            self.general_btn.md_bg_color = self.theme_cls.primary_color
            self.bazi_btn.md_bg_color = [0, 0, 0, 0]
        else:
            self.bazi_btn.md_bg_color = self.theme_cls.primary_color
            self.general_btn.md_bg_color = [0, 0, 0, 0]
        
        # 重建表单
        self.form_container.clear_widgets()
        if mode == 'general':
            self.build_general_form()
        else:
            self.build_bazi_form()
    
    def build_general_form(self):
        """构建黄道吉日输入表单"""
        # 事件类型
        self.event_type = MDTextField(
            hint_text="事件类型（如：结婚嫁娶、开业开张等）",
            size_hint_y=None,
            height=dp(48)
        )
        self.form_container.add_widget(self.event_type)
        
        # 开始日期
        self.start_date = MDTextField(
            hint_text="开始日期（YYYY-MM-DD）",
            size_hint_y=None,
            height=dp(48)
        )
        self.form_container.add_widget(self.start_date)
        
        # 结束日期
        self.end_date = MDTextField(
            hint_text="结束日期（YYYY-MM-DD）",
            size_hint_y=None,
            height=dp(48)
        )
        self.form_container.add_widget(self.end_date)
    
    def build_bazi_form(self):
        """构建八字择日输入表单"""
        # 提示：需要先计算八字
        tip = MDLabel(
            text="八字择日模式：请先在'八字算命'中计算八字，然后返回此界面进行分析",
            theme_text_color="Secondary",
            font_style="Body2",
            size_hint_y=None,
            height=dp(80)
        )
        self.form_container.add_widget(tip)
        
        # 事件类型
        self.bazi_event_type = MDTextField(
            hint_text="事件类型",
            size_hint_y=None,
            height=dp(48)
        )
        self.form_container.add_widget(self.bazi_event_type)
        
        # 开始日期
        self.bazi_start_date = MDTextField(
            hint_text="开始日期（YYYY-MM-DD）",
            size_hint_y=None,
            height=dp(48)
        )
        self.form_container.add_widget(self.bazi_start_date)
        
        # 结束日期
        self.bazi_end_date = MDTextField(
            hint_text="结束日期（YYYY-MM-DD）",
            size_hint_y=None,
            height=dp(48)
        )
        self.form_container.add_widget(self.bazi_end_date)
    
    def analyze_zeri(self, instance):
        """执行择日分析"""
        try:
            # 清空之前的结果
            self.result_container.clear_widgets()
            
            if self.mode == 'general':
                # 黄道吉日模式
                event_type = self.event_type.text or "通用择日"
                start_date_str = self.start_date.text or datetime.now().strftime('%Y-%m-%d')
                end_date_str = self.end_date.text or (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
                
                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                except:
                    self.show_error("日期格式错误，请使用YYYY-MM-DD格式")
                    return
                
                from mobile_app.services.zeri_service import ZeriService
                service = ZeriService()
                result = service.analyze_general_auspicious_dates(
                    event_type, start_date, end_date
                )
                
                if result.get('success'):
                    self.display_result(result['data'])
                else:
                    self.show_error(result.get('error', '分析失败'))
            else:
                # 八字择日模式
                app = self.get_running_app()
                if not hasattr(app, 'current_bazi_result') or not app.current_bazi_result:
                    self.show_error("请先在'八字算命'中计算八字")
                    return
                
                event_type = self.bazi_event_type.text or "通用择日"
                start_date_str = self.bazi_start_date.text or datetime.now().strftime('%Y-%m-%d')
                end_date_str = self.bazi_end_date.text or (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
                
                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                except:
                    self.show_error("日期格式错误，请使用YYYY-MM-DD格式")
                    return
                
                from mobile_app.services.zeri_service import ZeriService
                service = ZeriService()
                result = service.analyze_bazi_auspicious_dates(
                    event_type, app.current_bazi_result, start_date, end_date
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
            text="【择日分析结果】",
            theme_text_color="Primary",
            font_style="H6",
            size_hint_y=None,
            height=dp(30)
        )
        card_layout.add_widget(title)
        
        analysis_text = data.get('analysis', '')
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

