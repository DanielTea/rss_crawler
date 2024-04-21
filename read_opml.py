link = "https://raw.githubusercontent.com/simevidas/web-dev-feeds/master/feeds.opml"

# link = "https://www.notebooksbilliger.de"

# link = "https://www.autocar.co.uk/car-news"

from rss_crawler_module.rssFeedCrawler import WebCrawler

crawler = WebCrawler(link)
rss_links = crawler.crawl()

for rss_link in rss_links:
    print(rss_link)
