# Standard Library
import urllib.parse
from collections import defaultdict
from dataclasses import dataclass
from typing import List

# First Party
from processors import BaseResultData, ResultSet, hookimpl_processor


@dataclass
class ResultData(BaseResultData):
    image: str
    urls: List[str]


class ExternalImagesByURL:
    """List of external images for each URL."""

    default_disabled = True

    def __init__(self, crawler):
        self.crawler = crawler
        self.images = defaultdict(lambda: [])

    @hookimpl_processor
    def get_results_set(self):
        data = [ResultData(image, sorted(urls)) for (image, urls) in self.images.items()]

        return ResultSet("External Images by URL", f"{self.__doc__}", data)

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
                self.images[full_url].append(url)
