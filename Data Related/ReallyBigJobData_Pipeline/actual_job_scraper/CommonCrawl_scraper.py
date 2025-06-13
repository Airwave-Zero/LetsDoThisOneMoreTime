import requests
from warcio.archiveiterator import ArchiveIterator
from bs4 import BeautifulSoup

# Example: CDX index gave us these values
warc_url = 'https://commoncrawl.s3.amazonaws.com/crawl-data/CC-MAIN-2024-10/segments/1711136700321.64/warc/CC-MAIN-20240422081850-20240422111850-00000.warc.gz'
offset = 215049873  # From CDX

headers = {'Range': f'bytes={offset}-'}
resp = requests.get(warc_url, headers=headers, stream=True)

for record in ArchiveIterator(resp.raw):
    if record.rec_type == 'response':
        url = record.rec_headers.get_header('WARC-Target-URI')
        html = record.content_stream().read()
        soup = BeautifulSoup(html, 'html.parser')
        print(f"🔗 URL: {url}")
        print(f"📝 Content Preview:\n{ soup.get_text()[:1000] }")
        break
