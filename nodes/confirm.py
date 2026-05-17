# nodes/confirm.py

from typing import Any
from graph_state import MeetingState


def confirmation_node(state: MeetingState) -> dict[str, Any]:
    title = state.get("title", "Meeting")
    date = state.get("date", "")
    time = state.get("time", "")
    participants = state.get("participants", [])

    participant_str = ", ".join(participants) if participants else "No participants"

    message = (
        f"Please confirm the meeting details:\n\n"
        f"📌 Title: {title}\n"
        f"📅 Date: {date}\n"
        f"⏰ Time: {time}\n"
        f"👥 Participants: {participant_str}\n\n"
        f"Reply with 'confirm' or 'change'."
    )

    return {
        **state,
        "agent_output": message,
        "awaiting_confirmation": True,
        "confirmed": False,  # IMPORTANT
    }
    