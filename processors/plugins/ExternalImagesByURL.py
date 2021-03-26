import urllib.parse
from collections import defaultdict

from processors import ResultSet, hookimpl_processor


class ExternalImagesByURL:
    """List of external images for each URL"""

    def __init__(self, crawler):
        self.crawler = crawler
        self.images = defaultdict(lambda: [])

    @hookimpl_processor
    def get_results_set(self):
        data = [{"Image": image, "url": ",".join(urls)} for (image, urls) in self.images.items()]

        return ResultSet("External Images by URL", f"{self.__doc__}", data)

    @hookimpl_processor
    def process(self, html, url):
        images = html.find_all("a")
        parsed_base = urllib.parse.urlparse(self.crawler.base_url)

        for image in images:
            try:
                full_url = urllib.parse.urljoin(self.crawler.base_url, image["href"])
            except KeyError:
                continue

            parsed_url = urllib.parse.urlparse(full_url)
            if parsed_url.netloc != parsed_base.netloc:
                self.images[url].append(full_url)
