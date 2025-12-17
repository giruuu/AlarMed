"""
AlarMed - Backup & Restore Screen
Clean responsive design
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
from kivy.app import App
from datetime import datetime
import shutil
from pathlib import Path
import sqlite3

try:
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path
    ANDROID = True
except ImportError:
    ANDROID = False

class BackupScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
    
    def build_ui(self):
        app = App.get_running_app()
        
        main_layout = MDBoxLayout(orientation='vertical')
        
        toolbar = MDTopAppBar(
            title="Backup & Restore",
            left_action_items=[["arrow-left", lambda x: app.go_to_screen('dashboard')]],
            md_bg_color=[0.12, 0.42, 0.65, 1],
            elevation=0
        )
        main_layout.add_widget(toolbar)
        
        scroll = MDScrollView()
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(20),
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter('height'))
        
        # Backup card
        backup_card = MDCard(
            orientation='vertical',
            padding=dp(25),
            spacing=dp(15),
            size_hint_y=None,
            md_bg_color=[0.1, 0.1, 0.1, 1],
            radius=[15, 15, 15, 15]
        )
        
        backup_title = MDLabel(
            text="Create Backup",
            font_style="H6",
            size_hint_y=None,
            height=dp(35)
        )
        backup_card.add_widget(backup_title)
        
        backup_desc = MDLabel(
            text="Save all your data to a backup file",
            theme_text_color='Secondary',
            font_style="Body2",
            size_hint_y=None,
            height=dp(25)
        )
        backup_card.add_widget(backup_desc)
        
        included_card = MDCard(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(8),
            size_hint_y=None,
            md_bg_color=[0.15, 0.15, 0.15, 1],
            radius=[10, 10, 10, 10]
        )
        
        included_items = [
            "All medication records",
            "All reminders",
            "Emergency contacts",
            "Medicine library",
            "All user profiles"
        ]
        
        for item in included_items:
            item_label = MDLabel(
                text=item,
                font_style="Caption",
                size_hint_y=None,
                height=dp(25)
            )
            included_card.add_widget(item_label)
        
        included_card.height = dp(160)
        backup_card.add_widget(included_card)
        
        backup_btn = MDRaisedButton(
            text="CREATE BACKUP NOW",
            size_hint=(1, None),
            height=dp(56),
            md_bg_color=[0.12, 0.42, 0.65, 1],
            on_release=lambda x: self.create_backup()
        )
        backup_card.add_widget(backup_btn)
        
        backup_card.height = dp(400)
        content.add_widget(backup_card)
        
        # Restore card
        restore_card = MDCard(
            orientation='vertical',
            padding=dp(25),
            spacing=dp(15),
            size_hint_y=None,
            md_bg_color=[0.1, 0.1, 0.1, 1],
            radius=[15, 15, 15, 15]
        )
        
        restore_title = MDLabel(
            text="Restore Backup",
            font_style="H6",
            size_hint_y=None,
            height=dp(35)
        )
        restore_card.add_widget(restore_title)
        
        restore_desc = MDLabel(
            text="Restore data from a backup file",
            theme_text_color='Secondary',
            font_style="Body2",
            size_hint_y=None,
            height=dp(25)
        )
        restore_card.add_widget(restore_desc)
        
        warning_card = MDCard(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(8),
            size_hint_y=None,
            height=dp(90),
            md_bg_color=[0.94, 0.68, 0.31, 1],
            radius=[10, 10, 10, 10]
        )
        
        warning_label = MDLabel(
            text="Warning",
            font_style="Subtitle1",
            bold=True,
            halign='center',
            size_hint_y=None,
            height=dp(25)
        )
        warning_card.add_widget(warning_label)
        
        warning_text = MDLabel(
            text="This will replace ALL current data with data from the backup file",
            halign='center',
            font_style="Caption",
            size_hint_y=None,
            height=dp(50)
        )
        warning_card.add_widget(warning_text)
        
        restore_card.add_widget(warning_card)
        
        restore_btn = MDRaisedButton(
            text="SELECT & RESTORE BACKUP",
            size_hint=(1, None),
            height=dp(56),
            md_bg_color=[0.85, 0.33, 0.31, 1],
            on_release=lambda x: self.restore_backup()
        )
        restore_card.add_widget(restore_btn)
        
        restore_card.height = dp(300)
        content.add_widget(restore_card)
        
        # Info card
        info_card = MDCard(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(10),
            size_hint_y=None,
            md_bg_color=[0.1, 0.1, 0.1, 1],
            radius=[15, 15, 15, 15]
        )
        
        info_title = MDLabel(
            text="Backup Information",
            font_style="Subtitle1",
            bold=True,
            size_hint_y=None,
            height=dp(30)
        )
        info_card.add_widget(info_title)
        
        info_items = [
            "Backups are saved with timestamps",
            "Keep backups safe and secure",
            "Transfer backups to other devices",
            "Regular backups recommended"
        ]
        
        for item in info_items:
            item_label = MDLabel(
                text=item,
                theme_text_color='Secondary',
                font_style="Caption",
                size_hint_y=None,
                height=dp(25)
            )
            info_card.add_widget(item_label)
        
        info_card.height = dp(170)
        content.add_widget(info_card)
        
        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
    
    def create_backup(self):
        app = App.get_running_app()
        
        try:
            if ANDROID:
                backup_dir = Path(primary_external_storage_path()) / "AlarMed" / "backups"
            else:
                backup_dir = Path("backups")
            
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"alarmed_backup_{timestamp}.db"
            
            app.db.conn.close()
            shutil.copy2('alarmed.db', backup_file)
            
            app.db.conn = sqlite3.connect('alarmed.db', check_same_thread=False)
            app.db.cursor = app.db.conn.cursor()
            
            dialog = MDDialog(
                title="Success",
                text=f"Backup created!\n\nFile: {backup_file.name}\nLocation: {backup_dir}",
                buttons=[
                    MDRaisedButton(text="OK", on_release=lambda x: dialog.dismiss())
                ]
            )
            dialog.open()
            
        except Exception as e:
            try:
                app.db.conn = sqlite3.connect('alarmed.db', check_same_thread=False)
                app.db.cursor = app.db.conn.cursor()
            except:
                pass
            
            dialog = MDDialog(
                title="Error",
                text=f"Failed to create backup:\n{str(e)}",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
            )
            dialog.open()
    
    def restore_backup(self):
        dialog = MDDialog(
            title="Restore Backup",
            text="This feature requires manual file selection.\n\nPlace your backup file in the app directory and restart the app.",
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())]
        )
        dialog.open()
