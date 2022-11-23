# Standard Library
import urllib.parse
from dataclasses import dataclass

# First Party
from processors import BaseResultData, ResultSet, hookimpl_processor
from seotool.crawl import Crawler


@dataclass
class ResultData(BaseResultData):
    link: str


class ExternalLinks:
    """List of external links."""

    default_disabled = True

    def __init__(self, crawler: Crawler) -> None:
        self.crawler = crawler
        self.links = []

    @hookimpl_processor
    def get_results_set(self):
        data = [ResultData(link) for link in set(self.links)]

        return ResultSet("External Links", f"{self.__doc__}", data)

    @hookimpl_processor
    def process(self, html):
        links = html.find_all("a")
        parsed_base = urllib.parse.urlparse(self.crawler.base_url)

        for link in links:
            try:
                full_url = urllib.parse.urljoin(self.crawler.base_url, link["href"])
            except KeyError:
                continue

            parsed_url = urllib.parse.urlparse(full_url)
            if parsed_url.netloc != parsed_base.netloc:
                self.links.append(full_url)
