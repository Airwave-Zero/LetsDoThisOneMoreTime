from pathlib import Path
import os

root_dir = Path(__file__).resolve().parent.parent
config_folder_dir = os.path.join(root_dir, "config")
filter_path = os.path.join(config_folder_dir, "osrs_filters.json")
script_config_path = os.path.join(config_folder_dir, "script_config_private.json")
group_names_path = os.path.join(config_folder_dir, "group_names.json")

parquet_folder_path = os.path.join(root_dir, "parquet_data")
bronze_parquet_folder_path = os.path.join(parquet_folder_path, "raw_parquet_bronze")
raw_player_parquet_folder_path = os.path.join(bronze_parquet_folder_path, "players")
bronze_group_player_parquet_path = os.path.join(raw_player_parquet_folder_path, "Group_Player_List_private.parquet")
bronze_all_leaderboard_player_parquet_path = os.path.join(raw_player_parquet_folder_path, "Leaderboard_Combined_Player_List_private.parquet")
bronze_snapshot_parquet_folder_path = os.path.join(bronze_parquet_folder_path, "snapshots")

silver_parquet_folder_path = os.path.join(parquet_folder_path, "cleaned_parquet_silver")
dims_folder_path = os.path.join(silver_parquet_folder_path, "dims")
fact_table_folder_path = os.path.join(silver_parquet_folder_path, "fact_tables")
silver_combined_player_dim_path = os.path.join(dims_folder_path, "all_player_dim_private.parquet")
silver_metric_dim_path = os.path.join(dims_folder_path, "metric_dim.parquet")
silver_period_dim_path = os.path.join(dims_folder_path, "period_dim.parquet")
silver_group_dim_path = os.path.join(dims_folder_path, "group_dim.parquet")