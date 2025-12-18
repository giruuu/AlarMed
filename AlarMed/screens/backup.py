from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup

from datetime import datetime
import os


class BackupScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._popup = None
        self.status_label = None
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()
        app = App.get_running_app()

        root = MDBoxLayout(orientation="vertical")

        # Header card (matches your app style, but no icon buttons)
        header = MDCard(
            orientation="vertical",
            padding=dp(18),
            spacing=dp(6),
            size_hint_y=None,
            height=dp(120),
            md_bg_color=[0.12, 0.42, 0.65, 1],
            radius=[0, 0, 20, 20],
        )

        top_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(44),
            spacing=dp(10),
        )

        back_btn = MDFlatButton(
            text="BACK",
            on_release=lambda x: app.go_to_screen("dashboard"),
        )
        top_row.add_widget(back_btn)

        top_row.add_widget(MDLabel(text="", size_hint_x=1))
        header.add_widget(top_row)

        header.add_widget(MDLabel(text="Backup & Restore", font_style="H5"))
        header.add_widget(
            MDLabel(
                text="Save or restore one profile using a JSON file.",
                font_style="Caption",
                theme_text_color="Secondary",
            )
        )

        root.add_widget(header)

        # Scrollable content (prevents awkward empty space and keeps layout consistent)
        scroll = MDScrollView()
        content = MDBoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(14),
            size_hint_y=None,
        )
        content.bind(minimum_height=content.setter("height"))
        scroll.add_widget(content)
        root.add_widget(scroll)

        # Center column to keep buttons nicely aligned on wide screens
        center = MDBoxLayout(
            orientation="vertical",
            spacing=dp(12),
            size_hint_x=None,
            width=dp(340),
            pos_hint={"center_x": 0.5},
            size_hint_y=None,
        )
        center.bind(minimum_height=center.setter("height"))
        content.add_widget(center)

        center.add_widget(
            MDRaisedButton(
                text="BACKUP CURRENT PROFILE",
                size_hint_y=None,
                height=dp(48),
                pos_hint={"center_x": 0.5},
                on_release=lambda x: self.backup_profile(),
            )
        )

        center.add_widget(
            MDRaisedButton(
                text="RESTORE FROM BACKUP FILE",
                size_hint_y=None,
                height=dp(48),
                pos_hint={"center_x": 0.5},
                on_release=lambda x: self.open_restore_dialog(),
            )
        )

        # Status / last action info
        self.status_label = MDLabel(
            text="",
            theme_text_color="Secondary",
            halign="left",
            size_hint_y=None,
        )
        self.status_label.bind(texture_size=self.status_label.setter("size"))
        center.add_widget(self.status_label)

        self.add_widget(root)

    def on_enter(self, *args):
        # Ensure UI exists (safe if screen recreated)
        if not self.children:
            self.build_ui()

    def _set_status(self, text):
        if self.status_label:
            self.status_label.text = text

    def _get_backup_dir(self):
        app = App.get_running_app()
        base_dir = getattr(app, "user_data_dir", os.path.expanduser("~"))
        backup_dir = os.path.join(base_dir, "AlarMedBackups")
        os.makedirs(backup_dir, exist_ok=True)
        return backup_dir

    def backup_profile(self):
        app = App.get_running_app()
        if not app.current_profile_id:
            app.show_dialog("Backup Failed", "No active profile selected.")
            return

        safe_name = (app.current_profile_name or "profile").strip().replace(" ", "_")
        filename = f"alarmed_backup_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        backup_dir = self._get_backup_dir()
        full_path = os.path.join(backup_dir, filename)

        try:
            app.db.backup_profile(app.current_profile_id, full_path)
            app.show_dialog("Backup Successful", f"Saved to:\n{full_path}")
            self._set_status(f"Last backup:\n{full_path}")
        except Exception as e:
            app.show_dialog("Backup Failed", str(e))

    def open_restore_dialog(self):
        start_dir = self._get_backup_dir()

        chooser = FileChooserListView(
            path=start_dir,
            filters=["*.json"],
        )

        layout = MDBoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        layout.add_widget(chooser)

        buttons = MDBoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        buttons.add_widget(
            MDRaisedButton(text="CANCEL", on_release=lambda x: self._dismiss_popup())
        )
        layout.add_widget(buttons)

        self._popup = Popup(
            title="Select Backup File (double click to select)",
            content=layout,
            size_hint=(0.95, 0.9),
        )

        def on_submit(instance, selection, touch=None):
            if selection:
                self._restore_from_path(selection[0])

        chooser.bind(on_submit=on_submit)
        self._popup.open()

    def _dismiss_popup(self):
        if self._popup:
            self._popup.dismiss()
            self._popup = None

    def _restore_from_path(self, path):
        app = App.get_running_app()
        try:
            app.db.restore_profile(path)
            self._dismiss_popup()
            app.show_dialog("Restore Successful", "Profile restored. Select it from Profiles.")
            app.go_to_screen("profile_selector")
        except Exception as e:
            self._dismiss_popup()
            app.show_dialog("Restore Failed", str(e))
