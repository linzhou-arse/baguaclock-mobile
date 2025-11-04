#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
神煞分析界面 - 移动端
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField
from kivymd.uix.chip import MDChip
from kivy.metrics import dp


class ShenshaScreen(MDScreen):
    """神煞分析界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'shensha'
        self.bazi_result = None  # 从八字计算结果获取
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
            text="神煞分析",
            halign="center",
            theme_text_color="Primary",
            font_style="H4",
            size_hint_y=None,
            height=dp(48)
        )
        layout.add_widget(title)
        
        # 提示信息
        tip_card = MDCard(
            size_hint_y=None,
            height=dp(80),
            padding=15
        )
        tip_label = MDLabel(
            text="请先进行八字计算，然后查看神煞分析结果",
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
        btn_analyze.bind(on_press=self.analyze_shensha)
        layout.add_widget(btn_analyze)
        
        # 结果显示区域
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
    
    def analyze_shensha(self, instance):
        """分析神煞"""
        if not self.bazi_result:
            # 尝试从应用获取
            app = self.get_running_app()
            if hasattr(app, 'current_bazi_result') and app.current_bazi_result:
                self.bazi_result = app.current_bazi_result
            else:
                self.show_error("请先进行八字计算")
                return
        
        try:
            from mobile_app.services.analysis_service import AnalysisService
            service = AnalysisService()
            
            # 提取四柱信息
            if 'sizhu' in self.bazi_result:
                sizhu = self.bazi_result['sizhu']
                pillars = {
                    'year': (sizhu.get('year_gan', ''), sizhu.get('year_zhi', '')),
                    'month': (sizhu.get('month_gan', ''), sizhu.get('month_zhi', '')),
                    'day': (sizhu.get('day_gan', ''), sizhu.get('day_zhi', '')),
                    'hour': (sizhu.get('hour_gan', ''), sizhu.get('hour_zhi', ''))
                }
            else:
                self.show_error("八字数据格式不正确")
                return
            
            birth_info = {
                'gender': self.bazi_result.get('gender', '男')
            }
            
            # 执行分析
            result = service.analyze_shensha(pillars, birth_info)
            
            if result.get('success'):
                self.display_result(result['data'])
            else:
                self.show_error(result.get('error', '分析失败'))
                
        except Exception as e:
            self.show_error(f"分析出错：{str(e)}")
    
    def display_result(self, data):
        """显示分析结果"""
        # 清空之前的结果
        self.result_container.clear_widgets()
        
        # 总体评价
        level = data.get('level', '未知')
        level_card = MDCard(
            size_hint_y=None,
            height=dp(100),
            padding=15
        )
        level_layout = MDBoxLayout(
            orientation='vertical',
            spacing=10
        )
        level_title = MDLabel(
            text=f"总体评价：{level}",
            theme_text_color="Primary",
            font_style="H6",
            size_hint_y=None,
            height=dp(40)
        )
        level_desc = MDLabel(
            text=data.get('analysis', ''),
            theme_text_color="Secondary",
            font_style="Body1",
            size_hint_y=None,
            height=dp(50)
        )
        level_layout.add_widget(level_title)
        level_layout.add_widget(level_desc)
        level_card.add_widget(level_layout)
        self.result_container.add_widget(level_card)
        
        # 吉神
        ji_sha = data.get('ji_sha', [])
        if ji_sha:
            ji_card = MDCard(
                size_hint_y=None,
                height=dp(150),
                padding=15
            )
            ji_title = MDLabel(
                text="吉神",
                theme_text_color="Primary",
                font_style="H6",
                size_hint_y=None,
                height=dp(30)
            )
            ji_card.add_widget(ji_title)
            
            ji_chips = MDBoxLayout(
                orientation='horizontal',
                spacing=10,
                adaptive_height=True
            )
            for sha in ji_sha[:10]:  # 最多显示10个
                name = sha.get('name', '')
                chip = MDChip(
                    text=name,
                    color=[0, 1, 0, 0.3]  # 绿色背景
                )
                ji_chips.add_widget(chip)
            ji_card.add_widget(ji_chips)
            self.result_container.add_widget(ji_card)
        
        # 凶煞
        xiong_sha = data.get('xiong_sha', [])
        if xiong_sha:
            xiong_card = MDCard(
                size_hint_y=None,
                height=dp(150),
                padding=15
            )
            xiong_title = MDLabel(
                text="凶煞",
                theme_text_color="Primary",
                font_style="H6",
                size_hint_y=None,
                height=dp(30)
            )
            xiong_card.add_widget(xiong_title)
            
            xiong_chips = MDBoxLayout(
                orientation='horizontal',
                spacing=10,
                adaptive_height=True
            )
            for sha in xiong_sha[:10]:  # 最多显示10个
                name = sha.get('name', '')
                chip = MDChip(
                    text=name,
                    color=[1, 0, 0, 0.3]  # 红色背景
                )
                xiong_chips.add_widget(chip)
            xiong_card.add_widget(xiong_chips)
            self.result_container.add_widget(xiong_card)
    
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

