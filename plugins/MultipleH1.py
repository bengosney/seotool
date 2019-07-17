class MultipleH1:
    def __init__(self, crawler):
        self.multiple_h1s = []
        self.crawler = crawler

    def get_results_header(self):
        return ["url", "h1s"]

    def get_results(self):
        return self.multiple_h1s

    def parse(self, html_soup, url=None):
        h1s = html_soup.find_all("h1")

        count = len(h1s)
        if count > 1:
            h1s = [h1.getText() for h1 in h1s].insert(0, url)
            self.multiple_h1s.append([h1s])
            self.crawler.printERR(f"Found {count} H1s on {url}")
