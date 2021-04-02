# Standard Library
import urllib.parse

# First Party
from processors import ResultSet, hookimpl_processor


class Internal301:
    """Internal links that 301."""

    def __init__(self, crawler):
        self.crawler = crawler
        self.links = {}
        self.url301s = []

    def _find_links(self, url):
        return sorted([page for page in self.links if url in self.links[page]])

    @hookimpl_processor
    def get_results_set(self):
        resolve_cache = self.crawler.resolve_cache
        data = [{"src": url, "dest": resolve_cache[url], "links": self._find_links(url)} for url in self.url301s]

        return ResultSet("Internal 301s", f"{self.__doc__}", data)

    @hookimpl_processor
    def process(self, html, url, status_code):
        if status_code == 301:
            self.url301s.append(url)

        links = html.find_all("a")
        urls = []

        for link in links:
            try:
                urls.append(urllib.parse.urljoin(self.crawler.base_url, link["href"]))
            except KeyError:
                continue

        self.links.update({url: urls})
