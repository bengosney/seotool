# Standard Library
from dataclasses import dataclass

# First Party
from processors import BaseResultData, ResultSet, hookimpl_processor
from seotool.crawl import Crawler


@dataclass
class ResultData(BaseResultData):
    url: str


class MissingH1:
    """H1's give users and search engins a good idea of what the page is
    about."""

    def __init__(self, crawler: Crawler) -> None:
        self.missing_h1s = []
        self.crawler = crawler

    @hookimpl_processor
    def get_results_set(self):
        data = [ResultData(v) for v in self.missing_h1s]
        return ResultSet("Missing H1's", f"{self.__doc__}", data)

    @hookimpl_processor
    def process(self, html, url):
        h1s = html.find_all("h1")

        if len([h1 for h1 in h1s if h1.getText() != ""]) == 0:
            self.missing_h1s.append(url)
            self.crawler.printERR(f"Found no H1 on {url}")
