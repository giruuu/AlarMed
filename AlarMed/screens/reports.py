"""
AlarMed - Reports Screen
Clean responsive design
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivy.app import App
from datetime import datetime, timedelta

class ReportsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.period_days = 30
        self.build_ui()
    
    def on_enter(self):
        self.refresh_reports()
    
    def build_ui(self):
        app = App.get_running_app()
        
        main_layout = MDBoxLayout(orientation='vertical')
        
        toolbar = MDTopAppBar(
            title="Reports",
            left_action_items=[["arrow-left", lambda x: app.go_to_screen('dashboard')]],
            right_action_items=[["filter-variant", lambda x: self.show_period_menu()]],
            md_bg_color=[0.12, 0.42, 0.65, 1],
            elevation=0
        )
        main_layout.add_widget(toolbar)
        
        self.period_label = MDLabel(
            text=f"Last {self.period_days} days",
            halign='center',
            font_style="Caption",
            size_hint_y=None,
            height=dp(40),
            theme_text_color='Secondary'
        )
        main_layout.add_widget(self.period_label)
        
        scroll = MDScrollView()
        self.reports_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(20),
            size_hint_y=None
        )
        self.reports_layout.bind(minimum_height=self.reports_layout.setter('height'))
        
        scroll.add_widget(self.reports_layout)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
        self.refresh_reports()
    
    def show_period_menu(self):
        period_items = [
            {"text": "Last 7 days", "viewclass": "OneLineListItem", "on_release": lambda: self.set_period(7)},
            {"text": "Last 30 days", "viewclass": "OneLineListItem", "on_release": lambda: self.set_period(30)},
            {"text": "Last 90 days", "viewclass": "OneLineListItem", "on_release": lambda: self.set_period(90)},
            {"text": "All Time", "viewclass": "OneLineListItem", "on_release": lambda: self.set_period(9999)},
        ]
        menu = MDDropdownMenu(items=period_items, width_mult=4)
        menu.open()
    
    def set_period(self, days):
        self.period_days = days
        if days == 9999:
            self.period_label.text = "All Time"
        else:
            self.period_label.text = f"Last {days} days"
        self.refresh_reports()
    
    def refresh_reports(self):
        app = App.get_running_app()
        self.reports_layout.clear_widgets()
        
        if self.period_days == 9999:
            cutoff_date = "1900-01-01"
            days_in_period = 999
        else:
            cutoff_date = (datetime.now() - timedelta(days=self.period_days)).strftime("%Y-%m-%d")
            days_in_period = self.period_days
        
        # Adherence card
        adherence_card = MDCard(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(15),
            size_hint_y=None,
            md_bg_color=[0.1, 0.1, 0.1, 1],
            radius=[15, 15, 15, 15]
        )
        
        adherence_title = MDLabel(
            text="Medication Adherence",
            font_style="H6",
            size_hint_y=None,
            height=dp(30)
        )
        adherence_card.add_widget(adherence_title)
        
        completed_days = app.db.get_adherence_stats(app.current_profile_id, cutoff_date)
        
        if self.period_days == 9999:
            records = app.db.get_medicine_records(app.current_profile_id)
            if records:
                first_date = min([r[5] for r in records])
                days_in_period = (datetime.now() - datetime.strptime(first_date, "%Y-%m-%d")).days + 1
            else:
                days_in_period = 0
        
        missed_days = max(0, days_in_period - completed_days)
        adherence_rate = (completed_days / days_in_period * 100) if days_in_period > 0 else 0
        
        stats_grid = MDGridLayout(
            cols=3,
            spacing=dp(15),
            size_hint_y=None,
            height=dp(120)
        )
        
        def stat_box(title, value):
            box = MDBoxLayout(orientation='vertical', padding=dp(5))
            box.add_widget(MDLabel(text=title, font_style="Caption", halign='center'))
            box.add_widget(MDLabel(text=value, font_style="H5", halign='center'))
            return box
        
        stats_grid.add_widget(stat_box("Days with Records", str(completed_days)))
        stats_grid.add_widget(stat_box("Days without Records", str(missed_days)))
        stats_grid.add_widget(stat_box("Adherence Rate", f"{adherence_rate:.1f}%"))
        
        adherence_card.add_widget(stats_grid)
        adherence_card.height = dp(190)
        self.reports_layout.add_widget(adherence_card)
        
        # Most taken medicines
        top_card = MDCard(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(10),
            size_hint_y=None,
            md_bg_color=[0.1, 0.1, 0.1, 1],
            radius=[15, 15, 15, 15]
        )
        
        top_title = MDLabel(
            text="Most Taken Medicines",
            font_style="H6",
            size_hint_y=None,
            height=dp(30)
        )
        top_card.add_widget(top_title)
        
        top_medicines = app.db.get_most_taken_medicines(app.current_profile_id, cutoff_date)
        
        if top_medicines:
            max_count = top_medicines[0][1]
            for medicine, count in top_medicines:
                row = MDBoxLayout(orientation='vertical', size_hint_y=None, height=dp(55), spacing=dp(5))
                
                line = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(25))
                line.add_widget(MDLabel(text=medicine, size_hint_x=0.7))
                line.add_widget(MDLabel(text=f"{count} times", halign='right', theme_text_color='Secondary', size_hint_x=0.3))
                row.add_widget(line)
                
                progress_bg = MDBoxLayout(size_hint_y=None, height=dp(6), md_bg_color=[0.2, 0.2, 0.2, 1])
                width = (count / max_count) if max_count > 0 else 0
                progress = MDBoxLayout(size_hint=(width, 1), md_bg_color=[0.12, 0.42, 0.65, 1])
                progress_bg.add_widget(progress)
                row.add_widget(progress_bg)
                
                top_card.add_widget(row)
            
            top_card.height = dp(80 + len(top_medicines) * 60)
        else:
            top_card.add_widget(MDLabel(
                text="No records in this period",
                halign='center',
                theme_text_color='Secondary',
                size_hint_y=None,
                height=dp(40)
            ))
            top_card.height = dp(130)
        
        self.reports_layout.add_widget(top_card)
        
        # Total stats
        total_card = MDCard(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(10),
            size_hint_y=None,
            md_bg_color=[0.1, 0.1, 0.1, 1],
            radius=[15, 15, 15, 15]
        )
        
        total_title = MDLabel(
            text="Overall Statistics",
            font_style="H6",
            size_hint_y=None,
            height=dp(30)
        )
        total_card.add_widget(total_title)
        
        total_records = app.db.get_total_records(app.current_profile_id, cutoff_date)
        unique_medicines = app.db.get_unique_medicines(app.current_profile_id, cutoff_date)
        
        grid = MDGridLayout(
            cols=2,
            spacing=dp(15),
            size_hint_y=None,
            height=dp(100)
        )
        
        def small_box(title, value):
            box = MDBoxLayout(orientation='vertical', padding=dp(5))
            box.add_widget(MDLabel(text=title, font_style="Caption", halign='center'))
            box.add_widget(MDLabel(text=value, font_style="H5", halign='center'))
            return box
        
        grid.add_widget(small_box("Total Medications", str(total_records)))
        grid.add_widget(small_box("Unique Medicines", str(unique_medicines)))
        
        total_card.add_widget(grid)
        total_card.height = dp(170)
        self.reports_layout.add_widget(total_card)
