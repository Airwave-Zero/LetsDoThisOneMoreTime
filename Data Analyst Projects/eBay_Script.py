import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re

def scrape_ebay_sold(card_name, max_results=10):
    base_url = "https://www.ebay.com/sch/i.html"
    params = {
        "_nkw": f"{card_name} pokemon",
        "_sacat": "0",
        "LH_Sold": "1",
        "LH_Complete": "1",
    }

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(base_url, params=params, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    listings = soup.select(".s-item")
    results = []

    for item in listings[:max_results]:
        title_tag = item.select_one(".s-item__title")
        price_tag = item.select_one(".s-item__price")
        date_tag = item.select_one(".s-item__title--tagblock")

        if not title_tag or not price_tag:
            continue

        title = title_tag.get_text()
        price_text = price_tag.get_text()
        price_match = re.search(r"[\d,.]+", price_text)
        price = float(price_match.group().replace(",", "")) if price_match else None

        date_text = date_tag.get_text() if date_tag else ""
        date_match = re.search(r"(\w+ \d{1,2}, \d{4})", date_text)
        sold_date = datetime.strptime(date_match.group(), "%b %d, %Y") if date_match else None

        results.append({
            "Card Name": card_name,
            "Title": title,
            "Sold Price": price,
            "Sold Date": sold_date,
            "Source": "eBay"
        })

    return pd.DataFrame(results)
cards = ["Charizard", "Pikachu", "Umbreon"]
df_all = pd.concat([scrape_ebay_sold(card) for card in cards], ignore_index=True)

# Optional: Save to CSV or return to Power BI
df_all.to_csv("ebay_sold_prices.csv", index=False)

from datetime import datetime
import os

def track_price_history(card_names, history_path="ebay_prices_history.csv", max_results=10):
    all_data = []

    for card in card_names:
        df = scrape_ebay_sold(card, max_results)
        df["Scrape Timestamp"] = datetime.now()
        all_data.append(df)

    new_data = pd.concat(all_data, ignore_index=True)

    if os.path.exists(history_path):
        existing_data = pd.read_csv(history_path)
        updated_data = pd.concat([existing_data, new_data], ignore_index=True)
    else:
        updated_data = new_data

    updated_data.to_csv(history_path, index=False)
    print(f"[✔] Logged {len(new_data)} new entries to {history_path}")
    return updated_data
