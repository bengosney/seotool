# Third Party
from bs4 import BeautifulSoup

# First Party
from processors.plugins.MissingMeta import MissingMeta
from seotool.crawl import Crawler

c = Crawler("")


def test_missing_meta():
    html = BeautifulSoup(
        """
<p>content</p>
    """,
        "html.parser",
    )

    plugin = MissingMeta(c)
    plugin.process(html=html, url="/")
    res = plugin.get_results_set()

    assert res.data == [{"url": "/"}]


def test_not_missing_meta():
    html = BeautifulSoup(
        """
<meta name="description" content="bob" />
    """,
        "html.parser",
    )

    plugin = MissingMeta(c)
    plugin.process(html=html, url="/")
    res = plugin.get_results_set()

    assert res.data == []
