#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风水分析界面 - 移动端
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivy.metrics import dp


class FengshuiScreen(MDScreen):
    """风水分析界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'fengshui'
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
            text="风水分析",
            halign="center",
            theme_text_color="Primary",
            font_style="H4",
            size_hint_y=None,
            height=dp(48)
        )
        layout.add_widget(title)
        
        # 输入表单区域
        scroll = MDScrollView()
        form_layout = MDBoxLayout(
            orientation='vertical',
            spacing=15,
            adaptive_height=True,
            padding=10
        )
        
        # 风水类型
        self.fengshui_type = MDTextField(
            hint_text="风水类型（阳宅/阴宅/办公室）",
            size_hint_y=None,
            height=dp(48)
        )
        form_layout.add_widget(self.fengshui_type)
        
        # 房屋朝向
        self.direction = MDTextField(
            hint_text="房屋朝向（如：坐北朝南）",
            size_hint_y=None,
            height=dp(48)
        )
        form_layout.add_widget(self.direction)
        
        # 总层数
        self.total_floors = MDTextField(
            hint_text="总层数",
            input_filter='int',
            size_hint_y=None,
            height=dp(48)
        )
        form_layout.add_widget(self.total_floors)
        
        # 当前楼层
        self.current_floor = MDTextField(
            hint_text="当前楼层",
            input_filter='int',
            size_hint_y=None,
            height=dp(48)
        )
        form_layout.add_widget(self.current_floor)
        
        # 面积
        self.area = MDTextField(
            hint_text="面积（平方米）",
            input_filter='float',
            size_hint_y=None,
            height=dp(48)
        )
        form_layout.add_widget(self.area)
        
        # 主要居住者
        self.main_resident = MDTextField(
            hint_text="主要居住者（可选）",
            size_hint_y=None,
            height=dp(48)
        )
        form_layout.add_widget(self.main_resident)
        
        # 分析按钮
        analyze_btn = MDRaisedButton(
            text="开始风水分析",
            size_hint_y=None,
            height=dp(48)
        )
        analyze_btn.bind(on_press=self.analyze_fengshui)
        form_layout.add_widget(analyze_btn)
        
        scroll.add_widget(form_layout)
        layout.add_widget(scroll)
        
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
    
    def analyze_fengshui(self, instance):
        """执行风水分析"""
        try:
            # 获取输入
            fengshui_type = self.fengshui_type.text or "阳宅"
            direction = self.direction.text or "坐北朝南"
            total_floors = int(self.total_floors.text) if self.total_floors.text else 6
            current_floor = int(self.current_floor.text) if self.current_floor.text else 1
            area = float(self.area.text) if self.area.text else 100.0
            main_resident = self.main_resident.text or ""
            
            # 尝试获取八字信息（用于命卦计算）
            app = self.get_running_app()
            birth_year = None
            gender = None
            if hasattr(app, 'current_bazi_result') and app.current_bazi_result:
                birth_year = app.current_bazi_result.get('birth_year')
                gender = app.current_bazi_result.get('gender')
            
            # 清空之前的结果
            self.result_container.clear_widgets()
            
            from mobile_app.services.fengshui_service import FengshuiService
            service = FengshuiService()
            result = service.analyze_fengshui(
                fengshui_type, direction, total_floors, current_floor,
                area, main_resident, "", birth_year, gender
            )
            
            if result.get('success'):
                self.display_result(result['data'])
            else:
                self.show_error(result.get('error', '分析失败'))
                
        except Exception as e:
            self.show_error(f"分析出错：{str(e)}")
    
    def display_result(self, data):
        """显示分析结果"""
        # 朝向信息
        direction_info = data.get('direction_info', {})
        if direction_info:
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
                text="【朝向分析】",
                theme_text_color="Primary",
                font_style="H6",
                size_hint_y=None,
                height=dp(30)
            )
            card_layout.add_widget(title)
            
            content_text = f"卦位：{direction_info.get('gua', '')}\n"
            content_text += f"五行：{direction_info.get('element', '')}\n"
            content_text += f"评分：{direction_info.get('score', 0)}分\n"
            content_text += f"等级：{direction_info.get('level', '')}\n"
            content_text += f"\n描述：{direction_info.get('desc', '')}\n"
            content_text += f"布局建议：{direction_info.get('layout', '')}"
            
            content = MDLabel(
                text=content_text,
                theme_text_color="Secondary",
                font_style="Body1",
                size_hint_y=None,
                height=dp(200)
            )
            card_layout.add_widget(content)
            card.add_widget(card_layout)
            self.result_container.add_widget(card)
        
        # 玄空飞星
        flying_star = data.get('flying_star', {})
        if flying_star:
            star_card = MDCard(
                size_hint_y=None,
                padding=15,
                spacing=10
            )
            star_layout = MDBoxLayout(
                orientation='vertical',
                spacing=10,
                adaptive_height=True
            )
            
            star_title = MDLabel(
                text="【玄空飞星】",
                theme_text_color="Primary",
                font_style="H6",
                size_hint_y=None,
                height=dp(30)
            )
            star_layout.add_widget(star_title)
            
            star_text = flying_star.get('analysis', '')
            star_content = MDLabel(
                text=star_text,
                theme_text_color="Secondary",
                font_style="Body1",
                size_hint_y=None,
                height=dp(100)
            )
            star_layout.add_widget(star_content)
            star_card.add_widget(star_layout)
            self.result_container.add_widget(star_card)
    
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

