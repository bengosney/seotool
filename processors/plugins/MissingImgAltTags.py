# Standard Library
from dataclasses import dataclass

# First Party
from processors import BaseResultData, ResultSet, hookimpl_processor
from seotool.crawl import Crawler


@dataclass
class ResultData(BaseResultData):
    url: str
    src: str


class MissingImgAltTags:
    """Images missing alt tags."""

    def __init__(self, crawler: Crawler) -> None:
        self.missing_alts = []
        self.crawler = crawler

    @hookimpl_processor
    def get_results_set(self):
        return ResultSet("Images missing alt tags", f"{self.__doc__}", self.missing_alts)

    @hookimpl_processor
    def process(self, html, url):
        images = html.find_all("img")

        for image in images:
            try:
                image["alt"]
            except KeyError:
                try:
                    output = image["src"]
                except KeyError:
                    output = str(image)

                self.missing_alts.append(ResultData(url, output))
                self.crawler.printERR(f"Found missing alt tag for {output}")
