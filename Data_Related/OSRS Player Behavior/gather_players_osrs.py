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

Load filter lists from external JSON so they can be edited without
modifying the script. A default fallback is included.
Include all necessary paths for config and output data
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
#master_player_list_csv_path = os.path.join(bronze_csv_folder_path, "Master_Player_List.csv")
master_player_list_csv_path = os.path.join(bronze_csv_folder_path, "Master_Player_List.csv")


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
        "Abyssal Sire",
        "Alchemical Hydra",
        "Amoxliatl",
        "Araxxor",
        "Artio",
        "Barrows Chests",
        "Bryophyta",
        "Callisto",
        "Calvar'ion",
        "Cerberus",
        "Chambers of Xeric",
        "Chambers of Xeric: Challenge Mode",
        "Chaos Elemental",
        "Chaos Fanatic",
        "Commander Zilyana",
        "Corporeal Beast",
        "Crazy Archaeologist",
        "Dagannoth Prime",
        "Dagannoth Rex",
        "Dagannoth Supreme",
        "Deranged Archaeologist",
        "Doom of Mokhaiotl",
        "Duke Sucellus",
        "General Graardor",
        "Giant Mole",
        "Grotesque Guardians",
        "Hespori",
        "Kalphite Queen",
        "King Black Dragon",
        "Kraken",
        "Kree'Arra",
        "K'ril Tsutsaroth",
        "Lunar Chests",
        "Mimic",
        "Nex",
        "Nightmare",
        "Obor",
        "Phantom Muspah",
        "Phosani's Nightmare",
        "Sarachnis",
        "Scorpia",
        "Scurrius",
        "Shellbane Gryphon",
        "Skotizo",
        "Sol Heredit",
        "Spindel",
        "Tempoross",
        "The Gauntlet",
        "The Corrupted Gauntlet",
        "The Hueycoatl",
        "The Leviathan",
        "The Royal Titans",
        "The Whisperer",
        "Theatre of Blood",
        "Theatre of Blood: Hard Mode",
        "Thermonuclear Smoke Devil",
        "Tombs of Amascut",
        "Tombs of Amascut: Expert Mode",
        "TzKal-Zuk",
        "TzTok-Jad",
        "Vardorvis",
        "Venenatis",
        "Vet'ion",
        "Vorkath",
        "Wintertodt",
        "Yama",
        "Zalcano",
        "Zulrah"
    ],
    "account_types": [
        "Normal",
        "Ironman",
        "Ultimate Ironman",
        "Hardcore Ironman",
        "Deadman Mode",
        "Seasonal Deadman Mode",
        "Tournament"
    ],
    "other_build_types": [
        "Main",
        "F2P",
        "P2P",
        "Skillers",
        "1 Defence",
        "Level 3",
        "1 Hitpoint Pure",
        "Pure",
        "Zero Defence",
        "Iron Pure"
    ]
}
wom_base_url = "https://api.wiseoldman.net/v2"


@dataclass(frozen=True)
class ScriptConfig:
    api_key: str
    discord_username: str
    request_delay: float
    csv_output_dir_raw: str
    csv_output_dir_processed: str

@dataclass(frozen=True)
class FilterConfig:
    skill_names: list
    boss_hiscores: list
    account_types: list
    other_build_types: list

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
    
    return FilterConfig(skill_names, boss_hiscores, account_types, other_build_types)

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

# ============================================================
# MAIN EXECUTION
# ============================================================


# ============================================================
# Helper Functions
# ============================================================

#
def make_wom_api_call(url: str, headers:Dict, params: Dict = None, delay_rate: float = 0.7) -> Dict:
    """
    Wrapper around requests.get with rate limiting.
    """
    print("making api call to: ", url)
    response = requests.get(url, headers=headers, params=params)
    time.sleep(delay_rate)

    response.raise_for_status()
    return response.json()

def write_player_to_csv(player_data: Dict, filepath: str):
    """
    Write player data to a CSV file. If the file doesn't exist, it creates it and writes the header.
    If it does exist, it appends the new player data as a new row.
    """
    file_exists = os.path.isfile(filepath)

    with open(filepath, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=player_data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(player_data)

# ============================================================
# Leaderboards
# ============================================================

def fetch_top_players_for_metric(metric: str, headers: Dict, limit: int = 100) -> List[Dict]:
    """
    Fetch top players for a given metric.
    """
    url = f"{wom_base_url}/leaderboards"
    params = {
        "metric": metric,
        "limit": limit,
        "offset": 0
    }

    data = make_wom_api_call(url, headers=headers, params=params)
    return data.get("entries", [])


def fetch_all_leaderboards(metrics: List[str]) -> Dict[str, List[Dict]]:
    """
    Fetch top 100 players across all provided metrics.
    """
    results = {}

    for metric in metrics:
        print(f"Fetching leaderboard: {metric}")
        results[metric] = fetch_top_players_for_metric(metric)

    return results


def write_leaderboards_to_csv(leaderboards: Dict[str, List[Dict]]):
    """
    Write leaderboard data to CSV files (one per metric).
    """
    for metric, entries in leaderboards.items():
        if not entries:
            continue

        filepath = os.path.join(OUTPUT_DIR, f"leaderboard_{metric}.csv")
        print(f"Writing {filepath}")

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=entries[0].keys())
            writer.writeheader()
            writer.writerows(entries)


# ============================================================
# Groups / Clans
# ============================================================

def fetch_all_groups(headers: Dict, limit: int = 50) -> List[Dict]:
    """
    Fetch all registered Wise Old Man groups using pagination.
    """
    groups = []
    offset = 0
    '''
    curl -X GET https://api.wiseoldman.net/v2/groups?name=the&limit=2 \
    -H "Content-Type: application/json"'''
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


def write_groups_to_json_file(groups: List[Dict]):
    """
    Write groups/clans to JSON file. This list is fairly static, so this only ever
    needs to be run once/user can delete the file if they want to refresh it.
    """
    if not groups:
        return

    with open(groupnames_path, "w", encoding="utf-8") as f:
        json.dump(groups, f, indent=4, ensure_ascii=False)


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
    if os.path.exists(groupnames_path) and os.path.getsize(groupnames_path) > 0:
        print(f"{groupnames_path} already has group data, skipping retrieval process.")
        with open(groupnames_path, "r", encoding="utf-8") as f:
            random_groups = json.load(f)
    else:
        random_groups = fetch_all_groups(wom_headers, limit=50)
        write_groups_to_json_file(random_groups)

    for group in random_groups:
        group_id = group["id"]
        url = f"{wom_base_url}/groups/{group_id}"
        group_details = make_wom_api_call(url, headers=wom_headers)
        for member in group_details["memberships"]:
            write_player_to_csv(member["player"], master_player_list_csv_path)
        return
    
    '''
    Skeleton code / control structure
    1. Leaderboards
    leaderboards = fetch_all_leaderboards(LEADERBOARD_METRICS)
    write_leaderboards_to_csv(leaderboards)

    # 2. Get Groups / Clans
    groups = fetch_all_groups()
    write_groups_to_csv(groups)

        '''


if __name__ == "__main__":
    # keep this simple/bare
    main()

