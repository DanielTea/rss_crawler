link = "https://raw.githubusercontent.com/simevidas/web-dev-feeds/master/feeds.opml"

#link = ""

import listparser as lp
result = lp.parse(link)
urls = []
for feed in result.feeds:
    urls.append(feed.url)
print(urls)