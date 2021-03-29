# Standard Library
import urllib.parse

# First Party
from processors import ResultSet, hookimpl_processor


class ExternalImages:
    """List of external images"""

    def __init__(self, crawler):
        self.crawler = crawler
        self.images = []

    @hookimpl_processor
    def get_results_set(self):
        data = [{"Image": image} for image in set(self.images)]

        return ResultSet("External Images", f"{self.__doc__}", data)

    @hookimpl_processor
    def process(self, html, url):
        images = html.find_all("img")
        parsed_base = urllib.parse.urlparse(self.crawler.base_url)

        for image in images:
            try:
                full_url = urllib.parse.urljoin(self.crawler.base_url, image["src"])
            except KeyError:
                continue

            parsed_url = urllib.parse.urlparse(full_url)
            if parsed_url.netloc != parsed_base.netloc:
                self.images.append(full_url)
