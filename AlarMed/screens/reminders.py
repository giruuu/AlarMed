from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.textfield import MDTextField
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivy.metrics import dp
from kivy.app import App
from kivy.clock import Clock
from datetime import datetime, timedelta

from utils import time_to_24h, time_to_ampm


class RemindersScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reminder_times = []
        self.selected_medicine = None
        self.selected_dosage = None
        self.build_ui()

    def on_enter(self):
        """Refresh when entering"""
        self.refresh_reminders()
        self.load_medicine_buttons()
        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 1), 0.1)

    def build_ui(self):
        """Build clean reminders UI"""
        app = App.get_running_app()
        self.main_layout = MDBoxLayout(orientation="vertical")

        toolbar = MDTopAppBar(
            title="Reminders",
            left_action_items=[["arrow-left", lambda x: app.go_to_screen("dashboard")]],
            md_bg_color=[0.12, 0.42, 0.65, 1],
            elevation=0,
        )
        self.main_layout.add_widget(toolbar)

        self.scroll = MDScrollView()
        self.content = MDBoxLayout(
            orientation="vertical",
            spacing=dp(20),
            padding=dp(20),
            size_hint_y=None,
        )
        self.content.bind(minimum_height=self.content.setter("height"))

        add_card = MDCard(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(20),
            size_hint_y=None,
            md_bg_color=[0.1, 0.1, 0.1, 1],
            radius=[15, 15, 15, 15],
        )
        add_card.height = dp(800)

        add_title = MDLabel(
            text="Add New Reminder",
            font_style="H6",
            size_hint_y=None,
            height=dp(2),
        )
        add_card.add_widget(add_title)

        self.medicine_buttons_container = MDBoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
        )
        add_card.add_widget(self.medicine_buttons_container)

        self.medicine_display_label = MDLabel(
            text="No medicine selected",
            theme_text_color="Secondary",
            font_style="Caption",
            size_hint_y=None,
            height=dp(30),
        )
        add_card.add_widget(self.medicine_display_label)

        self.rem_medicine = MDTextField(
            hint_text="Medicine Name (or use buttons above)",
            size_hint_y=None,
            height=dp(56),
            mode="rectangle",
        )
        add_card.add_widget(self.rem_medicine)

        self.rem_dosage = MDTextField(
            hint_text="Dosage",
            size_hint_y=None,
            height=dp(56),
            mode="rectangle",
        )
        add_card.add_widget(self.rem_dosage)

        schedule_items = [
            {"text": s, "viewclass": "OneLineListItem", "on_release": lambda x=s: self.set_schedule_type(x)}
            for s in ["Daily", "Specific Days", "Every Other Day", "Weekly"]
        ]
        self.schedule_menu = MDDropdownMenu(items=schedule_items, width_mult=4)

        self.schedule_btn = MDRaisedButton(
            text="Schedule: Daily",
            size_hint_y=None,
            height=dp(48),
            md_bg_color=[0.15, 0.15, 0.15, 1],
            on_release=lambda x: self.schedule_menu.open(),
        )
        self.schedule_menu.caller = self.schedule_btn
        add_card.add_widget(self.schedule_btn)

        self.rem_days = MDTextField(
            hint_text="Days (e.g., Mon, Wed, Fri)",
            size_hint_y=None,
            height=dp(56),
            mode="rectangle",
        )
        add_card.add_widget(self.rem_days)

        add_card.add_widget(MDLabel(text="Reminder Times", font_style="Subtitle2", size_hint_y=None, height=dp(30)))

        time_btn = MDRaisedButton(
            text="ADD TIME",
            size_hint_y=None,
            height=dp(48),
            md_bg_color=[0.12, 0.42, 0.65, 1],
            on_release=lambda x: self.show_add_time_dialog(),
        )
        add_card.add_widget(time_btn)

        self.times_label = MDLabel(
            text="No times added yet",
            theme_text_color="Secondary",
            font_style="Caption",
            size_hint_y=None,
            height=dp(40),
        )
        add_card.add_widget(self.times_label)

        clear_times_btn = MDFlatButton(
            text="CLEAR ALL TIMES",
            size_hint_y=None,
            height=dp(40),
            on_release=lambda x: self.clear_times(),
        )
        add_card.add_widget(clear_times_btn)

        save_btn = MDRaisedButton(
            text="CREATE REMINDER",
            size_hint=(1, None),
            height=dp(56),
            md_bg_color=[0.18, 0.65, 0.45, 1],
            on_release=lambda x: self.add_reminder(),
        )
        add_card.add_widget(save_btn)

        self.content.add_widget(add_card)

        self.content.add_widget(MDLabel(text="Active Reminders", font_style="H6", size_hint_y=None, height=dp(50)))

        self.reminders_list = MDBoxLayout(orientation="vertical", spacing=dp(15), size_hint_y=None)
        self.reminders_list.bind(minimum_height=self.reminders_list.setter("height"))
        self.content.add_widget(self.reminders_list)

        self.scroll.add_widget(self.content)
        self.main_layout.add_widget(self.scroll)
        self.add_widget(self.main_layout)

    def load_medicine_buttons(self):
        app = App.get_running_app()
        meds = app.db.get_recent_medicines(app.current_profile_id, limit=20)
        self.medicine_buttons_container.clear_widgets()

        if not meds:
            self.medicine_buttons_container.add_widget(
                MDLabel(
                    text="No medicines found. Log a medicine first.",
                    theme_text_color="Secondary",
                    font_style="Caption",
                    size_hint_y=None,
                    height=dp(30),
                )
            )
            return

        row_layout = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(40))
        for idx, (name, dosage) in enumerate(meds):
            display = f"{name}" if not dosage else f"{name} - {dosage}"
            btn = MDRaisedButton(
                text=display,
                size_hint_x=None,
                width=dp(120),
                md_bg_color=[0.15, 0.15, 0.15, 1],
                on_release=lambda x, n=name, d=dosage: self.select_medicine_quick(n, d),
            )
            row_layout.add_widget(btn)
            if (idx + 1) % 3 == 0:
                self.medicine_buttons_container.add_widget(row_layout)
                row_layout = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(40))
        if len(row_layout.children) > 0:
            self.medicine_buttons_container.add_widget(row_layout)

    def select_medicine_quick(self, name, dosage):
        self.selected_medicine = name
        self.selected_dosage = dosage or ""
        self.medicine_display_label.text = f"{name}" + (f" - {dosage}" if dosage else "")
        self.rem_medicine.text = name
        self.rem_dosage.text = dosage or ""

    def set_schedule_type(self, schedule_type):
        self.schedule_btn.text = f"Schedule: {schedule_type}"
        self.schedule_menu.dismiss()

    def show_add_time_dialog(self):
        content = MDBoxLayout(orientation="vertical", spacing=dp(15), size_hint_y=None, height=dp(120), padding=dp(15))
        time_input_layout = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(56))
        hour_field = MDTextField(hint_text="HH", text=datetime.now().strftime("%I"), input_filter="int", size_hint_x=0.3, mode="rectangle")
        minute_field = MDTextField(hint_text="MM", text=datetime.now().strftime("%M"), input_filter="int", size_hint_x=0.3, mode="rectangle")
        ampm_field = MDTextField(hint_text="AM/PM", text=datetime.now().strftime("%p"), size_hint_x=0.3, mode="rectangle")
        colon = MDLabel(text=":", font_style="H5", halign="center", size_hint_x=0.1)
        time_input_layout.add_widget(hour_field)
        time_input_layout.add_widget(colon)
        time_input_layout.add_widget(minute_field)
        time_input_layout.add_widget(ampm_field)
        content.add_widget(time_input_layout)

        def add_time(instance):
            hour = hour_field.text.strip().zfill(2)
            minute = minute_field.text.strip().zfill(2)
            ampm = ampm_field.text.strip().upper()
            if hour and minute and ampm in ["AM", "PM"]:
                time_str = f"{hour}:{minute} {ampm}"
                if time_str not in self.reminder_times:
                    self.reminder_times.append(time_str)
                    self.update_times_display()
                dialog.dismiss()
            else:
                error_dialog = MDDialog(
                    title="Invalid Time",
                    text="Please enter valid hour, minute, and AM/PM",
                    buttons=[MDFlatButton(text="OK", on_release=lambda x: error_dialog.dismiss())],
                )
                error_dialog.open()

        dialog = MDDialog(
            title="Add Time",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(text="ADD", on_release=add_time),
                MDFlatButton(text="CANCEL", on_release=lambda x: dialog.dismiss()),
            ],
        )
        dialog.open()

    def clear_times(self):
        self.reminder_times = []
        self.update_times_display()

    def update_times_display(self):
        self.times_label.text = ", ".join(self.reminder_times) if self.reminder_times else "No times added yet"

    def add_reminder(self):
        app = App.get_running_app()
        medicine = self.rem_medicine.text.strip() or self.selected_medicine
        dosage = self.rem_dosage.text.strip() or self.selected_dosage
        schedule_type = self.schedule_btn.text.replace("Schedule: ", "")
        days = self.rem_days.text.strip()

        if not medicine or not dosage or not self.reminder_times:
            dialog = MDDialog(
                title="Missing Information",
                text="Please select a medicine, dosage, and add at least one time.",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())],
            )
            dialog.open()
            return

        try:
            times_24 = [time_to_24h(t) for t in self.reminder_times]
            times_str = ", ".join(times_24)
            app.db.add_reminder(app.current_profile_id, medicine, dosage, schedule_type, times_str, days)

            dialog = MDDialog(
                title="Success",
                text="Reminder created successfully!",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())],
            )
            dialog.open()

            self.selected_medicine = None
            self.selected_dosage = None
            self.medicine_display_label.text = "No medicine selected"
            self.rem_medicine.text = ""
            self.rem_dosage.text = ""
            self.rem_days.text = ""
            self.reminder_times = []
            self.update_times_display()
            self.schedule_btn.text = "Schedule: Daily"
            self.refresh_reminders()
            self.load_medicine_buttons()
            Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 1), 0.1)

        except Exception as e:
            dialog = MDDialog(
                title="Error",
                text=f"Failed to add reminder: {str(e)}",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())],
            )
            dialog.open()

    def refresh_reminders(self):
        app = App.get_running_app()
        self.reminders_list.clear_widgets()
        reminders = app.db.get_active_reminders(app.current_profile_id)

        if not reminders:
            empty_card = MDCard(
                orientation="vertical",
                padding=dp(30),
                size_hint_y=None,
                height=dp(120),
                md_bg_color=[0.1, 0.1, 0.1, 1],
                radius=[15, 15, 15, 15],
            )
            empty_card.add_widget(
                MDLabel(
                    text="No active reminders",
                    halign="center",
                    theme_text_color="Secondary",
                    font_style="Body2",
                )
            )
            self.reminders_list.add_widget(empty_card)
            return

        for reminder in reminders:
            reminder_id, profile_id, medicine, dosage, schedule_type, times, days, active, last_reminded, snoozed_until = reminder
            reminder_card = MDCard(
                orientation="vertical",
                padding=dp(20),
                spacing=dp(12),
                size_hint_y=None,
                md_bg_color=[0.1, 0.1, 0.1, 1],
                radius=[15, 15, 15, 15],
            )
            reminder_card.add_widget(MDLabel(text=medicine, font_style="H6", size_hint_y=None, height=dp(30)))
            times_list = [t.strip() for t in times.split(",")]
            times_ampm = [time_to_ampm(t) for t in times_list]
            times_display = ", ".join(times_ampm)
            details_text = f"Dosage: {dosage}\nTimes: {times_display}\nSchedule: {schedule_type}"
            if days:
                details_text += f"\nDays: {days}"
            details = MDLabel(text=details_text, theme_text_color="Secondary", font_style="Body2", size_hint_y=None)
            details.bind(texture_size=details.setter("size"))
            reminder_card.add_widget(details)

            if snoozed_until:
                reminder_card.add_widget(
                    MDLabel(
                        text="Snoozed",
                        theme_text_color="Custom",
                        text_color=[0.94, 0.68, 0.31, 1],
                        font_style="Caption",
                        size_hint_y=None,
                        height=dp(25),
                    )
                )

            btn_layout = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(48))
            btn_layout.add_widget(MDFlatButton(text="SNOOZE 1H", on_release=lambda x, r_id=reminder_id: self.snooze_reminder(r_id)))
            btn_layout.add_widget(MDFlatButton(text="DELETE", theme_text_color="Error", on_release=lambda x, r_id=reminder_id: self.confirm_delete_reminder(r_id)))
            reminder_card.add_widget(btn_layout)
            reminder_card.height = dp(220)
            self.reminders_list.add_widget(reminder_card)

        Clock.schedule_once(lambda dt: setattr(self.scroll, 'scroll_y', 1), 0.1)

    def snooze_reminder(self, reminder_id):
        app = App.get_running_app()
        snooze_until = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        try:
            app.db.update_reminder_snooze(reminder_id, snooze_until)
            self.refresh_reminders()
        except Exception as e:
            print(f"Error snoozing: {e}")

    def confirm_delete_reminder(self, reminder_id):
        dialog = MDDialog(
            title="Delete Reminder",
            text="Are you sure you want to delete this reminder?",
            buttons=[
                MDRaisedButton(
                    text="DELETE",
                    md_bg_color=[0.85, 0.33, 0.31, 1],
                    on_release=lambda x: self.delete_reminder(reminder_id, dialog),
                ),
                MDFlatButton(text="CANCEL", on_release=lambda x: dialog.dismiss()),
            ],
        )
        dialog.open()

    def delete_reminder(self, reminder_id, dialog):
        app = App.get_running_app()
        try:
            app.db.delete_reminder(reminder_id)
            dialog.dismiss()
            self.refresh_reminders()
        except Exception as e:
            print(f"Error deleting: {e}")
