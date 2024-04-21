from rssFeedCrawler import WebCrawler
from utilityDbScript import insert_website_to_database, insert_rss_link_to_database, load_websites_from_database, insert_rss_article, load_rss_links_from_database
from rssReader import RSSReader
from concurrent.futures import ThreadPoolExecutor
from utilityDbScript import insert_rss_article
import csv

def start_crawl_with_urls():
    print("Starting crawl with URLs...")
    urls = [
        "https://raw.githubusercontent.com/simevidas/web-dev-feeds/master/feeds.opml",
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
        "https://github.com/plenaryapp/awesome-rss-feeds#-france",
        "https://raw.githubusercontent.com/matthiasjost/dotnet-creators-opml/main/OPML/blog-opml.xml",
        "https://raw.githubusercontent.com/matthiasjost/dotnet-creators-opml/main/OPML/youtube-opml.xml",
        "https://gist.githubusercontent.com/webpro/5907452/raw/a71a3b59c108267fb667510dbe91154035f1ed10/feeds.opml",
        "https://raw.githubusercontent.com/edsoncezar/RSS/master/feedbro-subscriptions-20191118-091313.opml",

        #WEBSITES
        "https://www.autocar.co.uk/car-news"
    ]
    for url in urls:
        print(f"Inserting {url} into the database...")
        insert_website_to_database(url)

    urls = list(load_websites_from_database())


    with open('./top10milliondomains.csv', 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)  # Skip the header
        for row in csv_reader:
            urls.append("https://" + row[1])  # Append the domain to the urls list with https:// prefix

    total_crawled_links = 0

    def process_url(url):
        nonlocal total_crawled_links
        print(f"Starting crawl for {url}...")
        crawler = WebCrawler(url)
        crawled_links = crawler.crawl()
        print(f"Found {len(crawled_links)} links in {url}")
        total_crawled_links += len(crawled_links)
        for link in crawled_links:
            print(f"Inserting crawled link {link} into the database...")
            insert_rss_link_to_database(link)

    with ThreadPoolExecutor(max_workers=100) as executor:
        executor.map(process_url, urls)

if __name__ == "__main__":
    start_crawl_with_urls()
