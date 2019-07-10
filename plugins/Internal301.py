import urllib.parse

class Internal301:
    def __init__(self, crawler):
        self.crawler = crawler

    def get_results_header(self):
        return ['src', 'dest']
        
    def get_results(self):
        return [[src, dest] for (src, dest) in self.crawler.resolve_cache.items() if src != dest]
        
    def parse(self, html_soup, url=None):
        pass
