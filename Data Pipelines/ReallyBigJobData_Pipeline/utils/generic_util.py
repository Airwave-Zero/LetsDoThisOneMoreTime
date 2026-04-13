# This file is for generic functions that can be re-used across files
from utils import project_paths
import pandas as pd
import requests
import time
import logging
import json
import random
from typing import Dict

def fetch(url, headers=None, stream=False, retries=3, request_delay=1, retry_delay=10):
    # Simple URL fetch request, allow multiple retries with long waits due to 
    # commoncrawl API being slow
    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, headers=headers, stream=stream, timeout=300)
            resp.raise_for_status()
            # if actually got a good response
            print(f"Successfully fetched: {url}")
            time.sleep(request_delay) # Respect API limits generously
            return resp
        except requests.RequestException as e:
            randomized_delay = random.random() * retry_delay * 5
            logging.warning(f"{e} — retry {attempt}/{retries} in {randomized_delay} s")
            time.sleep(randomized_delay)  # Randomize retry delay to avoid thundering herd
            if attempt == retries:
                raise Exception(f"Failed to fetch {url}")
        
def read_json_config(file_path: str) -> Dict:
    '''Helper function to read in JSON config files with error handling and defaults.'''
    try:
        with open(file_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            print(f"Data successfully loaded from: {file_path}")
    except Exception:
        print(f"Config not found or unreadable at {file_path}; using defaults.")
    return data

def parse_dates(df, cols):
    '''Helper function to parse date columns from API into proper datetime format in pandas'''
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], utc=True, errors="coerce")
    return df