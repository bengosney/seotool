# Third Party
from pytest_httpserver import HTTPServer

# First Party
from seotool.crawl import Crawler


def get_page(body, content):
    return f"""
<html>
<head>
    <title>{content}</title>
</head>
<body>
{body}
</body>
</html>
"""


def test_duplicates(httpserver: HTTPServer):
    title = "content"
    httpserver.expect_request("/page2").respond_with_data(get_page("<h1>page2</h1>", title), content_type="text/html")
    page2_url = httpserver.url_for("/page2")

    httpserver.expect_request("/page3").respond_with_data(get_page("<h1>page3</h1>", "Other title"), content_type="text/html")
    page3_url = httpserver.url_for("/page3")

    httpserver.expect_request("/").respond_with_data(
        get_page(
            f"""
        <h1>page1</h1>
        <a href="{page2_url}">page 2</a>
        <a href="{page3_url}">page 3</a>
        """,
            title,
        ),
        content_type="text/html",
    )

    crawler = Crawler(httpserver.url_for("/"), verbose=False, plugins=["DuplicateTitle"])
    (res,) = crawler.asyncio_crawl(save=False)

    expected_data = [{"title": title, "urls": sorted([httpserver.url_for("/"), httpserver.url_for("/page2")])}]

    assert res.data == expected_data


def test_no_duplicates(httpserver: HTTPServer):
    httpserver.expect_request("/page2").respond_with_data(get_page("<h1>page1</h1>", "page1"), content_type="text/html")
    page2_url = httpserver.url_for("/page2")
    httpserver.expect_request("/").respond_with_data(
        get_page(f'<h1>page1</h1><a href="{page2_url}">page 2</a>', "page2"),
        content_type="text/html",
    )

    crawler = Crawler(httpserver.url_for("/"), verbose=False, plugins=["DuplicateTitle"])
    res = crawler.asyncio_crawl(save=False)[0]

    assert res.data == []
