from googleapiclient.discovery import build
from google_auth import get_credentials

def test_calendar():
    creds = get_credentials()
    service = build("calendar", "v3", credentials=creds)

    events_result = service.events().list(
        calendarId = "primary",
        maxResults = 5,
        singleEvents = True,
        orderBy = "startTime",
    ).execute()

    events = events_result.get("items", [])

    print("Upcoming Events:")
    for event in events:
        print(event.get("summary"))

if __name__ == "__main__":
    test_calendar()