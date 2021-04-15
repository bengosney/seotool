# Third Party
from bs4 import BeautifulSoup

# First Party
from processors.plugins.MultipleH1 import MultipleH1, ResultData
from seotool.crawl import Crawler

c = Crawler("example.com")


def test_multiple_h1():
    html = BeautifulSoup(
        """
<h1>h1-1</h1>
<h1>h1-2</h1>
    """,
        "html.parser",
    )

    plugin = MultipleH1(c)
    plugin.process(html=html, url="/")
    res = plugin.get_results_set()

    assert res.data == [ResultData("/", ["h1-1", "h1-2"])]


def test_not_multiple_h1():
    html = BeautifulSoup(
        """
<h1>h1-1</h1>
    """,
        "html.parser",
    )

    plugin = MultipleH1(c)
    plugin.process(html=html, url="/")
    res = plugin.get_results_set()

    assert res.data == []
