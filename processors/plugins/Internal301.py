# Standard Library
import urllib.parse
from dataclasses import dataclass

# First Party
from engines.dataModels import response
from processors import BaseResultData, ResultSet, hookimpl_processor


@dataclass
class ResultData(BaseResultData):
    src: str
    dest: str
    links: list[str]


class Internal301:
    """Internal links that 301."""

    def __init__(self, crawler):
        self.crawler = crawler
        self.links = {}
        self.url301s = []

    def _find_links(self, url):
        return sorted(page for page in self.links if url in self.links[page])

    @hookimpl_processor
    def get_results_set(self):
        resolve_cache = self.crawler.resolve_cache
        data = [ResultData(url, resolve_cache[url], self._find_links(url)) for url in self.url301s]

        return ResultSet("Internal 301s", f"{self.__doc__}", data)

    @hookimpl_processor
    def process(self, html, url, status_code):
        if status_code == 301:
            self.url301s.append(url)

        links = html.find_all("a")
        urls = []

        for link in links:
            try:
                urls.append(urllib.parse.urljoin(self.crawler.base_url, link["href"]))
            except KeyError:
                continue

        self.links.update({url: urls})

    @hookimpl_processor
    def should_process(self, url: str, response: response) -> bool:
        if url != response.url:
            self.url301s.append(url)

        return True
