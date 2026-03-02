import os
import time
import csv
import json
import requests
from typing import List, Dict
from dataclasses import dataclass
import pandas as pd

'''
============================================================
Configuration/Initialization/Helper Functions and Variables
============================================================
Establish all global variable names and file locations here
Establish functions for loading in configurations and returning objects that store important config types
'''

config_folder_dir = os.path.join(os.path.dirname(__file__), "config")
os.makedirs(config_folder_dir, exist_ok=True)
filter_path = os.path.join(config_folder_dir, "osrs_filters.json")
groupnames_path = os.path.join(config_folder_dir, "group_names.json")
#replace with private config for API key and user agent
#script_config_path = os.path.join(config_folder_dir, "script_config.json")
script_config_path = os.path.join(config_folder_dir, "script_config_private.json")

parquet_folder_path = os.path.join(os.path.dirname(__file__), "parquet_data")
os.makedirs(parquet_folder_path, exist_ok=True)
bronze_parquet_folder_path = os.path.join(parquet_folder_path, "raw_parquet_bronze")

#group_player_list_parquet_path = os.path.join(bronze_parquet_folder_path, "Group_Player_List.parquet")
#leaderboard_player_list_parquet_path = os.path.join(bronze_parquet_folder_path, "Gains_Leaderboard_Player_List.parquet")
#common_bot_area_player_list_parquet_path = os.path.join(bronze_parquet_folder_path, "Common_Bot_Area_List.parquet")

# distinction between private and non private, only push non private to github
group_player_list_parquet_path = os.path.join(bronze_parquet_folder_path, "Group_Player_List_private.parquet")
leaderboard_player_list_parquet_path = os.path.join(bronze_parquet_folder_path, "Gains_Leaderboard_Player_List_private.parquet")
#common_bot_area_player_list_parquet_path = os.path.join(bronze_parquet_folder_path, "Common_Bot_Area_List_private.parquet")
combined_player_list_parquet_path = os.path.join(bronze_parquet_folder_path, "Combined_Player_List_private.parquet")

# object in case file doesn't exist or is unfindable
default_filters = { 
  "skill_names": [
    "overall",
    "attack",
    "strength",
    "defence",
    "hitpoints",
    "ranged",
    "prayer",
    "magic",
    "cooking",
    "woodcutting",
    "fishing",
    "firemaking",
    "crafting",
    "smithing",
    "mining",
    "herblore",
    "agility",
    "thieving",
    "slayer",
    "farming",
    "runecrafting",
    "hunter",
    "construction",
    "sailing"
  ],

  "boss_hiscores": [
    "abyssal_sire",
    "alchemical_hydra",
    "amoxliatl",
    "araxxor",
    "artio",
    "barrows_chests",
    "bryophyta",
    "callisto",
    "calvarion",
    "cerberus",
    "chambers_of_xeric",
    "chambers_of_xeric_challenge_mode",
    "chaos_elemental",
    "chaos_fanatic",
    "commander_zilyana",
    "corporeal_beast",
    "crazy_archaeologist",
    "dagannoth_prime",
    "dagannoth_rex",
    "dagannoth_supreme",
    "deranged_archaeologist",
    "doom_of_mokhaiotl",
    "duke_sucellus",
    "general_graardor",
    "giant_mole",
    "grotesque_guardians",
    "hespori",
    "kalphite_queen",
    "king_black_dragon",
    "kraken",
    "kreearra",
    "kril_tsutsaroth",
    "lunar_chests",
    "mimic",
    "nex",
    "nightmare",
    "obor",
    "phantom_muspah",
    "phosanis_nightmare",
    "sarachnis",
    "scorpia",
    "scurrius",
    "shellbane_gryphon",
    "skotizo",
    "sol_heredit",
    "spindel",
    "tempoross",
    "the_gauntlet",
    "the_corrupted_gauntlet",
    "the_hueycoatl",
    "the_leviathan",
    "the_royal_titans",
    "the_whisperer",
    "theatre_of_blood",
    "theatre_of_blood_hard_mode",
    "thermonuclear_smoke_devil",
    "tombs_of_amascut",
    "tombs_of_amascut_expert",
    "tzkal_zuk",
    "tztok_jad",
    "vardorvis",
    "venenatis",
    "vetion",
    "vorkath",
    "wintertodt",
    "yama",
    "zalcano",
    "zulrah"
  ],
  "activities": [
    "league_points",
    "bounty_hunter_hunter",
    "bounty_hunter_rogue",
    "clue_scrolls_all",
    "clue_scrolls_beginner",
    "clue_scrolls_easy",
    "clue_scrolls_medium",
    "clue_scrolls_hard",
    "clue_scrolls_elite",
    "clue_scrolls_master",
    "last_man_standing",
    "pvp_arena",
    "soul_wars_zeal",
    "guardians_of_the_rift",
    "colosseum_glory",
    "collections_logged"
    ],

  "computed": ["ehp", "ehb", "ttm"],

  "account_types": [
    "normal",
    "ironman",
    "ultimate_ironman",
    "hardcore_ironman"
  ],

  "other_build_types": [
    "main",
    "f2p",
    "p2p",
    "skillers",
    "1_defence",
    "level_3",
    "1_hitpoint_pure",
    "pure",
    "zero_defence",
    "iron_pure"
  ]
}
wom_base_url = "https://api.wiseoldman.net/v2"


