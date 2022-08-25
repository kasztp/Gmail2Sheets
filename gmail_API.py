from base64 import urlsafe_b64decode
import os.path
import re
from quopri import decodestring
import html2text

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
PATH = os.path.abspath(os.path.dirname(__file__))


def remove_html_tags(text):
    """Remove html tags from a string"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(f'{PATH}/token.json'):
        creds = Credentials.from_authorized_user_file(f'{PATH}/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                f'{PATH}/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(f'{PATH}/token.json', 'w', encoding='utf-8') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        messages = service.users().messages().list(userId='me').execute()

        print('Messages:')
        for message in messages['messages'][50:61]:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            print(msg['snippet'])
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts'][0:1]:
                    if part['mimeType'] == 'text/plain':
                        print('\nText:\n')
                        try:
                            print(decodestring(urlsafe_b64decode(part['body']['data']))
                            .decode('utf-8'))
                        except UnicodeDecodeError as error:
                            print('error:', error)
                            print(decodestring(urlsafe_b64decode(part['body']['data']))
                            .decode('iso-8859-2'))
                    elif part['mimeType'] == 'text/html':
                        print('\nHTML:\n')
                        try:
                            print(html2text.html2text(
                                decodestring(urlsafe_b64decode(part['body']['data']))
                                .decode('utf-8')))
                        except UnicodeDecodeError as error:
                            print('error:', error)
                            print(html2text.html2text(
                                decodestring(urlsafe_b64decode(part['body']['data']))
                                .decode('iso-8859-2')))
        
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()
