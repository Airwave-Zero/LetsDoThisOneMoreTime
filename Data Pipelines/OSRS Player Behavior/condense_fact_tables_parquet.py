import os
from utils import project_paths
import pandas as pd
import logging
import random
import io

random.seed(42)  # For reproducible results

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

snapshots_cleaned_parquet_dir = project_paths.silver_parquet_folder_path
snapshots_fact_tables_dir = project_paths.silver_fact_table_folder_path

gold_parquet_layer_dir = project_paths.gold_parquet_folder_path
gold_parquet_fact_tables_path = project_paths.gold_parquet_folder_path
gold_parquet_by_month_path = project_paths.gold_parquet_by_month_path
gold_parquet_combined_path = project_paths.gold_parquet_combined_path

############### HELPER FUNCTIONS ###############
def write_df_to_parquet(df, output_file_path):
    df.to_parquet( output_file_path, index=False, engine="pyarrow", compression="snappy")
    file_size_mb = os.path.getsize(output_file_path) / (1024 * 1024)
    logging.info( f"Saved {output_file_path} | {len(df)} rows | {file_size_mb:.2f} MB")

def estimate_bytes_per_row(folder_path, sample_files=5, sample_rows=5000):
    '''
    Estimate bytes per row using random sampling across parquet files.
    '''
    parquet_files = [f for f in os.listdir(folder_path) if f.endswith(".parquet")]
    
    if not parquet_files:
        logging.warning(f"No parquet files found for sampling in folder {folder_path}.")
        return 0

    sampled_files = random.sample(parquet_files, min(sample_files, len(parquet_files)))
    logging.info(f"Sampling {len(sampled_files)} files for byte estimation...")
    samples = []
    for f in sampled_files:
        df = pd.read_parquet(os.path.join(folder_path, f))
        if not df.empty:
            samples.append(df.head(sample_rows))

    sample_df = pd.concat(samples, ignore_index=True)

    buffer = io.BytesIO()
    sample_df.to_parquet(buffer, index=False)

    bytes_per_row = buffer.tell() / len(sample_df)

    logging.info(f"Estimated bytes per row: {bytes_per_row:.2f}")
    return bytes_per_row

def get_snapshot_info_from_name(file_name):
    '''
    Extract year and month from snapshot fact file name.
    File format: snapshot_fact_{YYYY-MM-DD}_private.parquet
    Example: snapshot_fact_2026-03-21_private.parquet
    
    Returns: (year, month, year_month) or None if format doesn't match
    '''
    # Remove .parquet extension
    base_name = file_name.replace(".parquet", "")
    parts = base_name.split("_")
    
    # Expected format: snapshot_fact_2026-03-21_private
    if len(parts) < 3 or parts[0] != "snapshot" or parts[1] != "fact":
        logging.warning(f"Unexpected file name format: {file_name}")
        return None
    
    date_str = parts[2]  # e.g., "2026-03-21"
    date_parts = date_str.split("-")
    
    if len(date_parts) != 3:
        logging.warning(f"Unexpected date format in {file_name}: {date_str}")
        return None
    
    year = date_parts[0]  # e.g., "2026"
    month = date_parts[1]  # e.g., "03"
    year_month = f"{year}-{month}"  # e.g., "2026-03"
    
    return year, month, year_month


############### MAIN FUNCTIONS ###############
def combine_by_month(folder_path, output_folder_name="by_month"):
    '''
    This function:
    1) groups all parquet files by year-month (extracted from filename)
    2) combines all files in each month group into one large parquet per month
    3) returns the path to the output folder containing the month-combined files
    '''
    output_path = os.path.join(folder_path, output_folder_name)
    os.makedirs(output_path, exist_ok=True)
    
    # Group files by year-month
    month_groups = {}
    
    parquet_files = [
        f for f in os.listdir(folder_path)
        if f.endswith(".parquet") and not f.startswith("combined_") and not f.startswith("month_")
    ]
    
    logging.info(f"Found {len(parquet_files)} parquet files to process")
    
    for file in parquet_files:
        snapshot_info = get_snapshot_info_from_name(file)
        if snapshot_info is None:
            continue
        year, month, year_month = snapshot_info
        
        if year_month not in month_groups:
            month_groups[year_month] = []
        month_groups[year_month].append(file)
    
    logging.info(f"Grouped files into {len(month_groups)} month(s): {list(month_groups.keys())}")
    
    # Combine files for each month
    combined_month_files = []
    for year_month, files in sorted(month_groups.items()):
        logging.info(f"Combining {len(files)} files for month {year_month}")
        
        dfs = []
        for file in files:
            file_path = os.path.join(folder_path, file)
            try:
                df = pd.read_parquet(file_path)
                dfs.append(df)
                logging.info(f"  Read {file} ({len(df)} rows)")
            except Exception as e:
                logging.error(f"Failed to read {file}: {e}")
                continue
        
        if dfs:
            combined_df = pd.concat(dfs, ignore_index=True)
            output_file = os.path.join(output_path, f"month_{year_month}_private.parquet")
            write_df_to_parquet(combined_df, output_file)
            combined_month_files.append(output_file)
    
    logging.info(f"Created {len(combined_month_files)} month-combined parquet files")
    return output_path, combined_month_files

