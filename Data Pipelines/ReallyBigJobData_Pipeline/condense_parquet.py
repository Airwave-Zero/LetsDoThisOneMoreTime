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

snapshots_cleaned_parquet_dir = project_paths.cleaned_parquet_dir
gold_extracted_parquet_dir = project_paths.gold_extracted_parquet_dir

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
    This function takes in a file name and extracts the snapshot information (year, job board, crawl name) from the file name. See below for example.
    
    # example cleaned_parquet_private/cleaned_https___index.commoncrawl.org_CC-MAIN-2024-10-index_url__.greenhouse.io____output_json.parquet
    # ['cleaned', 'https', '', '', 'index.commoncrawl.org', 'CC-MAIN-2026-12-index', 'url', '', '.jobs.ashbyhq.com', '', '', '', 'output', 'json.parquet']
    '''
    parts = file_name.split("_")
    if len(parts) < 14: # unfortunately hard coded
        logging.warning(f"Unexpected file name format: {file_name}")
        return None
    year = parts[5].split("-")[2]  # should extract 2024 from CC-MAIN-2024-10
    job_board = parts[8].replace(".", "_")[1:]    # turn .jobs.ashbyhq.com into jobs_ashbyhq_com
    crawl_name = parts[5]  # should extract CC-MAIN-2024-10
    return year, job_board, crawl_name


############### MAIN FUNCTIONS ###############
def combine_parquets_within_partitions(start_dir):
    '''
    This is the main function that
    1) iterates through all of the folders in cleaned_private_parquet
    1.1) skips over empties and anything that isnt a folder
    2) iterates through all job folders and skips over all non-folders
    3) looks to see if files have been combined yet, and skip if so
    4) otherwise execute the combining function
    '''
    
    for year_folder in os.listdir(start_dir):
        if year_folder == "empty":
            continue
        year_path = os.path.join(start_dir, year_folder)
        if not os.path.isdir(year_path):
            continue
        for job_board_folder in os.listdir(year_path):
            if job_board_folder == ".DS_Store":
                continue
            job_board_path = os.path.join(year_path, job_board_folder)
            if not os.path.isdir(job_board_path):
                continue
            raw_path = os.path.join(job_board_path, "raw")
            combined_path = os.path.join(job_board_path, "combined")
            # TODO: check based on memory instead of just solely checking existence
            if os.listdir(combined_path).count(".parquet") > 0:
                logging.info(f"Combined parquets already exists for {job_board_path}, skipping combination.")
                continue
            else:
                process_and_chunk_parquets(raw_path, job_board_folder, combined_path, target_mb=300)

def process_and_chunk_parquets(folder_path, job_board_folder_name, output_path, target_mb=300):
    '''
    This function iterates through all of the parquet files and
    1) estimates the bytes per row from a random # of parquet files
    2) uses that estimate to determine how many rows to write out per file in order to not exceed the target file size (in mb)
    3) iterates through the parquet files and writes out combined parquet files in chunks, making sure to include the crawl name and the year for easier/better analysis
    3.1) writes out any leftovers
    '''
    TARGET_BYTES = target_mb * 1024 * 1024

    # Step 1: Estimate row size
    logging.info(f"Estimating bytes per row for folder: {folder_path}")
    bytes_per_row = estimate_bytes_per_row(folder_path)
    
    # For some reason, entered a folder with no parquet files, skip the folder
    if bytes_per_row == 0:
        return
    
    # Step 2: Compute rows per output file
    rows_per_file = int(TARGET_BYTES / bytes_per_row)
    logging.info(f"Target rows per file: {rows_per_file}")

    parquet_files = [
        f for f in os.listdir(folder_path)
        if f.endswith(".parquet") and not f.startswith("combined_")
    ]

    buffer_chunks = []
    current_rows = 0
    part_num = 1

    year = ''
    crawl_name = ''
    
    for file in parquet_files:
        file_path = os.path.join(folder_path, file)
        logging.info(f"Reading {file}")

        try:
            df = pd.read_parquet(file_path)
            
            # uncomment these if running on bronze data, aka for creating partition folders
            #year, _ , crawl_name = get_snapshot_info_from_name(file)
            #df['snapshot_year'] = year
            #df['snapshot_crawl_name'] = crawl_name
        except Exception as e:
            logging.error(f"Failed to read {file}: {e}")
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

                output_file = os.path.join(output_path,f"combined_{job_board_folder_name}_part{part_num}.parquet")

                write_df_to_parquet(final_df, output_file)

                # Reset buffer
                buffer_chunks = []
                current_rows = 0
                part_num += 1

    # Write any remaining data
    if buffer_chunks:
        final_df = pd.concat(buffer_chunks, ignore_index=True)
        #final_df['snapshot_year'] = year
        #final_df['snapshot_crawl_name'] = crawl_name

        output_file = os.path.join(output_path, f"combined_{job_board_folder_name}_part{part_num}.parquet")
        write_df_to_parquet(final_df, output_file)

def create_folder_partitions(start_dir):
    '''
    for each file in the cleaned_parquet_private folder, get the snapshot information from the file name, and then create a nested folder structure based on the year, job board, and crawl name (if it doesn't already exist)
    '''
    for each_file in os.listdir(start_dir):
        file_path = os.path.join(start_dir, each_file)
        if os.path.isfile(file_path) and each_file.endswith(".parquet"):
            if each_file.startswith("cleaned_"):
                year, job_board, _ = get_snapshot_info_from_name(each_file)
                new_folder_path = os.path.join(start_dir, year, job_board, "raw")
                combined_path = os.path.join(start_dir, year, job_board, "combined")
                os.makedirs(new_folder_path, exist_ok=True)
                os.makedirs(combined_path, exist_ok=True)
                new_file_path = os.path.join(new_folder_path, each_file)
            else:
                os.makedirs(os.path.join(start_dir, "empty"), exist_ok=True)
                new_file_path = os.path.join(start_dir, "empty", each_file)
            if not os.path.exists(new_file_path):
                os.rename(file_path, new_file_path)
                logging.info(f"Moved {each_file} to {new_folder_path}")
            else:
                logging.warning(f"File already exists at destination: {new_file_path}. Skipping move for {each_file}.")
             
def main():
    # The nested folder structure is going to be: cleaned_parquet_private / 2024, 2025, 2026 / ashbyhq, greenhouse, lever / raw_silver, combined_silver/ (cleaned_) or combined_.parquet
    
    # Step 1) create the folder structure (year, job_board, raw_silver, combined_silver) if it doesn't already exist
    # 1.1) move the cleaned parquet files into the raw_silver folder (and move any empty files into an empty folder)
    # create_folder_partitions(snapshots_cleaned_parquet_dir)

    # Step 2) now go through every nested folder, read in all the cleaned_*.parquet files, add snapshot information column, and combine them into one parquet file per job board (with suffix _combined.parquet and split into parts if file size is > 500 mb)
    #combine_parquets_within_partitions(snapshots_cleaned_parquet_dir)
    combine_parquets_within_partitions(gold_extracted_parquet_dir)

if __name__ == "__main__":
    main()