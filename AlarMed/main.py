"""
AlarMed - Medicine Reminder & Tracker
Clean, responsive UI with Poppins font
"""

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.clock import Clock

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

# Set responsive window size
Window.size = (450, 800)

# Register Poppins font
LabelBase.register(
    name='Poppins',
    fn_regular='fonts/Poppins-Regular.ttf',
    fn_bold='fonts/Poppins-Bold.ttf',
    fn_italic='fonts/Poppins-Regular.ttf',
    fn_bolditalic='fonts/Poppins-Bold.ttf'
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
    
    def build(self):
        """Build the app"""
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.material_style = "M3"
        
        # Set default font to Poppins
        self.theme_cls.font_styles["H1"] = ["Poppins", 96, False, 0.0]
        self.theme_cls.font_styles["H2"] = ["Poppins", 60, False, 0.0]
        self.theme_cls.font_styles["H3"] = ["Poppins", 48, False, 0.0]
        self.theme_cls.font_styles["H4"] = ["Poppins", 34, False, 0.0]
        self.theme_cls.font_styles["H5"] = ["Poppins", 24, False, 0.0]
        self.theme_cls.font_styles["H6"] = ["Poppins", 20, False, 0.0]
        self.theme_cls.font_styles["Subtitle1"] = ["Poppins", 16, False, 0.15]
        self.theme_cls.font_styles["Subtitle2"] = ["Poppins", 14, False, 0.1]
        self.theme_cls.font_styles["Body1"] = ["Poppins", 16, False, 0.5]
        self.theme_cls.font_styles["Body2"] = ["Poppins", 14, False, 0.25]
        self.theme_cls.font_styles["Button"] = ["Poppins", 14, True, 0.0]
        self.theme_cls.font_styles["Caption"] = ["Poppins", 12, False, 0.0]
        self.theme_cls.font_styles["Overline"] = ["Poppins", 10, True, 0.0]
        
        # Screen manager
        self.sm = MDScreenManager()
        
        # Add all screens
        self.sm.add_widget(ProfileSelectorScreen(name='profile_selector'))
        self.sm.add_widget(DashboardScreen(name='dashboard'))
        self.sm.add_widget(RecordMedicineScreen(name='record'))
        self.sm.add_widget(RemindersScreen(name='reminders'))
        self.sm.add_widget(HistoryScreen(name='history'))
        self.sm.add_widget(ReportsScreen(name='reports'))
        self.sm.add_widget(EmergencyScreen(name='emergency'))
        self.sm.add_widget(BackupScreen(name='backup'))
        
        return self.sm
    
    def on_start(self):
        """Called when app starts"""
        if self.db.get_profile_count() == 0:
            self.sm.current = 'profile_selector'
        else:
            last_profile = self.db.get_last_active_profile()
            if last_profile:
                profile_id, name, age, gender, color, avatar, created_at, last_active = last_profile
                self.load_profile(profile_id, name, color, avatar)
            else:
                self.sm.current = 'profile_selector'
    
    def load_profile(self, profile_id, name, color, avatar):
        """Load a profile"""
        self.current_profile_id = profile_id
        self.current_profile_name = name
        self.current_profile_color = color
        self.current_profile_avatar = avatar
        
        self.db.update_profile_last_active(profile_id)
        
        if self.reminder_checker:
            self.reminder_checker.stop()
        
        self.reminder_checker = ReminderChecker(self.db, profile_id)
        self.reminder_checker.start()
        
        self.sm.current = 'dashboard'
    
    def switch_profile(self):
        """Switch to profile selector"""
        if self.reminder_checker:
            self.reminder_checker.stop()
        self.sm.current = 'profile_selector'
    
    def go_to_screen(self, screen_name):
        """Navigate to a screen"""
        if screen_name in [s.name for s in self.sm.screens]:
            self.sm.current = screen_name
    
    def on_stop(self):
        """Called when app stops"""
        if self.reminder_checker:
            self.reminder_checker.stop()

if __name__ == '__main__':
    AlarMedApp().run()
