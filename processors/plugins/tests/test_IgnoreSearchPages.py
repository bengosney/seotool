# Standard Library

# Third Party

# First Party

# Third Party
from bs4 import BeautifulSoup

# First Party
from processors.plugins.IgnoreSearchPages import IgnoreSearchPages


def test_ignore_search_pages() -> None:
    html = BeautifulSoup(
        """
<a href="/link">link</a>
<a href="http://www.example.com/search/page2">example</a>
<a href="/search/page1">Search Page 1</a>
<a href="/search">Search</a>
    """,
        "html.parser",
    )

    links = html.find_all("a")
    assert len(links) == 4

    plugin = IgnoreSearchPages()
    plugin.process_html(html)

    links = html.find_all("a")
    assert len(links) == 2
