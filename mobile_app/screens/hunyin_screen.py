#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
婚姻分析界面 - 移动端
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp


class HunyinScreen(MDScreen):
    """婚姻分析界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'hunyin'
        self.bazi_result = None
        self.build_ui()
    
    def build_ui(self):
        """构建UI界面"""
        layout = MDBoxLayout(
            orientation='vertical',
            padding=20,
            spacing=20
        )
        
        # 标题
        title = MDLabel(
            text="婚姻分析",
            halign="center",
            theme_text_color="Primary",
            font_style="H4",
            size_hint_y=None,
            height=dp(48)
        )
        layout.add_widget(title)
        
        # 提示
        tip_card = MDCard(
            size_hint_y=None,
            height=dp(80),
            padding=15
        )
        tip_label = MDLabel(
            text="请先进行八字计算，然后查看婚姻分析",
            halign="center",
            theme_text_color="Secondary",
            font_style="Body2"
        )
        tip_card.add_widget(tip_label)
        layout.add_widget(tip_card)
        
        # 分析按钮
        btn_analyze = MDRaisedButton(
            text="开始分析",
            size_hint_y=None,
            height=dp(48)
        )
        btn_analyze.bind(on_press=self.analyze_hunyin)
        layout.add_widget(btn_analyze)
        
        # 结果显示
        scroll = MDScrollView()
        self.result_container = MDBoxLayout(
            orientation='vertical',
            spacing=15,
            adaptive_height=True,
            padding=10
        )
        scroll.add_widget(self.result_container)
        layout.add_widget(scroll)
        
        # 返回按钮
        back_btn = MDFlatButton(
            text="返回",
            size_hint_y=None,
            height=dp(48)
        )
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)
        
        self.add_widget(layout)
    
    def set_bazi_result(self, bazi_result):
        """设置八字计算结果"""
        self.bazi_result = bazi_result
    
    def analyze_hunyin(self, instance):
        """分析婚姻"""
        if not self.bazi_result:
            app = self.get_running_app()
            if hasattr(app, 'current_bazi_result') and app.current_bazi_result:
                self.bazi_result = app.current_bazi_result
            else:
                self.show_error("请先进行八字计算")
                return
        
        try:
            from mobile_app.services.analysis_service import AnalysisService
            service = AnalysisService()
            
            # 提取信息
            if 'sizhu' in self.bazi_result:
                sizhu = self.bazi_result['sizhu']
                pillars = {
                    'year': sizhu.get('year', ''),
                    'month': sizhu.get('month', ''),
                    'day': sizhu.get('day', ''),
                    'hour': sizhu.get('hour', '')
                }
                day_master = sizhu.get('day_gan', '')
                gender = self.bazi_result.get('gender', '男')
            else:
                self.show_error("八字数据格式不正确")
                return
            
            # 执行分析
            result = service.analyze_marriage(pillars, day_master, gender, self.bazi_result)
            
            if result.get('success'):
                self.display_result(result['data'])
            else:
                self.show_error(result.get('error', '分析失败'))
                
        except Exception as e:
            self.show_error(f"分析出错：{str(e)}")
    
    def display_result(self, data):
        """显示分析结果"""
        self.result_container.clear_widgets()
        
        # 婚姻质量
        quality = data.get('quality', '未知')
        quality_card = MDCard(
            size_hint_y=None,
            height=dp(150),
            padding=15
        )
        quality_layout = MDBoxLayout(
            orientation='vertical',
            spacing=10
        )
        quality_title = MDLabel(
            text=f"婚姻质量：{quality}",
            theme_text_color="Primary",
            font_style="H6",
            size_hint_y=None,
            height=dp(40)
        )
        quality_summary = MDLabel(
            text=data.get('summary', ''),
            theme_text_color="Secondary",
            font_style="Body1",
            size_hint_y=None,
            height=dp(100)
        )
        quality_layout.add_widget(quality_title)
        quality_layout.add_widget(quality_summary)
        quality_card.add_widget(quality_layout)
        self.result_container.add_widget(quality_card)
    
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

