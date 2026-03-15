import os
from pathlib import Path
import pandas as pd
import json

config_folder_dir = os.path.join(os.path.dirname(__file__), "config")
os.makedirs(config_folder_dir, exist_ok=True)
filter_path = os.path.join(config_folder_dir, "osrs_filters.json")

parquet_folder_dir = os.path.join(os.path.dirname(__file__), "parquet_data")
raw_parquet_bronze_dir = os.path.join(parquet_folder_dir, "raw_parquet_bronze")
cleaned_parquet_silver_dir = os.path.join(parquet_folder_dir, "cleaned_parquet_silver")
dims_folder_dir = os.path.join(cleaned_parquet_silver_dir, "dims")
fact_table_dir = os.path.join(cleaned_parquet_silver_dir, "fact_tables")

group_player_parquet = os.path.join(raw_parquet_bronze_dir, "Group_Player_List_private.parquet")
leaderboard_gains_parquet = os.path.join(raw_parquet_bronze_dir, "Leaderboard_Combined_Player_List_private.parquet")

with open(filter_path, "r", encoding="utf-8") as fh:
    data = json.load(fh)
    
skills_list = data.get("skill_names")
bosses_list = data.get("boss_hiscores")
activities = data.get("activities")
computed = data.get("computed")

# big TODO: refactor everything from bronze csv to bronze parquet instead
def parse_dates(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], utc=True, errors="coerce")
    return df

def write_df_to_parquet(df: pd.DataFrame, endLocation: str, compression: str = "snappy") -> str:
    """
    This function takes a DataFrame and an end location for the parquet file, and only
    creates a parquet file if it doesn't already exist at that location. 
    It returns the path to the Parquet file for ease of debugging/locating.
    """

    if os.path.exists(endLocation) and os.path.getsize(endLocation) > 0:
        print(f"Leaderboard player dim already exists at {endLocation}, skipping creation.")
    else:
        print("Writing DataFrame to Parquet at: ", endLocation)
        df.to_parquet(endLocation, index=False, compression=compression, engine="pyarrow")

    return str(endLocation)

def build_player_dim(df: pd.DataFrame, dataCategory:str) -> pd.DataFrame:
    player_cols = [
        "player_id", "username", "displayName", "type", "build",
        "status", "country", "patron", "registeredAt", "dataCategory"
    ]

    player_dim = (
        df[player_cols]
        .drop_duplicates(subset=["player_id"])
        .rename(columns={
            "displayName": "display_name",
            "registeredAt": "registered_at",
            "dataCategory": "data_category"
        })
    )

    return parse_dates(player_dim, ["registered_at"])


def build_metric_dim(df: pd.DataFrame) -> pd.DataFrame:
    # Normalize expected columns
    metric_col = "metric_name" if "metric_name" in df.columns else "metric"
    type_col = "metric_type" if "metric_type" in df.columns else None

    metric_dim = (
        df[[c for c in [metric_col, type_col] if c is not None]]
        .drop_duplicates()
        .assign(
            metric_category=lambda x: (
                x[type_col]
                if type_col
                else x[metric_col].apply(
                    lambda m:
                        "skill" if m in skills_list
                        else "boss" if m in bosses_list 
                        else "activity" if m in activities
                        else "computed" if m in computed
                        else "other"
                )
            )
        )
        .rename(columns={metric_col: "metric"})
        .reset_index(drop=True)
    )
    # Clean up metric category types for ease of analysis further downstream
    metric_dim = metric_dim.assign(
        value_type=lambda x: x["metric_category"].map({
            "skill": "experience",
            "boss": "kills",
            "activity": "score",
            "computed": "value",
        }),
        has_level=lambda x: x["metric_category"].eq("skill"),
        has_rank=True,
    )
    metric_dim["metric_id"] = metric_dim.index + 1
    return metric_dim[
        [
            "metric_id",
            "metric",
            "metric_category",
            "value_type",
            "has_level",
            "has_rank",
        ]
    ]

