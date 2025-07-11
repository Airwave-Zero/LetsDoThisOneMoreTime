from warcio.archiveiterator import ArchiveIterator
from bs4 import BeautifulSoup
from kafka import KafkaProducer
from datetime import datetime
from functools import wraps
import json
import argparse
import logging
import re
import time
import random
import requests
import gzip
import io


parser = argparse.ArgumentParser()
parser.add_argument("--year", required=False, default="2025",  help="Please enter the year to extract from (2009-2025)")
args = parser.parse_args()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=f'commoncrawl_scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
)

# reference link for later
# https://index.commoncrawl.org/CC-MAIN-2025-21-index?url=*.greenhouse.io/**&output=json 
# https://index.commoncrawl.org/CC-MAIN-2025-21-index?url=*.bamboohr.com/**&output=json

def retry_with_backoff(retries=3, backoff_in_seconds=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            x = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if x == retries:
                        logging.error(f"Failed after {retries} retries. Error: {str(e)}")
                        raise
                    wait = (backoff_in_seconds * 2 ** x + random.uniform(0, 1))
                    logging.warning(f"Attempt {x + 1} failed. Retrying in {wait:.2f} seconds. Error: {str(e)}")
                    time.sleep(wait)
                    x += 1
        return wrapper
    return decorator

class RateLimiter:
    def __init__(self, requests_per_second=1):
        self.delay = 1.0 / requests_per_second
        self.last_request = 0

    def wait(self):
        now = time.time()
        elapsed = now - self.last_request
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request = time.time()
        
# Create rate limiter instance
rate_limiter = RateLimiter(requests_per_second=0.5)  # 2 seconds between requests

job_sites_with_patterns = [
    ("*.greenhouse.io/*", re.compile(r"^https://boards\.greenhouse\.io/[^/]+/jobs/[^/?#]+")),
    ("*.jobs.lever.co/*", re.compile(r"^https://(?:[^/]+\.)?jobs\.lever\.co/[^?#]*")),
    ("*.workable.com/*", re.compile(r"^https://apply\.workable\.com/[^/]+/j/[^/?#]+")),
    ("*.bamboohr.com/*", re.compile(r"^https://[^/]+\.bamboohr\.com/careers/[^/?#]*"))]

def get_all_url(years):
    '''Takes in a list of years, or arguments provided by the script, and generates the appropriate
    URLs from each crawl per year per job site format
    e.g. searching for all greenhouse within 2025 may crawl, then 2025 april crawl, etc...
    returns a list of urls'''
    all_snapshots_url = "https://index.commoncrawl.org/collinfo.json"
    snapshots = requests.get(all_snapshots_url).json()
    snapshots_by_year = {year: [snap for snap in snapshots if year in snap["id"]] for year in years} # returns a dictionary where each year key gives you all the snapshots from tha tyear
    allURL = []
    # triple for loop is bad but because we're limiting it to a small sample size, it's okay
    for year in years:
        for snapshot in snapshots_by_year[year]:
            for jobSource in job_sites_with_patterns:
                cdx_api = snapshot["cdx-api"]
                baseURL = cdx_api + "?url=" + jobSource[0] + "*&output=json"
                allURL.append(baseURL)        
    #print(allURL)
    return allURL

@retry_with_backoff(retries=3)
def fetch_with_retry(url, headers=None, stream=False):
    print("fetching url..." + url)
    rate_limiter.wait()  # Rate limit all requests
    response = requests.get(url, headers=headers, stream=stream)
    response.raise_for_status()
    return response

def get_relevant_objects(json_response, url):
    '''Takes in a json response from extractHTML, and the json URL link, and 
    returns all the objects that have links with the specific format.
    i.e. go through all the greenhouse links and only return the actual job postings in the greenhouse domain
    This is done to reduce the number of objects/files dealt with, and thus reduce api calls made to the server,
    which hopefully reduces rate limiting and increases performance
    
    example: 
    jron_response: the actual json objects returned from url
    url: https://index.commoncrawl.org/CC-MAIN-2025-21-index?url=*.greenhouse.io/**&output=json 
    parses it for "greenhouse.io" and grabs the appropriate regex, then looks for urls that actually fit that regex
    '''
    print(f"Getting actual job postings from: {url}")
    trimmed_list = []


    # parse the URL and extract between the query parameters
    get_job_base = url.split('*')[1]
    proper_regex = None
    for job_sites in job_sites_with_patterns:
        if get_job_base in job_sites[0]:
            proper_regex = job_sites[1]

    for line in json_response.text.strip().split('\n'):
        try:
            record = json.loads(line)
            json_url = record.get("url", "")
            ''' here, we only want the 200 status codes; a lot of the pages end up being 301/302, which are redirects
                the code performance suffers immensely if we follow the rabbit hole down, 
                so on initial pass let's only look at immediately valid info 
                TODO: actually use recursion and visit every redirect '''
            if proper_regex.match(json_url) and record.get("status") == "200":
                trimmed_list.append(record)
        except json.JSONDecodeError as je:
            logging.warning(f"Failed to parse JSON line: {str(je)}")
        except Exception as e:
            logging.error(f"Error processing record: {str(e)}")
    print(f"Retrieved {len(trimmed_list)} links to go through")
    return trimmed_list

def extractHTML(url_list):
    total_urls = len(url_list)
    '''
    TODO
    instead of getting every link and then extracting from there, parse all the jobs
    that follow some format like https://job-boards.greenhouse.io/meritamerica/jobs/5566396004
    and then pull the gz file using regex, should reduce number of calls
    '''
    all_job_data = []
    for idx, url in enumerate(url_list, 1):
        logging.info(f"Processing URL {idx}/{total_urls}: {url}")
        try:
            # url should be the .json webpage, do not use for regex
            response = fetch_with_retry(url) # response is the returned page from https://index.commoncrawl.org/CC-MAIN-2025-21-index?url=*.greenhouse.io/**&output=json 
            desired_objects = get_relevant_objects(response, url) 
            
            # after this point, desired_objects should be a list of actual job posting links that had status code 200
            for json_obj in desired_objects:
                if json_obj.get("mime") == "text/html":
                    warc_url = f"https://data.commoncrawl.org/{json_obj['filename']}"
                    print(f"Getting warc url: {warc_url}")
                    logging.info(f"Fetching WARC file: {warc_url}")
                    headers = {
                        'Range': f"bytes={json_obj['offset']}-{int(json_obj['offset']) + int(json_obj['length']) - 1}"
                    }
                    warc_response = fetch_with_retry(warc_url, headers=headers, stream=True)
                    try:
                        # Decompress the GZIP content
                        decompressed = gzip.GzipFile(fileobj=warc_response.raw)
                        buffered = io.BufferedReader(decompressed)
                        # Iterate over the decompressed WARC content
                        for warc_record in ArchiveIterator(buffered):
                            if warc_record.rec_type == 'response':
                                html = warc_record.content_stream().read()
                                soup = BeautifulSoup(html, 'html.parser')
                                text = soup.get_text()
                                ''' Despite the heavy payload size, we are okay with passing along >all< the HTML for it to
                                be cleaned downstream later with Kafka/Spark. If we do everything inline here, it defeats
                                the purpose of the pipeline aspect. Performance slows down a bit but it's ultimately more scalable'''
                                if any(keyword in text.lower() for keyword in ['apply', 'description', 'experience']):
                                    job_data = {
                                        'url': json_obj.get("url"),
                                        'html': html.decode('utf-8', errors='ignore'),
                                        'timestamp': json_obj.get("timestamp")
                                    }
                                    #all_job_data.append(job_data)
                                    yield job_data
                                    logging.info(f"Successfully extracted job data from: {json_obj['url']}")
                                    print(f"Found job listing at: {json_obj['url']}")
                    except Exception as e:
                        logging.error(f"Error processing WARC record: {str(e)}")
        except requests.RequestException as req_err:
            logging.error(f"Request error for URL {url}: {str(req_err)}")
        except Exception as e:
            logging.error(f"General error for URL {url}: {str(e)}")
    #logging.info(f"Extraction completed. Total job listings found: {len(allJobData)}")
    #return all_job_data


if __name__ == "__main__":
    # modify this to accept docker compose parameter, we pass in the year and it'll do the rest to hopefully the rest
    # worst case we "dumb it down" to only read crawl by crawl instead of multiple mass crawls and then just do more containers
    #all_url = get_all_url(["2025"])
    producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))

    allURL = get_all_url(args)
    for each_job in extractHTML(all_url):
        if job_data:
            try:
                producer.send("raw_jobs", job)
                print(f"Sent: {job['url']}")
            except Exception as e:
                logging.error(f"Failed to send job: {str(e)}")
    producer.flush()        

