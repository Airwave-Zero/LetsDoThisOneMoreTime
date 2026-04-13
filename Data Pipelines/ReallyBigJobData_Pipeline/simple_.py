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
from utils.generic_util import fetch, read_json_config
from utils import project_paths

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
years = ["2026", "2025"] # Format: ["year1", "year2", ... "yearN"], keep as 2026 for now because of size/scale
job_sites_with_regex = [
    ("*.greenhouse.io/*", re.compile(r"^https://boards.greenhouse\.io/[^/]+/jobs/[^/?#]+")),
    ("*.jobs.lever.co/*", re.compile(r"^https://(?:[^/]+\.)?jobs\.lever\.co/[^?#]*")), # some have robots.txt
    #("*.workable.com/*", re.compile(r"^https://apply\.workable\.com/[^/]+/j/[^/?#]+")),
    #("*.bamboohr.com/*", re.compile(r"^https://[^/]+\.bamboohr\.com/careers/[^/?#]*")),
    ("*.jobs.ashbyhq.com/*", re.compile(r"^https://jobs\.ashbyhq\.com/[^/]+/[^/?#]+")),
    ]

JOB_KEYWORDS = ("job description",)
"""
While we could look for extra terms for more coverage,
we are mainly concerned about something that is almost 99%
likely to be a job description page.
"""
JOB_KEYWORDS += (
    " responsibilities",
    " qualifications",
    " requirements",
    " skills",
    " experience",
    " apply now",
)

def get_snapshot_urls_to_visit() -> List[str]:
    # ---------------- STEP 1: GET INDEX URLS ----------------
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
    
def determine_regex_pattern(index_url: str) -> re.Pattern | None:
    base = index_url.split("*")[1] if "*" in index_url else ""
    for job_pattern, pattern in job_sites_with_regex:
        if base in job_pattern:
            return pattern
    return None

snapshots_dir = os.path.join(project_paths.root_dir, "snapshots2_private")

def visit_urls(index_urls):
    candidates: List[Dict] = []
    candidate_url_set = set()  # to track duplicates across indexes
    for idx, index_url in enumerate(index_urls, start=1):
        safe_name = re.sub(r"[^a-zA-Z0-9._-]", "_", index_url)
        new_filename = f"{safe_name}.txt"
        full_filenamepath = os.path.join(snapshots_dir, new_filename)
        proper_regex = determine_regex_pattern(index_url)
        if not proper_regex:
            logging.warning(f"No regex pattern found for index URL: {index_url}")
            continue
        if os.path.exists(full_filenamepath):
            logging.info(f"Snapshot already exists for index {idx}/{len(index_urls)}: {index_url}, skipping fetch.")
            # read file instead
            with open(full_filenamepath, "r", encoding="utf-8") as log_file:
                resp = log_file.read()
            file_lines = resp.strip().splitlines()
            progress = 0
            max = len(file_lines)
            progress_amt = max//20
            for line in file_lines:
                if progress % progress_amt == 0:
                    logging.info(f"Processing snapshot {idx}/{len(index_urls)}: {index_url}")
                try:
                    record = json.loads(line)
                    url = record.get("url", "")
                    if url in candidate_url_set:
                        continue  # skip duplicates across indexes
                    if (proper_regex.match(url) and record.get("status") == "200" 
                        and record.get("mime") == "text/html" and "/warc/" in record.get("filename", "")):
                        candidates.append(record)
                        #print(f"Successfully loaded candidate from snapshot: {url}")
                        candidate_url_set.add(url)
                except Exception:
                    continue
                progress += 1
            continue
        else:
            logging.info(f"Processing index {idx}/{len(index_urls)}: {index_url}")
            try:
                resp = fetch(index_url)
                # write json response to log for debugging
                with open(os.path.join(snapshots_dir, new_filename), "a") as log_file:
                    log_file.write(resp.text + "\n")
                # ---------------- STEP 2: FILTER CDX ----------------
                for line in resp.text.strip().splitlines():
                    try:
                        record = json.loads(line)
                        url = record.get("url", "")
                        if (proper_regex.match(url) and record.get("status") == "200" 
                            and record.get("mime") == "text/html" and "/warc/" in record.get("filename", "")):
                            candidates.append(record)
                    except Exception:
                        continue
            except Exception:
                logging.exception(f"Failed index processing: {index_url}")
    print(f"Total candidates found across all indexes: {len(candidates)}")
    return candidates 

