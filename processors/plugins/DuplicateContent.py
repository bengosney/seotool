# Standard Library
from collections import defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
from itertools import permutations, product
from typing import List

# Third Party
import click
from bs4 import BeautifulSoup

# First Party
from processors import BaseResultData, ResultSet, hookimpl_processor


@dataclass
class ResultData(BaseResultData):
    content: str
    urls: List[str]


@dataclass
class PageContent:
    url: str
    content: List[str]


class DuplicateContent:
    """Duplicate Content."""

    def __init__(self, crawler, duplicate_content_min_length: int = 20, duplicate_content_ratio: float = 0.8):
        self.min_length = duplicate_content_min_length
        self.content: List[PageContent] = []
        self.crawler = crawler
        self.ratio = duplicate_content_ratio

    @hookimpl_processor
    def get_options(self):
        return [
            click.option("--duplicate-content-min-length", default=20, help="Minimum length for a block of content"),
            click.option("--duplicate-content-ratio", default=0.8, help="Match ratio for the content comparison"),
        ]

    @hookimpl_processor
    def get_results_set(self):
        data = defaultdict(lambda: [])

        for pagePair in permutations(self.content, 2):
            for contentPair in product(pagePair[0].content, pagePair[1].content):
                match = SequenceMatcher(None, *contentPair)
                if match.ratio() > self.ratio:
                    key = 1 if contentPair[1] in data else 0
                    data[contentPair[key]].append(pagePair[0].url)
                    data[contentPair[key]].append(pagePair[1].url)

        dataSet = [ResultData(c, sorted(list(set(u)))) for (c, u) in data.items()]

        return ResultSet("Duplicate Content", f"{self.__doc__}", dataSet)

    @hookimpl_processor
    def process(self, html: BeautifulSoup, url, status_code):
        if status_code == 200:
            canonical = html.find("link", {"rel": "canonical"})
            if canonical is None:
                sep = chr(1)
                texts = [t.strip(" \n\t") for t in html.getText(separator=sep).split(sep)]
                data = PageContent(url, [t for t in texts if len(t.split()) > self.min_length])
                self.content.append(data)
