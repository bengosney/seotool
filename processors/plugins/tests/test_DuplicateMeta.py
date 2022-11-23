# Third Party
from pytest_httpserver import HTTPServer

# First Party
from processors.plugins.DuplicateMeta import ResultData
from seotool.crawl import Crawler


def get_page(body: str, content: str) -> str:
    return f"""
<html>
<head>
    <meta name="description" content="{content}" />
</head>
<body>
{body}
</body>
</html>
"""


def test_duplicates(httpserver: HTTPServer):
    meta = "content"
    httpserver.expect_request("/page2").respond_with_data(get_page("<h1>page2</h1>", meta), content_type="text/html")
    page2_url = httpserver.url_for("/page2")
    httpserver.expect_request("/page3").respond_with_data(
        get_page("<h1>page3</h1>", "Other Meta"), content_type="text/html"
    )
    page3_url = httpserver.url_for("/page3")
    httpserver.expect_request("/").respond_with_data(
        get_page(
            f"""
        <h1>page1</h1>
        <a href="{page2_url}">page 2</a>
        <a href="{page3_url}">page 3</a>
        """,
            meta,
        ),
        content_type="text/html",
    )

    crawler = Crawler(httpserver.url_for("/"), verbose=False, plugins=["DuplicateMeta"])
    (res,) = crawler.asyncio_crawl(save=False)

    expected_data = [ResultData(meta, sorted([httpserver.url_for("/"), httpserver.url_for("/page2")]))]

    assert res.data == expected_data


def test_no_duplicates(httpserver: HTTPServer):
    httpserver.expect_request("/page2").respond_with_data(get_page("<h1>page1</h1>", "page1"), content_type="text/html")
    page2_url = httpserver.url_for("/page2")
    httpserver.expect_request("/").respond_with_data(
        get_page(f'<h1>page1</h1><a href="{page2_url}">page 2</a>', "page2"),
        content_type="text/html",
    )

    crawler = Crawler(httpserver.url_for("/"), verbose=False, plugins=["DuplicateMeta"])
    res = crawler.asyncio_crawl(save=False)[0]

    assert res.data == []
