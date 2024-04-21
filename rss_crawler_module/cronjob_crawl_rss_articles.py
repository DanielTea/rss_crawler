from utilityDbScript import insert_rss_article, load_rss_links_from_database
from rssReader import RSSReader
from concurrent.futures import ThreadPoolExecutor
from utilityDbScript import insert_rss_article

def start_crawl_with_urls():
 
    links = load_rss_links_from_database()

    total_crawled_links = 0
    rss_reader = RSSReader()

    def process_url(url):
        nonlocal total_crawled_links
        print(f"Starting crawl for {url}...")
        
        crawled_entries = rss_reader._fetch_rss_entries(url)
        if crawled_entries:
            print(f"Found {len(crawled_entries)} entries in {url}")
            total_crawled_links += len(crawled_entries)
            for entry in crawled_entries:
                print(f"Inserting crawled entry {entry['link']} into the database...")
                if entry:
                    insert_rss_article(entry['publisher'], entry['title'], entry['link'], entry['published'], entry['language'], entry['crawl_date'])

    with ThreadPoolExecutor(max_workers=100) as executor:
        executor.map(process_url, links)

    print(f"Total crawled entries: {total_crawled_links}")

if __name__ == "__main__":
    start_crawl_with_urls()
