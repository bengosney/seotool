# Standard Library
import urllib.parse

# First Party
from processors import ResultSet, hookimpl_processor


class Internal301:
    """Internal links that 301."""

    def __init__(self, crawler):
        self.crawler = crawler
        self.links = {}

    def _find_links(self, url):
        return [page for page in self.links if url in self.links[page]]

    @hookimpl_processor
    def get_results_set(self):
        data = [{"src": src, "dest": dest, "links": self._find_links(src)} for (src, dest) in self.crawler.resolve_cache.items() if src.rstrip("/") != dest.rstrip("/")]

        return ResultSet("Internal 301s", f"{self.__doc__}", data)

    @hookimpl_processor
    def process(self, html, url):
        links = html.find_all("a")
        urls = []

        for link in links:
            try:
                urls.append(urllib.parse.urljoin(self.crawler.base_url, link["href"]))
            except KeyError:
                continue

        self.links.update({url: urls})
