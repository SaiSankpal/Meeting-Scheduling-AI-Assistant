from typing import Any
from graph_state import MeetingState
from google_calendar import create_event
import datetime
import dateparser


def schedule_node(state: MeetingState) -> MeetingState:
    """Schedule meeting after confirmation using Google Calendar"""

    try:
        date_str = state.get("date")
        time_str = state.get("time")
        participants = state.get("participants", [])

        # ✅ Ensure participants is always list
        if isinstance(participants, str):
            participants = [participants]

        # ✅ Validate required fields
        if not date_str or not time_str:
            return {
                **state,
                "agent_output": "❌ Missing date or time. Please try again.",
                "awaiting_confirmation": False,
            }

        # ✅ Parse natural language date + time
        parsed_datetime = dateparser.parse(
            f"{date_str} {time_str}",
            settings={
                "TIMEZONE": "Asia/Kolkata",
                "RETURN_AS_TIMEZONE_AWARE": True,
            },
        )

        # ❌ If parsing failed
        if not parsed_datetime:
            return {
                **state,
                "agent_output": "❌ Could not understand the provided date/time.",
                "awaiting_confirmation": False,
            }

        start_time = parsed_datetime
        end_time = start_time + datetime.timedelta(hours=1)

        # ✅ Google Calendar API call
        event_link = create_event(
            summary="Meeting Scheduled via AI Agent",
            start_time=start_time,
            end_time=end_time,
            attendees=participants,
        )

        return {
            **state,
            "agent_output": f"✅ Meeting Scheduled Successfully!\n\n📅 {start_time.strftime('%d %b %Y, %I:%M %p')}\n🔗 {event_link}",
            "awaiting_confirmation": False,
            "awaiting_change": False,
            "input": "",   # 🔥 reset input so router doesn't loop
        }

    except Exception as e:
        return {
            **state,
            "agent_output": f"❌ Failed to schedule meeting.\n\nError: {str(e)}",
            "awaiting_confirmation": False,
        }