import sqlite3
import csv
import yaml
from pathlib import Path

import os
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

# Load configuration from config.yaml
with open('config.yaml', 'r') as config_file:
    config = yaml.safe_load(config_file)

SQLITE_PATH = config['database']['sqlite_path']
RSS_LINKS_TABLE_NAME = config['database']['rss_links_table_name']
RSS_FEED_WEBSITES_TABLE_NAME = config['database']['website_table_name']

RSS_LINKS_CSV_PATH = config['csv']['rss_links']
RSS_FEED_WEBSITES_CSV_PATH = config['csv']['rss_feed_websites']

def setup_database():
    with sqlite3.connect(SQLITE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {RSS_LINKS_TABLE_NAME} (link TEXT UNIQUE)''')
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {RSS_FEED_WEBSITES_TABLE_NAME} (website TEXT UNIQUE)''')
        conn.commit()

def insert_website_to_database(website):
    with sqlite3.connect(SQLITE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f"INSERT OR IGNORE INTO {RSS_FEED_WEBSITES_TABLE_NAME} (website) VALUES (?)", (website,))
        conn.commit()

def insert_rss_link_to_database(rss_link):
    with sqlite3.connect(SQLITE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f"INSERT OR IGNORE INTO {RSS_LINKS_TABLE_NAME} (link) VALUES (?)", (rss_link,))
        conn.commit()

def insert_website_to_csv(website):
    with open(RSS_FEED_WEBSITES_CSV_PATH, "a", newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([website])

def load_websites_from_database():
    websites = set()
    with sqlite3.connect(SQLITE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT website FROM {RSS_FEED_WEBSITES_TABLE_NAME}")
        rows = cursor.fetchall()
        for row in rows:
            websites.add(row[0])
    return websites

def load_rss_links_from_database():
    rss_links = set()
    with sqlite3.connect(SQLITE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT link FROM {RSS_LINKS_TABLE_NAME}")
        rows = cursor.fetchall()
        for row in rows:
            rss_links.add(row[0])
    return rss_links


def insert_rss_article(publisher, title, link, published, language, crawl_date):
    with sqlite3.connect(SQLITE_PATH) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute('''
            INSERT INTO rss_article (publisher, title, link, published, language, crawl_date)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (publisher, title, link, published, language, crawl_date))
            conn.commit()
        except sqlite3.IntegrityError:  # Link already exists
            pass


if __name__ == "__main__":
    print("Choose method to store the website URLs:")
    print("1: SQLite")
    print("2: CSV")
    choice = input("Enter your choice (1/2): ")

    if choice == "1":
        setup_database()
        while True:
            website = input("Enter the website URL to be crawled (or 'exit' to stop): ")
            if website.lower() == 'exit':
                break
            insert_website_to_database(website)
            rss_link = input("Enter the RSS link to be stored (or 'exit' to stop): ")
            if rss_link.lower() == 'exit':
                break
            insert_rss_link_to_database(rss_link)

    elif choice == "2":
        while True:
            website = input("Enter the website URL to be crawled (or 'exit' to stop): ")
            if website.lower() == 'exit':
                break
            insert_website_to_csv(website)
    else:
        print("Invalid choice!")
