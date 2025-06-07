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

DB_CONFIG = {
    "dbname": "BoA Reporter",
    "user": "postgres",
    "password": "",
    "host": "localhost",
    "port": "5432"
}
CHANGES_CSV_OUTPUT_PATH = "../csv_data/account_balance_changes.csv"
BALANCE_CSV_OUTPUT_PATH = "../csv_data/account_balance_snapshots.csv"

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
    token_path = 'bank_token.pickle'
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

    
def get_email_data(service, num_emails, queryStatement = ''):
    '''This function interacts with the Gmail API and pulls out the desired
    number of emails from the users inbox, and extracts the metadata from it
    and returns a list of all the information'''
    emails = []
    next_page_token = None
    #category = {"deposit": 1, "withdrawal":-1}
    positive_query = ['from: onlinebanking@ealerts.bankofamerica.com subject: deposit',
                      'from: bank of america subject: "sent you"',
                      'from: venmo subject: "paid you"',
                      'from: venmo subject: "transfer"',]

    # determine if the amount found is positive or negative; fairly hard coded but works because we know exactly what is being queried
    posFlag = queryStatement in positive_query
    print("Currently searching for: '" + queryStatement + "'...")
    while len(emails) < (num_emails):
        maxResultsPerBatch = min(100, num_emails - len(emails))
        results = service.users().messages().list(userId='me', q=queryStatement,
                                              maxResults=maxResultsPerBatch,
                                                  pageToken = next_page_token).execute()
        messages = results.get('messages', [])
        for msg in messages:
            msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
            payload = msg_detail.get('payload', {})
            headers = payload.get('headers', [])

            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')                
            date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            try:
                cleaned = date_str.split(' (')[0].strip()
                date_received_at = parser.parse(cleaned, tzinfos=tzinfos)
            except:
                print(f"Warning: Failed to parse date from: {date_str}")
                date_received_at = None

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
            amount = None            
            amount_re = re.search(r'\$\s*(-?\d{1,3}(?:,\d{3})*|\d+)(\.\d{2})?', body, re.IGNORECASE)
            if amount_re:
                try:
                    # Clean and convert the extracted amount
                    whole = amount_re.group(1)  # e.g., '1,234'
                    cents = amount_re.group(2) or '.00'  # e.g., '.56'
                    value_str = whole.replace(',', '') + cents  # e.g., '1234.56'
                    amount = float(value_str)
                    amount = abs(amount) if posFlag else -abs(amount) # adjust based on spending or depositing money
                except ValueError:
                    print(f"Failed to parse amount from: {match.group(0)}")
            ### put extraction code here to parse the body and get the amount and whether its + or
            emails.append({
                'date': date_received_at,
                'amount': amount, # this should be a positive or negative number
                'queryStatement': queryStatement
                # 'category': category this is a future improvement, use AI to categorize what kind of expenditure it is for data-logging purposes
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
    CREATE TABLE IF NOT EXISTS transaction_emails (
        id SERIAL PRIMARY KEY,
        date TIMESTAMP,
        amount DECIMAL,
        queryStatement TEXT
    """
    cur.execute(create_table_query)
    
    for email in emails:
        insert_query = """
        INSERT INTO transaction_emails (date, amount, queryStatement)
        VALUES (%s, %s, %s)"""
        cur.execute(insert_query, (
                email['date'],
                email['amount'],
                email['queryStatement']))
    conn.commit()
    cur.close()
    conn.close()

def export_emails_to_csv(df_emails):
    ''' Outputs the email list into a csv, ideally for usage in PowerBI'''
    # Ensure all datetimes are tz-naive before creating the DataFrame
    for email in df_emails:
        if email['date'] and email['date'].tzinfo is not None:
            email['date'] = email['date'].astimezone(timezone.utc).replace(tzinfo=None)
    df = pd.DataFrame(df_emails)
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%#m/%#d/%Y %#H:%M')
    df = df.sort_values('date', ascending = False)
    df.to_csv(CHANGES_CSV_OUTPUT_PATH, index=False)

def get_starting_balance(filepath):
    df = pd.read_csv(filepath)
    most_recent_balance = df.iloc[-1]['balance']
    return most_recent_balance

def export_balance_to_csv(curr_date, new_balance):
    df = pd.read_csv(BALANCE_CSV_OUTPUT_PATH)
    new_data = pd.DataFrame([
        {
        'date': curr_date,
        'balance': new_balance
        }])
    df = pd.concat([df, new_data], ignore_index=True)
    try:
        df.to_csv(BALANCE_CSV_OUTPUT_PATH, index=False)
    except PermissionError:
        print("Cannot write to the file. Make sure it's not open.")

def main():
    print("Running the super fancy banking script...")
    num_emails = 50
    try:
        print("Attempting to establish secure connection to Gmail...")
        service = get_gmail_service()
    except Exception as e:
        print("Failed to establish connection to Gmail API...")
        print(f"Error: {e}")
        return
    
    print(f"Securely connected to Gmail API! Attempting to retrieve {num_emails} emails now...")

    email_queries = ['from: onlinebanking@ealerts.bankofamerica.com subject: deposit',
    'from: bank of america subject: "sent you"',
    'from: bank of america subject: account alert: debit card used online',
    'from: bank of america subject: credit card not present during this transaction',
    'from: bank of america subject: zelle "has been sent "',
    'from: venmo subject: "paid you"',
    'from: venmo subject: "transfer"',
    'from: venmo subject: "you paid"']
    all_emails = []    
    for query in email_queries:
        queried_emails = get_email_data(service, num_emails, query) # look up all the emails
        all_emails.extend(queried_emails)
    #df_emails.to_csv('lol.csv', index=False)
    #print(df_emails)
    #starting_balance = get_starting_balance(BALANCE_CSV_OUTPUT_PATH)
    #new_balance = starting_balance + df_emails['balances'].sum()
    #date_now = datetime.now().strftime('%#m/%#d/%Y %#H:%M')
    
    print("Emails retrieved...now exporting to PostgreSQL and csv...")
    #export_to_postgresql(df_emails)
    export_emails_to_csv(all_emails)
    #export_balance_to_csv(spending_amounts, starting_balance)
    #print(f"Exported {len(df_emails)} emails to PostgreSQL and CSV.")

if __name__ == '__main__':
    main()
