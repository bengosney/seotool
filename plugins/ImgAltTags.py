from collections import deque

class ImgAltTags:
    def __init__(self, crawler):
        self.missing_alts = []
        self.crawler = crawler

    def get_results_headder(self):
        return ['src', 'url']
        
    def get_results(self):
        return self.missing_alts
        
    def parse(self, html_soup, url=None):
        images = html_soup.find_all('img')

        for image in images:
            try:
                image['alt']
            except KeyError:
                self.missing_alts.append([url, image['src']])
                self.crawler.printERR("Found missing alt tag for {}".format(image['src']))