# Configs relevant for running the script
@dataclass(frozen=True)
class ScriptConfig:
    api_key: str # api key to raise API limits from 20 to 100 requests/minute
    discord_username: str # user discord ign so WOM API knows who to contact if necessary
    request_delay: float # adjustable delay to ensure we stay under 100 calls per minute
    parquet_output_dir_raw: str # directory for raw bronze data
    parquet_output_dir_processed: str # directory for cleaned silver data (parquet, etc.)

# Configs relevant for filtering players and categorizing them into different buckets for analysis
@dataclass(frozen=True)
class FilterConfig:
    skill_names: list # e.g. overall, attack, strength, etc.
    boss_hiscores: list # e.g. zulrah, vorkath, etc.
    account_types: list # e.g. ironman, hardcore ironman, etc.
    other_build_types: list # e.g. 1 defence pure, 1 hp pure, etc.
    activities: list # e.g. clue scrolls
    computed: list # e.g. ehp, ehb, ttm

def load_filters():
    '''Loads in different account filter types from default or project JSON file.
    Returns a FilterConfig dataclass instance with all necessary filter types.'''
    try:
        with open(filter_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            print(f"Filter Data successfully loaded from: {filter_path}")
    except Exception:
        print(f"Config not found or unreadable at {filter_path}; using defaults.")
        data = default_filters

    skill_names = data.get("skill_names", default_filters["skill_names"])
    boss_hiscores = data.get("boss_hiscores", default_filters["boss_hiscores"])
    account_types = data.get("account_types", default_filters["account_types"])
    other_build_types = data.get("other_build_types", default_filters["other_build_types"])
    activities = data.get("activities", default_filters["activities"])
    computed = data.get("computed", default_filters["computed"])
    
    return FilterConfig(skill_names, boss_hiscores, account_types, other_build_types, activities, computed)

def load_script_config():
    '''Loads in script config from default or project JSON file.
    Returns a ScriptConfig dataclass instance with all necessary config values.'''
    try:
        with open(script_config_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            print(f"Script Config data successfully loaded from: {script_config_path}")
    except Exception:
        print(f"Script config not found or unreadable at {script_config_path}; using environment variables.")
        data = {}

    api_key = data.get("api_key", "")
    discord_username = data.get("discord_username", "")
    request_delay = data.get("request_delay", 0.7)
    parquet_output_dir_raw = data.get("parquet_output_dir_raw", "")
    parquet_output_dir_processed = data.get("parquet_output_dir_processed", "")
    return ScriptConfig(api_key, discord_username, request_delay, parquet_output_dir_raw, parquet_output_dir_processed)

def make_wom_api_call(url: str, headers:Dict, params: Dict = None, delay_rate: float = 0.7) -> Dict:
    """
    Wrapper around requests.get with rate limiting.
    """
    response = requests.get(url, headers=headers, params=params)
    time.sleep(delay_rate)

    response.raise_for_status()
    return response.json()

def parse_dates(df, cols):
    '''Helper function to parse date columns from API into proper datetime format in pandas'''
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], utc=True, errors="coerce")
    return df

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

    #protect personally identifiable info 
    if "username" in df.columns:
        df = df.drop(columns=["username"])
    if "displayName" in df.columns:
        df = df.drop(columns=["displayName"])
        
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
    first_X_groups = fetch_group_names(wom_headers, json_file_path=groupnames_path, limit=50)
    json_filepath = write_groups_to_json_file(first_X_groups, groupnames_path) # write group names to json for easy reference since they are more static and don't fit well into parquet format
    group_players = generate_group_players(group_player_list_parquet_path, first_X_groups, wom_headers)
    write_group_players_to_parquet(group_players, group_player_list_parquet_path, compression="snappy")

    # ============== Dataset 2: Leaderboard Players ==============
    combined_players = generate_all_leaderboard_players(combined_player_list_parquet_path, wom_headers, account_filter_class)
    write_leaderboard_data_to_parquet(combined_players, combined_player_list_parquet_path, compression="snappy")
 
 
if __name__ == "__main__":
    # keep this simple/bare
    main()

