from warcio.archiveiterator import ArchiveIterator
import requests
import gzip
from bs4 import BeautifulSoup
from kafka import KafkaProducer
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--year", required=True, help="Please enter the year to extract from (2009-2025)")
args = parser.parse_args()


producer = KafkaProducer(bootstrap_servers='localhost:9092',
                         value_serializer=lambda v: json.dumps(v).encode('utf-8'))

job_sites = [
    "*.greenhouse.io/*"]
'''
    "*.jobs.lever.co/*",
    "*.workable.com/*",
    "*.bamboohr.com/*",
    "*.ziprecruiter.com/jobseeker/home*",
    "*.indeed.com/*",
    "*.linkedin.com/jobs/*"
]
'''

def get_all_url(years):
    all_snapshots_url = "https://index.commoncrawl.org/collinfo.json"
    snapshots = requests.get(all_snapshots_url).json()
    snapshots_by_year = {year: [snap for snap in snapshots if year in snap["id"]] for year in years} # returns a dictionary where each year key gives you all the snapshots from tha tyear

    allURL = []
    # triple for loop is bad but because we're limiting it to a small sample size, it's okay
    for year in years:
        for snapshot in snapshots_by_year[year]:
            for jobSource in job_sites:
                cdx_api = snapshot["cdx-api"]
                baseURL = cdx_api + "?url=" + jobSource + "*&output=json"
                allURL.append(baseURL)        
    # print(allURL)
    return allURL

def extractHTML(url_list):
    allJobData = []
    for url in url_list:
        response = requests.get(url)
        max = 5
        curr = 0
        for line in response.text.strip().split('\n'):
            if curr < max:
                record = json.loads(line)
                if record["mime"] == "text/html":
                    warc_url = f"https://data.commoncrawl.org/{record['filename']}"
                    print("curr url: " + warc_url)
                    headers = {'Range': f"bytes={record['offset']}-{int(record['offset']) + int(record['length']) - 1}"}
                    resp = requests.get(warc_url, headers=headers, stream=True)
                    try:
                        for warc_record in ArchiveIterator(gzip.GzipFile(fileobj=resp.raw)):
                            print(warc_record)
                            if warc_record.rec_type == 'response':
                                html = warc_record.content_stream().read()
                                soup = BeautifulSoup(html, 'html.parser')
                                text = soup.get_text()
                                # Check for job-related keywords
                                if any(keyword in text.lower() for keyword in ['apply', 'job description', 'apply now']):
                                    job_data = {
                                        'url': record['url'],
                                        'html': html.decode('utf-8', errors='ignore'),
                                        'timestamp': record['timestamp']
                                    }
                                    allJobData.append(job_data)
                                    producer.send('raw_jobs', job_data)
                                    producer.flush()
                                    print(job_data)
                    except Exception as e:
                        print(e)
                curr += 1
    return allJobData


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

