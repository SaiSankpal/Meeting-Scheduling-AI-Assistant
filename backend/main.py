from fastapi import FastAPI
from typing import Any, cast
from graph_state import MeetingState
from nodes.extract_intent import extract_details
from google_calendar import create_event, update_event, cancel_event
from datetime import datetime, timedelta

app = FastAPI()
User_States: dict[str, MeetingState] = {}


# ------------------ CHECK REQUIRED FIELDS ------------------

def _missing_fields(state: MeetingState):
    missing = []

    if not state.get("date"):
        missing.append("date")
    if not state.get("time"):
        missing.append("time")
    if not state.get("participants"):
        missing.append("attendee email")

    return missing


def _can_schedule(state: MeetingState) -> bool:
    return len(_missing_fields(state)) == 0


# ------------------ MAIN API ------------------

@app.post("/chat")
def chat(user_input: dict[str, Any]):

    user_id = user_input.get("user_id") or "default"
    text = user_input.get("user_input") or user_input.get("message") or ""
    lowered = text.strip().lower()

    previous_state = User_States.get(user_id)
    state: MeetingState


    # ------------------ CONFIRMATION ------------------

    if previous_state and lowered in {"yes", "y", "confirm", "confirmed"}:
        state = cast(MeetingState, {**previous_state, "confirmed": True})

    elif previous_state and lowered in {"no", "n", "change"}:
        state = cast(MeetingState, {
            **previous_state,
            "confirmed": False,
            "awaiting_change": True   
            })

    else:
        extracted_state = extract_details(text)

        if previous_state:
            merged = {**previous_state}
            for k, v in extracted_state.items():
                if v not in ("", [], None):
                    merged[k] = v
            state = cast(MeetingState, merged)
        else:
            state = cast(MeetingState, extracted_state)

        state["awaiting_change"] = False

    print("STATE DEBUG:", state)
    User_States[user_id] = state

# ------------------ HANDLE CHANGE ------------------

    if state.get("awaiting_change"):
        return {
            "status": "pending",
            "response": "Please provide the updated details (date, time, or participants).",
            "details": state,
            }

    intent = state.get("intent")

    # ------------------ CANCEL ------------------

    if intent == "cancel":

        if not state.get("event_id"):
            return {
                "status": "error",
                "response": "No meeting found to cancel."
            }

        try:
            cancel_event(state["event_id"])

            User_States.pop(user_id, None)

            return {
                "status": "success",
                "response": "Meeting cancelled successfully ❌"
            }

        except Exception as e:
            print("ERROR:", str(e))   # 👈 ADD THIS
            return {
                "status": "error",
                "response": f"Error scheduling meeting: {str(e)}",
                "details": state,
                }

    # ------------------ RESCHEDULE INIT ------------------

    if intent == "reschedule":
        
        if not state.get("event_id"):
            return {
            "status": "error",
            "response": "No meeting found to reschedule."
        }
        state["awaiting_reschedule"] = True
        
        # If missing info → ask
        if not (state.get("date") and state.get("time")):
            User_States[user_id] = state
            return {
                "status": "pending",
                "response": "Please provide new date and time to reschedule."
                }

    # ------------------ HANDLE RESCHEDULE ------------------

    if state.get("awaiting_reschedule"):

        missing = _missing_fields(state)

        if missing:
            return {
                "status": "incomplete",
                "response": f"I still need {', '.join(missing)}.",
                "details": state,
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

            state["awaiting_reschedule"] = False
            User_States[user_id] = state

            return {
                "status": "success",
                "response": f"Meeting Rescheduled ✅\n\n🔗 Meet Link: {link}",
                "event_link": link,
                "details": state,
            }

        except Exception as e:
            return {
                "status": "error",
                "response": f"Reschedule failed: {str(e)}"
            }

    # ------------------ MISSING DATA ------------------

    missing = _missing_fields(state)

    if missing:
        return {
            "status": "incomplete",
            "response": f"I still need {', '.join(missing)}.",
            "details": state,
        }

    # ------------------ CONFIRMATION ------------------

    if not state.get("confirmed"):
        return {
            "status": "pending_confirmation",
            "response": (
                f"Please confirm the meeting:\n\n"
                f"📅 Date: {state.get('date')}\n"
                f"⏰ Time: {state.get('time')}\n"
                f"👥 Participants: {', '.join(state.get('participants', []))}\n\n"
                f"Reply with 'confirm' or 'change'."
            ),
            "details": state,
        }

    # ------------------ SCHEDULING ------------------

    try:
        start_datetime = datetime.strptime(
            f"{state['date']} {state['time']}",
            "%Y-%m-%d %H:%M"
        )

        end_datetime = start_datetime + timedelta(
            minutes=state.get("duration_minutes", 60)
        )

        link, event_id = create_event(
            summary=state.get("title") or "Meeting",
            start_time=start_datetime,
            end_time=end_datetime,
            attendees=state.get("participants", [])
        )

        # 🔥 STORE EVENT ID
        state["event_id"] = event_id
        User_States[user_id] = state

        return {
            "status": "success",
            "response": f"Meeting Scheduled ✅\n\n🔗 Meet Link: {link}",
            "event_link": link,
            "details": state,
        }

    except Exception as e:
        return {
            "status": "error",
            "response": f"Error scheduling meeting: {str(e)}",
            "details": state,
        }