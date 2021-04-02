# Third Party
from bs4 import BeautifulSoup

# First Party
from processors.plugins.MultipleH1 import MultipleH1
from seotool.crawl import Crawler

c = Crawler("")


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

    assert res.data == [{"h1s": ["h1-1", "h1-2"], "url": "/"}]


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
