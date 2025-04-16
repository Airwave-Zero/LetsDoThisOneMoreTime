from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re # regular expressions
import os # for local file savings
import time # for sleep to increase c hances of accepted API calls
import csv
import requests


def create_eBay_Soup(card_name):
    # This function handles the entire eBay creation and requests and returns
    # and interaction process and returns a parsed BeautifulSoup object
    base_url = "https://www.ebay.com/sch/i.html"

    # can be modified for further subquerying
    params = {
        "_nkw": f"{card_name} pokemon",
        "_sacat": "0",
        "LH_Sold": "1",
        "LH_Complete": "1",
    }
    # headers to better mimic a real browser that doesn't get requests blocked by eBay
    headers = {
        "User-Agent": "Chrome/122.0.0.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive"
    }

    # establish connection and parse the data
    response = requests.get(base_url, params=params, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    listings = soup.select(".s-item")
    return listings

def extractCardInfo(pageParsed, card_name, max_results):
    # This function takes in the BeautifulSoup object (HTML parsed), card name, and
    # max results and searches through the data to extract a
    # dataframe object containing: card name, price sold at, and date of sale
    # for later PowerBI usage
    
    results = []
    for item in pageParsed[:max_results]:
        name_tag = item.select_one(".s-item__title") # item listing name
        price_tag = item.select_one(".s-item__price") # price sold at
        date_tag = item.select_one(".s-item__caption") # date sold (no timestamp)

        # pass over incomplete sales data for clarity
        if not name_tag and not price_tag and not date_tag:
            continue 

        name_text = name_tag.get_text()

        # ensure card name is in the sale
        if card_name not in name_text:
            continue 
        
        price_text = price_tag.get_text()
        price_match = re.search(r"[\d,.]+", price_text)
        price = float(price_match.group().replace(",", "")) if price_match else None

        date_text = date_tag.get_text()
        date_match = re.search(r"(\w+ \d{1,2}, \d{4}(?:, \d{1,2}:\d{2} [APMapm]{2})?)", date_text)

        # A bit of an edge case, but some listings don't have a sold date for some reason, so filtering those out
        if date_match:
            try:
                sold_date = datetime.strptime(date_match.group(), "%b %d, %Y, %I:%M %p")
            except ValueError:
                sold_date = datetime.strptime(date_match.group(), "%b %d, %Y")
            if sold_date:
                results.append({
                    "Card Name": name_text,
                    "Sold Price": price,
                    "Sold Date": sold_date
                })
        else:
            None
            
    return pd.DataFrame(results)

def drop_duplicates(new_data, existing_data):
    # Normalize 'Sold Date' to date only (no time component)
    existing_data["Sold Date"] = pd.to_datetime(existing_data["Sold Date"]).dt.date

    # Create unique keys for existing entries
    existing_keys = set(
        existing_data.apply(lambda row: f"{row['Card Name']}|{row['Sold Price']}|{row['Sold Date']}", axis=1)
    )

    # Filter new data
    new_data["Sold Date"] = pd.to_datetime(new_data["Sold Date"]).dt.date
    new_data["Unique Key"] = new_data.apply(
        lambda row: f"{row['Card Name']}|{row['Sold Price']}|{row['Sold Date']}", axis=1
    )
    filtered_data = new_data[~new_data["Unique Key"].isin(existing_keys)].drop(columns=["Unique Key"])
    
    return filtered_data

def track_price_history(card_names, history_path, max_results=25):
    # High level function that handles overall control flow of script
    # 1) Make connection and look up the card on eBay
    # 2) Extract the posting name, date, and price sold
    # 3) Transform the data a bit and remove duplicates
    # 4) Output the non-duplicates into the csv data
    
    all_data = []
    
    for card in card_names:
        pageSoup = create_eBay_Soup(card)
        df = extractCardInfo(pageSoup, card, max_results)
        df["Scrape Timestamp"] = datetime.now().strftime("%#m/%#d/%Y %#I:%M:%S %p")
        all_data.append(df)
        time.sleep(1) # help with avoiding timeouts/bad HTTP requests
        
    new_data = pd.concat(all_data, ignore_index=True)

    if os.path.exists(history_path):
        existing_data = pd.read_csv(history_path)
    else:
        existing_data = pd.DataFrame(columns=["Card Name", "Sold Price", "Sold Date", "Scrape Timestamp"])

    # Drop duplicates using the existing data
    filtered_data = drop_duplicates(new_data, existing_data)

    # drop empty columns to prevent future errors
    existing_data = existing_data.dropna(axis=1, how='all') 
    filtered_data = filtered_data.dropna(axis=1, how='all')

    # Check if filtered_data is empty or all NA values before concatenating
    if not filtered_data.empty:
        updated_data = pd.concat([existing_data, filtered_data], ignore_index=True)
        updated_data = updated_data.dropna(how='all')
        updated_data.to_csv(history_path, index=False)
        print(f"[✔] Logged {len(filtered_data)} new entries to {history_path}")
        return updated_data
    else:
        print("[⚠️] No new valid entries to log.")
        return existing_data

cards = ["Umbreon"]
track_price_history(cards, "ebay_prices_history.csv", 55)
