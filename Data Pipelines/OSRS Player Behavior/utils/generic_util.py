import time
import pandas as pd
import requests
from typing import Dict
from dataclasses import dataclass
import json
from utils import project_paths

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
    data = read_json_config(project_paths.filter_path, default_filters)

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
    data = read_json_config(project_paths.script_config_path, default_filters)

    api_key = data.get("api_key", "")
    discord_username = data.get("discord_username", "")
    request_delay = data.get("request_delay", 0.7)
    parquet_output_dir_raw = data.get("parquet_output_dir_raw", "")
    parquet_output_dir_processed = data.get("parquet_output_dir_processed", "")
    return ScriptConfig(api_key, discord_username, request_delay, parquet_output_dir_raw, parquet_output_dir_processed)

def read_json_config(file_path: str, default_data: Dict = default_filters) -> Dict:
    '''Helper function to read in JSON config files with error handling and defaults.'''
    try:
        with open(file_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            print(f"Data successfully loaded from: {file_path}")
    except Exception:
        print(f"Config not found or unreadable at {file_path}; using defaults.")
        data = default_data
    return data

def make_wom_api_call(url: str, headers:Dict, params: Dict = None, delay_rate: float = 0.65) -> Dict:
    """
    Wrapper around requests.get with rate limiting.
    Delay must be >= .6 because maximum API rate is 100 requests per minute, which is 1 request every 0.6 seconds.
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