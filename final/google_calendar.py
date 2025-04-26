from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def create_calendar_event(event_details, service_account_json, user_email):
    try:
        credentials = service_account.Credentials.from_service_account_info(service_account_json)
        service = build('calendar', 'v3', credentials=credentials)
        event = service.events().insert(calendarId=user_email, body=event_details).execute()
        print('Event created: %s' % (event.get('htmlLink')))
        return event
    except HttpError as error:
        error_content = error.content.decode('utf-8')
        if error.resp.status == 404:
            return {'success': False, 'message': 'Allow access to your calendar, Give mealplanner@cloud-puttaswamyballari-varshi.iam.gserviceaccount.com email create event access in your calendar'}
            print(f'Calendar access required: {error_content}')
        else:
            print(f'An HTTP error occurred: {error_content}')
        return None
    except Exception as error:
        print(f'An unexpected error occurred: {error}')
        return None

