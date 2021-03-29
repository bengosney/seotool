# Standard Library
import urllib.parse
from collections import defaultdict

# First Party
from processors import ResultSet, hookimpl_processor


class ExternalLinksByURL:
    """List of external links for each URL."""

    def __init__(self, crawler):
        self.crawler = crawler
        self.links = defaultdict(lambda: [])

    @hookimpl_processor
    def get_results_set(self):
        data = [{"Link": link, "url": urls} for (link, urls) in self.links.items()]

        return ResultSet("External Links by URL", f"{self.__doc__}", data)

    @hookimpl_processor
    def process(self, html, url):
        links = html.find_all("a")
        parsed_base = urllib.parse.urlparse(self.crawler.base_url)

        for link in links:
            try:
                full_url = urllib.parse.urljoin(self.crawler.base_url, link["href"])
            except KeyError:
                continue

            parsed_url = urllib.parse.urlparse(full_url)
            if parsed_url.netloc != parsed_base.netloc:
                self.links[url].append(full_url)
