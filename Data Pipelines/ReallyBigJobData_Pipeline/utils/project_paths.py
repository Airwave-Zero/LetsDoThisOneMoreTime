from pathlib import Path
import os

root_dir = Path(__file__).resolve().parent.parent
config_folder_dir = os.path.join(root_dir, "config")
json_config_file_dir = os.path.join(config_folder_dir, "script_config_private.json")

website_data_dir = os.path.join(root_dir, "Website_Data")

raw_website_data_bronze_dir = os.path.join(website_data_dir, "Raw_Website_Data_Bronze")

cleaned_website_data_silver_dir = os.path.join(website_data_dir, "Cleaned_Website_Data_Silver")

snapshot_json_responses_dir = os.path.join(root_dir, "snapshot_json_responses_private")
snapshot_visited_dir = os.path.join(root_dir, "snapshot_visited_private")
snapshots_parquet_dir = os.path.join(root_dir, "snapshot_parquet_private")

cleaned_parquet_dir = os.path.join(root_dir, "cleaned_parquet_private")