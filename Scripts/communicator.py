import datetime
import os.path
from calendar import calendar
from datetime import timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


def add_calendar_event(start_date, end_date, title, description, color_id, notify):
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        start_of_week = datetime.date.today() - timedelta(days=datetime.date.today().weekday())
        now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=start_of_week.strftime("%Y-%m-%dT%H:%M:%SZ"),
                maxResults=30,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return

        # Prints the start and name of the next 10 events
        for event in events:
            try:
                if event["start"].get("dateTime", event["start"].get("dateTime")) == start_date.strftime("%Y-%m-%dT%H:%M:%SZ") and "⍓" in event["description"]:
                    print(f"Deleting {event}")

                    service.events().delete(calendarId="primary", eventId=event['id']).execute()
            except KeyError:
                pass

        # '2024-06-06T09:00:00+00:00'
        s_start_date = start_date.strftime("%Y-%m-%dT%H:%M:00+00:00")
        s_end_date = end_date.strftime("%Y-%m-%dT%H:%M:00+00:00")
        event = {
            'summary': title,
            'location': 'Work',
            'description': description + "\n⍓",
            'colorId': color_id,
            'start': {
                'dateTime': s_start_date,
                'timeZone': 'Europe/London',
            },
            'end': {
                'dateTime': s_end_date,
                'timeZone': 'Europe/London',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 90},
                ],
            },
        }
        event_no_reminder = {
            'summary': title,
            'location': 'Work',
            'description': description + "\n⍓",
            'colorId': color_id,
            'start': {
                'dateTime': s_start_date,
                'timeZone': 'Europe/London',
            },
            'end': {
                'dateTime': s_end_date,
                'timeZone': 'Europe/London',
            },
            'reminders': {
                'useDefault': False,
            },
        }

        event = service.events().insert(calendarId='primary', body=event if notify else event_no_reminder).execute()
        print('Event created: %s' % (event.get('htmlLink')))


    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
  # add_calendar_event(datetime.datetime.now(), datetime.datetime(2024, 6, 5, 17), "Hello", "desc")
    pass