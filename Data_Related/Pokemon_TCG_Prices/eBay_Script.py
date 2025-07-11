def create_eBay_Soup(card_name):
    ''' This function handles the entire eBay creation and requests and returns
        and interaction process and returns a parsed BeautifulSoup object '''
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

def normalize_card_name(title):
    ''' Function to clean up the posting names a bit'''
    title = title.lower()

    # Remove grading terms
    title = re.sub(r'\bpsa\s?\d+|\bcgc\s?\d+|\bbgs\s?\d+|\bsgc\s?\d+', '', title)

    # Remove condition tags
    title = re.sub(r'\b(nm|lp|mp|hp|damaged|graded|mint|lightly played|moderately played|heavily played)\b', '', title)

    # Remove common fluff
    title = re.sub(r'\b(pokemon|card|tcg|holo|foil|reverse|full art|rare|ultra|english|japanese|promo|202\d|19\d{2})\b', '', title)

    # Remove special characters and trim
    title = re.sub(r'[^a-z0-9\s]', '', title)
    title = re.sub(r'\s+', ' ', title).strip()

    return title

def extractCardInfo(pageParsed, card_name, max_results):
    ''' This function takes in the BeautifulSoup object (HTML parsed), card name, and
        max results and searches through the data to extract a
        dataframe object for later PowerBI usage containing:
        normalized card name, listing name, price sold at, and date of sale '''
    
    results = []
    for item in pageParsed[:max_results]:
        name_tag = item.select_one(".s-item__title") # item listing name
        price_tag = item.select_one(".s-item__price") # price sold at
        date_tag = item.select_one(".s-item__caption") # date sold (no timestamp)

        # only proceed if data has necessary info
        if name_tag and price_tag and date_tag:
            name_text = name_tag.get_text()

            # ensure card name is in the sale
            if card_name in name_text:
                name_text = normalize_card_name(name_text) # clean up the posting name a bit
                
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
                            "Normalized Card Name": card_name,
                            "Card Name": name_text,
                            "Sold Price": price,
                            "Sold Date": sold_date
                        })
    return pd.DataFrame(results)

def drop_duplicates(new_data, card_name, history_path):
    ''' This function checks for duplicates in the csv for the current card'''

    # Generates the file path to check for the specific card name csv
    card_file_path = os.path.join(history_path, f"{card_name.replace(' ', '_').replace('/', '_')}.csv")

    if os.path.exists(card_file_path):
        existing_data = pd.read_csv(card_file_path)
        if not existing_data.empty:
            # Generate a set of keys for cards already inputted, we are using Listing Name, Price, and Date as a unique kkey
            existing_keys = set(
                existing_data.apply(lambda row: f"{row['Card Name']}|{row['Sold Price']}|{row['Sold Date']}", axis=1)
            )
        else:
            existing_keys = set()
    else:
        # Otherwise no keys to verify against
        existing_keys = set()

    # Normalize new data "Sold Date" for comparison, avoid duplicates
    new_data["Sold Date"] = pd.to_datetime(new_data["Sold Date"]).dt.date
    
    new_data["Unique Key"] = new_data.apply(
        lambda row: f"{row['Card Name']}|{row['Sold Price']}|{row['Sold Date']}", axis=1
    )
    
    # Filter out records that already exist
    filtered_data = new_data[~new_data["Unique Key"].isin(existing_keys)].drop(columns=["Unique Key"])
    
    return filtered_data

def get_existing_data(file_path, filtered_df):
    '''This function retrieves the existing data in the card CSV'''
    
    # Load existing data and combine with filtered new data
    if os.path.exists(file_path):
        existing_data = pd.read_csv(file_path)
    else:
        existing_data = pd.DataFrame(columns=filtered_df.columns)

    # Clean and remove empty columns for avoiding future warnings
    existing_data = existing_data.dropna(axis=1, how='all')
        
    return existing_data


def track_price_history(card_names, folder_path, max_results=25):
    ''' High-level function that handles overall control flow of script
    0) Make a folder for the csv's to be saved into
    1) Make connection and look up the card on eBay
    2) Extract the posting name, date, and price sold
    3) Transform the data a bit, adding normalized names and dates, remove empties
    4) Remove duplicates
    5) Combine (now clean) new data and old data
    6) Output card data to specific csv
    '''

    # Create output folder
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    all_data = []

    for card in card_names:
        print(f"Currently scraping data for: {card}")
        
        # Scrape eBay data
        pageSoup = create_eBay_Soup(card)
        df = extractCardInfo(pageSoup, card, max_results)
        df["Scrape Timestamp"] = datetime.now().strftime("%#m/%#d/%Y %#I:%M:%S %p")
        df = df.dropna(axis=1, how='all') # Clean and remove empty columns for avoiding future warnings
        
        filtered_df = drop_duplicates(df, card, folder_path)
        
        safe_card_name = card.replace(" ", "_").replace("/", "_")
        file_path = os.path.join(folder_path, f"{safe_card_name}.csv")

        # Read into existing csv or create new ones       
        existing_data = get_existing_data(file_path, filtered_df)
        
        combined_data = pd.concat([existing_data, filtered_df], ignore_index=True)
        # Clean and remove empty columns for avoiding future warnings
        combined_data = combined_data.dropna(axis=1, how='all')

        # Save the combined data back to the file
        combined_data.to_csv(file_path, index=False)

        print(f"Saved {len(filtered_df)} new entries to {file_path}")

        # Append filtered data (new entries) to the list for later combining
        all_data.append(filtered_df)

        time.sleep(2)  # Avoid trying to hit API max or be declared as inhuman activity
        
    # Combine all new items into one dataframe to export
    final_df = pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

    # Optionally, we could return one giant dataframe of all cards across all csv's but that sounds excessive

    print(f"\nFinished tracking prices for {len(card_names)} cards.")
    return final_df




if __name__ == '__main__':
    from bs4 import BeautifulSoup
    import pandas as pd
    from datetime import datetime
    import re # regular expressions
    import os # for local file savings
    import time # for sleep to increase c hances of accepted API calls
    import requests
    '''
    This chunk of code can be uncommented to pull the names of the cards in the master
    dataset already in PowerBI. However, I do not want to explode my computer nor PowerBI
    by running this script on 17000 cards...
    try:
        card_names = dataset['Name'].dropna().unique()
    except Exception as e:
        print("Tried PowerBI dataset import, failed")
        card_names = [
        "Charizard", "Bulbasaur", "Gengar", "Umbreon", "Eevee",
        "Flygon", "Gardevoir", "Metagross", "Swampert", "Snorlax",
        "Arcanine", "Lucario", "Absol", "Blaziken", "Dragonite",
        "Greninja", "Mimikyu", "Garchomp", "Mudkip", "Sceptile",
        "Tyranitar", "Raichu", "Mew", "Ampharos", "Torterra"]
    '''
    # Top 25 most favorite Pokemon voted on Reddit in 2024
    # https://www.reddit.com/r/pokemon/comments/1bozvz5/results_favourite_pokemon_survey_2024/?rdt=61986
    card_names = [
        "Charizard", "Bulbasaur", "Gengar", "Umbreon", "Eevee",
        "Flygon", "Gardevoir", "Metagross", "Swampert", "Snorlax",
        "Arcanine", "Lucario", "Absol", "Blaziken", "Dragonite",
        "Greninja", "Mimikyu", "Garchomp", "Mudkip", "Sceptile",
        "Tyranitar", "Raichu", "Mew", "Ampharos", "Torterra"]

    newCardsDF = track_price_history(card_names, "eBay_Card_Prices", 200)
