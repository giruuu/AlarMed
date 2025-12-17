"""
AlarMed - Database Management
All database operations
"""

import sqlite3
from datetime import datetime


class Database:
    def __init__(self, db_name='alarmed.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.init_tables()
    
    def init_tables(self):
        """Initialize all database tables"""
        
        # User profiles table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                profile_color TEXT DEFAULT '#1f6aa5',
                avatar_emoji TEXT DEFAULT '👤',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_active TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Medicine records table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS medicine_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER NOT NULL,
                medicine_name TEXT NOT NULL,
                dosage TEXT NOT NULL,
                time_taken TEXT NULLABLE,
                date_taken TEXT NULLABLE,
                notes TEXT,
                completed INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (profile_id) REFERENCES user_profiles(id)
            )
        ''')
        
        # Reminders table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER NOT NULL,
                medicine_name TEXT NOT NULL,
                dosage TEXT NOT NULL,
                schedule_type TEXT NOT NULL,
                time_schedule TEXT NOT NULL,
                days_schedule TEXT,
                active INTEGER DEFAULT 1,
                last_reminded TEXT,
                snoozed_until TEXT,
                FOREIGN KEY (profile_id) REFERENCES user_profiles(id)
            )
        ''')
        
        # Emergency contacts table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS emergency_contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_name TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                contact_type TEXT,
                priority INTEGER DEFAULT 1
            )
        ''')
        
        # Medicine library
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS medicine_library (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER NOT NULL,
                medicine_name TEXT NOT NULL,
                common_dosage TEXT,
                usage_count INTEGER DEFAULT 0,
                last_used TEXT,
                FOREIGN KEY (profile_id) REFERENCES user_profiles(id),
                UNIQUE(profile_id, medicine_name)
            )
        ''')
        
        # Add default emergency contacts
        self.cursor.execute('SELECT COUNT(*) FROM emergency_contacts')
        if self.cursor.fetchone()[0] == 0:
            default_contacts = [
                ("Emergency Services", "911", "Emergency", 1),
                ("Poison Control", "1-800-222-1222", "Emergency", 2),
                ("Primary Doctor", "000-000-0000", "Medical", 3)
            ]
            self.cursor.executemany(
                'INSERT INTO emergency_contacts (contact_name, phone_number, contact_type, priority) VALUES (?, ?, ?, ?)',
                default_contacts
            )
        
        self.conn.commit()
    
    # Profile operations
    def get_all_profiles(self):
        self.cursor.execute('SELECT * FROM user_profiles ORDER BY last_active DESC')
        return self.cursor.fetchall()
    
    def get_profile_count(self):
        self.cursor.execute('SELECT COUNT(*) FROM user_profiles')
        return self.cursor.fetchone()[0]
    
    def get_profile_by_id(self, profile_id):
        self.cursor.execute('SELECT * FROM user_profiles WHERE id = ?', (profile_id,))
        return self.cursor.fetchone()
    
    def create_profile(self, name, age, gender, color, emoji):
        self.cursor.execute('''
            INSERT INTO user_profiles (profile_name, age, gender, profile_color, avatar_emoji)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, age, gender, color, emoji))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def update_profile(self, profile_id, name, age, gender, color, emoji):
        self.cursor.execute('''
            UPDATE user_profiles 
            SET profile_name = ?, age = ?, gender = ?, profile_color = ?, avatar_emoji = ?
            WHERE id = ?
        ''', (name, age, gender, color, emoji, profile_id))
        self.conn.commit()
    
    def delete_profile(self, profile_id):
        self.cursor.execute('DELETE FROM medicine_records WHERE profile_id = ?', (profile_id,))
        self.cursor.execute('DELETE FROM reminders WHERE profile_id = ?', (profile_id,))
        self.cursor.execute('DELETE FROM medicine_library WHERE profile_id = ?', (profile_id,))
        self.cursor.execute('DELETE FROM user_profiles WHERE id = ?', (profile_id,))
        self.conn.commit()
    
    def update_last_active(self, profile_id):
        """Legacy helper – you can still call this if used somewhere."""
        self.cursor.execute(
            'UPDATE user_profiles SET last_active = ? WHERE id = ?',
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), profile_id)
        )
        self.conn.commit()

    # New helpers used by main.py
    def get_last_active_profile(self):
        """Return the most recently active user profile (or None)."""
        self.cursor.execute(
            "SELECT * FROM user_profiles ORDER BY last_active DESC LIMIT 1"
        )
        return self.cursor.fetchone()
    
    def update_profile_last_active(self, profile_id):
        """Alias for update_last_active used by the app."""
        self.cursor.execute(
            "UPDATE user_profiles SET last_active = ? WHERE id = ?",
            (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), profile_id),
        )
        self.conn.commit()
    
    # Medicine records operations
    def add_medicine_record(self, profile_id, medicine_name, dosage, time_taken, date_taken, notes=""):
        self.cursor.execute('''
            INSERT INTO medicine_records (profile_id, medicine_name, dosage, time_taken, date_taken, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (profile_id, medicine_name, dosage, time_taken, date_taken, notes))
        self.conn.commit()
    
    def get_medicine_records(self, profile_id, date_filter=None):
        if date_filter:
            self.cursor.execute('''
                SELECT * FROM medicine_records 
                WHERE profile_id = ? AND date_taken >= ?
                ORDER BY date_taken DESC, time_taken DESC
            ''', (profile_id, date_filter))
        else:
            self.cursor.execute('''
                SELECT * FROM medicine_records 
                WHERE profile_id = ?
                ORDER BY date_taken DESC, time_taken DESC
            ''', (profile_id,))
        return self.cursor.fetchall()
    
    def get_today_medicine_count(self, profile_id, today_date):
        self.cursor.execute(
            'SELECT COUNT(*) FROM medicine_records WHERE date_taken = ? AND profile_id = ?',
            (today_date, profile_id)
        )
        return self.cursor.fetchone()[0]
    
    def get_streak_dates(self, profile_id):
        self.cursor.execute('''
            SELECT DISTINCT date_taken 
            FROM medicine_records 
            WHERE completed = 1 AND profile_id = ?
            ORDER BY date_taken DESC
        ''', (profile_id,))
        return [row[0] for row in self.cursor.fetchall()]
    
    # Reminder operations
    def add_reminder(self, profile_id, medicine_name, dosage, schedule_type, time_schedule, days_schedule=""):
        self.cursor.execute('''
            INSERT INTO reminders (profile_id, medicine_name, dosage, schedule_type, time_schedule, days_schedule)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (profile_id, medicine_name, dosage, schedule_type, time_schedule, days_schedule))
        self.conn.commit()
    
    def get_active_reminders(self, profile_id):
        self.cursor.execute(
            'SELECT * FROM reminders WHERE active = 1 AND profile_id = ?',
            (profile_id,)
        )
        return self.cursor.fetchall()
    
    def get_active_reminder_count(self, profile_id):
        self.cursor.execute(
            'SELECT COUNT(*) FROM reminders WHERE active = 1 AND profile_id = ?',
            (profile_id,)
        )
        return self.cursor.fetchone()[0]
    
    def update_reminder_snooze(self, reminder_id, snooze_until):
        self.cursor.execute('UPDATE reminders SET snoozed_until = ? WHERE id = ?', (snooze_until, reminder_id))
        self.conn.commit()
    
    def update_reminder_last_reminded(self, reminder_id, timestamp):
        self.cursor.execute('UPDATE reminders SET last_reminded = ? WHERE id = ?', (timestamp, reminder_id))
        self.conn.commit()
    
    def delete_reminder(self, reminder_id):
        self.cursor.execute('UPDATE reminders SET active = 0 WHERE id = ?', (reminder_id,))
        self.conn.commit()
    
    # Medicine library operations
    def get_medicine_suggestions(self, profile_id, limit=20):
        self.cursor.execute(
            'SELECT medicine_name FROM medicine_library WHERE profile_id = ? ORDER BY usage_count DESC LIMIT ?',
            (profile_id, limit)
        )
        return [row[0] for row in self.cursor.fetchall()]
    
    def update_medicine_library(self, profile_id, medicine_name, dosage, date_used):
        self.cursor.execute('''
            INSERT INTO medicine_library (profile_id, medicine_name, common_dosage, usage_count, last_used)
            VALUES (?, ?, ?, 1, ?)
            ON CONFLICT(profile_id, medicine_name) DO UPDATE SET
                usage_count = usage_count + 1,
                common_dosage = ?,
                last_used = ?
        ''', (profile_id, medicine_name, dosage, date_used, dosage, date_used))
        self.conn.commit()
    
    def get_recent_medicines(self, profile_id, limit=5):
        self.cursor.execute('''
            SELECT medicine_name, common_dosage FROM medicine_library 
            WHERE profile_id = ?
            ORDER BY usage_count DESC, last_used DESC LIMIT ?
        ''', (profile_id, limit))
        return self.cursor.fetchall()
    
    # Emergency contacts
    def get_all_emergency_contacts(self):
        self.cursor.execute('SELECT * FROM emergency_contacts ORDER BY priority, contact_type, contact_name')
        return self.cursor.fetchall()
    
    def add_emergency_contact(self, name, phone, contact_type):
        self.cursor.execute('''
            INSERT INTO emergency_contacts (contact_name, phone_number, contact_type)
            VALUES (?, ?, ?)
        ''', (name, phone, contact_type))
        self.conn.commit()
    
    def delete_emergency_contact(self, contact_id):
        self.cursor.execute('DELETE FROM emergency_contacts WHERE id = ?', (contact_id,))
        self.conn.commit()
    
    # Statistics
    def get_most_taken_medicines(self, profile_id, cutoff_date, limit=5):
        self.cursor.execute('''
            SELECT medicine_name, COUNT(*) as count 
            FROM medicine_records 
            WHERE date_taken >= ? AND profile_id = ?
            GROUP BY medicine_name 
            ORDER BY count DESC 
            LIMIT ?
        ''', (cutoff_date, profile_id, limit))
        return self.cursor.fetchall()
    
    def get_adherence_stats(self, profile_id, cutoff_date):
        self.cursor.execute('''
            SELECT COUNT(DISTINCT date_taken) 
            FROM medicine_records 
            WHERE date_taken >= ? AND completed = 1 AND profile_id = ?
        ''', (cutoff_date, profile_id))
        return self.cursor.fetchone()[0]
    
    def get_total_records(self, profile_id, cutoff_date):
        self.cursor.execute(
            'SELECT COUNT(*) FROM medicine_records WHERE date_taken >= ? AND profile_id = ?',
            (cutoff_date, profile_id)
        )
        return self.cursor.fetchone()[0]
    
    def get_unique_medicines(self, profile_id, cutoff_date):
        self.cursor.execute(
            'SELECT COUNT(DISTINCT medicine_name) FROM medicine_records WHERE date_taken >= ? AND profile_id = ?',
            (cutoff_date, profile_id)
        )
        return self.cursor.fetchone()[0]
    
    def close(self):
        self.conn.close()
