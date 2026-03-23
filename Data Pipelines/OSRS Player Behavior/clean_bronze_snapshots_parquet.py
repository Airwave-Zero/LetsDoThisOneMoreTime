# this file is for cleaning up the bronze snapshot parquet files, and establishing the snapshot fact tables
import os
import pandas as pd
from utils import project_paths
from utils.generic_util import parse_dates
from typing import List,Dict

bronze_snapshot_parquet_folder_path = project_paths.bronze_snapshot_parquet_folder_path
silver_fact_table_folder_path = project_paths.silver_fact_table_folder_path

silver_all_player_dim_path = project_paths.silver_all_player_dim_path
silver_metric_dim_path = project_paths.silver_metric_dim_path
silver_period_dim_path = project_paths.silver_period_dim_path

def flatten_dict(player, data_category:str) -> List[Dict]:
    '''This function takes in a row of the player dataframe and unpacks/flattens the nested json for one of the data categories (skills, bosses, or activities) into a long format table with other necessary things. Returns a list of dicts that all correspond to one player and can be converted to a dataframe.'''
    flattened_player_rows = []
    if data_category == "skills":
        metric_type = "experience"
    elif data_category == "bosses":
        metric_type = "kills"
    elif data_category == "activities":
        metric_type = "score"
    else:
        metric_type = "value" # default for computed or any other categories
    if not pd.isna(player["error"]):
        flattened_player_rows.append({
            "snapshot_ts": player["created_at"],
            "player_id": player["player_id"],
            "username": player["username"],
            "display_name": player["display_name"],
            "metric": None,
            "value": None,
            "rank": None,
            "data_category_type": player["data_category_type"],
            "data_category_name": player["data_category_name"],
            "error": player["error"]})
    else:
        for thing in player[data_category]:
            nested_metric_obj = player[data_category][thing]
            flattened_player_rows.append({
                "snapshot_ts": player["created_at"],
                "player_id": player["player_id"],
                "username": player["username"],
                "display_name": player["display_name"],
                "metric": thing,
                "value": nested_metric_obj[metric_type],
                "rank": nested_metric_obj["rank"],
                "data_category_type": player["data_category_type"],
                "data_category_name": player["data_category_name"],
                # completely drop level since only skills have it and it's easy to just get from the metric_dim if needed, and it will save a lot of space and performance on the fact table
                # "level": nested_metric_object["level"]
                "error": player["error"]
            })
    return flattened_player_rows # a list where each row is one stat/metric for the player, i.e. only one player's data is returned from this function but its just in long format

def flatten_dataframe(file_dataframe:Dict) -> List[Dict]:
    '''This function takes in the parquet read from one file, and flattens the nested json for skills, bosses, and activities into a long format table with other necessary things. Returns a list of dicts that can be easily converted to a dataframe.'''
    all_flattened_rows_from_df = []
    for _, player in file_dataframe.iterrows():
        for data_category in ["skills", "bosses", "activities"]:
            print(f"Flattening data category: {data_category}...")
            thing = flatten_dict(player, data_category)
            all_flattened_rows_from_df.extend(thing)
    return all_flattened_rows_from_df

def generate_snapshot_fact_table(snapshot_file_path:str, snapshot_date:str, player_dim:pd.DataFrame, metric_dim:pd.DataFrame, period_dim: pd.DataFrame):
    '''This function takes in a folder of snapshot parquet data (1 folder = 2 parquets, 1 for group and 1 for leader) and generates 1 big fact table for that folder/date.'''
    all_flattened_snapshots = []
    snapshots_per_folder = os.listdir(snapshot_file_path)
    for each_file in snapshots_per_folder:
        if each_file.endswith(".parquet"):
            file_path = os.path.join(snapshot_file_path, each_file)
            print(f"Cleaning snapshot parquet file: {each_file}...")
            file_dataframe = pd.read_parquet(file_path)
            file_dataframe = parse_dates(file_dataframe, "created_at")
            flattened_data = flatten_dataframe(file_dataframe)
            all_flattened_snapshots.extend(flattened_data)
    flattened_df = pd.DataFrame(all_flattened_snapshots)
    silver_snapshot_parquet_path = os.path.join(silver_fact_table_folder_path, f"snapshot_fact_{snapshot_date}_private.parquet")
    print(f"Saving snapshot fact table to: {silver_snapshot_parquet_path}")
    flattened_df.to_parquet(silver_snapshot_parquet_path, compression="snappy", index=False, engine="pyarrow")

def main():
    all_player_dim  = pd.read_parquet(silver_all_player_dim_path)
    metric_dim = pd.read_parquet(silver_metric_dim_path)
    period_dim = pd.read_parquet(silver_period_dim_path)
    
    all_snapshot_folders = os.listdir(bronze_snapshot_parquet_folder_path)
    all_paths = []
    for each_folder in all_snapshot_folders:
        if each_folder != '.DS_Store':
            print(f"Cleaning snapshot folder: {each_folder}")
            full_folder_path = os.path.join(bronze_snapshot_parquet_folder_path, each_folder)
            snapshot_fact_path = generate_snapshot_fact_table(full_folder_path, each_folder, all_player_dim, metric_dim, period_dim)
            all_paths.append(snapshot_fact_path)

if __name__ == "__main__":
    main()