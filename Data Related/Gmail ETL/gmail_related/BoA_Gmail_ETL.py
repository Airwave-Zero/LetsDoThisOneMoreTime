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
POSTGRE_SQL_PASSWORD_PATH = "postgre_secret.txt"

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
    positive_query = ['from: onlinebanking@ealerts.bankofamerica.com subject: deposit',
                      'from: bank of america subject: "sent you"',
                      'from: venmo subject: "paid you"',
                      'from: venmo subject: "transfer"',]
    posFlag = queryStatement in positive_query # fairly hard coded but works because we know exactly what the exact subjects are
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
            emails.append({
                'date': date_received_at,
                'amount': amount, # this should be a positive or negative number
                'queryStatement': queryStatement
            })
        print("Extracted " + str(len(emails)) + '/' + str(num_emails) + " emails...")
        next_page_token = results.get('nextPageToken')
        if not next_page_token:
            break
    return emails

def export_to_postgresql(emails):
    '''Exports the email list into the database table'''
    userPassword = open(POSTGRE_SQL_PASSWORD_PATH).read()
    DB_CONFIG['password'] = userPassword
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        # Create table if it doesn't exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS BoA_Reporter (
            id SERIAL PRIMARY KEY,
            date TIMESTAMP,
            amount DECIMAL,
            queryStatement TEXT
        );
        """
        try:
            cur.execute(create_table_query)
        except Exception as e:
            print("Failed to create table")
            print(f"Error: {e}")
            conn.rollback()
            cur.close()
            conn.close()
            return
        
        insert_query = """
        INSERT INTO BoA_Reporter (date, amount, queryStatement)
        VALUES (%s, %s, %s)
        """
        try:
            data = [(row.date, row.amount, row.queryStatement) for row in emails.itertuples(index=False)]
            cur.executemany(insert_query, data)
        except Exception as e:
            print("Failed to export emails to PostgreSQL")
            print(f"Error: {e}")
            conn.rollback()
            cur.close()
            conn.close()
            return
        conn.commit()
        print("Export to PostgreSQL completed successfully.")
    except Exception as conn_error:
        print("Database connection failed.")
        print(f"Error: {conn_error}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def get_starting_info(filepath, lookFor):
    ''' Function tha reads in the starting balance to work with, returns
    either a date string or a balance string '''
    df = pd.read_csv(filepath)
    if lookFor == "balance":
        balanceValue = str(df.iloc[-1]['balance']); # should be a string, but just in case
        print("Last known balance: " + balanceValue
        return float(balanceValue.replace('$', '').replace(',', '').strip()) # clean it so it's purely a number
    elif lookFor == "date":
        dateValue = str(df.iloc[-1]['date'])
        print("Accessing from last known date: " + dateValue)
        return dateValue

def export_emails_to_csv(df_emails, old_df):
    ''' Outputs the email list into a csv, ideally for usage in PowerBI, and returns the dataframe for later use '''
    df = pd.DataFrame(df_emails)
    combined_df = pd.concat([df, old_df], ignore_index=True)
    df['date'] = pd.to_datetime(df['date'])           
    df = df.sort_values('date', ascending=False)
    df['date'] = df['date'].dt.strftime('%#m/%#d/%Y %#H:%M') # clean up and set as strings after sorted by date
    df = df.drop_duplicates() # just in case
    df.to_csv(CHANGES_CSV_OUTPUT_PATH, index=False)
    return df # return the "complete" full data with no duplicates

def export_balance_to_csv(curr_date, new_balance):
    df = pd.read_csv(BALANCE_CSV_OUTPUT_PATH)
    new_data = pd.DataFrame([
        {
        'date': curr_date,
        'balance': f"${new_balance:,.2f}"
        }])
    df = pd.concat([df, new_data], ignore_index=True)
    try:
        df.to_csv(BALANCE_CSV_OUTPUT_PATH, index=False)
    except PermissionError:
        print("Cannot write to the file. Make sure it's not open.")

def main():
    print("Running the super fancy banking script...")
    num_emails = 1000
    try:
        print("Attempting to establish secure connection to Gmail...")
        service = get_gmail_service()
    except Exception as e:
        print("Failed to establish connection to Gmail API...")
        print(f"Error: {e}")
        return
    
    print(f"Securely connected to Gmail API! Attempting to retrieve {num_emails} emails now...")
    email_queries =
    [ 'from: onlinebanking@ealerts.bankofamerica.com subject: deposit', # positive
    'from: bank of america subject: "sent you"', # positive
    'from: bank of america subject: account alert: debit card used online', # negative
    'from: bank of america subject: credit card not present during this transaction', # negative
    'from: bank of america subject: credit card transaction exceeds alert limit you set',# negative
    'from: bank of america subject: "Activity Alert: Online Transfer Over Your Requested Alert Limit"', # negative
    'from: bank of america subject: zelle "has been sent "', # negative
    'from: venmo subject: "paid you"', # positive
    'from: venmo subject: "transfer"', # positive
    'from: venmo subject: "you paid"' ] # negative
    starting_balance = get_starting_info(BALANCE_CSV_OUTPUT_PATH, "balance")
    starting_date = datetime.strptime(get_starting_info(BALANCE_CSV_OUTPUT_PATH, "date"), "%m/%d/%Y")
    old_data = pd.read_csv(CHANGES_CSV_OUTPUT_PATH)
    date_now = datetime.now().strftime('%#m/%#d/%Y')
    
    all_emails = []
    # Doing a nested for loop b/c # of operations is the same, not O(n^2) vs two for loops
    for query in email_queries:
        queried_emails = get_email_data(service, num_emails, query)
        for email in queried_emails:
            if email.get('date') and email['date'].tzinfo is not None:
                email['date'] = email['date'].astimezone(timezone.utc).replace(tzinfo=None)
            all_emails.append(email)
    # we only care about updating the balances after the last known one
    new_balance = starting_balance + sum(email['amount'] for email in all_emails if email['date'] > starting_date) 
    
    print("Emails retrieved...now exporting to PostgreSQL and csv...")
    df_emails = export_emails_to_csv(all_emails, old_data)
    export_balance_to_csv(date_now, new_balance)
    export_to_postgresql(df_emails)

if __name__ == '__main__':
    main()
