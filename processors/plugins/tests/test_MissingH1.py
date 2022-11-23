# Third Party
from bs4 import BeautifulSoup

# First Party
from processors.plugins.MissingH1 import MissingH1, ResultData
from seotool.crawl import Crawler

c = Crawler("example.com")


def test_missing_h1() -> None:
    html = BeautifulSoup(
        """
<p>Page Content</p>
    """,
        "html.parser",
    )

    plugin = MissingH1(c)
    plugin.process(html=html, url="/")
    res = plugin.get_results_set()

    assert res.data == [ResultData("/")]


def test_empty_h1() -> None:
    html = BeautifulSoup(
        """
<h1></h1>
<p>Page Content</p>
    """,
        "html.parser",
    )

    plugin = MissingH1(c)
    plugin.process(html=html, url="/")
    res = plugin.get_results_set()

    assert res.data == [ResultData("/")]


def test_not_missing_h1() -> None:
    html = BeautifulSoup(
        """
<h1>Page Content</h1>
    """,
        "html.parser",
    )

    plugin = MissingH1(c)
    plugin.process(html=html, url="/")
    res = plugin.get_results_set()

    assert res.data == []
