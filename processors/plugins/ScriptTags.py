# Standard Library
from dataclasses import dataclass

# First Party
from processors import BaseResultData, ResultSet, hookimpl_processor
from seotool.crawl import Crawler


@dataclass
class ResultData(BaseResultData):
    src: str
    url: str


class ScriptTags:
    """Script tags used in the site."""

    default_disabled = True

    def __init__(self, crawler: Crawler) -> None:
        self.scriptTags = []
        self.crawler = crawler

    @hookimpl_processor
    def get_results_set(self):
        data = [ResultData(src, url) for (url, src) in self.scriptTags]
        return ResultSet("Script tags", f"{self.__doc__}", data)

    @hookimpl_processor
    def process(self, html, url):
        scriptTags = html.find_all("script")

        for scriptTag in scriptTags:
            try:
                self.scriptTags.append([url, scriptTag["src"]])
            except KeyError:
                pass
