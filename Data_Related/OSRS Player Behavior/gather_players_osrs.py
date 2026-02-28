import os
import time
import csv
import json
import requests
from typing import List, Dict
from dataclasses import dataclass

'''
============================================================
Configuration/Initialization Functions and Variables
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

csv_folder_path = os.path.join(os.path.dirname(__file__), "csv_data")
os.makedirs(csv_folder_path, exist_ok=True)
bronze_csv_folder_path = os.path.join(csv_folder_path, "raw_csv_bronze")
silver_csv_folder_path = os.path.join(csv_folder_path, "cleaned_parquet_silver")

#group_player_list_csv_path = os.path.join(bronze_csv_folder_path, "Group_Player_List.csv")
#leaderboard_player_list_csv_path = os.path.join(bronze_csv_folder_path, "Gains_Leaderboard_Player_List.csv")
#common_bot_area_player_list_csv_path = os.path.join(bronze_csv_folder_path, "Common_Bot_Area_List.csv")

# distinction between private and non private, only push non private to github
group_player_list_csv_path = os.path.join(bronze_csv_folder_path, "Group_Player_List_private.csv")
leaderboard_player_list_csv_path = os.path.join(bronze_csv_folder_path, "Gains_Leaderboard_Player_List_private.csv")
#common_bot_area_player_list_csv_path = os.path.join(bronze_csv_folder_path, "Common_Bot_Area_List_private.csv")

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
    "grid_points",
    "league_points",
    "deadman_points",
    "bounty_hunter_hunter",
    "bounty_hunter_rogue",
    "bounty_hunter_legacy_hunter",
    "bounty_hunter_legacy_rogue",
    "clue_scrolls_all",
    "clue_scrolls_beginner",
    "clue_scrolls_easy",
    "clue_scrolls_medium",
    "clue_scrolls_hard",
    "clue_scrolls_elite",
    "clue_scrolls_master",
    "last_man_standing",
    "pvp_arena_rank",
    "soul_wars_zeal",
    "rifts_closed",
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
    csv_output_dir_raw: str # directory for raw bronze data
    csv_output_dir_processed: str # directory for cleaned silver data (parquet, etc.)

# Configs relevant for filtering players and categorizing them into different buckets for analysis
@dataclass(frozen=True)
class FilterConfig:
    skill_names: list # e.g. overall, attack, strength, etc.
    boss_hiscores: list # e.g. zulrah, vorkath, etc.
    activities: list # e.g. clue scrolls
    computed: list # e.g. ehp, ehb, ttm
    account_types: list # e.g. ironman, hardcore ironman, etc.
    other_build_types: list # e.g. 1 defence pure, 1 hp pure, etc.

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
    activities = data.get("activity_hiscores", default_filters["activities"])
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
    csv_output_dir_raw = data.get("csv_output_dir_raw", "")
    csv_output_dir_processed = data.get("csv_output_dir_processed", "")
    return ScriptConfig(api_key, discord_username, request_delay, csv_output_dir_raw, csv_output_dir_processed)

'''
============================================================
Getter/Fetch Functions
============================================================
These functions are responsible for making API calls and fetching the relevant data. 
This includes fetching group names, players from group names, and players from the leaderboards from
different categories. The functions are built to be reusable and modular.
'''
def make_wom_api_call(url: str, headers:Dict, params: Dict = None, delay_rate: float = 0.7) -> Dict:
    """
    Wrapper around requests.get with rate limiting.
    """
    response = requests.get(url, headers=headers, params=params)
    time.sleep(delay_rate)

    response.raise_for_status()
    return response.json()


def fetch_group_names(headers: Dict, limit: int = 50) -> List[Dict]:
    """
    Fetch all registered Wise Old Man groups using pagination.
    """
    groups = []
    offset = 0
    
    if os.path.exists(groupnames_path) and os.path.getsize(groupnames_path) > 0:
        print(f"{groupnames_path} already has group data, skipping retrieval process.")
        with open(groupnames_path, "r", encoding="utf-8") as f:
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
                each_player_dict["metric"] = category # add metric and period to each player dict so we know which category and time period they belong to when we write to csv
                each_player_dict["period"] = time_period
            leaderboard_players.extend(data)
    return leaderboard_players
'''
============================================================
Write Functions
============================================================
These functions are responsible for writing the fetched data to CSV or JSON files. 
Most are built on top of calling write_data_to_csv since that writes every item in a list to a row
'''
def write_data_to_csv(data: Dict, filepath: str):
    """
    Write data to a CSV file. If the file doesn't exist, it creates it and writes the header.
    If it does exist, it appends the new data as a new row.
    This function is generic as this can be used for players, snapshots, etc.
    """
    file_exists = os.path.isfile(filepath)

    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

def write_groups_to_json_file(groups: List[Dict]):
    """
    Write groups/clans to JSON file. This list is fairly static, so this only ever
    needs to be run once/user can delete the file if they want to refresh it.
    This is different than CSV because the data is more nested and doesn't fit well into a tabular format, 
    plus we don't need to track changes over time for groups/clans, just need a reference of group names and IDs
    """
    if not groups:
        return
    with open(groupnames_path, "w", encoding="utf-8") as f:
        json.dump(groups, f, indent=4, ensure_ascii=False)

def write_group_players_to_csv(groups: List[Dict], headers: Dict, output_path: str):
    '''This file iterates through the list of all groups, looks them up, 
    and then writes the players into the csv that are within the current group'''
    group_players_list = []
    for group in groups:
        group_id = group["id"]
        url = f"{wom_base_url}/groups/{group_id}"
        group_details = make_wom_api_call(url, headers=headers)
        for member in group_details["memberships"]:
            write_data_to_csv(member["player"], output_path)
            group_players_list.append(member["player"])
    return group_players_list # in case we want to do anything else with the list of players in groups after writing to csv    

def write_leaderboard_players_to_csv(players: List[Dict], output_path: str):
    '''This file iterates through the list of all players on the exp leaderboards, looks them up, 
    and then writes the player details into the csv'''
    for player in players:
        player_obj = player["player"]
        player_with_extrafields = {
            "startDate": player["startDate"],
            "endDate": player["endDate"],
            "expGained": player["gained"],
            "metric": player["metric"],
            "period": player["period"],
            **player_obj,  # expands all player fields
        }
        write_data_to_csv(player_with_extrafields, output_path)

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

    # Dataset 1: Group/Clan Players
    #random_groups = fetch_group_names(wom_headers, limit=50)
    #group_players = write_group_players_to_csv(random_groups, wom_headers, group_player_list_csv_path)
    #write_groups_to_json_file(random_groups)


    # Dataset 2: Leaderboard Players (by category and time periods)
    # NOTE: If filtering by account type, the proper query parameter name is playerType
    # NOTE: It is also worth breaking these writes down by time period/writing more frequently in order to 
    # prevent issues when writing too many players and losing data, but for now we will write them all at once 
    # and then break down by category/period in the analysis phase since there is a field for both in the csv.
    exp_leaderboard_players = fetch_current_leaderboard_names(wom_headers, account_filter_class.skill_names)
    bosskc_leaderboard_players = fetch_current_leaderboard_names(wom_headers, account_filter_class.boss_hiscores)
    activity_leaderboard_players = fetch_current_leaderboard_names(wom_headers, account_filter_class.activities)

    
    # write to same leaderboard CSV since there is a field for metric and period, can drill down later
    write_leaderboard_players_to_csv(exp_leaderboard_players, leaderboard_player_list_csv_path)
    write_leaderboard_players_to_csv(bosskc_leaderboard_players, leaderboard_player_list_csv_path)
    write_leaderboard_players_to_csv(activity_leaderboard_players, leaderboard_player_list_csv_path)

    # Dataset 3: Common Bot Area Players - this is more of a manual process where we would identify commonly botted areas 
    # and then query the players in those hiscores and track them in a separate csv.
    # common_botarea_players = load data from JSON
    # write_common_botarea_players_to_csv(common_botarea_players, wom_headers, common_bot_area_player_list_csv_path)

    '''
    much later todo: write runelite plugin to extract names from screen when gaming in 
    commonly botted areas and add to csvv to track those players as well

    todo2: write dag/common script to essentially update/get the stats for all players
    in the separate csv's
    write functions: get_group_player_list_snapshots, get_leaderboard_player_snapshots, 

    # this is for getting the top of ALL TIME RECORDS leaderboard
    https://api.wiseoldman.net/v2/records/leaderboard?metric=abyssal_sire&period=day&playerType=hardcore

    # this is for getting the CURRENT TOP leaderboard for a category
    https://api.wiseoldman.net/v2/deltas/leaderboard?metric=agility&period=day
    '''

if __name__ == "__main__":
    # keep this simple/bare
    main()

