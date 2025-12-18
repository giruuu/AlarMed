"""
AlarMed - Dashboard Screen
Clean responsive design
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.toolbar import MDTopAppBar
from kivy.metrics import dp
from kivy.app import App
from datetime import datetime

from utils import (
    get_greeting,
    calculate_streak,
    get_upcoming_doses_from_reminders,
    time_to_ampm,
)


class DashboardScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def on_enter(self):
        self.refresh_dashboard()

    def build_ui(self):
        app = App.get_running_app()
        main_layout = MDBoxLayout(orientation="vertical")

        toolbar = MDTopAppBar(
            title="Dashboard",
            left_action_items=[["arrow-left", lambda x: app.switch_profile()]],
            md_bg_color=[0.12, 0.42, 0.65, 1],
            elevation=0,
        )
        main_layout.add_widget(toolbar)

        scroll = MDScrollView()
        self.content_layout = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            padding=dp(20),
            size_hint_y=None,
        )
        self.content_layout.bind(minimum_height=self.content_layout.setter("height"))
        scroll.add_widget(self.content_layout)
        main_layout.add_widget(scroll)

        nav_layout = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(60),
            md_bg_color=[0.08, 0.08, 0.08, 1],
            padding=dp(10),
            spacing=dp(5),
        )

        nav_buttons = [
            ("Dashboard", "dashboard"),
            ("Record", "record"),
            ("Reminders", "reminders"),
            ("History", "history"),
        ]

        for text, screen in nav_buttons:
            btn = MDFlatButton(
                text=text,
                size_hint_x=0.25,
                on_release=lambda x, s=screen: app.go_to_screen(s),
            )
            nav_layout.add_widget(btn)

        main_layout.add_widget(nav_layout)
        self.add_widget(main_layout)
        self.refresh_dashboard()

    def refresh_dashboard(self):
        app = App.get_running_app()
        self.content_layout.clear_widgets()

        if not app.current_profile_id or not app.current_profile_name:
            placeholder_card = MDCard(
                orientation="vertical",
                padding=dp(25),
                size_hint_y=None,
                height=dp(150),
                md_bg_color=[0.1, 0.1, 0.1, 1],
                radius=[15, 15, 15, 15],
            )
            placeholder_label = MDLabel(
                text="Select or create a profile to view your dashboard.",
                halign="center",
                theme_text_color="Secondary",
                font_style="Body2",
            )
            placeholder_card.add_widget(placeholder_label)
            self.content_layout.add_widget(placeholder_card)
            return

        greeting = get_greeting()
        greeting_card = MDCard(
            orientation="vertical",
            padding=dp(25),
            size_hint_y=None,
            height=dp(120),
            md_bg_color=[0.12, 0.42, 0.65, 1],
            radius=[20, 20, 20, 20],
        )
        greeting_card.add_widget(
            MDLabel(text=greeting, font_style="H5", size_hint_y=None, height=dp(35))
        )
        greeting_card.add_widget(
            MDLabel(
                text=app.current_profile_name,
                font_style="H6",
                size_hint_y=None,
                height=dp(30),
            )
        )
        greeting_card.add_widget(
            MDLabel(
                text=datetime.now().strftime("%A, %B %d, %Y"),
                font_style="Caption",
                theme_text_color="Secondary",
                size_hint_y=None,
                height=dp(20),
            )
        )
        self.content_layout.add_widget(greeting_card)

        today_date_str = datetime.now().strftime("%Y-%m-%d")
        today_count = app.db.get_today_medicine_count(app.current_profile_id, today_date_str)
        reminder_count = app.db.get_active_reminder_count(app.current_profile_id)
        dates = app.db.get_streak_dates(app.current_profile_id)
        streak = calculate_streak(dates)
        reminders = app.db.get_active_reminders(app.current_profile_id)
        upcoming = get_upcoming_doses_from_reminders(reminders)

        stats_grid = MDGridLayout(cols=2, spacing=dp(15), size_hint_y=None, height=dp(200))
        stats = [
            ("Today's Medicines", str(today_count), [0.12, 0.42, 0.65, 1]),
            ("Active Reminders", str(reminder_count), [0.18, 0.65, 0.45, 1]),
            ("Day Streak", f"{streak} days", [0.94, 0.68, 0.31, 1]),
            ("Upcoming", str(len(upcoming)), [0.85, 0.33, 0.31, 1]),
        ]
        for title, value, color in stats:
            stat_card = MDCard(
                orientation="vertical",
                padding=dp(20),
                md_bg_color=color,
                radius=[15, 15, 15, 15],
            )
            stat_card.add_widget(
                MDLabel(
                    text=value,
                    font_style="H4",
                    halign="center",
                    size_hint_y=None,
                    height=dp(50),
                )
            )
            stat_card.add_widget(
                MDLabel(
                    text=title,
                    font_style="Caption",
                    halign="center",
                    size_hint_y=None,
                    height=dp(20),
                )
            )
            stats_grid.add_widget(stat_card)
        self.content_layout.add_widget(stats_grid)

        self.content_layout.add_widget(
            MDLabel(text="Quick Actions", font_style="H6", size_hint_y=None, height=dp(40))
        )

        quick_actions_grid = MDGridLayout(cols=2, spacing=dp(15), size_hint_y=None, height=dp(330))
        actions = [
            ("Log Medicine", "record", [0.12, 0.42, 0.65, 1]),
            ("Add Reminder", "reminders", [0.18, 0.65, 0.45, 1]),
            ("View History", "history", [0.94, 0.68, 0.31, 1]),
            ("View Reports", "reports", [0.85, 0.33, 0.31, 1]),
            ("Backup & Restore", "backup", [0.35, 0.35, 0.35, 1]),
        ]

        for text, screen, color in actions:
            action_btn = MDRaisedButton(
                text=text.upper(),
                size_hint_y=None,
                height=dp(90),
                md_bg_color=color,
                on_release=lambda x, s=screen: app.go_to_screen(s),
            )
            quick_actions_grid.add_widget(action_btn)

        self.content_layout.add_widget(quick_actions_grid)

        self.content_layout.add_widget(
            MDLabel(text="Upcoming Doses", font_style="H6", size_hint_y=None, height=dp(40))
        )

        upcoming_card = MDCard(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(10),
            size_hint_y=None,
            md_bg_color=[0.1, 0.1, 0.1, 1],
            radius=[15, 15, 15, 15],
        )

        if upcoming:
            for med_name, dose, time_str in upcoming[:5]:
                dose_layout = MDBoxLayout(
                    orientation="vertical",
                    size_hint_y=None,
                    height=dp(70),
                    spacing=dp(8),
                )
                dose_layout.add_widget(
                    MDLabel(
                        text=time_to_ampm(time_str),
                        font_style="Caption",
                        theme_text_color="Secondary",
                    )
                )
                dose_layout.add_widget(MDLabel(text=f"{med_name} - {dose}", font_style="Body1"))
                dose_layout.add_widget(
                    MDBoxLayout(size_hint_y=None, height=dp(1), md_bg_color=[0.2, 0.2, 0.2, 1])
                )
                upcoming_card.add_widget(dose_layout)
            upcoming_card.height = dp(30 + len(upcoming[:5]) * 80)
        else:
            upcoming_card.add_widget(
                MDLabel(
                    text="No upcoming doses today",
                    halign="center",
                    theme_text_color="Secondary",
                    font_style="Body2",
                )
            )
            upcoming_card.height = dp(100)

        self.content_layout.add_widget(upcoming_card)
