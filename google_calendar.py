import datetime
from googleapiclient.discovery import build
from google_auth import get_credentials
from config import settings

credentials_file = settings.GOOGLE_CREDENTIALS_FILE
token_file = settings.GOOGLE_TOKEN_FILE

def _build_service():
    creds = get_credentials()
    return build("calendar", "v3", credentials=creds)

def create_event(summary, start_time, end_time, attendees):
    service = _build_service()

    event = {
        "summary": summary,
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
        "attendees": [{"email": email} for email in attendees],
        "conferenceData": {
            "createRequest": {
                "requestId": "meeting-123",
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
    }
    
    created_event = service.events().insert(
        calendarId="primary",
        body=event,
        conferenceDataVersion=1,
        sendUpdates="all",
    ).execute()

    # Google Calendar API uses "htmlLink" (capital L). Some events also include a Meet link.
    link = (
        created_event.get("htmlLink")
        or created_event.get("hangoutLink")
        or created_event.get("conferenceData", {})
        .get("entryPoints", [{}])[0]
        .get("uri")
    )
    event_id = created_event.get("id")
    return link, event_id

def update_event(event_id, summary, start_time, end_time, attendees):
    service = _build_service()

    event = service.events().get(calendarId="primary", eventId=event_id).execute()

    event["summary"] = summary
    event["start"]["dateTime"] = start_time.isoformat()
    event["start"]["timeZone"] = "Asia/Kolkata"
    event["end"]["dateTime"] = end_time.isoformat()
    event["end"]["timeZone"] = "Asia/Kolkata"
    event["attendees"] = [{"email": email} for email in attendees]

    updated_event = (
        service.events()
        .update(
            calendarId="primary",
            eventId=event_id,
            body=event,
            sendUpdates="all",
        )
        .execute()
    )

    link = (
        updated_event.get("htmlLink")
        or updated_event.get("hangoutLink")
        or updated_event.get("conferenceData", {})
        .get("entryPoints", [{}])[0]
        .get("uri")
    )
    return link


def cancel_event(event_id):
    service = _build_service()
    service.events().delete(
        calendarId="primary",
        eventId=event_id,
        sendUpdates="all",
    ).execute()