class DuplicateH1:
    def __init__(self, crawler):
        self.h1s = {}
        self.crawler = crawler

    def get_results_headder(self):
        return ['h1', 'urls']
        
    def get_results(self):
        return [[h1, *urls] for (h1, urls) in self.h1s.items() if len(urls) > 1]
        
    def parse(self, html_soup, url=None):
        h1s = html_soup.find_all('h1')
        
        for h1Tag in h1s:
            h1 = h1Tag.getText()
            try:                
                self.crawler.printERR("H1 already seen on {}".format(", ".join(self.h1s[h1])))
                self.h1s[h1].append(url)
            except KeyError:
                self.h1s.update({h1: [url]})
