import urllib.parse
from pprint import pprint

class Internal301:
    def __init__(self, crawler):
        self.crawler = crawler
        self.links = {}

    def get_results_header(self):
        return ['src', 'dest', 'pages']

    def _find_links(self, url):
        found = []
        for page in self.links:
            if url in self.links[page]:
                found.append(page)

        return found
    
    def get_results(self):
        out = []
        for (src, dest) in self.crawler.resolve_cache.items():
            if src.rstrip('/') != dest.rstrip('/'):
                out.append([src, dest] + self._find_links(src))

        return out
            
        
    def parse(self, html_soup, url=None):
        links = html_soup.find_all('a')
        urls = []

        for link in links:
            try:
                urls.append(urllib.parse.urljoin(self.crawler.base_url, link['href']))
            except KeyError:
                continue

        self.links.update({url: urls})
