import os
import base64
import pandas as pd
from datetime import datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ----------------------- CONFIGURATION -----------------------
DB_CONFIG = {
    "dbname": "your_db",
    "user": "your_user",
    "password": "your_password",
    "host": "localhost"
}
CSV_OUTPUT_PATH = "emails_export.csv"

# ----------------------- GMAIL API SETUP ---------------------
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

# -------------------- CLASSIFICATION LOGIC -------------------
def classify_email(subject, body):
    # TODO: use a model to classify email for me and return the info

def extract_company(subject, sender):
    # TODO: get company name 

# ------------------ GMAIL MESSAGE HANDLING -------------------
def get_email_data(service):
    emails = []
    # TODO: get all the important info like content, sender, date, etc.
    return emails

# --------------------- DATABASE EXPORT -----------------------
def export_to_postgresql(emails):
    #  TODO: export information to postgresql for easier db usage

# ----------------------- CSV EXPORT --------------------------
def export_to_csv(emails):
    df = pd.DataFrame(emails)
    df.to_csv(CSV_OUTPUT_PATH, index=False)

# ------------------------- MAIN ------------------------------
def main():
    service = authenticate_gmail()
    emails = get_email_data(service)
    export_to_postgresql(emails)
    export_to_csv(emails)
    print(f"Exported {len(emails)} emails to PostgreSQL and CSV.")

if __name__ == '__main__':
    main()
