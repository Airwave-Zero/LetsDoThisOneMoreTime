# this will be the script that handles all the update_players_osrs functions

import os
import time
import requests
from typing import List, Dict
import pandas as pd

# step 1 gather the lsit of players from the parquet files in the raw_parquet_bronze folder
# step2 for each player, gather snapshot data and write to parquet in the raw_parquet_bronze folder, partitioned by snapshot_date

config_folder_dir = os.path.join(os.path.dirname(__file__), "config")
script_config_path = os.path.join(config_folder_dir, "script_config_private.json")

parquet_folder_dir = os.path.join(os.path.dirname(__file__), "parquet_data")
raw_parquet_bronze_dir = os.path.join(parquet_folder_dir, "raw_parquet_bronze")
player_parquet_folder_dir = os.path.join(raw_parquet_bronze_dir, "players")
snapshot_parquet_folder_dir = os.path.join(raw_parquet_bronze_dir, "snapshots")

cleaned_parquet_silver_dir = os.path.join(parquet_folder_dir, "cleaned_parquet_silver")
fact_table_dir = os.path.join(cleaned_parquet_silver_dir, "fact_tables")

group_player_parquet = os.path.join(player_parquet_folder_dir, "Group_Player_List_private.parquet")
leaderboard_gains_parquet = os.path.join(player_parquet_folder_dir, "Leaderboard_Combined_Player_List_private.parquet")


def main():
    group_player_df = pd.read_parquet(group_player_parquet)
    #leaderboard_players_df = pd.read_parquet(leaderboard_gains_parquet)
    
    print(group_player_df["username"])

if __name__ == "__main__":
    main()