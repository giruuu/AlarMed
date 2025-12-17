"""
AlarMed - Record Medicine Screen
Clean responsive design
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
from kivy.app import App
from datetime import datetime

from config import COMMON_DOSAGES, TIME_PRESETS
from utils import time_to_24h

class RecordMedicineScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()
        self.selected_time = datetime.now().strftime("%I:%M %p")
    
    def build_ui(self):
        """Build clean record UI"""
        app = App.get_running_app()
        
        main_layout = MDBoxLayout(orientation='vertical')
        
        # Top app bar
        toolbar = MDTopAppBar(
            title="Log Medicine",
            left_action_items=[["arrow-left", lambda x: app.go_to_screen('dashboard')]],
            md_bg_color=[0.12, 0.42, 0.65, 1],
            elevation=0
        )
        main_layout.add_widget(toolbar)
        
        # Scroll view
        scroll = MDScrollView()
        content = MDBoxLayout(
            orientation='vertical',
            spacing=dp(20),
            padding=dp(20),
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter('height'))
        
        # Section label
        section_label = MDLabel(
            text="Medicine Information",
            font_style="H6",
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(section_label)
        
        # Medicine name
        self.medicine_field = MDTextField(
            hint_text="Medicine Name",
            required=True,
            size_hint_y=None,
            height=dp(56),
            mode="rectangle"
        )
        content.add_widget(self.medicine_field)
        
        # Recent medicines
        recent_meds = app.db.get_recent_medicines(app.current_profile_id, limit=3)
        if recent_meds:
            recent_label = MDLabel(
                text="Recent:",
                font_style="Caption",
                theme_text_color='Secondary',
                size_hint_y=None,
                height=dp(25)
            )
            content.add_widget(recent_label)
            
            recent_grid = MDGridLayout(
                cols=1,
                spacing=dp(8),
                size_hint_y=None,
                height=dp(len(recent_meds) * 48)
            )
            
            for med_name, dosage in recent_meds:
                suggest_btn = MDFlatButton(
                    text=f"{med_name} - {dosage or ''}",
                    size_hint_y=None,
                    height=dp(40),
                    on_release=lambda x, m=med_name, d=dosage: self.autofill(m, d)
                )
                recent_grid.add_widget(suggest_btn)
            
            content.add_widget(recent_grid)
        
        # Dosage
        self.dosage_field = MDTextField(
            hint_text="Dosage",
            required=True,
            size_hint_y=None,
            height=dp(56),
            mode="rectangle"
        )
        content.add_widget(self.dosage_field)
        
        # Dosage presets
        dosage_label = MDLabel(
            text="Quick Select:",
            font_style="Caption",
            theme_text_color='Secondary',
            size_hint_y=None,
            height=dp(25)
        )
        content.add_widget(dosage_label)
        
        dosage_grid = MDGridLayout(
            cols=3,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(130)
        )
        
        for dosage in COMMON_DOSAGES:
            btn = MDRaisedButton(
                text=dosage,
                size_hint_y=None,
                height=dp(40),
                md_bg_color=[0.15, 0.15, 0.15, 1],
                on_release=lambda x, d=dosage: setattr(self.dosage_field, 'text', d)
            )
            dosage_grid.add_widget(btn)
        
        content.add_widget(dosage_grid)
        
        # Time section
        time_label = MDLabel(
            text="Time Taken",
            font_style="H6",
            size_hint_y=None,
            height=dp(40)
        )
        content.add_widget(time_label)
        
        # Time input
        time_input_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(56)
        )
        
        self.hour_field = MDTextField(
            hint_text="HH",
            text=datetime.now().strftime("%I"),
            input_filter='int',
            size_hint_x=0.3,
            mode="rectangle"
        )
        time_input_layout.add_widget(self.hour_field)
        
        colon_label = MDLabel(
            text=":",
            font_style="H5",
            halign='center',
            size_hint_x=0.1
        )
        time_input_layout.add_widget(colon_label)
        
        self.minute_field = MDTextField(
            hint_text="MM",
            text=datetime.now().strftime("%M"),
            input_filter='int',
            size_hint_x=0.3,
            mode="rectangle"
        )
        time_input_layout.add_widget(self.minute_field)
        
        self.ampm_field = MDTextField(
            hint_text="AM/PM",
            text=datetime.now().strftime("%p"),
            size_hint_x=0.3,
            mode="rectangle"
        )
        time_input_layout.add_widget(self.ampm_field)
        
        content.add_widget(time_input_layout)
        
        # Time presets
        preset_label = MDLabel(
            text="Quick Select:",
            font_style="Caption",
            theme_text_color='Secondary',
            size_hint_y=None,
            height=dp(25)
        )
        content.add_widget(preset_label)
        
        time_grid = MDGridLayout(
            cols=2,
            spacing=dp(10),
            size_hint_y=None,
            height=dp(160)
        )
        
        for label, time_val in TIME_PRESETS.items():
            btn = MDFlatButton(
                text=label,
                size_hint_y=None,
                height=dp(48),
                on_release=lambda x, t=time_val: self.set_time(t)
            )
            time_grid.add_widget(btn)
        
        content.add_widget(time_grid)
        
        # Notes
        notes_label = MDLabel(
            text="Notes (Optional)",
            font_style="Subtitle2",
            size_hint_y=None,
            height=dp(30)
        )
        content.add_widget(notes_label)
        
        self.notes_field = MDTextField(
            hint_text="Add notes...",
            multiline=True,
            size_hint_y=None,
            height=dp(100),
            mode="rectangle"
        )
        content.add_widget(self.notes_field)
        
        # Save button
        save_btn = MDRaisedButton(
            text="SAVE MEDICINE LOG",
            size_hint=(1, None),
            height=dp(56),
            md_bg_color=[0.18, 0.65, 0.45, 1],
            on_release=lambda x: self.save_record()
        )
        content.add_widget(save_btn)
        
        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        
        self.add_widget(main_layout)
    
    def autofill(self, medicine, dosage):
        """Autofill fields"""
        self.medicine_field.text = medicine
        if dosage:
            self.dosage_field.text = dosage
    
    def set_time(self, time_str):
        """Set time from preset"""
        try:
            time_obj = datetime.strptime(time_str, "%I:%M %p")
            self.hour_field.text = time_obj.strftime("%I")
            self.minute_field.text = time_obj.strftime("%M")
            self.ampm_field.text = time_obj.strftime("%p")
        except:
            pass
    
    def save_record(self):
        """Save medicine record"""
        app = App.get_running_app()
        
        medicine = self.medicine_field.text.strip()
        dosage = self.dosage_field.text.strip()
        hour = self.hour_field.text.strip().zfill(2)
        minute = self.minute_field.text.strip().zfill(2)
        ampm = self.ampm_field.text.strip().upper()
        notes = self.notes_field.text.strip()
        
        if not medicine or not dosage or not hour or not minute:
            dialog = MDDialog(
                title="Missing Information",
                text="Please fill in medicine name, dosage, and time.",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: dialog.dismiss()
                    )
                ]
            )
            dialog.open()
            return
        
        try:
            time_str = f"{hour}:{minute} {ampm}"
            time_24 = time_to_24h(time_str)
            date_taken = datetime.now().strftime("%Y-%m-%d")
            
            app.db.add_medicine_record(
                app.current_profile_id,
                medicine,
                dosage,
                time_24,
                date_taken,
                notes
            )
            
            app.db.update_medicine_library(
                app.current_profile_id,
                medicine,
                dosage,
                date_taken
            )
            
            dialog = MDDialog(
                title="Success",
                text="Medicine logged successfully!",
                buttons=[
                    MDRaisedButton(
                        text="OK",
                        on_release=lambda x: (dialog.dismiss(), app.go_to_screen('dashboard'))
                    )
                ]
            )
            dialog.open()
            
            # Clear form
            self.medicine_field.text = ""
            self.dosage_field.text = ""
            self.notes_field.text = ""
            self.hour_field.text = datetime.now().strftime("%I")
            self.minute_field.text = datetime.now().strftime("%M")
            self.ampm_field.text = datetime.now().strftime("%p")
            
        except Exception as e:
            dialog = MDDialog(
                title="Error",
                text=f"Failed to save: {str(e)}",
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: dialog.dismiss()
                    )
                ]
            )
            dialog.open()
