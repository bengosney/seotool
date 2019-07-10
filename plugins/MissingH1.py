class MissingH1:
    def __init__(self, crawler):
        self.missing_h1s = []
        self.crawler = crawler

    def get_results_headder(self):
        return ['url']
        
    def get_results(self):
        return self.missing_h1s
        
    def parse(self, html_soup, url=None):
        h1s = html_soup.find_all('h1')

        if len(h1s) == 0:
            self.missing_h1s.append([url])
            self.crawler.printERR(f"Found no H1 on {url}")
