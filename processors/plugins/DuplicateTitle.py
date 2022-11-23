# Standard Library
from dataclasses import dataclass

# First Party
from processors import BaseResultData, ResultSet, hookimpl_processor
from seotool.crawl import Crawler


@dataclass
class ResultData(BaseResultData):
    title: str
    urls: list[str]


class DuplicateTitle:
    """Duplicate title tags."""

    def __init__(self, crawler: Crawler) -> None:
        self.titles = {}
        self.crawler = crawler

    @hookimpl_processor
    def get_results_set(self):
        data = [ResultData(title, sorted(urls)) for (title, urls) in self.titles.items() if len(urls) > 1]

        return ResultSet("Duplicate Titles", f"{self.__doc__}", data)

    @hookimpl_processor
    def process(self, html, url):
        titles = html.find_all("title")

        canonicals = html.find_all("link", {"rel": "canonical"})
        if len(canonicals) > 0:
            try:
                url = canonicals[0]["href"]
            except KeyError:
                pass

        for titleTag in titles:
            title = titleTag.getText()
            try:
                self.titles[title].append(url)
                self.titles[title] = list(set(self.titles[title]))
                self.crawler.printERR(f"Title already seen on {', '.join(self.titles[title])}")
            except KeyError:
                self.titles.update({title: [url]})
