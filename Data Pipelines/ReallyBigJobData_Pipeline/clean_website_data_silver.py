# This file is to take the raw bronze parquet website data and clean it into
# dims and fact tables if necessary
from __future__ import annotations
import logging
import time
from typing import List, Dict
import pandas as pd
import os
from utils import project_paths
from utils.generic_util import worker_amount 
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

snapshots_parquet_dir = project_paths.snapshots_parquet_dir
snapshots_cleaned_parquet_dir = project_paths.cleaned_parquet_dir

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

########### HELPER FUNCTIONS ############
def extract_job_id(url):
    # Example URLs to parse: https://boards.greenhouse.io/10xgenomics/jobs/5361076
    # Example 2: https://boards.greenhouse.io/10xgenomics/jobs/5515988?gh_jid=5515988&utm_source=Venrock+job+board&utm_medium=getro.com&gh_src=Venrock+job+board
    if not url: 
        return None
    parts = url.strip('/').split('/')
    if len(parts) >= 2:
        # drop query parameters if they exist, otherwise return the last part as is
        if '?' in parts[-1]:
             return parts[-1].split('?')[0]
        else:
            return parts[-1] 
    return None

def extract_job_source(url):
    if not url: 
        return None
    lowered = url.lower()
    if 'greenhouse' in lowered: 
        return 'greenhouse'
    elif 'lever' in lowered: 
        return 'lever'
    elif 'ashbyhq' in lowered: 
        return 'ashbyhq'
    return None

def extract_company(url):
    if not url: 
        return None
    parts = [p for p in urlparse(url).path.split('/') if p]
    if parts:
        return parts[0]
    return None

def extract_all_info(df: pd.DataFrame, cleaned_file_name:str) -> List[Dict]:
    """Reads in a dataframe, lightly extracts necessary information
    and returns a list of dictionaries to be converted later."""
    print(f"Processing {cleaned_file_name}, extracting info... ")
    job_info_list = []
    for _, row in df.iterrows():
        url = row.get('url', '')

        job_id = extract_job_id(url)
        company = extract_company(url)
        job_source = extract_job_source(url)
        raw_html = row.get('html')
        description = row.get('job_text')
        timestamp = row.get('timestamp')
        
        job_info = {
            'job_id': job_id,
            'company_name': company,
            'job_source': job_source,
            'raw_html': raw_html,
            'description': description,
            'timestamp': timestamp,
            'url': url,
        }
        job_info_list.append(job_info)
    
    return job_info_list

def process_one_parquet(file):
    curr_file_df = pd.read_parquet(os.path.join(snapshots_parquet_dir, file))
    cleaned_file_name = os.path.join(snapshots_cleaned_parquet_dir, f"cleaned_{file}")
    if curr_file_df.empty:
        logging.warning(f"{file} is empty. Skipping.")
        cleaned_file_name = os.path.join(snapshots_cleaned_parquet_dir, f"empty_{file}")
    if os.path.exists(cleaned_file_name):
        logging.info(f"Cleaned file for {file} already exists. Skipping.")
        return cleaned_file_name
    all_job_info = extract_all_info(curr_file_df, cleaned_file_name) # list of objects
    try:
        cleaned_silver_df = pd.DataFrame(all_job_info)
        cleaned_silver_df.to_parquet(cleaned_file_name)
    except Exception as e:
        logging.error(f"Error writing cleaned parquet for {file}: {e}")
        cleaned_file_name = os.path.join(snapshots_cleaned_parquet_dir, f"error_{file}")
    return cleaned_file_name
    

def process_all_parquets():
    # We can adjust the number of workers based on system capabilities, we are increasing from
    # normal amount because this is purely file processing and not API calls, 
    # so we can be more aggressive with parallelism. 
    new_worker_amt = worker_amount // 3  # Use 1/3 the threads for file processing to avoid overwhelming the system
    all_files = os.listdir(snapshots_parquet_dir)
    total = len(all_files)
    logging.info(f"Starting silver cleaning for {total} parquet files")
    if not os.path.exists(snapshots_cleaned_parquet_dir):
        os.makedirs(snapshots_cleaned_parquet_dir)
    results = []
    completed = 0
    progress_increment = max(total // 10, 1)  # log progress every 10%
    with ThreadPoolExecutor(max_workers=new_worker_amt) as executor:
        futures = [executor.submit(process_one_parquet, c) for c in all_files if c.endswith('.parquet')]
        for future in as_completed(futures):
            r = future.result()
            if r:
                results.append(r) # gradually builds a list of the completed parquet files
            completed += 1
            if completed % progress_increment == 0 or completed == total:
                logging.info(f"Progress: {completed}/{total} ({completed/total:.1%})")

    logging.info(f"Finished processing {len(results)} valid results")
    return results

########### MAIN FUNCTIONS ############
def main():
    full_program_runtime = time.time()
    all_cleaned_files_list = process_all_parquets()
    
    full_program_elapsed_time = time.time() - full_program_runtime
    file_write_string = f"{time.strftime("%Y-%m-%d")}: Total time taken for entire program (silver cleaning): {full_program_elapsed_time:.2f} seconds ; {full_program_elapsed_time/60:.2f} minutes.\n"
    with open(os.path.join(project_paths.root_dir, "job_pipeline_runtimes.txt"), "a") as output_file:
        output_file.write(file_write_string + "\n")

if __name__ == "__main__":
    main()