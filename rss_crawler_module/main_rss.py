from rssFeedCrawler import WebCrawler
from utilityDbScript import insert_website_to_database, insert_rss_link_to_database, load_websites_from_database, insert_rss_article, load_rss_links_from_database
from rssReader import RSSReader

def start_crawl_with_urls():
    print("Starting crawl with URLs...")
    urls = [
        "https://github.com/simevidas/web-dev-feeds/blob/master/feeds.opml",
        "https://github.com/plenaryapp/awesome-rss-feeds",
        "https://raw.githubusercontent.com/androidsx/micro-rss/master/list-of-feeds.txt",
        "https://github.com/joshuawalcher/rssfeeds",
        "https://raw.githubusercontent.com/impressivewebs/frontend-feeds/master/frontend-feeds.opml",
        "https://raw.githubusercontent.com/tuan3w/awesome-tech-rss/main/feeds.opml",
        "https://github.com/plenaryapp/awesome-rss-feeds/tree/master/recommended/with_category",
        "https://github.com/plenaryapp/awesome-rss-feeds/tree/master/countries/without_category",
        "https://gist.githubusercontent.com/stungeye/fe88fc810651174d0d180a95d79a8d97/raw/35cf2dc0db2c28aac21d03709592567c3fc60180/crypto_news.json",
        "https://raw.githubusercontent.com/yavuz/news-feed-list-of-countries/master/news-feed-list-of-countries.json",
        "https://raw.githubusercontent.com/git-list/security-rss-list/master/README.md",
        "https://github.com/plenaryapp/awesome-rss-feeds#-france"
    ]
    for url in urls:
        print(f"Inserting {url} into the database...")
        insert_website_to_database(url)

    urls = load_websites_from_database()

    total_crawled_links = 0
    for url in urls:
        print(f"Starting crawl for {url}...")
        crawler = WebCrawler(url)
        crawled_links = crawler.crawl()
        print(f"Found {len(crawled_links)} links in {url}")
        total_crawled_links += len(crawled_links)
        for link in crawled_links:
            print(f"Inserting crawled link {link} into the database...")
            insert_rss_link_to_database(link)

    from utilityDbScript import insert_rss_article

    links = load_rss_links_from_database()

    total_crawled_links = 0
    rss_reader = RSSReader()
    for url in links:
        print(f"Starting crawl for {url}...")
        crawled_entries = rss_reader._fetch_rss_entries(url)
        print(f"Found {len(crawled_entries)} entries in {url}")
        total_crawled_links += len(crawled_entries)
        for entry in crawled_entries:
            print(f"Inserting crawled entry {entry['link']} into the database...")
            insert_rss_article(entry['publisher'], entry['title'], entry['link'], entry['published'], entry['language'], entry['crawl_date'])
            
    print(f"Total crawled entries: {total_crawled_links}")

if __name__ == "__main__":
    start_crawl_with_urls()
