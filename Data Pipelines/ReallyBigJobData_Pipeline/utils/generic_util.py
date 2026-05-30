# This file is for generic functions that can be re-used across files
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
    'lead', 'senior', 'junior', 'principal', 'director', 'intern'
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
        "benefits", "perks", "we offer", "compensation", "salary",
        "health insurance", "401k", "pto", "paid time off", "bonus", 
        "equity", "stock options", "retirement", "wellness", "parental leave",
        "commuter benefit", "professional development", "tuition reimbursement"
    ],
    "overview": [
        "about the role", "this role", "you will be part of",
        "join our team", "position overview", "role overview",
        "what you'll do", "what you will do", "about this position"
    ],    
    "nice_to_have_skills": [
        "nice to have", "bonus", "preferred", "plus", "good to have",
        "if you also have", "additional", "helpful", "would be great"
    ],    
    "requirements": [
        "requirements", "must", "required", "need", "minimum", "experience with",
        "proficient in", "strong knowledge", "familiar with", "understanding of",
        "ability to", "qualifications", "we need", "we're looking for",
        "essential", "prerequisite"
    ],
    "responsibilities": [
        "responsibilities", "you will", "you'll", "responsible for", "build", 
        "develop", "design", "implement", "maintain", "work with", "own", "lead",
        "collaborate", "manage", "create", "oversee", "drive", "execute"
    ],
}

YOE_REGEX = re.compile(r'(\d+)\+?\s*(years|yrs).*?(experience)', re.I)

DEGREE_REGEX = re.compile(r"(bachelor|master|phd|bs|ms)", re.I)

SALARY_REGEX = re.compile(r"\$[\d,]+(?:\s*-\s*\$[\d,]+)?")


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

NOISE_WORDS = ["apply", "resume", "email", "phone"]


SCORING_RULES = {
    # positive signals
    "responsibilities": 2,
    "requirements": 2,
    "qualifications": 2,
    "what you'll do": 2,
    "what you will do": 2,
    "who you are": 2,
    "additional skills": 1,
    "benefits": 1,
}
def clean_text(text):
    return re.sub(r"\s+", " ", text).strip()

def classify_section(text):
    """Classify a line into a section category with improved matching."""
    t = text.lower()
    best_match = None
    best_score = 0
    
    for section, patterns in SECTION_PATTERNS.items():
        for p in patterns:
            if p in t:
                # Boost score for exact phrase matches at start
                if t.startswith(p):
                    score = 3
                else:
                    score = 1
                if score > best_score:
                    best_score = score
                    best_match = section
    
    return best_match

def split_lines(text):
    # Split aggressively but preserve meaningful chunks
    return [clean_text(x) for x in re.split(r"\n+|\r+|\.\s+", text) if clean_text(x)]

def compute_relevance_score(text):
    text_lower = text.lower()
    score = 0
    for key, val in SCORING_RULES.items():
        if key in text_lower:
            score += val
    return score

def compute_confidence(result):
    """Calculate confidence score for extraction quality."""
    score = 0

    if result.get("title"):
        score += 1
    if result.get("company"):
        score += 1
    if result.get("location"):
        score += 1

    # Check responsibilities
    resp = result.get("responsibilities", "")
    resp_len = len(resp.split()) if isinstance(resp, str) else sum(len(item.split()) for item in (resp or []))
    if resp_len > 20:
        score += 2

    # Check requirements  
    req = result.get("requirements", "")
    req_len = len(req.split()) if isinstance(req, str) else sum(len(item.split()) for item in (req or []))
    if req_len > 20:
        score += 2
        
    if result.get("benefits"):
        score += 1

    return score

def classify_line_with_confidence(line):
    t = line.lower()
    scores = {k: 0 for k in SECTION_PATTERNS}

    for category, patterns in SECTION_PATTERNS.items():
        for p in patterns:
            if p in t:
                scores[category] += 1

    # heuristic boosts
    if t.startswith(("•", "-", "*")):
        if any(w in t for w in ["build", "develop", "design", "implement", "create"]):
            scores["responsibilities"] += 2
        if any(w in t for w in ["experience", "years", "degree", "knowledge"]):
            scores["requirements"] += 2
        if any(w in t for w in ["nice", "preferred", "bonus", "helpful"]):
            scores["nice_to_have_skills"] += 2

    best = max(scores, key=scores.get)
    total = sum(scores.values())

    confidence = scores[best] / total if total > 0 else 0

    return best if confidence > 0 else "other", confidence


def classify_multi_label(line):
    t = line.lower()
    matched = []

    for category, patterns in SECTION_PATTERNS.items():
        if any(p in t for p in patterns):
            matched.append(category)

    return matched if matched else ["other"]

def extract_job_type(text):
    """Extract job type (full-time, part-time, etc.) from text."""
    if not text:
        return None
    text_lower = text.lower()
    for job_type, pattern in JOB_TYPE_PATTERNS.items():
        if re.search(pattern, text_lower):
            return job_type
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