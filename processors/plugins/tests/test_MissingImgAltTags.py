# Third Party
from bs4 import BeautifulSoup

# First Party
from processors.plugins.MissingImgAltTags import MissingImgAltTags, ResultData
from seotool.crawl import Crawler

c = Crawler("example.com")


def test_missing_img_alt() -> None:
    html = BeautifulSoup(
        """
<img src="/bob.png" />
    """,
        "html.parser",
    )

    plugin = MissingImgAltTags(c)
    plugin.process(html=html, url="/")
    res = plugin.get_results_set()

    assert res.data == [ResultData("/", "/bob.png")]


def test_not_missing_img_alt() -> None:
    html = BeautifulSoup(
        """
<img src="/bob.png" alt="bob" />
    """,
        "html.parser",
    )

    plugin = MissingImgAltTags(c)
    plugin.process(html=html, url="/")
    res = plugin.get_results_set()

    assert res.data == []
