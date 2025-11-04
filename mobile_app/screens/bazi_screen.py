#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
八字算命界面 - 移动端（整合版）
一个界面显示所有分析结果：八字、神煞、财运、婚姻、职业等
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.chip import MDChip
from kivy.metrics import dp
from datetime import datetime


class BaziScreen(MDScreen):
    """八字算命界面（整合所有分析结果）"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'bazi'
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
            text="八字算命",
            halign="center",
            theme_text_color="Primary",
            font_style="H4",
            size_hint_y=None,
            height=dp(48)
        )
        layout.add_widget(title)
        
        # 输入表单区域
        input_card = MDCard(
            size_hint_y=None,
            padding=15,
            spacing=10
        )
        input_layout = MDBoxLayout(
            orientation='vertical',
            spacing=10,
            adaptive_height=True
        )
        
        # 姓名
        self.name_input = MDTextField(
            hint_text="姓名（可选）",
            size_hint_y=None,
            height=dp(48)
        )
        input_layout.add_widget(self.name_input)
        
        # 性别选择
        gender_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint_y=None,
            height=dp(48)
        )
        gender_label = MDLabel(
            text="性别：",
            size_hint_x=None,
            width=dp(80)
        )
        self.gender_male = MDRaisedButton(
            text="男",
            size_hint_x=0.5
        )
        self.gender_male.bind(on_press=lambda x: self.set_gender('male'))
        self.gender_female = MDFlatButton(
            text="女",
            size_hint_x=0.5
        )
        self.gender_female.bind(on_press=lambda x: self.set_gender('female'))
        self.selected_gender = 'male'
        
        gender_layout.add_widget(gender_label)
        gender_layout.add_widget(self.gender_male)
        gender_layout.add_widget(self.gender_female)
        input_layout.add_widget(gender_layout)
        
        # 出生日期
        self.birth_year = MDTextField(
            hint_text="出生年份（如：1990）",
            input_filter='int',
            size_hint_y=None,
            height=dp(48)
        )
        input_layout.add_widget(self.birth_year)
        
        self.birth_month = MDTextField(
            hint_text="出生月份（1-12）",
            input_filter='int',
            size_hint_y=None,
            height=dp(48)
        )
        input_layout.add_widget(self.birth_month)
        
        self.birth_day = MDTextField(
            hint_text="出生日期（1-31）",
            input_filter='int',
            size_hint_y=None,
            height=dp(48)
        )
        input_layout.add_widget(self.birth_day)
        
        self.birth_hour = MDTextField(
            hint_text="出生时辰（0-23）",
            input_filter='int',
            size_hint_y=None,
            height=dp(48)
        )
        input_layout.add_widget(self.birth_hour)
        
        # 出生地（可选）
        self.birth_location = MDTextField(
            hint_text="出生地（可选，用于真太阳时修正）",
            size_hint_y=None,
            height=dp(48)
        )
        input_layout.add_widget(self.birth_location)
        
        # 计算按钮
        calc_btn = MDRaisedButton(
            text="开始计算",
            size_hint_y=None,
            height=dp(48)
        )
        calc_btn.bind(on_press=self.calculate_all)
        input_layout.add_widget(calc_btn)
        
        input_card.add_widget(input_layout)
        layout.add_widget(input_card)
        
        # 结果显示区域（可滚动）
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
    
    def set_gender(self, gender):
        """设置性别"""
        self.selected_gender = gender
        if gender == 'male':
            self.gender_male.md_bg_color = self.theme_cls.primary_color
            self.gender_female.md_bg_color = [0, 0, 0, 0]
        else:
            self.gender_female.md_bg_color = self.theme_cls.primary_color
            self.gender_male.md_bg_color = [0, 0, 0, 0]
    
    def calculate_all(self, instance):
        """计算所有分析结果"""
        try:
            # 获取输入
            year = int(self.birth_year.text) if self.birth_year.text else None
            month = int(self.birth_month.text) if self.birth_month.text else None
            day = int(self.birth_day.text) if self.birth_day.text else None
            hour = int(self.birth_hour.text) if self.birth_hour.text else None
            
            if not all([year, month, day, hour is not None]):
                self.show_error("请填写完整的出生信息")
                return
            
            # 清空之前的结果
            self.result_container.clear_widgets()
            
            # 显示加载提示
            loading_card = MDCard(
                size_hint_y=None,
                height=dp(80),
                padding=15
            )
            loading_label = MDLabel(
                text="正在计算，请稍候...",
                halign="center",
                theme_text_color="Primary"
            )
            loading_card.add_widget(loading_label)
            self.result_container.add_widget(loading_card)
            
            # 1. 计算八字
            from mobile_app.services.bazi_service import BaziService
            bazi_service = BaziService()
            bazi_result = bazi_service.calculate(
                year=year,
                month=month,
                day=day,
                hour=hour,
                gender=self.selected_gender,
                location=self.birth_location.text or None
            )
            
            if not bazi_result or 'error' in bazi_result:
                self.show_error("八字计算失败，请检查输入信息")
                return
            
            # 保存结果到应用
            app = self.get_running_app()
            if app:
                app.current_bazi_result = bazi_result
                # 自动保存（如果启用）
                if hasattr(app, 'storage'):
                    settings = app.storage.load_settings()
                    if settings.get('auto_save', True):
                        name = self.name_input.text or '未命名'
                        app.storage.save_bazi_result(bazi_result, name)
            
            # 清空加载提示
            self.result_container.clear_widgets()
            
            # 2. 显示八字结果
            self.display_bazi_result(bazi_result)
            
            # 3. 提取四柱信息用于后续分析
            if 'sizhu' in bazi_result:
                sizhu = bazi_result['sizhu']
                pillars = {
                    'year': (sizhu.get('year_gan', ''), sizhu.get('year_zhi', '')),
                    'month': (sizhu.get('month_gan', ''), sizhu.get('month_zhi', '')),
                    'day': (sizhu.get('day_gan', ''), sizhu.get('day_zhi', '')),
                    'hour': (sizhu.get('hour_gan', ''), sizhu.get('hour_zhi', ''))
                }
                day_master = sizhu.get('day_gan', '')
                birth_info = {'gender': '男' if self.selected_gender == 'male' else '女'}
                
                # 4. 神煞分析
                self.display_shensha(pillars, birth_info)
                
                # 5. 财运分析
                self.display_caiyun(pillars, day_master)
                
                # 6. 婚姻分析
                self.display_hunyin(pillars, day_master, birth_info)
                
                # 7. 职业分析
                self.display_zhiye(pillars, day_master, birth_info)
                
        except Exception as e:
            self.show_error(f"计算出错：{str(e)}")
    
    def display_bazi_result(self, result):
        """显示八字计算结果"""
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
            text="【八字结果】",
            theme_text_color="Primary",
            font_style="H6",
            size_hint_y=None,
            height=dp(30)
        )
        card_layout.add_widget(title)
        
        if 'sizhu' in result:
            sizhu = result['sizhu']
            sizhu_text = f"年柱：{sizhu.get('year', '')}\n"
            sizhu_text += f"月柱：{sizhu.get('month', '')}\n"
            sizhu_text += f"日柱：{sizhu.get('day', '')}\n"
            sizhu_text += f"时柱：{sizhu.get('hour', '')}"
        else:
            sizhu_text = "无法获取四柱信息"
        
        content = MDLabel(
            text=sizhu_text,
            theme_text_color="Secondary",
            font_style="Body1",
            size_hint_y=None,
            height=dp(100)
        )
        card_layout.add_widget(content)
        card.add_widget(card_layout)
        self.result_container.add_widget(card)
    
    def display_shensha(self, pillars, birth_info):
        """显示神煞分析"""
        try:
            from mobile_app.services.analysis_service import AnalysisService
            service = AnalysisService()
            result = service.analyze_shensha(pillars, birth_info)
            
            if not result.get('success'):
                return
            
            data = result['data']
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
                text="【神煞分析】",
                theme_text_color="Primary",
                font_style="H6",
                size_hint_y=None,
                height=dp(30)
            )
            card_layout.add_widget(title)
            
            # 总体评价
            level = data.get('level', '未知')
            level_label = MDLabel(
                text=f"总体评价：{level}",
                theme_text_color="Secondary",
                font_style="Body1",
                size_hint_y=None,
                height=dp(40)
            )
            card_layout.add_widget(level_label)
            
            # 吉神
            ji_sha = data.get('ji_sha', [])
            if ji_sha:
                ji_label = MDLabel(
                    text="吉神：",
                    theme_text_color="Secondary",
                    font_style="Body2",
                    size_hint_y=None,
                    height=dp(25)
                )
                card_layout.add_widget(ji_label)
                ji_chips = MDBoxLayout(
                    orientation='horizontal',
                    spacing=5,
                    adaptive_height=True
                )
                for sha in ji_sha[:8]:  # 最多显示8个
                    name = sha.get('name', '')
                    chip = MDChip(
                        text=name,
                        color=[0, 1, 0, 0.3]
                    )
                    ji_chips.add_widget(chip)
                card_layout.add_widget(ji_chips)
            
            # 凶煞
            xiong_sha = data.get('xiong_sha', [])
            if xiong_sha:
                xiong_label = MDLabel(
                    text="凶煞：",
                    theme_text_color="Secondary",
                    font_style="Body2",
                    size_hint_y=None,
                    height=dp(25)
                )
                card_layout.add_widget(xiong_label)
                xiong_chips = MDBoxLayout(
                    orientation='horizontal',
                    spacing=5,
                    adaptive_height=True
                )
                for sha in xiong_sha[:8]:  # 最多显示8个
                    name = sha.get('name', '')
                    chip = MDChip(
                        text=name,
                        color=[1, 0, 0, 0.3]
                    )
                    xiong_chips.add_widget(chip)
                card_layout.add_widget(xiong_chips)
            
            card.add_widget(card_layout)
            self.result_container.add_widget(card)
        except Exception as e:
            print(f"神煞分析出错：{e}")
    
    def display_caiyun(self, pillars, day_master):
        """显示财运分析"""
        try:
            from mobile_app.services.analysis_service import AnalysisService
            service = AnalysisService()
            result = service.analyze_caiyun(pillars, day_master)
            
            if not result.get('success'):
                return
            
            data = result['data']
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
                text="【财运分析】",
                theme_text_color="Primary",
                font_style="H6",
                size_hint_y=None,
                height=dp(30)
            )
            card_layout.add_widget(title)
            
            status = data.get('caiyun_status', '未知')
            desc = data.get('description', '')
            
            content = MDLabel(
                text=f"财运状态：{status}\n\n{desc}",
                theme_text_color="Secondary",
                font_style="Body1",
                size_hint_y=None,
                height=dp(120)
            )
            card_layout.add_widget(content)
            card.add_widget(card_layout)
            self.result_container.add_widget(card)
        except Exception as e:
            print(f"财运分析出错：{e}")
    
    def display_hunyin(self, pillars, day_master, birth_info):
        """显示婚姻分析"""
        try:
            from mobile_app.services.analysis_service import AnalysisService
            service = AnalysisService()
            gender = '男' if birth_info.get('gender', '男') == '男' else '女'
            result = service.analyze_marriage(pillars, day_master, gender, birth_info)
            
            if not result.get('success'):
                return
            
            data = result['data']
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
                text="【婚姻分析】",
                theme_text_color="Primary",
                font_style="H6",
                size_hint_y=None,
                height=dp(30)
            )
            card_layout.add_widget(title)
            
            quality = data.get('quality', '未知')
            summary = data.get('summary', '')
            
            content = MDLabel(
                text=f"婚姻质量：{quality}\n\n{summary}",
                theme_text_color="Secondary",
                font_style="Body1",
                size_hint_y=None,
                height=dp(120)
            )
            card_layout.add_widget(content)
            card.add_widget(card_layout)
            self.result_container.add_widget(card)
        except Exception as e:
            print(f"婚姻分析出错：{e}")
    
    def display_zhiye(self, pillars, day_master, birth_info):
        """显示职业分析"""
        try:
            from mobile_app.services.analysis_service import AnalysisService
            service = AnalysisService()
            gender = '男' if birth_info.get('gender', '男') == '男' else '女'
            result = service.analyze_career(pillars, day_master, gender, birth_info)
            
            if not result.get('success'):
                return
            
            data = result['data']
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
                text="【职业分析】",
                theme_text_color="Primary",
                font_style="H6",
                size_hint_y=None,
                height=dp(30)
            )
            card_layout.add_widget(title)
            
            summary = data.get('summary', '暂无分析结果')
            
            content = MDLabel(
                text=summary,
                theme_text_color="Secondary",
                font_style="Body1",
                size_hint_y=None,
                height=dp(120)
            )
            card_layout.add_widget(content)
            card.add_widget(card_layout)
            self.result_container.add_widget(card)
        except Exception as e:
            print(f"职业分析出错：{e}")
    
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
