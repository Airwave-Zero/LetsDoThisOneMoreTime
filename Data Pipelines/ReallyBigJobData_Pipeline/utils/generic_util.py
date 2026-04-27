# This file is for generic functions that can be re-used across files
from utils import project_paths
import pandas as pd
import requests
import time
import logging
import json
import random
from threading import Semaphore
from typing import Dict
import re

worker_amount = 6  # Number of threads to use for concurrent requests, adjust based on API limits and system capabilities
semaphore_amount = 6

rate_limit_semaphore = Semaphore(semaphore_amount)  # Allow only 1 request at a time to respect API limits

years = ["2024"] # Format: ["year1", "year2", ... "yearN"]
job_sites_with_regex = [
    ("*.jobs.ashbyhq.com/*", re.compile(r"^https://jobs\.ashbyhq\.com/[^/]+/[^/?#]+")),    
    ("*.greenhouse.io/*", re.compile(r"^https://boards.greenhouse\.io/[^/]+/jobs/[^/?#]+")),
    ("*.jobs.lever.co/*", re.compile(r"^https://(?:[^/]+\.)?jobs\.lever\.co/[^?#]*")), # some have robots.txt
    ]

TECHNICAL_JOB_TITLE_KEYWORDS = {
    'engineer', 'developer', 'scientist', 'analyst', 'manager',
    'architect', 'designer', 'consultant', 'specialist', 'coordinator',
    'lead', 'senior', 'junior', 'principal', 'director'
}

# should break this down by domain / skillset e.g. backend, frontend, etc.
SOFTWARE_KEYWORDS = {
    'python', 'java', 'javascript', 'typescript', 'sql', 'r',
    'golang', 'rust', 'c++', 'c#', 'php', 'ruby', 'swift',
    'react', 'angular', 'vue', 'node', 'django', 'flask',
    'aws', 'gcp', 'azure', 'kubernetes', 'docker',
    'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
    'git', 'ci/cd', 'jenkins', 'gitlab', 'github',
    'machine learning', 'deep learning', 'nlp', 'computer vision',
    'data analysis', 'statistics', 'etl', 'spark', 'hadoop',
    'agile', 'scrum', 'jira', 'linux', 'windows', 'macos'
}

SECTION_PATTERNS = {
    "benefits": [
        "benefits", "what we offer", "perks"
    ],
    "overview": [
        "about the role", "role overview", "about this role"
    ],
    "preferred_qualifications": [
        "preferred", "nice to have", "bonus", "preferred qualifications"
    ],
    "requirements": [
        "requirements", "who you are", "what we're looking for", "what you need to succeed",
        "minimum requirements", "qualifications", "skills required", "required"
    ],
    "responsibilities": [
        "responsibilities", "what you will do", "what you'll do"
    ]
}

SENIORITY_LEVEL_PATTERNS = {
    'entry-level': r'entry[- ]level|junior|intern|graduate',
    'mid-level': r'mid[- ]level|mid\s*career',
    'senior': r'senior|lead|principal|manager',
    'executive': r'director|vp|chief|cto|ceo|cfo',    
}

JOB_TYPE_PATTERNS = {
    'full-time': r'full[- ]time',
    'part-time': r'part[- ]time',
    'contract': r'contract(?:or)?|contracted',
    'temporary': r'temporary|temp\b',
    'internship': r'internship|intern',
}
# Exclude common words, used to know what to skip over when counting important keywords in job descriptions
JOB_COMMON_WORDS = {
    'the', 'that', 'what', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'is', 'are', 'be', 'been', 'being', 'will', 'would',
    'could', 'should', 'may', 'might', 'can', 'must', 'you', 'we', 'i',
    'job', 'position', 'role', 'we', 'our', 'your', 'company', 'team'
}

def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()
def classify_section(text):
    t = text.lower()
    for section, patterns in SECTION_PATTERNS.items():
        for p in patterns:
            if p in t:
                return section
    return None


def fetch(url, headers=None, stream=False, retries=3, request_delay=1, retry_delay=10, show_logs=True):
    # Simple URL fetch request, allow multiple retries with long waits due to 
    # commoncrawl API being slow
    for attempt in range(1, retries + 1):
        try:
            with rate_limit_semaphore:  # Ensure
                resp = requests.get(url, headers=headers, stream=stream, timeout=300)
            if resp.status_code == 403:
                if show_logs:
                    logging.warning(f"403 Forbidden (not retrying): {url}")
                # dont need to retry
                return resp  
            resp.raise_for_status()
            # if actually got a good response
            if show_logs:
                print(f"Successfully fetched: {url}")
            time.sleep(request_delay + random.random()) # Respect API limits generously
            return resp
        except requests.RequestException as e:
            randomized_delay = random.random() * retry_delay + retry_delay  # Randomize between retry_delay and 2*retry_delay
            logging.warning(f"{e} — retry {attempt}/{retries} in {randomized_delay} s")
            time.sleep(randomized_delay)  # Randomize retry delay to avoid thundering herd
            if attempt == retries:
                raise Exception(f"Failed to fetch {url}")
        
def determine_regex_pattern(index_url: str, job_sites_with_regex: list) -> re.Pattern | None:
    base = index_url.split("*")[1] if "*" in index_url else ""
    for job_pattern, pattern in job_sites_with_regex:
        if base in job_pattern:
            return pattern
    return None

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