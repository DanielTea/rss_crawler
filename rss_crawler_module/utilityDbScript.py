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

def insert_website_to_database(website):
    with sqlite3.connect(SQLITE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f"INSERT OR IGNORE INTO {RSS_FEED_WEBSITES_TABLE_NAME} (website, last_crawl_date) VALUES (?, NULL)", (website,))
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

def bulk_insert_websites_to_database(websites):
    with sqlite3.connect(SQLITE_PATH) as conn:
        cursor = conn.cursor()
        cursor.executemany(f"INSERT OR IGNORE INTO {RSS_FEED_WEBSITES_TABLE_NAME} (website, last_crawl_date) VALUES (?, NULL)", ((website,) for website in websites))
        conn.commit()

def load_websites_from_database():
    websites = []
    with sqlite3.connect(SQLITE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT website, last_crawl_date FROM {RSS_FEED_WEBSITES_TABLE_NAME}")
        rows = cursor.fetchall()
        for row in rows:
            websites.append({"website": row[0], "last_crawl_date": row[1]})
    return websites

def update_last_crawl_date(website, date):
    with sqlite3.connect(SQLITE_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE {RSS_FEED_WEBSITES_TABLE_NAME} SET last_crawl_date = ? WHERE website = ?", (date, website))
        conn.commit()


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
