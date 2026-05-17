# nodes/extract_intent.py

import re
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
    lowered = text.lower()

    # handle typos
    if "tomorrow" in lowered or "tomorow" in lowered:
        return (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    if "today" in lowered:
        return datetime.now().strftime("%Y-%m-%d")

    # explicit date
    match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
    if match:
        return match.group(1)

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