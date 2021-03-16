import urllib.parse


class Internal301:
    def __init__(self, crawler):
        self.crawler = crawler
        self.links = {}

    def get_results_header(self):
        return ["src", "dest", "pages"]

    def _find_links(self, url):
        return [page for page in self.links if url in self.links[page]]

    def get_results(self):
        return [
            [src, dest] + self._find_links(src)
            for (src, dest) in self.crawler.resolve_cache.items()
            if src.rstrip("/") != dest.rstrip("/")
        ]

    def parse(self, html_soup, url=None):
        links = html_soup.find_all("a")
        urls = []

        for link in links:
            try:
                urls.append(urllib.parse.urljoin(self.crawler.base_url, link["href"]))
            except KeyError:
                continue

        self.links.update({url: urls})
