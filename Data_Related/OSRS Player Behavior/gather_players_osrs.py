import os
import time
import csv
import json
import requests
from typing import List, Dict
from dataclasses import dataclass

# ============================================================
# Configuration/Initialization Functions and Variables
# ============================================================

# Load filter lists from external JSON so they can be edited without
# modifying the script. A default fallback is included.
config_folder_dir = os.path.join(os.path.dirname(__file__), "config")
os.makedirs(config_folder_dir, exist_ok=True)
filter_path = os.path.join(config_folder_dir, "osrs_filters.json")
groupnames_path = os.path.join(config_folder_dir, "group_names.json")

#replace with private config for API key and user agent
#script_config_path = os.path.join(config_folder_dir, "script_config.json")
script_config_path = os.path.join(config_folder_dir, "script_config_private.json")

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

output_dir = "data_output"
os.makedirs(output_dir, exist_ok=True)

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

    # todo return dataclass instead of tuple for better readability
    
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
    # todo return dataclass instead of tuple for better readability

    return ScriptConfig(api_key, discord_username, request_delay, csv_output_dir_raw, csv_output_dir_processed)

# ============================================================
# MAIN EXECUTION
# ============================================================

def main():
    # actually handles all the control logic flow
    account_filter_class = load_filters()
    script_config_class = load_script_config()

    HEADERS = {
        "x-api-key": script_config_class.api_key,
        "User-Agent": script_config_class.discord_username
    }
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

