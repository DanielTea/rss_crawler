import csv
import requests
import yaml
from bs4 import BeautifulSoup
import re
import PyPDF2
import io
import listparser as lp

class WebCrawler:
    def __init__(self, base_url, max_depth=30):
        print("Initializing WebCrawler with base URL: ", base_url)
        self.base_url = base_url
        self.visited_urls = set()  # To keep track of visited URLs
        self.max_depth = max_depth

    @staticmethod
    def _is_valid_url(url):
        """Validate the URL structure to avoid invalid ones."""
        print("Validating URL: ", url)
        parsed_url = requests.utils.urlparse(url)
        return all([parsed_url.scheme, parsed_url.netloc, parsed_url.path])

    def _extract_links_from_text(self, content):
        print("Extracting links from text content")
        rss_links = set()
        # Improved regex pattern that avoids capturing unwanted HTML tags
        url_pattern = re.compile(
            r'https?://[\w\d\-._~:/?#[\]@!$&\'()*+,;=%]+')
        links = re.findall(url_pattern, content)
        for link in links:
            if link.endswith(('.rss', '.rss.xml', '.xml', '.atom') or 'feed' in link or 'rss' in link) and not any(ext in link for ext in ['wlwmanifest',
                                                                                                                                           'sitemap',
                                                                                                                                           'osd.xml',
                                                                                                                                           'feedback',
                                                                                                                                           '.jpg', 
                                                                                                                                           '.png', 
                                                                                                                                           'img']):
                if self._is_valid_url(link):
                    rss_links.add(link)
        return rss_links

    def _parse_opml_content(self, url):
        
        result = lp.parse(url)
        rss_links = []
        for feed in result.feeds:
            rss_links.append(feed.url)
        
        return rss_links

    def _parse_for_rss_links(self, html, depth=0):
        print("Parsing for RSS links in HTML content")
        soup = BeautifulSoup(html, 'html.parser')
        rss_links = set()

        for link in soup.find_all("a", href=True):
            href = requests.compat.urljoin(self.base_url, link['href'])
            if (href.endswith(('.rss', '.rss.xml', '.xml', '.atom')) or 'feed' in href or 'rss' in href) and not any(ext in href for ext in ['feedback',
                                                                                                                                             'sitemap',
                                                                                                                                             'osd.xml',
                                                                                                                                             'wlwmanifest',
                                                                                                                                             '.jpg', 
                                                                                                                                             '.png', 
                                                                                                                                             'img']):
                if self._is_valid_url(href):
                    rss_links.add(href)

            # Check for resource type links and recurse if necessary
            elif any(href.endswith(ext) for ext in ['.csv', 
                                                    '.yml', 
                                                    '.yaml', 
                                                    '.opml', 
                                                    '.txt', 
                                                    # '.pdf'
                                                    ]) or 'feed' in href or 'rss' in href:
                if depth < self.max_depth and href not in self.visited_urls:  # Check if depth is within limit and URL is not visited
                    print("Found resource type link, recursing")
                    self.visited_urls.add(href)
                    rss_links.update(self.crawl(href, depth + 1))  # Recurse

        # Extracting from plain text inside HTML
        rss_links_from_text = self._extract_links_from_text(html)
        rss_links.update(rss_links_from_text)

        return rss_links
    
    def _parse_csv_content(self, content):
        print("Parsing CSV content")
        rss_links = set()
        csv_data = csv.reader(content.splitlines())
        for row in csv_data:
            for cell in row:
                links = self._extract_links_from_text(cell.strip())
                rss_links.update(links)
        return rss_links
    
    def _parse_pdf_content(self, content):
        print("Parsing PDF content")
        rss_links = set()
        pdf_file = PyPDF2.PdfReader(io.BytesIO(content))
        for page_num in range(len(pdf_file.pages)):
            page = pdf_file.pages[page_num]
            content = page.extract_text()
            links = self._extract_links_from_text(content)
            rss_links.update(links)
        return rss_links
    
    def _parse_yaml_content(self, content):
        print("Parsing YAML content")
        try:
            data = yaml.safe_load(content)
            if isinstance(data, list):  # Check if the YAML content is a list of URLs
                return set(filter(self._is_valid_url, data))
            else:
                return set()  # Return an empty set if the YAML format is not as expected
        except yaml.YAMLError:
            print("Error parsing the YAML content")
            return set()

    def crawl(self, url=None, depth=0):
        if not url:
            url = self.base_url

        print("Crawling URL: ", url)

        try:
            response = requests.get(url, timeout=5)
        except requests.exceptions.RequestException:
            print("Error occurred while fetching the URL, skipping...")
            print(requests.exceptions.RequestException)
            return set()
        
        if response.status_code != 200:
            print(f"Failed to fetch content from {url}")
            return set()

        if url.endswith('.csv'):
            print("URL ends with .csv, parsing CSV content")
            return self._parse_csv_content(response.text)

        if url.endswith(('.yml', '.yaml')):
            print("URL ends with .yml or .yaml, parsing YAML content")
            return self._parse_yaml_content(response.text)

        if url.endswith('.opml'):
            print("URL ends with .opml, parsing OPML content")
            return self._parse_opml_content(url)
        
        if url.endswith('.xml'):
            print("URL ends with .xml, parsing xml as OPML content")
            return self._parse_opml_content(url)

        if url.endswith('.txt'):
            print("URL ends with .txt, extracting links from text")
            return self._extract_links_from_text(response.text)

        # if url.endswith('.pdf'):
        #     print("URL ends with .pdf, parsing PDF content")
        #     return self._parse_pdf_content(response.content)

        # If it's none of the above, then parse as HTML
        print("URL does not match any known extensions, parsing as HTML")
        return self._parse_for_rss_links(response.text, depth)