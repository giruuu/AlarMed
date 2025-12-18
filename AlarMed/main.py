"""
AlarMed - Medicine Reminder & Tracker
Clean, responsive UI with Poppins font
"""

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.core.window import Window
from kivy.core.text import LabelBase

from database import Database
from reminders_checker import ReminderChecker

# Import all screens
from screens.profile_selector import ProfileSelectorScreen
from screens.dashboard import DashboardScreen
from screens.record_medicine import RecordMedicineScreen
from screens.reminders import RemindersScreen
from screens.history import HistoryScreen
from screens.reports import ReportsScreen
from screens.emergency import EmergencyScreen
from screens.backup import BackupScreen

Window.size = (450, 800)

LabelBase.register(
    name="Poppins",
    fn_regular="fonts/Poppins-Regular.ttf",
    fn_bold="fonts/Poppins-Bold.ttf",
)


class AlarMedApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database()
        self.reminder_checker = None

        self.current_profile_id = None
        self.current_profile_name = None
        self.current_profile_color = None
        self.current_profile_avatar = None

        self._dialog = None

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.material_style = "M3"

        self.sm = MDScreenManager()
        self.sm.add_widget(ProfileSelectorScreen(name="profile_selector"))
        self.sm.add_widget(DashboardScreen(name="dashboard"))
        self.sm.add_widget(RecordMedicineScreen(name="record"))
        self.sm.add_widget(RemindersScreen(name="reminders"))
        self.sm.add_widget(HistoryScreen(name="history"))
        self.sm.add_widget(ReportsScreen(name="reports"))
        self.sm.add_widget(EmergencyScreen(name="emergency"))
        self.sm.add_widget(BackupScreen(name="backup"))
        return self.sm

    def on_start(self):
        if self.db.get_profile_count() == 0:
            self.sm.current = "profile_selector"
            return

        last_profile = self.db.get_last_active_profile()
        if last_profile:
            pid, name, age, gender, color, avatar, *_ = last_profile
            self.load_profile(pid, name, color, avatar)
        else:
            self.sm.current = "profile_selector"

    def load_profile(self, profile_id, name, color, avatar):
        self.current_profile_id = profile_id
        self.current_profile_name = name
        self.current_profile_color = color
        self.current_profile_avatar = avatar

        self.db.update_profile_last_active(profile_id)

        if self.reminder_checker:
            self.reminder_checker.stop()

        self.reminder_checker = ReminderChecker(self.db, profile_id)
        self.reminder_checker.start()

        self.sm.current = "dashboard"

    def switch_profile(self):
        if self.reminder_checker:
            self.reminder_checker.stop()
        self.sm.current = "profile_selector"

    def go_to_screen(self, screen_name: str):
        self.sm.current = screen_name

    def show_dialog(self, title, message):
        dialog = MDDialog(
            title=title,
            text=message,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())],
        )
        dialog.open()

    def on_stop(self):
        if self.reminder_checker:
            self.reminder_checker.stop()


if __name__ == "__main__":
    AlarMedApp().run()
