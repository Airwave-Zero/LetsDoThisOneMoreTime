# this will be the script that handles all the update_players_osrs functions
from dataclasses import dataclass
from typing import List, Dict
from utils.generic_util import load_script_config, make_wom_api_call, parse_dates, wom_base_url
from utils import project_paths
import pandas as pd
import os
import pathlib
import time

group_player_parquet_path = project_paths.bronze_group_player_parquet_path
leaderboard_gains_parquet_path = project_paths.bronze_all_leaderboard_player_parquet_path
#dims_folder_dir = project_paths.dims_folder_path

bronze_snapshots_folder_dir = project_paths.bronze_snapshot_parquet_folder_path

def lookup_single_player(player_username:str, headers: Dict, script_config: dataclass) -> Dict:
    # Modular function to just lookup one player, returns a (nested) json object
    try:
        # print(f"Looking up player: {player_username}") # uncomment if debugging
        if player_username.find(" "):
            player_username = player_username.replace(" ", "%20") # replace spaces with ASCII encoding for URL
        url = f"{wom_base_url}/players/{player_username}"
        updated_player = make_wom_api_call(url, headers, delay_rate=script_config.request_delay)
        username = updated_player.get("username")
        display_name = updated_player.get("displayName")
        updated_player = updated_player.get("latestSnapshot") # we mainly care about this, most recent one
        updated_player["username"] = username
        updated_player["display_name"] = display_name
        updated_player["snapshot_datetime"] = time.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"Error looking up player {player_username}: {e}")
        updated_player = {"username": player_username, "error": str(e)}
    return updated_player

