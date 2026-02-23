import os
from pathlib import Path
import pandas as pd

csv_folder_dir = os.path.join(os.path.dirname(__file__), "csv_data")
raw_csv_bronze_dir = os.path.join(csv_folder_dir, "raw_csv_bronze")
cleaned_parquet_silver_dir = os.path.join(csv_folder_dir, "cleaned_parquet_silver")
dims_folder_dir = os.path.join(cleaned_parquet_silver_dir, "dims")
fact_table_dir = os.path.join(cleaned_parquet_silver_dir, "fact_tables")

def csv_to_parquet(csv_path: str, compression: str = "snappy") -> str:
    """
    Convert CSV → Parquet with a new folder structure while keeping filename.
    Returns the file path of the new Parquet file.

    TODO: Normalize the data and split it into different dims and
    fact tables
    """
    # Extract the pure filename and then build the new filename 
    # with the desired output and suffixes
    csv_path = Path(csv_path)
    csv_filename = csv_path.stem
    new_parquet_filename = f"{csv_filename}_dim.parquet"
    parquet_path = os.path.join(dims_folder_dir, new_parquet_filename)

    df = pd.read_csv(csv_path)
    df.to_parquet(
        parquet_path,
        index=False,
        compression=compression,
        engine="pyarrow",
    )

    return str(parquet_path)

def main():
    group_player_csv = os.path.join(raw_csv_bronze_dir, "Group_Player_List_private.csv")
    leaderboard_gains_csv = os.path.join(raw_csv_bronze_dir, "Gains_Leaderboard_Player_List_private.csv")

    group_player_dim = csv_to_parquet(csv_path=group_player_csv, compression="snappy")
    leaderboard_gains_dim = csv_to_parquet(csv_path=leaderboard_gains_csv, compression="snappy")
    
if __name__ == "__main__":    
    main()