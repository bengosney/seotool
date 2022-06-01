# Standard Library
import urllib.parse
from dataclasses import dataclass

# Third Party
from bs4 import BeautifulSoup

# First Party
from processors import BaseResultData, ResultSet, hookimpl_processor


@dataclass
class ResultData(BaseResultData):
    link: str
    pages: list[str]


class Internal404:
    """Internal 404 links."""

    def __init__(self, crawler) -> None:
        self.crawler = crawler
        self.links: dict[str, list[str]] = {}
        self.f404s: list[str] = []

    def _find_links(self, url: str) -> list[str]:
        return sorted(page for page in self.links if url in self.links[page])

    @hookimpl_processor
    def get_results_set(self) -> ResultSet:
        data = [ResultData(url, self._find_links(url)) for url in self.f404s]

        return ResultSet("Internal 404's", f"{self.__doc__}", data)

    @hookimpl_processor
    def process(self, html: BeautifulSoup, url: str, status_code: int) -> None:
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
