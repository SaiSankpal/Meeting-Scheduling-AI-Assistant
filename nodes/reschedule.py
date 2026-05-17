from typing import Any
from graph_state import MeetingState
from google_calendar import update_event
from datetime import datetime, timedelta


def reschedule_node(state: MeetingState) -> dict[str, Any]:

    # Step 1: Ask for new date/time
    if state.get("awaiting_reschedule_input"):
        return {
            **state,
            "agent_output": "Please provide the new date and time.",
        }

    # Step 2: Perform reschedule
    if not state.get("event_id"):
        return {
            **state,
            "agent_output": "❌ No meeting found to reschedule.",
        }

    try:
        start_datetime = datetime.strptime(
            f"{state['date']} {state['time']}",
            "%Y-%m-%d %H:%M"
        )

        end_datetime = start_datetime + timedelta(
            minutes=state.get("duration_minutes", 60)
        )

        link = update_event(
            event_id=state["event_id"],
            summary=state.get("title") or "Meeting",
            start_time=start_datetime,
            end_time=end_datetime,
            attendees=state.get("participants", [])
        )

        return {
            **state,
            "agent_output": f"✅ Meeting Rescheduled!\n\n🔗 {link}",
            "awaiting_reschedule_input": False,
        }

    except Exception as e:
        return {
            **state,
            "agent_output": f"❌ Failed to reschedule: {str(e)}",
        }