import urllib.parse


class Internal404:
    def __init__(self, crawler):
        self.crawler = crawler
        self.links = {}
        self.f404s = []

    def get_results_header(self):
        return ["url", "pages"]

    def get_results(self):
        return [[url] + self.links[url] for url in self.f404s]

    def parse(self, html_soup, url=None, status_code=None):
        if url is None or status_code is None:
            return

        if status_code == 404:
            self.f404s.append(url)
            self.crawler.printERR(f"404 found: {url}")
        else:
            links = html_soup.find_all("a")

            for link in links:
                try:
                    abs_url = urllib.parse.urljoin(self.crawler.base_url, link["href"])
                except KeyError:
                    continue

                try:
                    self.links[abs_url].append(url)
                except KeyError:
                    self.links.update({abs_url: [url]})
