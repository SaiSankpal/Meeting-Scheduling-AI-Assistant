from typing import TypedDict
from langgraph.graph import StateGraph, END

from nodes.change_options import change_options_node
from nodes.extract_intent import extract_intent_node
from nodes.confirm import confirmation_node
from nodes.schedule import schedule_node
from nodes.reschedule import reschedule_node
from nodes.cancel import cancel_node


class MeetingState(TypedDict, total=False):
    input: str
    intent: str
    participants: list[str]
    date: str
    time: str
    agent_output: str
    awaiting_confirmation: bool
    awaiting_change: bool 
    event_id : str


def intent_router(state: MeetingState):
    """Route based on high-level intent after extraction."""
    intent = (state.get("intent") or "").lower()

    # Reschedule existing meeting
    if intent in ["reschedule", "edit", "modify", "change_time"]:
        return "reschedule"

    # Cancel existing meeting
    if intent in ["cancel", "delete", "remove"]:
        return "cancel"

    # Default: go through confirmation + schedule flow
    return "confirm"


def confirmation_router(state: MeetingState):
    if not state.get("awaiting_confirmation"):
        return END

    input = state.get("input", "").lower()

    if input in ["yes", "y", "confirm"]:
        return "schedule"

    if input in ["no", "n", "change"]:
        return "change_options"

    return END


def change_options_router(state: MeetingState):
    input = state.get("input", "").lower()

    if input in ["reschedule", "res"]:
        return "reschedule"

    if input in ["cancel", "c"]:
        return "cancel"

    return END

def entry_router(state: MeetingState):
    if state.get("awaiting_confirmation"):
        return "confirm"

    if state.get("awaiting_change"):
        return "change_options"

    return "extract_intent"
    
# Build Graph
graph = StateGraph(MeetingState)

graph.add_node("extract_intent", extract_intent_node)
graph.add_node("confirm", confirmation_node)
graph.add_node("schedule", schedule_node)
graph.add_node("change_options", change_options_node)
graph.add_node("reschedule", reschedule_node)
graph.add_node("cancel", cancel_node)
graph.add_node("entry", lambda state: state)

graph.set_entry_point("entry")

# Flow
# After extracting intent, route based on intent value
graph.add_conditional_edges(
    "extract_intent",
    intent_router,
    {
        "confirm": "confirm",
        "reschedule": "reschedule",
        "cancel": "cancel",
    },
)

graph.add_conditional_edges(
    "confirm",
    confirmation_router,
    {
        "schedule": "schedule",
        "change_options": "change_options",
        END: END,
    }
)

graph.add_conditional_edges(
    "change_options",
    change_options_router,
    {
        "reschedule": "reschedule",
        "cancel": "cancel",
        END: END,
    }
)

graph.add_conditional_edges(
    "entry",
    entry_router,
    {
        "extract_intent": "extract_intent",
        "confirm": "confirm",
        "change_options": "change_options",
    }
)
# Terminal nodes
graph.add_edge("schedule", END)
graph.add_edge("reschedule", END)
graph.add_edge("cancel", END)

# Compile LAST
meeting_graph = graph.compile()