def build_period_dim(df: pd.DataFrame) -> pd.DataFrame:
    period_dim = (
        df[["period"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    period_dim["period_id"] = period_dim.index + 1
    return period_dim[["period_id", "period"]]

def build_snapshot_fact(snapshot_df: pd.DataFrame, metric_dim: pd.DataFrame,) -> pd.DataFrame:
    df = snapshot_df.copy()

    df["snapshot_time"] = pd.to_datetime(
        df["snapshot_time"], utc=True, errors="coerce"
    )

    df = (
        df
        .merge(
            metric_dim[["metric_id", "metric", "metric_category"]],
            left_on=["metric_name", "metric_type"],
            right_on=["metric", "metric_category"],
            how="left",
        )
        .rename(columns={
            "value": "metric_value",
            "rank": "metric_rank",
        })
    )

    return df[
        [
            "snapshot_time",
            "snapshot_id",
            "player_id",
            "metric_id",
            "metric_value",
            "metric_rank",
        ]
    ]

def build_leaderboard_fact(df, metric_dim, period_dim) -> pd.DataFrame:
    df = parse_dates(df, ["startDate", "endDate"])

    df = (
        df
        .merge(metric_dim, on="metric", how="left")
        .merge(period_dim, on="period", how="left")
        .rename(columns={
            "startDate": "start_date",
            "endDate": "end_date",
            "expGained": "exp_gained"
        })
    )

    df["snapshot_ts"] = pd.Timestamp.utcnow()

    return df[
        [
            "player_id",
            "metric_id",
            "period_id",
            "start_date",
            "end_date",
            "exp_gained",
            "snapshot_ts",
        ]
    ]

def main():

    group_player_df = pd.read_parquet(group_player_parquet)
    player_data_df = pd.read_parquet(leaderboard_gains_parquet)

    # originals for preservation sake, but we drop username/displayname later for protecting info since pushing to github
    leaderboard_player_dim = build_player_dim(player_data_df, "leaderboard")
    group_player_dim = build_player_dim(group_player_df, "group")
    metric_dim = build_metric_dim(player_data_df)
    period_dim = build_period_dim(player_data_df)

    leaderboard_player_dim_path = ''
    group_player_dim_path = ''
    combined_player_dim_path = ''

    playerSetSameColumns = set(leaderboard_player_dim.columns) == set(group_player_dim.columns)
    if(playerSetSameColumns):
        print("Group and leaderboard player dims have the same columns, creating combined player dim.")
        combined_dim = pd.concat([leaderboard_player_dim, group_player_dim], ignore_index=True).drop_duplicates(subset=["player_id"]) #keep for debugging
        privatized_dim = combined_dim.drop(columns=["username", "display_name"]) # leave in if pushing to public/writing to public
        combined_player_dim_path = write_df_to_parquet(privatized_dim, f"{dims_folder_dir}/all_player_dim_EXAMPLE.parquet")
        #combined_player_dim_path = write_df_to_parquet(combined_dim, f"{dims_folder_dir}/all_player_dim_private.parquet")
    else:
        private_leaderboard_dim = leaderboard_player_dim.drop(columns=["username", "display_name"])
        leaderboard_player_dim_path = write_df_to_parquet(private_leaderboard_dim, f"{dims_folder_dir}/leaderboard_player_dim.parquet")   
             
        private_group_dim = group_player_dim.drop(columns=["username", "display_name"])
        group_player_dim_path = write_df_to_parquet(private_group_dim, f"{dims_folder_dir}/group_player_dim.parquet")
            
    metric_dim_path = write_df_to_parquet(metric_dim, f"{dims_folder_dir}/metric_dim.parquet")
    period_dim_path = write_df_to_parquet(period_dim, f"{dims_folder_dir}/period_dim.parquet")
    
    
    
if __name__ == "__main__":    
    main()

'''
updating a player : curl -X POST https://api.wiseoldman.net/v2/players/zezima \
  -H "Content-Type: application/json"

Tracks or updates a player. Returns a PlayerDetails object on success, which includes their latest snapshot.

extract the snapshot from the updated player and store it
'''