# nodes/extract_intent.py

import re
import dateparser
from datetime import datetime, timedelta
from typing import List
from graph_state import MeetingState


# ------------------ HELPERS ------------------

def _detect_intent(text: str) -> str:
    lowered = text.lower()

    # cancel variations
    if any(word in lowered for word in [
        "cancel", "delete", "remove", "abort"
    ]):
        return "cancel"

    # reschedule variations
    if any(word in lowered for word in [
        "reschedule", "change", "move", "shift"
    ]):
        return "reschedule"

    return "schedule"


def _extract_time(text: str) -> str:
    text = text.lower()

    # ✅ match 8:00 pm OR 8:00pm
    match = re.search(r"\b(\d{1,2})\s*:\s*(\d{2})\s*(am|pm)\b", text)
    if match:
        hour = int(match.group(1))
        minute = match.group(2)
        period = match.group(3)

        if period == "pm" and hour != 12:
            hour += 12
        if period == "am" and hour == 12:
            hour = 0

        return f"{hour:02d}:{minute}"

    # ✅ match 8 pm OR 8pm
    match = re.search(r"\b(\d{1,2})\s*(am|pm)\b", text)
    if match:
        hour = int(match.group(1))
        period = match.group(2)

        if period == "pm" and hour != 12:
            hour += 12
        if period == "am" and hour == 12:
            hour = 0

        return f"{hour:02d}:00"

    return ""

def _extract_date(text: str) -> str:
    cleaned = text.strip()

    # TRAP NUMERIC DATES FIRST (e.g., 20/06/2026, 20-06-2026, 20.06.2026)
    # This regex looks for DD/MM/YYYY or DD/MM/YY formats safely
    numeric_match = re.search(r"\b(\d{1,2})[./\-](\d{1,2})[./\-](\d{2,4})\b", cleaned)
    if numeric_match:
        day = int(numeric_match.group(1))
        month = int(numeric_match.group(2))
        year_str = numeric_match.group(3)
        
        # Handle 2-digit years safely (e.g., /26 -> 2026)
        year = int(year_str)
        if len(year_str) == 2:
            year += 2000
            
        try:
            # Validate that it's a real date and return standard ISO format
            valid_date = datetime(year, month, day)
            return valid_date.strftime("%d-%m-%Y")
        except ValueError:
            print("Following date does not exist: ", day, month, year)
            return "Following date does not exist"
            
    # EXPLICIT LOOKUP FOR "COMING/NEXT WEEKDAYS" TO AVOID DATEPARSER CONFUSION
    # Maps weekday names to their structural integer values in Python (Monday=0, Sunday=6)
    weekdays = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6
    }
    
    # Check if a weekday token exists in the sentence
    for day_name, day_num in weekdays.items():
        if day_name in cleaned:
            today = datetime.now()
            current_weekday = today.weekday()
            
            # Calculate how many days to add to get to that weekday
            days_ahead = day_num - current_weekday
            if days_ahead <= 0: 
                # If the day passed or is today, "coming/next" implies next week's day
                days_ahead += 7
                
            target_date = today + timedelta(days=days_ahead)
            return target_date.strftime("%d-%m-%Y")

    # FALLBACK TO DATEPARSER FOR TEXT DATES (e.g., "next Tuesday", "tomorrow")
    # Clean out email patterns to prevent confusion
    cleaned = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "", cleaned)
    cleaned = re.sub(r"\b(schedule|meeting|with|at)\b", "", cleaned, flags=re.IGNORECASE)
    
    settings = {
        'PREFER_DATES_FROM': 'future',
        'DATE_ORDER': 'DMY',
        'RELATIVE_BASE': datetime.now()
    }
    
    parsed_date = dateparser.parse(cleaned, settings=settings)
    if parsed_date:
        return parsed_date.strftime("%d-%m-%Y")
        
    return ""


def _extract_emails(text: str) -> List[str]:
    return re.findall(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        text
    )


# ------------------ MAIN FUNCTION ------------------

def extract_details(user_input: str) -> MeetingState:
    text = user_input.strip()

    attendees = _extract_emails(text)
    time = _extract_time(text)
    date = _extract_date(text)

    duration_match = re.search(r"(\d+)\s*(?:min|mins|minutes?)", text.lower())
    duration_minutes = int(duration_match.group(1)) if duration_match else 60

    confirmed = text.lower() in {"yes", "y", "confirm", "confirmed"}

    return {
        "input": text,
        "intent": _detect_intent(text),
        "participants": attendees,
        "date": date,
        "time": time,
        "duration_minutes": duration_minutes,
        "confirmed": confirmed,
    }