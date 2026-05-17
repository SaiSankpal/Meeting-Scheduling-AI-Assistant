from typing import Any
from graph_state import MeetingState
from google_calendar import cancel_event


def cancel_node(state: MeetingState) -> dict[str, Any]:

    if not state.get("event_id"):
        return {
            **state,
            "agent_output": "❌ No meeting found to cancel.",
        }

    try:
        cancel_event(state["event_id"])

        return {
            **state,
            "agent_output": "❌ Meeting cancelled successfully.",
            "awaiting_confirmation": False,
            "awaiting_change_option": False,
        }

    except Exception as e:
        return {
            **state,
            "agent_output": f"❌ Failed to cancel meeting: {str(e)}",
        }