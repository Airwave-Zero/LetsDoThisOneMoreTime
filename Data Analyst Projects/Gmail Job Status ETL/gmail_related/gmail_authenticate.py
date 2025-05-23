import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

scope = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    '''This function serves to authenticate and return a Gmail API service client
    with OAuth2.0. This function looks for existing user credentials, and if not found,
    prompts the user to sign in and give the application access to their acount (which is
    then saved)'''
    creds = None
    token_path = 'token.pickle'
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('gmail_json_secret.json', scope)
            creds = flow.run_local_server(port=0)
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds) # Gmail API service

get_gmail_service()
