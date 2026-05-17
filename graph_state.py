from typing import TypedDict, Optional, Literal
from typing_extensions import Required


class MeetingState(TypedDict, total=False):
    input: str
    intent: str
    title: str
    participants: list[str]
    date: Optional[str]
    time: Optional[str]
    duration_minutes: int
    confirmed: bool
    agent_output: str
    awaiting_confirmation: bool
    awaiting_change: bool
    event_id : str