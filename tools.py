from typing import Callable, Any
from langchain_core.tools import tool as _tool, BaseTool

def tool(func: Callable[..., Any]) -> BaseTool:  # type: ignore[return, misc]
    """Type-annotated tool decorator that returns BaseTool."""
    return _tool(func)  # type: ignore[misc]

@tool
def schedule_meeting(participants: str, date: str, time: str, duration_minutes: int):
    """Schedule a meeting(mock)."""
    return(
        f"Scheduled meeting with {participants} on {date} at {time} for {duration_minutes} minutes."
    ) 

@tool
def edit_meeting(meeting_id: str, new_time: str):
    """Edit an existing meeting(mock)."""
    return f"Meeting {meeting_id} rescheduled to {new_time}."

@tool
def cancel_meeting(meeting_id: str):
    """Cancel an existing meeting(mock)."""
    return f"Meeting {meeting_id} has been cancelled."
        
