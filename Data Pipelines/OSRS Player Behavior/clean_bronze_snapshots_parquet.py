# this file is for cleaning up the bronze snapshot parquet files, and establishing the snapshot fact tables
import os
import pandas as pd
from utils import project_paths
from utils.generic_util import parse_dates, calculate_level_from_xp, check_metric_has_level
from typing import List,Dict

bronze_snapshot_parquet_folder_path = project_paths.bronze_snapshot_parquet_folder_path
silver_fact_table_folder_path = project_paths.silver_fact_table_folder_path

silver_all_player_dim_path = project_paths.silver_all_player_dim_path
silver_metric_dim_path = project_paths.silver_metric_dim_path
silver_period_dim_path = project_paths.silver_period_dim_path

def get_metric_level(metric_obj:Dict):
    if check_metric_has_level(metric_obj['metric']):
        if metric_obj['level'] >= 99:
            return calculate_level_from_xp(metric_obj['experience'])
        else:
            return metric_obj['level']
    return None
    #calculate_level_from_xp(nested_metric_obj[metric_type]) if check_metric_has_level(metric) else None,

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
            "level": None,
            "error": player["error"]})
    else:
        for metric in player[data_category]:
            nested_metric_obj = player[data_category][metric]
            flattened_player_rows.append({
                "snapshot_ts": player["created_at"],
                "player_id": player["player_id"],
                "username": player["username"],
                "display_name": player["display_name"],
                "metric": metric,
                "value": nested_metric_obj[metric_type],
                "rank": nested_metric_obj["rank"],
                "data_category_type": player["data_category_type"],
                "data_category_name": player["data_category_name"],
                # completely drop level since only skills have it and it's easy to just get from the metric_dim if needed, and it will save a lot of space and performance on the fact table
                # re-add levels, and calculate 'true' level early on to save downstream gold time
                "level": get_metric_level(nested_metric_obj),
                "error": player["error"]
            })
    return flattened_player_rows # a list where each row is one stat/metric for the player, i.e. only one player's data is returned from this function but its just in long format

def flatten_dataframe(file_dataframe:Dict) -> List[Dict]:
    '''This function takes in the parquet read from one file, and flattens the nested json for skills, bosses, and activities into a long format table with other necessary things. Returns a list of dicts that can be easily converted to a dataframe.'''
    all_flattened_rows_from_df = []
    for _, player in file_dataframe.iterrows():
        for data_category in ["skills", "bosses", "activities"]:
            # print(f"Flattening data category: {data_category}...")
            curr_flattened = flatten_dict(player, data_category)
            all_flattened_rows_from_df.extend(curr_flattened)
    return all_flattened_rows_from_df

def generate_snapshot_fact_table(snapshot_file_path:str, snapshot_date:str, player_dim:pd.DataFrame, metric_dim:pd.DataFrame, period_dim: pd.DataFrame, final_parquet_path:str) -> str:
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
    print(f"Saving snapshot fact table to: {final_parquet_path}")
    flattened_df.to_parquet(final_parquet_path, compression="snappy", index=False, engine="pyarrow")
    return final_parquet_path

def main():
    all_player_dim  = pd.read_parquet(silver_all_player_dim_path)
    metric_dim = pd.read_parquet(silver_metric_dim_path)
    period_dim = pd.read_parquet(silver_period_dim_path)
    
    all_snapshot_folders = os.listdir(bronze_snapshot_parquet_folder_path)
    all_paths = []
    
    existing_files = os.listdir(silver_fact_table_folder_path)
    #print(existing_files)
    for each_folder in all_snapshot_folders:
        if each_folder != '.DS_Store':
            print(f"Cleaning snapshot folder: {each_folder}")
            new_parquet_path = os.path.join(silver_fact_table_folder_path, f"snapshot_fact_{each_folder}_private.parquet")
            # only generate a fact table if it doesn't already existw
            if not os.path.exists(new_parquet_path):
                full_folder_path = os.path.join(bronze_snapshot_parquet_folder_path, each_folder)
                snapshot_fact_path = generate_snapshot_fact_table(full_folder_path, each_folder, all_player_dim, metric_dim, period_dim, new_parquet_path)
                all_paths.append(snapshot_fact_path)
            else:
                print(f"Fact table for snapshot {each_folder} already exists at {new_parquet_path}, skipping fact table generation.")

if __name__ == "__main__":
    main()