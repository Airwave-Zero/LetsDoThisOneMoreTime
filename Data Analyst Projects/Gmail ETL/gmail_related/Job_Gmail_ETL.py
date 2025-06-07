import os
import sys
import base64
import re
import pickle
import psycopg2
import pandas as pd
from datetime import datetime, timezone
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from dateutil import parser

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # needed for finding parent folders
import ML_model.LogisticRegression_Model as ML

DB_CONFIG = {
    "dbname": "Email Categorizer",
    "user": "postgres",
    "password": "",
    "host": "localhost",
    "port": "5432"
}
CSV_OUTPUT_PATH = "../csv_data/Categorized Emails.csv"

scope = ['https://www.googleapis.com/auth/gmail.readonly']

tzinfos = {
    'PDT': -7 * 3600,  # UTC-7
    'PST': -8 * 3600,  # UTC-8
    'EDT': -4 * 3600,  # UTC-4
    'EST': -5 * 3600,  # UTC-5
    'CDT': -5 * 3600,  # UTC-5
    'CST': -6 * 3600,  # UTC-6
    'MDT': -6 * 3600,  # UTC-6
    'MST': -7 * 3600,  # UTC-7
}

def get_gmail_service():
    '''This function serves to authenticate and return a Gmail API service client
    with OAuth2.0. This function looks for existing user credentials, and if not found,
    prompts the user to sign in and give the application access to their acount (which is
    then saved)'''
    creds = None
    token_path = 'job_token.pickle'
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

def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, 'html.parser')
    return soup.get_text(separator=' ', strip=True)

def get_text_from_parts(parts, preferred_type='text/plain'):
    for part in parts:
        mime_type = part.get('mimeType')
        if mime_type == preferred_type:
            data = part['body'].get('data')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        elif mime_type.startswith('multipart'):
            sub_parts = part.get('parts', [])
            result = get_text_from_parts(sub_parts, preferred_type)
            if result:
                return result
    return None

def get_email_data(service, num_emails):
    '''This function interacts with the Gmail API and pulls out the desired
    number of emails from the users inbox, and extracts the metadata from it
    and returns a list of all the information'''
    emails = []
    next_page_token = None
    ML_model = ML.load_model()

    while len(emails) < (num_emails):
        maxResultsPerBatch = min(100, num_emails - len(emails))
        results = service.users().messages().list(userId='me', q='application',
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
                cleaned = date_str.split(' (')[0].strip()
                received_at = parser.parse(cleaned, tzinfos=tzinfos)
            except:
                print(f"Warning: Failed to parse date from: {date_str}")
                received_at = None

            parts = payload.get('parts', [])

            # Handle various email formats and record them in the csv
            if parts:
                body = get_text_from_parts(parts, 'text/plain')
                if not body:
                    html_data = get_text_from_parts(parts, 'text/html')
                    if html_data:
                        body = clean_html(html_data)
            else:
                # fallback
                if payload.get('mimeType') == 'text/plain':
                    data = payload['body'].get('data')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                elif payload.get('mimeType') == 'text/html':
                    data = payload['body'].get('data')
                    if data:
                        html = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                        body = clean_html(html)
                        
            # Use the trained model to categorize the email being read based on subject and body
            text = f"{subject} {body}"
            category = ML_model.predict([text])[0]

            emails.append({
                'sender': sender,
                'subject': subject,
                'body': body,
                'received_at': received_at,
                'category': category
            })
            
        print("Extracted " + str(len(emails)) + '/' + str(num_emails) + " emails...")
        next_page_token = results.get('nextPageToken')
        if not next_page_token:
            break
    return emails

def export_to_postgresql(emails):
    '''Exports the email list into the database table'''
    userPassword = input("Please input your password for postgres:\n")
    DB_CONFIG['password'] = userPassword
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Create the table if it doesn't exist
    create_table_query = """
    CREATE TABLE IF NOT EXISTS emails (
        id SERIAL PRIMARY KEY,
        sender TEXT,
        subject TEXT,
        body TEXT,
        received_at TIMESTAMPTZ,
        category TEXT
    );
    """
    cur.execute(create_table_query)

    
    for email in emails:
        insert_query = """
        INSERT INTO emails (sender, subject, body, received_at, category)
        VALUES (%s, %s, %s, %s, %s)"""
        cur.execute(insert_query, (
                email['sender'],
                email['subject'],
                email['body'],
                email['received_at'],
                email['category']))
    conn.commit()
    cur.close()
    conn.close()

def export_to_csv(emails):
    ''' Outputs the email list into a csv, ideally for usage in PowerBI'''
    # Ensure all datetimes are tz-naive before creating the DataFrame
    for email in emails:
        if email['received_at'] and email['received_at'].tzinfo is not None:
            email['received_at'] = email['received_at'].astimezone(timezone.utc).replace(tzinfo=None)
    df = pd.DataFrame(emails)
    df['received_at'] = pd.to_datetime(df['received_at']).dt.strftime('%#m/%#d/%Y %#H:%M')
    df.to_csv(CSV_OUTPUT_PATH, index=False)
    
def main():
    num_emails = 50
    print("Running the super fancy job script...")
    try:
        print("Attempting to establish secure connection to Gmail...")
        service = get_gmail_service()
    except Exception as e:
        print("Failed to establish connection to Gmail API...")
        print(f"Error: {e}")
        return
    print(f"Securely connected to Gmail API! Attempting to retrieve {num_emails} emails now...")
    emails = get_email_data(service, num_emails)
    print("Emails retrieved...now exporting to PostgreSQL and csv...")
    export_to_postgresql(emails)
    export_to_csv(emails)
    print(f"Exported {len(emails)} emails to PostgreSQL and CSV.")



if __name__ == '__main__':
    main()
