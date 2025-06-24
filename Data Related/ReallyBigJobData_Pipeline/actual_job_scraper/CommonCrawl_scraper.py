from warcio.archiveiterator import ArchiveIterator
import requests
import gzip
from bs4 import BeautifulSoup
from kafka import KafkaProducer
import json
import argparse
import logging
import re

parser = argparse.ArgumentParser()
parser.add_argument("--year", required=True, help="Please enter the year to extract from (2009-2025)")
args = parser.parse_args()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=f'commoncrawl_scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
)

# https://index.commoncrawl.org/CC-MAIN-2025-21-index?url=*.greenhouse.io/**&output=json reference link for later
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


producer = KafkaProducer(bootstrap_servers='localhost:9092',
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

job_sites_with_patterns = [
    ("*.greenhouse.io/*", re.compile(r"^https://job-boards\.greenhouse\.io/[^/]+/jobs/[^/?#]+")),
    ("*.jobs.lever.co/*", re.compile(r"^https://[^/]+\.jobs\.lever\.co/[^?#]*")),
    ("*.workable.com/*", re.compile(r"^https://apply\.workable\.com/[^/]+/j/[^/?#]+")),
    ("*.bamboohr.com/*", re.compile(r"^https://[^/]+\.bamboohr\.com/careers/[^/?#]*")),
]

def get_all_url(years):
    '''Returns a list of all of the job sites per crawl index for the current year'''
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
    # print(allURL)
    return allURL

@retry_with_backoff(retries=3)
def fetch_with_retry(url, headers=None, stream=False):
    rate_limiter.wait()  # Rate limit all requests
    response = requests.get(url, headers=headers, stream=stream)
    response.raise_for_status()
    return response

def get_relevant_objects(json_response):
    '''Takes in a json file response from extractHTML, and returns all the objects that have links with the specific format.
    This is done to reduce the number of objects/files dealt with, and thus reduce api calls made to the server,
    which hopefully reduces rate limiting'''
    trimmed_list = [] 
    for line in response.text.strip().split('\n'):
        try:
            record = json.loads(line)
            url = record.get("url", "")
            if bamboohr_regex.match(url):
                trimmed_list.append(record)
        except json.JSONDecodeError as je:
                        logging.warning(f"Failed to parse JSON line: {str(je)}")
        except Exception as e:
            logging.error(f"Error processing record: {str(e)}")
    print(trimmed_list) 
    return trimmed_list

def extractHTML(url_list):
    total_urls = len(url_list)
    '''
    TODO
    instead of getting every link and then extracting from there, parse all the jobs
    that follow some format like https://job-boards.greenhouse.io/meritamerica/jobs/5566396004
    and then pull the gz file using regex, should reduce number of calls
    '''
    for idx, url in enumerate(url_list, 1):
        logging.info(f"Processing URL {idx}/{total_urls}: {url}")
        try:
            response = fetch_with_retry(url)
            desired_objects = get_relevant_objects(response)
            # after this point, should be a list of relevant json objects 
            count = 0
            for json_obj in desired_objects:
                while count < 10:
                    if json_obj.get("mime") == "text/html":
                        warc_url = f"https://data.commoncrawl.org/{record['filename']}"
                        logging.info(f"Fetching WARC file: {warc_url}")
                        headers = {
                            'Range': f"bytes={record['offset']}-{int(record['offset']) + int(record['length']) - 1}"
                        }
                        warc_response = fetch_with_retry(warc_url, headers=headers, stream=True)
                        try:
                            with gzip.GzipFile(fileobj=warc_response.raw) as gzipped_file:
                                for warc_record in ArchiveIterator(gzipped_file):
                                    if warc_record.rec_type == 'response':
                                        html = warc_record.content_stream().read()
                                        soup = BeautifulSoup(html, 'html.parser')
                                        text = soup.get_text()

                                        if any(keyword in text.lower() for keyword in ['apply', 'job description', 'apply now']):
                                            job_data = {
                                                'url': record['url'],
                                                'html': html.decode('utf-8', errors='ignore'),
                                                'timestamp': record['timestamp']
                                            }
                                            allJobData.append(job_data)
                                            logging.info(f"Successfully extracted job data from: {record['url']}")
                                            print(f"Found job listing at: {record['url']}")
                        except Exception as e:
                            logging.error(f"Error processing WARC record: {str(e)}")
                    count += 1
        except requests.RequestException as req_err:
            logging.error(f"Request error for URL {url}: {str(req_err)}")
        except Exception as e:
            logging.error(f"General error for URL {url}: {str(e)}")

    logging.info(f"Extraction completed. Total job listings found: {len(allJobData)}")


if __name__ == "__main__":
    # modify this to accept docker compose parameter, we pass in the year and it'll do the rest to hopefully the rest
    # worst case we "dumb it down" to only read crawl by crawl instead of multiple mass crawls and then just do more containers
    allURL = get_all_url("2025")
    #allURL = get_all_url(args)
    allJobData = extractHTML(allURL)

'''bas
for record in ArchiveIterator(gzip.GzipFile(fileobj=resp.raw)):
    if record.rec_type == 'response':
        html = record.content_stream().read()
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        if any(x in text.lower() for x in ['hiring', 'job opening', 'apply now']):
            producer.send('raw_jobs', {
                'url': record.rec_headers.get_header('WARC-Target-URI'),
                'text': text[:1000]
            })
'''