def lookup_player_batch_set_size(player_batch: List[str], headers: Dict, script_config: dataclass, progress_amount:int = 20) -> List[Dict]:
    # Modular function to lookup every player in a defined batch/list, returns a list of (nested) json objects
    # progress_amount is an int for how often to print update; 20 = 5% intervals, 10 = 10% intervals
    player_list = []
    idx = 0
    progress_amount = max(1, len(player_batch) // progress_amount) # set progress print to every 5% of the batch, but at least every 1 player for small batches
    for player_username in player_batch:
        if (idx+1) % progress_amount == 0:
            print(f"Batch Progress: {idx+1}/{len(player_batch)} ({(idx+1)/len(player_batch)*100:.1f}%)")
        current_player = lookup_single_player(player_username, headers, script_config)
        player_list.append(current_player)
        idx += 1
        # break # uncomment if testing
    print(f"Finished looking up batch of {len(player_batch)} players.")
    return player_list

def lookup_all_groups(group_player_df, headers: Dict, script_config: dataclass) -> List[Dict]:
    all_group_snapshots = []
    group_names = group_player_df["data_category_name"].unique()
    idx = 0
    for each_group in group_names:
        player_usernames = group_player_df[group_player_df["data_category_name"] == each_group]["username"] # this is a list of usernames for each group
        print(f"Looking up group {idx+1}/{len(group_names)}: {each_group} with {len(player_usernames)} players.")
        group_snapshot = lookup_player_batch_set_size(player_usernames, headers, script_config) # set progress print to every 5% of the batch
        for each_person in group_snapshot:
            each_person["data_category_type"] = "group"
            each_person["data_category_name"] = each_group
        all_group_snapshots.append(group_snapshot)
        idx += 1
        print(f"Finished looking up group {each_group}.")
        # break # if doing 1 group for testing
    return all_group_snapshots

def lookup_all_leaderboard_categories(leaderboard_players_df, headers: Dict, script_config: dataclass) -> List[List[Dict]]:
    all_leaderboard_snapshots = []
    leaderboard_categories = leaderboard_players_df["data_category_name"].unique()
    #print(leaderboard_categories)
    idx = 0
    for each_category in leaderboard_categories:
        print(f"Looking up leaderboard category: {idx+1}/{len(leaderboard_categories)}: {each_category}")
        player_usernames = leaderboard_players_df[leaderboard_players_df["data_category_name"] == each_category]["username"] # this is a list of usernames for each group
        category_snapshot = lookup_player_batch_set_size(player_usernames, headers, script_config)
        for each_person in category_snapshot:
            each_person["data_category_name"] = each_category
            each_person["data_category_type"] = "leaderboard"
        all_leaderboard_snapshots.append(category_snapshot)
        idx += 1
        print(f"Finished looking up leaderboard category: {each_category}.")
        # break # if doing 1 category for testing
    return all_leaderboard_snapshots

def write_snapshots_to_parquet(snapshots_list: List[Dict], end_location:str, compression:str = "snappy", dropNames:bool = False) -> str:
    # takes a list of snapshot dicts and writes to parquet at the end location specified, with optional compression (default snappy)
    # returns the path to the Parquet file for ease of debugging/locating
    snapshots_df = pd.DataFrame(snapshots_list)
    snapshots_df = parse_dates(snapshots_df, "snapshot_datetime") # make sure snapshot_datetime is in datetime format for partitioning and querying later; this is the time we pulled the snapshot, not the time the snapshot was created in WOM
    
    # even though these strings are a little off from the snapshot datetimes, good enough for file write organization purposes
    date_str = time.strftime("%Y-%m-%d")
    time_str = time.strftime("%H%M%S")
    
    # add date and time partitioning
    end_location = os.path.join(end_location, f"{date_str}")
    # make folder if it doesnt exist
    pathlib.Path(end_location).mkdir(parents=True, exist_ok=True)
    end_location = os.path.join(end_location, f"snapshot_{time_str}_private.parquet")
    
    if os.path.exists(end_location) and os.path.getsize(end_location) > 0:
        print(f"Snapshot parquet already exists at {end_location}, skipping creation.")
    else:
        print("Writing snapshots DataFrame to Parquet at: ", end_location)
        if dropNames:
            snapshots_df = snapshots_df.drop(columns=["username", "display_name"], errors="ignore") # drop username/display_name if they exist and if dropNames is true, but ignore if they don't exist since some dims may not have these columns
        snapshots_df.to_parquet(end_location, index=False, compression=compression, engine="pyarrow")
    return str(end_location)

def flatten_bronze(data):
    flattened_rows = []
    for batch in data:
        for player in batch:
            if "error" in player:
                flattened_rows.append({
                    "username": player.get("username"),
                    "error": player.get("error")
                })
            else:
                flattened_rows.append({
                    "username": player["username"],
                    "display_name": player["display_name"],
                    "player_id": player["playerId"],
                    "created_at": player["createdAt"],
                    "imported_at": player["importedAt"],
                    "data_category_type": player["data_category_type"],
                    "data_category_name": player["data_category_name"],
                    # For bronze layer, we are going to keep nested json for the fields:
                    # This is so schema doesn't explode with 100 columns, can clean and process later for silver
                    "skills": player["data"]["skills"],
                    "bosses": player["data"]["bosses"],
                    "activities": player["data"]["activities"],
                    "computed": player["data"]["computed"],
                })
    return flattened_rows

def main():
    script_config_class = load_script_config()
    wom_headers = {
        "x-api-key": script_config_class.api_key,
        "User-Agent": script_config_class.discord_username
    }
    
    group_player_df = pd.read_parquet(group_player_parquet_path)
    group_player_snapshots = lookup_all_groups(group_player_df, wom_headers, script_config_class)
    group_player_flattened = flatten_bronze(group_player_snapshots)
    group_player_snapshots_parquet = write_snapshots_to_parquet(group_player_flattened, bronze_snapshots_folder_dir)
    
    leaderboard_players_df = pd.read_parquet(leaderboard_gains_parquet_path)
    leaderboard_player_snapshots = lookup_all_leaderboard_categories(leaderboard_players_df, wom_headers, script_config_class)
    leaderboard_players_flattened = flatten_bronze(leaderboard_player_snapshots)
    leaderboard_player_snapshots_parquet = write_snapshots_to_parquet(leaderboard_players_flattened, bronze_snapshots_folder_dir)

if __name__ == "__main__":
    main()