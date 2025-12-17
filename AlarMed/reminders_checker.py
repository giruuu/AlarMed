"""
AlarMed - Reminder Checker with Ringtone
"""

from kivy.clock import Clock
from datetime import datetime
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.core.audio import SoundLoader
import os

# Path to your ringtone
RINGTONE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "ringtone.mp3")


class ReminderChecker:
    def __init__(self, database, profile_id):
        self.db = database
        self.profile_id = profile_id
        self.check_event = None
        self.last_check_time = None
        self.sound = SoundLoader.load(RINGTONE_PATH)
        self.current_dialog = None  # Keep reference to the active dialog

    def start(self):
        # Check every 5 seconds to trigger exactly on the minute
        self.check_event = Clock.schedule_interval(self.check_reminders, 5)
        self.check_reminders(0)

    def stop(self):
        if self.check_event:
            self.check_event.cancel()
            self.check_event = None

    def play_sound(self):
        if self.sound:
            self.sound.stop()
            self.sound.play()

    def stop_sound(self):
        if self.sound:
            self.sound.stop()

    def check_reminders(self, dt):
        try:
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            current_date = now.strftime("%Y-%m-%d")
            current_day = now.strftime("%a")

            if self.last_check_time == current_time:
                return
            self.last_check_time = current_time

            reminders = self.db.get_active_reminders(self.profile_id)

            for reminder in reminders:
                (
                    reminder_id,
                    profile_id,
                    medicine,
                    dosage,
                    schedule_type,
                    times,
                    days,
                    active,
                    last_reminded,
                    snoozed,
                ) = reminder

                if snoozed:
                    snooze_time = datetime.strptime(snoozed, "%Y-%m-%d %H:%M:%S")
                    if now < snooze_time:
                        continue
                    else:
                        self.db.update_reminder_snooze(reminder_id, None)

                times_list = [t.strip() for t in times.split(",")]
                for reminder_time in times_list:
                    if reminder_time != current_time:
                        continue

                    should_trigger = False

                    if schedule_type == "Daily":
                        should_trigger = True
                    elif schedule_type == "Specific Days" and days:
                        days_list = [d.strip() for d in days.split(",")]
                        if current_day in days_list:
                            should_trigger = True
                    elif schedule_type == "Every Other Day":
                        if last_reminded:
                            last_date = datetime.strptime(
                                last_reminded.split()[0], "%Y-%m-%d"
                            )
                            if (now - last_date).days >= 2:
                                should_trigger = True
                        else:
                            should_trigger = True
                    elif schedule_type == "Weekly":
                        if last_reminded:
                            last_date = datetime.strptime(
                                last_reminded.split()[0], "%Y-%m-%d"
                            )
                            if (now - last_date).days >= 7:
                                should_trigger = True
                        else:
                            should_trigger = True

                    if should_trigger:
                        self.play_sound()
                        self.show_reminder_notification(medicine, dosage, reminder_time)
                        self.db.update_reminder_last_reminded(
                            reminder_id, f"{current_date} {current_time}:00"
                        )

        except Exception as e:
            print(f"Error checking reminders: {e}")

    def show_reminder_notification(self, medicine, dosage, time):
        from kivy.app import App
        app = App.get_running_app()

        # Define dialog buttons with sound stopping
        dismiss_btn = MDFlatButton(
            text="DISMISS",
            on_release=lambda x: (self.stop_sound(), self.current_dialog.dismiss())
        )
        log_btn = MDFlatButton(
            text="LOG NOW",
            on_release=lambda x: (self.stop_sound(), self.current_dialog.dismiss(), self.quick_log(medicine, dosage))
        )

        self.current_dialog = MDDialog(
            title="Medication Reminder",
            text=f"Time to take:\n\n{medicine}\n{dosage}\n\nScheduled for: {self.format_time_ampm(time)}",
            buttons=[dismiss_btn, log_btn],
        )
        self.current_dialog.open()

    def quick_log(self, medicine, dosage):
        from kivy.app import App
        try:
            app = App.get_running_app()
            current_time = datetime.now().strftime("%H:%M")
            current_date = datetime.now().strftime("%Y-%m-%d")

            app.db.add_medicine_record(
                self.profile_id,
                medicine,
                dosage,
                current_time,
                current_date,
                "Logged from reminder",
            )

            app.db.update_medicine_library(
                self.profile_id, medicine, dosage, current_date
            )

            dialog = MDDialog(
                title="Success",
                text=f"{medicine} logged successfully!",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: dialog.dismiss())],
            )
            dialog.open()
        except Exception as e:
            print(f"Error logging medicine: {e}")

    def format_time_ampm(self, time_24):
        try:
            hour, minute = map(int, time_24.split(":"))
            ampm = "AM" if hour < 12 else "PM"
            hour_12 = hour if hour <= 12 else hour - 12
            if hour_12 == 0:
                hour_12 = 12
            return f"{hour_12:02d}:{minute:02d} {ampm}"
        except Exception:
            return time_24
