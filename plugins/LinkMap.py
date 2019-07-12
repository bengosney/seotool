import urllib.parse

class LinkMap:
    def __init__(self, crawler):
        self.crawler = crawler
        self.links = {}

    def get_results_header(self):
        return ['src', 'dest', 'pages']
    
    def get_results(self):
        return [[url] + links for (url, links) in self.links.items()]
        
    def parse(self, html_soup, url=None):
        links = html_soup.find_all('a')
        urls = []

        for link in links:
            try:
                urls.append(urllib.parse.urljoin(self.crawler.base_url, link['href']))
            except KeyError:
                continue

        self.links.update({url: urls})
