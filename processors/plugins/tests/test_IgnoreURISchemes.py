# Standard Library

# Third Party

# First Party

# Third Party
from bs4 import BeautifulSoup

# First Party
from processors.plugins.IgnoreURISchemes import IgnoreURISchemes


def test_ignore_uri_schemes():
    html = BeautifulSoup(
        """
<a href="/link">link</a>
<a href="http://www.example.com/">example</a>
<a href="https://www.example.com/">example</a>
<a href="tel://00000000000">Phone</a>
    """,
        "html.parser",
    )

    links = html.find_all("a")
    assert len(links) == 4

    plugin = IgnoreURISchemes()
    plugin.process_html(html, None)

    links = html.find_all("a")
    assert len(links) == 3
