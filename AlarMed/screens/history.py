"""
AlarMed - History Screen
Clean responsive design
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivy.app import App
from datetime import datetime, timedelta

from utils import time_to_ampm

class HistoryScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.filter_days = 30
        self.build_ui()
    
    def on_enter(self):
        """Refresh when entering"""
        self.refresh_history()
    
    def build_ui(self):
        """Build clean history UI"""
        app = App.get_running_app()
        
        main_layout = MDBoxLayout(orientation='vertical')
        
        # Top app bar
        toolbar = MDTopAppBar(
            title="History",
            left_action_items=[["arrow-left", lambda x: app.go_to_screen('dashboard')]],
            right_action_items=[["filter-variant", lambda x: self.show_filter_menu()]],
            md_bg_color=[0.12, 0.42, 0.65, 1],
            elevation=0
        )
        main_layout.add_widget(toolbar)
        
        # Filter label
        self.filter_label = MDLabel(
            text=f"Last {self.filter_days} days",
            halign='center',
            font_style="Caption",
            size_hint_y=None,
            height=dp(40),
            theme_text_color='Secondary'
        )
        main_layout.add_widget(self.filter_label)
        
        # Scroll view
        scroll = MDScrollView()
        self.history_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(20),
            size_hint_y=None
        )
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        
        scroll.add_widget(self.history_layout)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
        self.refresh_history()
    
    def show_filter_menu(self):
        """Show filter menu"""
        filter_items = [
            {
                "text": "Last 7 days",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.set_filter(7)
            },
            {
                "text": "Last 14 days",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.set_filter(14)
            },
            {
                "text": "Last 30 days",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.set_filter(30)
            },
            {
                "text": "Last 90 days",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.set_filter(90)
            },
            {
                "text": "All Time",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.set_filter(9999)
            }
        ]
        
        menu = MDDropdownMenu(
            items=filter_items,
            width_mult=4
        )
        menu.open()
    
    def set_filter(self, days):
        """Set filter days"""
        self.filter_days = days
        if days == 9999:
            self.filter_label.text = "All Time"
        else:
            self.filter_label.text = f"Last {days} days"
        self.refresh_history()
    
    def refresh_history(self):
        """Refresh history display"""
        app = App.get_running_app()
        self.history_layout.clear_widgets()
        
        if self.filter_days == 9999:
            records = app.db.get_medicine_records(app.current_profile_id)
        else:
            cutoff_date = (datetime.now() - timedelta(days=self.filter_days)).strftime("%Y-%m-%d")
            records = app.db.get_medicine_records(app.current_profile_id, cutoff_date)
        
        if not records:
            empty_card = MDCard(
                orientation='vertical',
                padding=dp(30),
                size_hint_y=None,
                height=dp(150),
                md_bg_color=[0.1, 0.1, 0.1, 1],
                radius=[15, 15, 15, 15]
            )
            
            empty_label = MDLabel(
                text="No medication records found",
                halign='center',
                theme_text_color='Secondary',
                font_style="Body2"
            )
            empty_card.add_widget(empty_label)
            self.history_layout.add_widget(empty_card)
            return
        
        # Group by date
        records_by_date = {}
        for record in records:
            date = record[5]
            if date not in records_by_date:
                records_by_date[date] = []
            records_by_date[date].append(record)
        
        # Display
        for date in sorted(records_by_date.keys(), reverse=True):
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            date_display = date_obj.strftime("%A, %B %d, %Y")
            is_today = date == datetime.now().strftime("%Y-%m-%d")
            
            # Date card
            date_card = MDCard(
                orientation='vertical',
                padding=dp(20),
                spacing=dp(15),
                size_hint_y=None,
                md_bg_color=[0.12, 0.42, 0.65, 1] if is_today else [0.1, 0.1, 0.1, 1],
                radius=[15, 15, 15, 15]
            )
            
            date_text = date_display
            if is_today:
                date_text += " (Today)"
            
            date_label = MDLabel(
                text=date_text,
                font_style="Subtitle1",
                bold=True,
                size_hint_y=None,
                height=dp(30)
            )
            date_card.add_widget(date_label)
            
            # Records for this date
            for record in records_by_date[date]:
                record_id, profile_id, medicine, dosage, time_taken, date_taken, notes, completed, created_at = record
                
                record_box = MDBoxLayout(
                    orientation='vertical',
                    size_hint_y=None,
                    padding=[0, dp(10)],
                    spacing=dp(8)
                )
                
                time_ampm = time_to_ampm(time_taken)
                
                time_label = MDLabel(
                    text=time_ampm,
                    font_style="Caption",
                    theme_text_color='Secondary',
                    size_hint_y=None,
                    height=dp(20)
                )
                record_box.add_widget(time_label)
                
                med_label = MDLabel(
                    text=f"{medicine} - {dosage}",
                    font_style="Body1",
                    size_hint_y=None,
                    height=dp(25)
                )
                record_box.add_widget(med_label)
                
                if notes:
                    notes_label = MDLabel(
                        text=notes,
                        font_style="Caption",
                        theme_text_color='Secondary',
                        size_hint_y=None
                    )
                    notes_label.bind(texture_size=notes_label.setter('size'))
                    record_box.add_widget(notes_label)
                
                # Divider
                divider = MDBoxLayout(
                    size_hint_y=None,
                    height=dp(1),
                    md_bg_color=[0.2, 0.2, 0.2, 1]
                )
                record_box.add_widget(divider)
                
                record_box.bind(minimum_height=record_box.setter('height'))
                date_card.add_widget(record_box)
            
            date_card.bind(minimum_height=date_card.setter('height'))
            self.history_layout.add_widget(date_card)
