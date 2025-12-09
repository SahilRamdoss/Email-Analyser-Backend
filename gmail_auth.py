from __future__ import print_function
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from dotenv import load_dotenv, dotenv_values

# Loading the environment variables
load_dotenv()

# Getting the environment variable for the SCOPE used for the GMAIL API
GMAIL_SCOPE = os.getenv('GMAIL_SCOPE')

SCOPES = [GMAIL_SCOPE]

# Giving access to email account and creating token.json file
def authorize_gmail():
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file( 'credentials.json', SCOPES)
            creds = flow.run_local_server(port = 0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

if __name__ == "__main__":
    authorize_gmail()
    print("Done! token.json saved")