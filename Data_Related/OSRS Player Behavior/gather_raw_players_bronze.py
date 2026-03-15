import os
import time
import json
import requests
from typing import List, Dict
from dataclasses import dataclass
import pandas as pd
from utils.project_paths import *
from utils.generic_util import load_filters, load_script_config, parse_dates, make_wom_api_call, wom_base_url
from utils.generic_util import FilterConfig

'''
============================================================
Fetch Player Data Functions
============================================================
These functions are responsible for making API calls and fetching the relevant data. 
This includes fetching group names, players from group names, and players from the leaderboards from
different categories. The functions are built to be reusable and modular.
'''

def fetch_group_names(headers: Dict, json_file_path: str, limit: int = 50) -> List[Dict]:
    """
    Fetch all registered Wise Old Man groups using pagination, returns a list of all groups with their details. 
    This first 50 groups to appear is arbitrary and doesn't really matter, but # of groups can be changed to expand/decrease dataset size.
    If the groupnames JSON file already exists and has data, this function will skip the API call and load from the JSON file instead.
    """
    groups = []
    offset = 0
    
    if os.path.exists(json_file_path) and os.path.getsize(json_file_path) > 0:
        print(f"{json_file_path} already has group data, skipping API lookup.")
        with open(json_file_path, "r", encoding="utf-8") as f:
            groups = json.load(f)    
    else:
        while len(groups) < limit:
            print(f"Fetching groups offset={offset}")
            url = f"{wom_base_url}/groups"
            params = {
                "limit": limit,
                "offset": offset,
                "name": "",
            }
            data = make_wom_api_call(url, headers=headers, params=params)
            batch = data if isinstance(data, list) else data.get("groups", [])
            if not batch:
                break
            groups.extend(batch)
            offset += limit
    print(f"Total groups fetched: {len(groups)}")
    return groups

def fetch_current_leaderboard_names(headers: Dict, categories: List[str]) -> List[Dict]:
    """
    Fetch top players for each category in the provided list. 
    This function returns CURRENT leaderboards, not ALL TIME RECORDS leaderboards.
    The endpoint for ALL TIME RECORDS is https://api.wiseoldman.net/v2/records/leaderboard

    CURRENT TOP leaderboard for a category is: https://api.wiseoldman.net/v2/deltas/leaderboard

    This function could be refactored to be modular and simply update the records/deltas endpoint, or to include
    a specific parameter for time period, but we are only interested in current leaderboards,
    which almost guarantees they are somewhat active.
    """
    time_periods = ["day", "week", "month"]
    leaderboard_players = []
    for time_period in time_periods:
        for category in categories:
            print(f"Fetching leaderboard for category: {category}, time period: {time_period}")
            params = {
                "metric": category,
                "period": time_period
            }
            url = f"{wom_base_url}/deltas/leaderboard"
            data = make_wom_api_call(url, headers=headers, params=params) # returns a list of player dicts
            for each_player_dict in data:
                each_player_dict["metric"] = category # add metric and period to each player dict so we know which category and time period they belong to when we write to parquet
                each_player_dict["period"] = time_period
                each_player_dict["dataCategory"] = "leaderboard" # add data category to player dict so we know which dataset they belong to when we write to parquet
            leaderboard_players.extend(data)
        # break # comment out if testing
    return leaderboard_players

def fetch_all_group_players(groups: List[Dict], headers: Dict) -> List[Dict]:
    '''This file iterates through the list of all groups, looks the group up, 
    and then writes each player from the group'''
    group_players_list = []
    totalCount = len(groups)
    idx = 1
    for group in groups:
        print(f"Fetching players for group: {group['name']} ({idx}/{totalCount})")
        group_id = group["id"]
        url = f"{wom_base_url}/groups/{group_id}"
        group_details = make_wom_api_call(url, headers=headers)
        for member in group_details["memberships"]:
            member["player"]["dataCategory"] = "group" # add data category to player dict so we know which dataset they belong to when we write to parquet
            group_players_list.append(member["player"])
        idx += 1
        # break # comment out if testing
    return group_players_list

'''
============================================================
Write Functions
============================================================
These functions are responsible for writing the fetched data to CSV or JSON files. 
Most are built on top of calling write_data_to_parquet since that writes every item in a list to a row
'''

def write_dataframe_to_parquet(listofrows: list, datecols: list, endLocation: str, compression: str = "snappy") -> pd.DataFrame:
    '''Write a DataFrame to Parquet format with specified date columns. This function also handles basic normalizing
    for ease of use later on'''
    df = pd.DataFrame(listofrows)
    df = parse_dates(df, datecols)
    df = df.rename(columns={"id": "player_id"}) # for clarity purposes
    
    ### Leave in if you DON'T want usernames (privacy reasons, publishing to public, etc.), leave in if you want usernames
    '''
    if "username" in df.columns:
        df.drop(columns=["username"], inplace=True) # drop username column for 
    if "displayName" in df.columns:
        df.drop(columns=["displayName"], inplace=True) # drop displayName column for privacy
    '''
    ### End comment out section ###

    print(f"Writing DataFrame to Parquet at {endLocation} with compression={compression}...")
    df.to_parquet(endLocation, index=False, compression=compression, engine="pyarrow")
    return df

