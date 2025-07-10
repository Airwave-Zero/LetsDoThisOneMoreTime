def lookup_tcg_price(card_names):
    card_data_results = []
    #list of offered TCGPlayer pricing, declared upfront for dynamic iterations
    rarityTypes = ["normal", "holofoil", "reverseHolofoil", "firstEditionHolofoil" , "firstEditionNormal"]
    for name in card_names:
        try:
            print("Looking for the card: " + name)
            results = Card.where(q=f'name:"{name}"')
            for card in results:
                # use boolean shortcircuitting for clarity and only to proceed if it makes sense
                if card.tcgplayer and hasattr(card, 'tcgplayer') and hasattr(card.tcgplayer, 'prices'):
                    # TCGPlayer prices object
                    prices = card.tcgplayer.prices                
                    # temporarily store all rarity prices for current card being looked at
                    rarityList = []
                    for rarity in rarityTypes:
                        rarity_price = getattr(prices, rarity, None) if hasattr(prices, rarity) else None
                        rarityList.append(rarity_price.market if hasattr(rarity_price, 'market') else None)         
                    card_data_results.append({
                        'ID': card.id,
                        'Normalized Name': name,
                        'Card Name': card.name,
                        'Set': card.set.name if card.set else None,
                        'Market Price (Normal)': rarityList[0],
                        'Market Price (Holofoil)': rarityList[1],
                        'Market Price (Reverse Holofoil)': rarityList[2],
                        'Market Price (First Edition Holofoil)': rarityList[3],
                        'Market Price (First Edition Normal)': rarityList[4],
                        'Rarity': card.rarity,
                        'Release Date': card.set.releaseDate if card.set else None,
                        'Image_URL': card.images.large if hasattr(card, 'images') else None
                    })
                time.sleep(.5) #pause to avoid hitting api maxes
        except Exception as e:
            # Optional: append the failed name for debugging
            card_data_results.append({'Name': name, 'Error': str(e)})
    return pd.DataFrame(card_data_results)


if __name__ == "__main__":
    # Import necessary libraries
    from pokemontcgsdk import Card
    from pokemontcgsdk import RestClient
    import pandas as pd
    import time

    # Custom api key, can be signed up for at https://dev.pokemontcg.io/
    RestClient.configure('your_api_key_goes_here')

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
    # Final output to Power BI
    result_df = lookup_tcg_price(card_names)