def do_warc_processing(candidates):
    # logging.info(f"Found {len(candidates)} candidates")
    all_objects = []
    JOB_PATTERN = re.compile(r"(job description|responsibilities|qualifications|salary|benefits)",re.I)
    # ---------------- STEP 3: FETCH WARC + EXTRACT ----------------
    for cand in candidates:
        #if cand.get("mime") != "text/html" or cand.get("status") != "200" or "/warc/" not in cand.get("filename", ""):
        #    continue
        start_time = time.time()
        warc_url = f"https://data.commoncrawl.org/{cand['filename']}"
        headers = {
            "Range": f"bytes={cand['offset']}-{int(cand['offset']) + int(cand['length']) - 1}"
        }
        try:
            warc_resp = fetch(warc_url, headers=headers, stream=True)
            decompressed = gzip.GzipFile(fileobj=warc_resp.raw)
            buffered = io.BufferedReader(decompressed)

            for record in ArchiveIterator(buffered):
                if record.rec_type != "response":
                    continue

                html_bytes = record.content_stream().read()

                try:
                    html = html_bytes.decode("utf-8", errors="ignore")
                except Exception:
                    html = html_bytes.decode("latin-1", errors="ignore")
                    
                #if not JOB_PATTERN.search(html):
                #    return
                
                soup = BeautifulSoup(html, "lxml")
                # 1. try structured data first
                job_text = ""

                ld_json = soup.find("script", type="application/ld+json")
                if ld_json and "JobPosting" in ld_json.text:
                    job_text = ld_json.text  # parse JSON later if needed
                # 2. fallback DOM extraction
                if not job_text:
                    blocks = soup.find_all(["div", "section", "article"])
                    candidates = [
                        b.get_text(" ", strip=True)
                        for b in blocks
                    ]
                    job_text = max(candidates, key=len, default="")
                temp_obj = {
                    "url": cand.get("url"),
                    "html": html,          # raw snapshot
                    "job_text": job_text,  # normalized extraction
                    "timestamp": cand.get("timestamp"),
                }
                all_objects.append(temp_obj)
            '''
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(" ").lower()

            if any(k in text for k in JOB_KEYWORDS):
                found += 1
                logging.info(f"FOUND job: {cand.get('url')}")

                all_objects.append({
                    "url": cand.get("url"),
                    "html": html,
                    "timestamp": cand.get("timestamp"),
                })

                if found >= 5:  # safety limit
                    logging.info("Reached job processing limit of 5, stopping early")
                    elapsed = time.time() - start_time
                    logging.info(f"Elapsed time: {elapsed:.2f}s")
                    return all_objects
                '''
        except Exception:
            logging.exception(f"Failed WARC processing: {cand.get('url')}")
        elapsed = time.time() - start_time
        #print(f"Full method finished in {elapsed:.2f}s | Processed {len(all_objects)} job pages so far")
    print(f"Total job pages extracted: {len(all_objects)}")
    test = pd.DataFrame(all_objects)
    test.to_parquet(os.path.join(project_paths.root_dir, f"{time.time()}_extracted_jobs.parquet"))
    return all_objects

def main():
    super_start_time = time.time()
    #results = run_scraper()
    all_snapshot_urls = get_snapshot_urls_to_visit()
    candidates = visit_urls(all_snapshot_urls)
    results = do_warc_processing(candidates)
    total_elapsed_time = time.time() - super_start_time
    file_write_string = f"{time.strftime("%Y-%m-%d")}: Total time taken: {total_elapsed_time:.2f} seconds ; {total_elapsed_time/60:.2f} minutes."
    with open(os.path.join(project_paths.root_dir, "job_pipeline_runtimes.txt"), "a") as output_file:
        output_file.write(file_write_string + "\n")
    #print(file_write_string)
    #df = pd.DataFrame(results)
    #print(df.head())
    #print(df.columns)

    #df.to_parquet("extracted_jobs.parquet")
# ---------------- RUN ----------------
if __name__ == "__main__":
    main()