def write_leaderboard_data_to_parquet(data: list, endLocation: str, compression: str = "snappy") -> str:
    """Flattens leaderboard players and writes them to Parquet.
    This function returns the path to the Parquet file for ease of debugging/locating."""
    flattened_rows = []
    for player in data:
        player_obj = player["player"]
        player_with_extrafields = {
            "startDate": player["startDate"],
            "endDate": player["endDate"],
            "expGained": player["gained"],
            "metric": player["metric"],
            "period": player["period"],
            "dataCategory": player["dataCategory"],
            **player_obj,
            }
        flattened_rows.append(player_with_extrafields)
    date_cols = ["startDate", "endDate", "registeredAt", "updatedAt", "lastChangedAt","lastImportedAt"]
    df = write_dataframe_to_parquet(flattened_rows, date_cols, endLocation, compression)
    return str(endLocation)

def write_groups_to_json_file(groups: List[Dict], json_file_path: str) -> None:
    """
    Write groups/clans to JSON file. This list is fairly static, so this only ever
    needs to be run once/user can delete the file if they want to refresh it.
    This is different than CSV because the data is more nested and doesn't fit well into a tabular format, 
    plus we don't need to track changes over time for groups/clans, just need a reference of group names and IDs
    """
    if not groups:
        return
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(groups, f, indent=4, ensure_ascii=False)
    return json_file_path

def write_group_players_to_parquet(groups: List[Dict], endLocation: str, compression: str = "snappy") -> str:
    '''Write group players to parquet. This function returns the path to the Parquet file for ease of debugging/locating.'''
    date_cols = ["registeredAt","updatedAt","lastChangedAt","lastImportedAt"]
    df = write_dataframe_to_parquet(groups, date_cols, endLocation, compression)
    return str(endLocation)
    
def generate_group_players(group_player_list_parquet_path: str, groups: List[Dict], headers: Dict) -> List[Dict]:
    '''This function checks if group players are already written to parquet, if so it loads from parquet and returns a List[Dict]
    otherwise it builds the list via API calls'''
    if os.path.exists(group_player_list_parquet_path) and os.path.getsize(group_player_list_parquet_path) > 0:
        print(f"Group player's already extracted to parquet at {group_player_list_parquet_path}, skipping parquet writing.")
        group_players = pd.read_parquet(group_player_list_parquet_path).to_dict(orient="records")
    else:
        print("Group players not found in parquet format, fetching players from API and writing to parquet.")    
        group_players = fetch_all_group_players(groups, headers)
    return group_players

def generate_all_leaderboard_players(combined_player_list_parquet_path: str, headers: Dict, account_filter_class: FilterConfig) -> List[Dict]:
    '''This function checks if leaderboard players are already written to parquet, if so it loads from parquet and returns a List[Dict]
    otherwise it builds the list via API calls'''
    if os.path.exists(combined_player_list_parquet_path) and os.path.getsize(combined_player_list_parquet_path) > 0:
        print(f"Combined player list already extracted to parquet at {combined_player_list_parquet_path}, skipping parquet writing.")
        combined_players = pd.read_parquet(combined_player_list_parquet_path).to_dict(orient="records")
    else:
        print("Combined player list not found in parquet format, fetching players from API and writing to parquet.")    
        exp_leaderboard_players = fetch_current_leaderboard_names(headers, account_filter_class.skill_names) # list of dict
        bosskc_leaderboard_players = fetch_current_leaderboard_names(headers, account_filter_class.boss_hiscores) # list of dict
        activity_leaderboard_players = fetch_current_leaderboard_names(headers, account_filter_class.activities) # list of dict

        combined_players = exp_leaderboard_players + bosskc_leaderboard_players + activity_leaderboard_players
    return combined_players

def main():
    # actually handles all the control logic flow
    account_filter_class = load_filters()
    script_config_class = load_script_config()

    wom_headers = {
        "x-api-key": script_config_class.api_key,
        "User-Agent": script_config_class.discord_username
    }
    # The groups are essentially random because there is no  
    # particular order when querying for groups, but the same groups
    # appear everytime for the query so for our sake we will treat it as static

    # ============== Dataset 1: Group/Clan Players ==============
    # Always do b/c cheap, also fetch_group_names has built in check to see if we already have group names in JSON and will skip API call if found
    first_X_groups = fetch_group_names(wom_headers, json_file_path=group_names_path, limit=50)
    json_filepath = write_groups_to_json_file(first_X_groups, group_names_path) # write group names to json for easy reference since they are more static and don't fit well into parquet format
    group_players = generate_group_players(bronze_group_player_parquet_path, first_X_groups, wom_headers)
    write_group_players_to_parquet(group_players, bronze_group_player_parquet_path, compression="snappy")

    # ============== Dataset 2: Leaderboard Players ==============
    all_leaderboard_players = generate_all_leaderboard_players(bronze_all_leaderboard_player_parquet_path, wom_headers, account_filter_class)
    write_leaderboard_data_to_parquet(all_leaderboard_players, bronze_all_leaderboard_player_parquet_path, compression="snappy")
 
 
if __name__ == "__main__":
    # keep this simple/bare
    main()

