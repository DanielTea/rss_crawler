import csv
import sqlite3
import os
from pathlib import Path
import yaml
from rssFeedCrawler import WebCrawler

CONFIG_PATH = "./rss_crawler_module/config.yaml"

# Load config from config.yaml
with open(CONFIG_PATH, 'r') as file:
    config = yaml.safe_load(file)

SQLITE_PATH = config['database']['sqlite_path']
RSS_LINKS_TABLE_NAME = config['database']['rss_links_table_name']
RSS_FEED_WEBSITES_TABLE_NAME = config['database']['website_table_name']
RSS_ARTICLE_TABLE_NAME = 'rss_article'

RSS_LINKS_CSV_PATH = config['csv']['rss_links']
RSS_FEED_WEBSITES_CSV_PATH = config['csv']['rss_feed_websites']

def setup_database():
    with sqlite3.connect(SQLITE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {RSS_LINKS_TABLE_NAME} (link TEXT UNIQUE)''')
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {RSS_FEED_WEBSITES_TABLE_NAME} (website TEXT UNIQUE, last_crawl_date DATE)''')
        cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {RSS_ARTICLE_TABLE_NAME} (
            publisher TEXT NOT NULL,
            title TEXT NOT NULL,
            link TEXT UNIQUE NOT NULL,
            published TEXT NOT NULL,
            language TEXT NOT NULL,
            crawl_date DATE NOT NULL
        )''')
        conn.commit()

def save_links_to_database(links):
    with sqlite3.connect(SQLITE_PATH) as conn:
        cursor = conn.cursor()
        for link in links:
            cursor.execute(f"INSERT OR IGNORE INTO {RSS_LINKS_TABLE_NAME} (link) VALUES (?)", (link,))
        conn.commit()

def load_websites_from_database():
    websites = set()
    with sqlite3.connect(SQLITE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT website FROM {RSS_FEED_WEBSITES_TABLE_NAME}")
        rows = cursor.fetchall()
        for row in rows:
            websites.add(row[0])
    return websites

if __name__ == "__main__":
    setup_database()
    
    print("Choose loading source:")
    print("1: SQLite")
    print("2: CSV")
    choice = input("Enter your choice (1/2): ")

    if choice == "1":
        websites_to_crawl = load_websites_from_database()
    elif choice == "2":
        websites_to_crawl = set()
        csv_path = Path(RSS_FEED_WEBSITES_CSV_PATH)
        if csv_path.exists():
            with csv_path.open("r") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    websites_to_crawl.add(row[0])
    else:
        print("Invalid choice!")
        exit()

    all_found_links = set()
    for website in websites_to_crawl:
        crawler = WebCrawler(website)
        new_links = crawler.crawl()
        all_found_links.update(new_links)
        print(f"Found {len(new_links)} new RSS links from {website}!")

    print("Choose saving method:")
    print("1: SQLite")
    print("2: CSV")
    choice = input("Enter your choice (1/2): ")

    if choice == "1":
        save_links_to_database(all_found_links)
    elif choice == "2":
        existing_links = set()
        csv_path = Path(RSS_LINKS_CSV_PATH)
        if csv_path.exists():
            with csv_path.open("r") as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    existing_links.add(row[0])

        with csv_path.open("a", newline='') as csvfile:
            writer = csv.writer(csvfile)
            for link in all_found_links:
                if link not in existing_links:
                    writer.writerow([link])
                    print(link)
    else:
        print("Invalid choice!")
