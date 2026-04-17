from __future__ import annotations
import gzip
import io
import json
import logging
import re
import time
from typing import List, Dict
import pandas as pd
import os
from warcio.archiveiterator import ArchiveIterator
from bs4 import BeautifulSoup
from utils.generic_util import fetch, determine_regex_pattern, job_sites_with_regex, years, worker_amount
from utils import project_paths
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

snapshot_json_responses_dir = project_paths.snapshot_json_responses_dir
snapshot_visited_dir = project_paths.snapshot_visited_dir
snapshots_parquet_dir = project_paths.snapshots_parquet_dir

################## HELPER FUNCTIONS ##################
def get_candidates_from_json_response(resp_text, proper_regex, candidate_url_set):
    '''
    This helper function takes in the raw JSON text response returned from the Common Crawl index API for a given snapshot + job site pattern combination, and extracts candidate URLs that likely contain job descriptions based on the regex pattern and other metadata filters. 
    We also track candidate URLs in a set to avoid duplicates across different snapshots and speed up runtimes across multiple runs. 
    We finally return a list of candidate records (with metadata) that we will later fetch the WARC files for and the updated candidate URL set and some counts for logging purposes.
    '''

    candidates: List[Dict] = [] # to store good/successful candidates that likely contain job descriptions
    all_resp_lines = resp_text.strip().splitlines()
    progress = 0
    file_length = len(all_resp_lines) # all possible candidates
    progress_increment = max(file_length // 10, 1)  # log progress every 10%
    for line in all_resp_lines:
        if progress % progress_increment == 0:
            logging.info(f"Progress: {progress}/{file_length} lines ({progress/file_length*100:.1f}%)")
        try:
            record = json.loads(line)
            url = record.get("url", "")
            if url in candidate_url_set:
                continue  # skip duplicates across indexes
            if (proper_regex.match(url) and record.get("status") == "200" 
                and record.get("mime") == "text/html" and "/warc/" in record.get("filename", "")):
                candidates.append(record)
                candidate_url_set.add(url)
        except Exception:
            continue
        progress += 1
    return (candidates, candidate_url_set, len(candidates), file_length)

def do_warc_processing(warc_candidates, parquet_path) -> List[Dict]:
    '''This function processes all candidates by fetching the corresponding WARC file, extracting the HTML content, and then applying some basic extraction logic to extract the job description text from the HTML. 
    We then save the results as a parquet file at the end. However, we are incorporating threads to significantly boost performance and process in parallel. . We also log progress as we go along so that we can track how many candidates we have processed and how many valid results we have gotten.'''

    total = len(warc_candidates)
    logging.info(f"Starting WARC processing for {total} candidates")

    results = []
    completed = 0
    progress_increment = max(total // 10, 1)  # log progress every 10%
    with ThreadPoolExecutor(max_workers=worker_amount) as executor:
        futures = [executor.submit(process_single_candidate, c) for c in warc_candidates]
        for future in as_completed(futures):
            r = future.result()
            if r:
                results.append(r)
            completed += 1
            if completed % progress_increment == 0 or completed == total:
                logging.info(f"Progress: {completed}/{total} ({completed/total:.1%})")

    df = pd.DataFrame(results)
    df.to_parquet(parquet_path, index=False)

    logging.info(f"Finished processing {len(results)} valid results")
    return results

def process_single_candidate(warc_candidate):
    ''' This function handles the processing of a single candidate record by fetching the corresponding WARC file, extracting the HTML content, and then applying some basic extraction logic to extract the job description text from the HTML. We return a dictionary with the extracted information for this candidate, or an empty dictionary if there was an error or if the candidate did not meet our criteria. This function is designed to be run in parallel across multiple candidates to boost performance, as opposed to processing all warc_candidates sequentially.'''

    warc_url = f"https://data.commoncrawl.org/{warc_candidate['filename']}"
    headers = {
        "Range": f"bytes={warc_candidate['offset']}-{int(warc_candidate['offset']) + int(warc_candidate['length']) - 1}"
    }
    warc_obj = {}
    try:
        warc_resp = fetch(warc_url, headers=headers, stream=False, show_logs=False)
        if warc_resp.status_code == 403:
            logging.warning(f"Received 403 Forbidden for WARC URL: {warc_url}, skipping.")
            return warc_obj
        content = warc_resp.content
        if not content:
            logging.warning(f"No content in WARC response for {warc_candidate.get('url')}, skipping.")
            return warc_obj
        if not content.startswith(b"\x1f\x8b"):
            logging.warning(f"WARC response for {warc_candidate.get('url')} does not appear to be gzip-compressed, skipping.")
            return warc_obj
        
        buffered = io.BytesIO(content)
        decompressed = gzip.GzipFile(fileobj=buffered)
        for record in ArchiveIterator(decompressed):
            html_bytes = record.content_stream().read()
            try:
                html = html_bytes.decode("utf-8", errors="ignore")
            except Exception:
                html = html_bytes.decode("latin-1", errors="ignore")
            soup = BeautifulSoup(html, "lxml")
            # 1. try structured data first
            job_text = ""
            ld_json = soup.find("script", type="application/ld+json")
            if ld_json and "JobPosting" in ld_json.text:
                job_text = ld_json.text  # parse JSON later if needed
            # 2. fallback DOM extraction
            if not job_text:
                blocks = soup.find_all(["div", "section", "article"])
                text_candidates = [
                    b.get_text(" ", strip=True)
                    for b in blocks
                ]
                job_text = max(text_candidates, key=len, default="")
            warc_obj = {
                "url": warc_candidate.get("url"),
                "html": html,          # raw snapshot
                "job_text": job_text,  # normalized extraction
                "timestamp": warc_candidate.get("timestamp"),
            }
    except Exception:
        logging.exception(f"Failed WARC processing: {warc_candidate.get('url')}")
    return warc_obj

######################## MAIN FUNCTIONS ##################
def get_snapshot_urls_to_visit() -> List[str]:
    '''This function visits the json file that lists all the Common Crawl snapshots and their metadata, 
    and returns a list of URLs to visit for each snapshot.
    '''
    snapshots_list = fetch("https://index.commoncrawl.org/collinfo.json").json()
    index_urls: List[str] = []
    for year in years:
        for snap in snapshots_list:
            if year in snap.get("id", ""):
                cdx_api = snap.get("cdx-api")
                if not cdx_api:
                    continue
                for job_pattern, _ in job_sites_with_regex:
                    index_urls.append(f"{cdx_api}?url={job_pattern}*&output=json")
    return index_urls

def visit_urls_and_process_immediately(index_urls: List[str]):
    '''This function looks through every combination of crawl snapshot date + the job site patterns; we then either fetch the snapshot from the Common Crawl index API or read it from a local file if we have already fetched it in a previous run. 
    We then extract candidates from the snapshot (or file) and keep track of them in a list, which we return at the end. We also keep track of candidate URLs in a set to avoid duplicates across different snapshots and speed up runtimes across multiple runs.
    Lastly we also immediately process the candidates for each snapshot (instead of waiting until the end to process all candidates across all snapshots) to save memory and also so that we can see results incrementally and not lose everything if something fails in the middle of processing all snapshots.
    '''
    total_candidates: List[Dict] = []
    total_candidates_count = 0
    ''' to store the extracted WARC objects after processing, this is currently unused due to memory constraints but we can always return it at the end if we want to see all results in memory instead of just writing to parquet files, which is more efficient for memory but less convenient for seeing results immediately. '''
    all_warc_objects = [] 
    candidate_url_set = set()  # to track duplicates across indexes
    datetime_start = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for idx, index_url in enumerate(index_urls, start=1):
        curr_start_time = time.time()
        safe_name = re.sub(r"[^a-zA-Z0-9._-]", "_", index_url)
        snapshot_txt_name = f"{safe_name}.txt"
        snapshots_done_txt_name = f"{safe_name}_done.txt"
        snapshots_parquet_name = f"{safe_name}.parquet"
        full_snapshot_response_txt_path = os.path.join(snapshot_json_responses_dir, snapshot_txt_name)
        full_snapshots_visted_txt_path = os.path.join(snapshot_visited_dir, snapshots_done_txt_name)
        full_snapshots_parquet_path = os.path.join(snapshots_parquet_dir, snapshots_parquet_name)
        proper_regex = determine_regex_pattern(index_url, job_sites_with_regex)
        resp_text = ''
        temp_candidates = []
        if not proper_regex:
            logging.warning(f"No regex pattern found for index URL: {index_url}")
            continue
        # First, check if we already have the snapshot response saved as a text file locally. 
        # If so, read from the file instead; otherwise look it up and save it
        # This boosts efficiency and reliability in case of failed fetches across multiple runs, at the cost of memory
        if os.path.exists(full_snapshot_response_txt_path):
            logging.info(f"Snapshot text file already exists for index {idx}/{len(index_urls)}: {index_url}, skipping fetch.\nTrying to create parquet from file instead")
            if not os.path.exists(full_snapshots_visted_txt_path):
                logging.info(f"Finished snapshot file does not exist for index {idx}/{len(index_urls)}: {index_url}, creating from snapshot text file.")
                # read file instead
                with open(full_snapshot_response_txt_path, "r", encoding="utf-8") as log_file:
                    resp_text = log_file.read()
        else:
            logging.info(f"Snapshot file does not exist for index {idx}/{len(index_urls)}: {index_url}, fetching...")
            try:
                resp = fetch(index_url)
                # write json response to log for debugging
                resp_text = resp.text
                with open(full_snapshot_response_txt_path, "a") as log_file:
                    log_file.write(resp_text + "\n")
            except Exception:
                logging.exception(f"Failed to FETCH: {index_url}")
                continue

        # Second, after getting the response (regardless of from .txt or from fetch), extract candidates and also write to visited log with counts and time taken, so that we have a record of what we have done across runs and can debug if needed. 
        (temp_candidates, temp_candidate_urls, added_candidates, json_total_candidates) = get_candidates_from_json_response(resp_text, proper_regex, candidate_url_set)
        # not technically necessary to keep in memory, but helps with debugging if need be ; its also quite expensive to store it all 
        #total_candidates.extend(temp_candidates) 
        total_candidates_count += len(temp_candidates)
        candidate_url_set.update(temp_candidate_urls)
        curr_elapsed = time.time() - curr_start_time # how much time it took to fetch and extract candidates for this snapshot

        # Third, write to visited log if we haven't already (to avoid duplicates across runs), with counts and time taken for this snapshot, so that we have a record of what we have done across runs and can debug if needed.
        if not os.path.exists(full_snapshots_visted_txt_path):
            with open(full_snapshots_visted_txt_path, "a") as log_file:
                log_file.write(f"[{datetime_start}] Added {added_candidates} candidates (out of {json_total_candidates} possible) for index {idx}/{len(index_urls)}: {index_url}\n; time taken for this index: {curr_elapsed:.2f} seconds\n; total candidates so far: {total_candidates_count}\n\n")

        # In theory, we could cut the function here (or modify it so that visit_urls only returns candidates for one snapshot at a time) and then immediately process the WARCs for this snapshot before moving on to the next snapshot, which would save a lot of memory and also allow us to see results incrementally and not lose everything if something fails in the middle of processing all snapshots. 
        # However, this would make the code more complex and less modular, so for now we will keep it as is and just return the total candidates at the end, if we wanted to. We can always modify it later if we find that memory is an issue or if we want to see results incrementally.
        #return temp_candidates

        # Lastly, process candidates for this snapshot immediately after extracting them, to save time and memory and also so that we can see results incrementally and not lose everything if something fails in the middle of processing all snapshots
        if not os.path.exists(full_snapshots_parquet_path):
            snapshot_processing_start_time = time.time()
            do_warc_processing(temp_candidates, full_snapshots_parquet_path)
            # technically we can store the processed objects as we go (and return a full list when done) but this is quite memory intensive and we can always read the parquet files later if we want to see results, so for now we will just write to parquet and not keep in memory, to save memory and also to keep code simpler and more modular.
            # curr_index_warc_objects_list = do_warc_processing(temp_candidates, full_snapshots_parquet_path)
            # all_warc_objects.extend(curr_index_warc_objects_list)
            snapshot_processing_elapsed = time.time() - snapshot_processing_start_time
            with open(full_snapshots_visted_txt_path, "a") as log_file:
                log_file.write(f"Finished WARC processing for index {idx}/{len(index_urls)}: {index_url} in {snapshot_processing_elapsed:.2f} seconds\n")
    print(f"Total candidates found across all indexes: {total_candidates_count}")
    # return all_warc_objects

def main():

    full_program_runtime = time.time()

    all_snapshot_urls = get_snapshot_urls_to_visit()
    visit_urls_and_process_immediately(all_snapshot_urls) # this function technically returns nothing, but could if we wanted to

    full_program_elapsed_time = time.time() - full_program_runtime
    file_write_string = f"{time.strftime("%Y-%m-%d")}: Total time taken for entire program (bronze extraction): {full_program_elapsed_time:.2f} seconds ; {full_program_elapsed_time/60:.2f} minutes.\n"
    with open(os.path.join(project_paths.root_dir, "job_pipeline_runtimes.txt"), "a") as output_file:
        output_file.write(file_write_string + "\n")

if __name__ == "__main__":
    main()