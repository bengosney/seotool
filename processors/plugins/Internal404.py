# Standard Library
import urllib.parse

# First Party
from processors import ResultSet, hookimpl_processor


class Internal404:
    """Internal 404 links."""

    def __init__(self, crawler):
        self.crawler = crawler
        self.links = {}
        self.f404s = []

    def _find_links(self, url):
        return sorted([page for page in self.links if url in self.links[page]])

    @hookimpl_processor
    def get_results_set(self):
        data = [{"link": url, "pages": self._find_links(url)} for url in self.f404s]

        return ResultSet("Internal 404's", f"{self.__doc__}", data)

    @hookimpl_processor
    def process(self, html, url, status_code):
        if url is None or status_code is None:
            return

        if status_code == 404:
            self.f404s.append(url)
            self.crawler.printERR(f"404 found: {url}")

        links = html.find_all("a")
        urls = []
        for link in links:
            try:
                urls.append(urllib.parse.urljoin(self.crawler.base_url, link["href"]))
            except KeyError:
                continue

        self.links.update({url: urls})
