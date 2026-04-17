# This file is to take the raw bronze parquet website data and clean it into
# dims and fact tables if necessary
from __future__ import annotations
import io
import json
import logging
import re
import time
from typing import List, Dict
import pandas as pd
import os
from utils.generic_util import fetch, determine_regex_pattern, job_sites_with_regex, years, worker_amount
from utils import project_paths
from urllib.parse import urlparse

from concurrent.futures import ThreadPoolExecutor, as_completed

snapshots_parquet_dir = project_paths.snapshots_parquet_dir
snapshots_cleaned_parquet_dir = project_paths.cleaned_parquet_dir

########### HELPER FUNCTIONS ############
def extract_job_id(url):
    if not url: 
        return None
    parts = url.strip('/').split('/')
    if len(parts) >= 2:    
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

def extract_all_info(df: pd.DataFrame) -> List[Dict]:
    """Reads in a dataframe, lightly extracts necessary information
    and returns a list of dictionaries to be converted later."""
    job_info_list = []
    for _, row in df.iterrows():
        url = row.get('url', '')

        job_id = extract_job_id(url)
        company = extract_company(url)
        job_source = extract_job_source(url)
        description = row.get('job_text')
        timestamp = row.get('timestamp')
        
        job_info = {
            'job_id': job_id,
            'company_name': company,
            'job_source': job_source,
            'description': description,
            'timestamp': timestamp,
            'url': url,
        }
        job_info_list.append(job_info)
    
    return job_info_list

def process_all_parquets():
    clean_parquet_file_list = []
    for file in os.listdir(snapshots_parquet_dir):
        if file.endswith(".parquet"):
            cleaned_file_name = os.path.join(snapshots_cleaned_parquet_dir, f"cleaned_{file}.parquet")
            print(f"Processing {file}...")
            curr_file_df = pd.read_parquet(os.path.join(snapshots_parquet_dir, file))
            # get all job info
            all_job_info = extract_all_info(curr_file_df) # list of objects
            try:
                cleaned_silver_df = pd.DataFrame(all_job_info)
                cleaned_silver_df.to_parquet(cleaned_file_name)
                clean_parquet_file_list.append(cleaned_file_name)
            except Exception as e:
                logging.error(f"Error writing cleaned parquet for {file}: {e}")
    return clean_parquet_file_list

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