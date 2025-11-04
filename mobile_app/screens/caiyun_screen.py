#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财运分析界面 - 移动端
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp


class CaiyunScreen(MDScreen):
    """财运分析界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'caiyun'
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
            text="财运分析",
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
            text="请先进行八字计算，然后查看财运分析",
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
        btn_analyze.bind(on_press=self.analyze_caiyun)
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
    
    def analyze_caiyun(self, instance):
        """分析财运"""
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
                    'year': (sizhu.get('year_gan', ''), sizhu.get('year_zhi', '')),
                    'month': (sizhu.get('month_gan', ''), sizhu.get('month_zhi', '')),
                    'day': (sizhu.get('day_gan', ''), sizhu.get('day_zhi', '')),
                    'hour': (sizhu.get('hour_gan', ''), sizhu.get('hour_zhi', ''))
                }
                day_master = sizhu.get('day_gan', '')
            else:
                self.show_error("八字数据格式不正确")
                return
            
            # 执行分析
            result = service.analyze_caiyun(pillars, day_master)
            
            if result.get('success'):
                self.display_result(result['data'])
            else:
                self.show_error(result.get('error', '分析失败'))
                
        except Exception as e:
            self.show_error(f"分析出错：{str(e)}")
    
    def display_result(self, data):
        """显示分析结果"""
        self.result_container.clear_widgets()
        
        # 财运状态
        status = data.get('caiyun_status', '未知')
        status_card = MDCard(
            size_hint_y=None,
            height=dp(120),
            padding=15
        )
        status_layout = MDBoxLayout(
            orientation='vertical',
            spacing=10
        )
        status_title = MDLabel(
            text=f"财运状态：{status}",
            theme_text_color="Primary",
            font_style="H6",
            size_hint_y=None,
            height=dp(40)
        )
        status_desc = MDLabel(
            text=data.get('description', ''),
            theme_text_color="Secondary",
            font_style="Body1",
            size_hint_y=None,
            height=dp(70)
        )
        status_layout.add_widget(status_title)
        status_layout.add_widget(status_desc)
        status_card.add_widget(status_layout)
        self.result_container.add_widget(status_card)
        
        # 财星信息
        wealth_count = data.get('wealth_count', 0)
        wealth_card = MDCard(
            size_hint_y=None,
            height=dp(100),
            padding=15
        )
        wealth_label = MDLabel(
            text=f"财星数量：{wealth_count}",
            theme_text_color="Primary",
            font_style="Body1"
        )
        wealth_card.add_widget(wealth_label)
        self.result_container.add_widget(wealth_card)
    
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

