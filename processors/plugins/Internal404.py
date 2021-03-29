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

    @hookimpl_processor
    def get_results_set(self):
        data = [[url] + self.links[url] for url in self.f404s]

        return ResultSet("Internal 404's", f"{self.__doc__}", data)

    @hookimpl_processor
    def parse(self, html, url, status_code):
        if url is None or status_code is None:
            return

        if status_code == 404:
            self.f404s.append(url)
            self.crawler.printERR(f"404 found: {url}")
        else:
            links = html.find_all("a")

            for link in links:
                try:
                    abs_url = urllib.parse.urljoin(self.crawler.base_url, link["href"])
                except KeyError:
                    continue

                try:
                    self.links[abs_url].append(url)
                except KeyError:
                    self.links.update({abs_url: [url]})
