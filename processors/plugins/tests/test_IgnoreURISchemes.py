# Third Party
from bs4 import BeautifulSoup

# First Party
from processors.plugins.IgnoreURISchemes import IgnoreURISchemes


def test_ignore_uri_schemes() -> None:
    valid = [
        '<a href="/link">link</a>',
        '<a href="http://www.example.com/">example</a>',
        '<a href="https://www.example.com/">example</a>',
    ]
    invalid = [
        '<a href="tel://00000000000">Phone</a>',
        '<a href="tel:00000000000">Phone</a>',
        '<a href="mailto:example@example.com">email</a>',
    ]

    html = BeautifulSoup(
        "".join(valid + invalid),
        "html.parser",
    )

    links = html.find_all("a")
    assert len(links) == len(valid + invalid)

    plugin = IgnoreURISchemes()
    plugin.process_html(html, None)

    links = html.find_all("a")
    assert len(links) == len(valid)