def combine_parquets_from_folder(folder_path, output_folder_name="combined", target_mb=300):
    '''
    This is the main function that:
    1) combines files by month (into one big parquet per month)
    2) then chunks those month-combined files into smaller pieces based on target file size
    3) organizes output by month in separate folders
    4) skips months that already have combined files (guardrail for performance)
    '''
    # Step 0: Create the output_folder
    os.makedirs(gold_parquet_layer_dir, exist_ok=True)
    os.makedirs(gold_parquet_fact_tables_path, exist_ok=True)
    
    # Step 1: Combine by month
    month_combined_folder, month_files = combine_by_month(folder_path, gold_parquet_by_month_path)
    
    # Step 2: Chunk the month-combined files separately per month
    output_base_path = os.path.join(folder_path, gold_parquet_combined_path)
    os.makedirs(output_base_path, exist_ok=True)
    
    logging.info(f"Now chunking {len(month_files)} month-combined files to {target_mb}MB target size")
    
    for month_file in sorted(month_files):
        # Extract year and month from the file path (e.g., "month_2026-03.parquet")
        base_name = os.path.basename(month_file)
        year_month = base_name.replace("month_", "").replace(".parquet", "")  # e.g., "2026-03"
        year, month = year_month.split("-")  # e.g., year="2026", month="03"
        
        # Create month-specific output folder
        month_output_folder = os.path.join(output_base_path, year_month)
        os.makedirs(month_output_folder, exist_ok=True)
        
        # Check if this month already has combined files (guardrail)
        existing_files = [
            f for f in os.listdir(month_output_folder)
            if f.startswith(f"combined_{year}_{month}_part") and f.endswith(".parquet")
        ]
        
        if existing_files:
            logging.info(f"Skipping {year_month}: {len(existing_files)} combined file(s) already exist")
            continue
        
        logging.info(f"Processing month {year_month}...")
        process_and_chunk_parquets(
            folder_path=month_combined_folder,
            output_path=month_output_folder,
            year_month=year_month,
            target_mb=target_mb,
            month_file=month_file
        )

def process_and_chunk_parquets(folder_path, output_path, year_month, target_mb=300, month_file=None):
    '''
    This function processes a specific month's parquet file and chunks it:
    1) estimates the bytes per row
    2) uses that estimate to determine how many rows to write out per file to not exceed target file size
    3) writes out combined parquet files in chunks with month-specific naming
    4) writes out any leftovers
    
    If month_file is provided, only processes that specific file.
    '''
    TARGET_BYTES = target_mb * 1024 * 1024
    year, month = year_month.split("-")
    
    # Determine which files to process
    if month_file:
        # Single month file mode
        files_to_process = [month_file]
        logging.info(f"Processing single month file: {os.path.basename(month_file)}")
    else:
        # Legacy mode: process all parquet files in folder
        files_to_process = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.endswith(".parquet") and not f.startswith("combined_")
        ]
    
    # Step 1: Estimate row size
    logging.info(f"Estimating bytes per row for folder: {folder_path}")
    bytes_per_row = estimate_bytes_per_row(folder_path)
    
    # For some reason, entered a folder with no parquet files, skip the folder
    if bytes_per_row == 0:
        return
    
    # Step 2: Compute rows per output file
    rows_per_file = int(TARGET_BYTES / bytes_per_row)
    logging.info(f"Target rows per file: {rows_per_file}")

    buffer_chunks = []
    current_rows = 0
    part_num = 1
    
    for file_path in files_to_process:
        file_name = os.path.basename(file_path)
        logging.info(f"Reading {file_name}")

        try:
            df = pd.read_parquet(file_path)
        except Exception as e:
            logging.error(f"Failed to read {file_name}: {e}")
            continue

        start = 0
        total_rows = len(df)

        while start < total_rows:
            remaining_capacity = rows_per_file - current_rows

            chunk = df.iloc[start:start + remaining_capacity]

            buffer_chunks.append(chunk)
            current_rows += len(chunk)
            start += len(chunk)

            # When we hit target size → write file
            if current_rows >= rows_per_file:
                final_df = pd.concat(buffer_chunks, ignore_index=True)

                output_file = os.path.join(output_path, f"combined_{year}_{month}_part{part_num}_private.parquet")

                write_df_to_parquet(final_df, output_file)

                # Reset buffer
                buffer_chunks = []
                current_rows = 0
                part_num += 1

    # Write any remaining data
    if buffer_chunks:
        final_df = pd.concat(buffer_chunks, ignore_index=True)

        output_file = os.path.join(output_path, f"combined_{year}_{month}_part{part_num}_private.parquet")
        write_df_to_parquet(final_df, output_file)

def main():
    #test_fact_tables_folder = r"/Users/airwavezero/Desktop/coding/LetsDoThisOneMoreTime/Data Pipelines/OSRS Player Behavior/legacy/fact_tables"
    combine_parquets_from_folder(snapshots_fact_tables_dir)

if __name__ == "__main__":
    main()