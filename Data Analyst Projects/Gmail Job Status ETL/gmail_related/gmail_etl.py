import os
import base64
import re
import pickle
# import psycopg2
import pandas as pd
from datetime import datetime, timezone
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
    return

def extract_company(subject, sender):
    # TODO: get company name


# ------------------ GMAIL MESSAGE HANDLING -------------------
def get_email_data(service, num_emails):
    '''This function interacts with the Gmail API and pulls out the desired
    number of emails from the users inbox, and extracts the metadata from it
    and returns a list of all the information'''
    emails = []
    next_page_token = None

    while len(emails) < (num_emails):
        maxResultsPerBatch = min(100, num_emails - len(emails))
        results = service.users().messages().list(userId='me', q='',
                                              maxResults=maxResultsPerBatch,
                                                  pageToken = next_page_token).execute()
        messages = results.get('messages', [])
        for msg in messages:
            msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
            payload = msg_detail.get('payload', {})
            headers = payload.get('headers', [])

            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
            date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            try:
                received_at = datetime.strptime(date_str[:-6], '%a, %d %b %Y %H:%M:%S')
            except:
                received_at = datetime.now(timezone.utc)

            parts = payload.get('parts', [])
            body = ''
            if parts:
                for part in parts:
                    if part.get('mimeType') == 'text/plain':
                        data = part['body'].get('data')
                        if data:
                            body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                            break  # Use first plain-text part only
            else:
                # fallback: check top-level body
                if payload.get('mimeType') == 'text/plain':
                    data = payload['body'].get('data')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')

            #company = extract_company(subject, sender)
            #category = classify_email(subject, body)

            emails.append({
                'sender': sender,
                'subject': subject,
                'body': body,
                'received_at': received_at
                #'company': company,
                #'category': category
            })
        print("Extracted " + str(len(emails)) + '/' + str(num_emails) + " emails...")
        next_page_token = results.get('nextPageToken')
        if not next_page_token:
            break
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
    num_emails = 250
    try:
        print("Attemtping to establish secure connection to Gmail...")
        service = get_gmail_service()
    except Exception as e:
        print("Failed to establish connection to Gmail API...")
        print(f"Error: {e}")        
    print(f"Securely connected to Gmail API! Beginning retrieval of {num_emails} emails now...")
    emails = get_email_data(service, num_emails)
    print("Emails retrieved...now exporting to PostgreSQL and csv...")
    # export_to_postgresql(emails)
    export_to_csv(emails)
    print(f"Exported {len(emails)} emails to PostgreSQL and CSV.")



if __name__ == '__main__':
    main()
