# Import necessary libraries

from pokemontcgsdk import Card
import pandas as pd

# This variable is provided by Power BI (your query must send a Name column)
# card_names = dataset['Name'].dropna().unique()

# List of card names for specific pokemon querying
card_names = ["Charizard"]

card_data_results = []
#list of offered TCGPlayer pricing, declared upfront for dynamic iterations
rarityTypes = ["normal", "holofoil", "reverseHolofoil", "firstEditionHolofoil" , "firstEditionNormal"]

for name in card_names:
    try:
        results = Card.where(q=f'name:"{name}"')
        for card in results:
            # use hasattr ternaries as guardrails to ensure actual queried data exists
            if card.tcgplayer and hasattr(card, 'tcgplayer') and hasattr(card.tcgplayer, 'prices'):
                # TCGPlayer prices object
                prices = card.tcgplayer.prices
                
                # temporarily store all rarity prices for current card being looked at
                rarityList = []
                for rarity in rarityTypes:
                    rarity_price = getattr(prices, rarity, None) if hasattr(prices, rarity) else None
                    rarityList.append(rarity_price.market if hasattr(rarity_price, 'market') else None)         
                card_data.append({
                    'ID': card.id,
                    'Name': card.name,
                    'Set': card.set.name if card.set else None,
                    'Market Price (Normal)': rarityList[0],
                    'Market Price (Holofoil)': rarityList[1],
                    'Market Price (Reverse Holofoil)': rarityList[2],
                    'Market Price (First Edition Holofoil)': rarityList[3],
                    'Market Price (First Edition Normal)': rarityList[4],
                    'Rarity': card.rarity,
                    'Release Date': card.set.releaseDate if card.set else None
                })
    except Exception as e:
        # Optional: append the failed name for debugging
        card_data.append({'Name': name, 'Error': str(e)})

print(card_data)
# Return as DataFrame to Power BI
result_df = pd.DataFrame(card_data)
