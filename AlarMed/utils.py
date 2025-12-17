"""
AlarMed - Utility Functions
Helper functions for time conversion and calculations
"""

from datetime import datetime, timedelta

def time_to_ampm(time_24):
    """Convert 24-hour time to AM/PM format"""
    try:
        time_obj = datetime.strptime(time_24, "%H:%M")
        return time_obj.strftime("%I:%M %p")
    except:
        return time_24

def time_to_24h(time_ampm):
    """Convert AM/PM time to 24-hour format"""
    try:
        time_obj = datetime.strptime(time_ampm, "%I:%M %p")
        return time_obj.strftime("%H:%M")
    except:
        return time_ampm

def get_greeting():
    """Get time-appropriate greeting"""
    hour = datetime.now().hour
    if hour < 12:
        return "☀️ Good Morning"
    elif hour < 17:
        return "☁️ Good Afternoon"
    else:
        return "🌙 Good Evening"

def calculate_streak(dates_list):
    """Calculate streak from list of dates"""
    if not dates_list:
        return 0
    
    streak = 0
    current_date = datetime.now().date()
    
    for date_str in dates_list:
        check_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        expected_date = current_date - timedelta(days=streak)
        
        if check_date == expected_date:
            streak += 1
        else:
            break
    
    return streak

def get_upcoming_doses_from_reminders(reminders):
    """Get upcoming doses from reminders list"""
    current_time = datetime.now().time()
    upcoming = []
    
    for reminder in reminders:
        med_name = reminder[2]
        dose = reminder[3]
        times_str = reminder[5]
        
        times = [t.strip() for t in times_str.split(',')]
        for time_str in times:
            try:
                if 'AM' in time_str or 'PM' in time_str:
                    time_24 = time_to_24h(time_str)
                else:
                    time_24 = time_str
                
                time_obj = datetime.strptime(time_24, "%H:%M").time()
                if time_obj > current_time:
                    upcoming.append((med_name, dose, time_24))
            except:
                pass
    
    return sorted(upcoming, key=lambda x: x[2])
