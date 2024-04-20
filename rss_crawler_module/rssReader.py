import feedparser
from datetime import datetime, timedelta
import sqlite3
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
import http

class RSSReader:

    def __init__(self, database="rss_links.db", days_to_crawl=1):
        self.database = database
        self.days_to_crawl = days_to_crawl

    def _get_rss_links(self):
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT link FROM rss_links")
            return [row[0] for row in cursor.fetchall()]

    def _load_existing_entries(self):
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT publisher, title, link, published, language FROM rss_article")
            return set(cursor.fetchall())
        
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), retry=retry_if_exception_type(http.client.RemoteDisconnected))
    def _fetch_rss_entries(self, rss_link):
            
            try:

                feed = feedparser.parse(rss_link)
                current_entries = []
                cutoff_date = datetime.now() - timedelta(days=self.days_to_crawl)
                crawl_date = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %Z')

                publisher_name = feed.feed.title if hasattr(feed.feed, 'title') else "Unknown Publisher"
                language = feed.feed.language if hasattr(feed.feed, 'language') else "Unknown Language" 

                for entry in feed.entries:

                    try:
                        title = entry.title if hasattr(entry, 'title') else ""
                        link = entry.link if hasattr(entry, 'link') else ""
                        published = entry.published if hasattr(entry, 'published') else ""

                        try:
                            pub_date = datetime.strptime(published, '%a, %d %b %Y %H:%M:%S %Z')
                            if pub_date >= cutoff_date:
                                current_entries.append({'publisher': publisher_name, 'title': title, 'link': link, 
                                                        'published': published, 'language': language, 'crawl_date': crawl_date})
                        except ValueError:
                            pass
                    except Exception as e:
                        print(e)
                        pass

            except http.client.RemoteDisconnected:
                print("Remote end closed connection without response. Retrying...")
                pass

            return current_entries
    
