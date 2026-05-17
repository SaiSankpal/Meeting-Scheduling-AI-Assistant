# nodes/change_options_node.py

from typing import Any
from graph_state import MeetingState


def change_options_node(state: MeetingState) -> dict[str, Any]:
    message = (
        "What would you like to change?\n\n"
        "1. Reschedule\n"
        "2. Cancel\n\n"
        "Please reply with 'reschedule' or 'cancel'."
    )

    return {
        **state,

        # User-facing message
        "agent_output": message,

        # Flow control flags
        "awaiting_change_option": True,
        "awaiting_confirmation": False,

        # Optional: reset previous decisions if needed
        "intent": None,
    }