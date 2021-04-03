# Third Party
from pytest_httpserver import HTTPServer

# First Party
from seotool.crawl import Crawler


def test_internal_301(httpserver: HTTPServer):
    httpserver.expect_request("/page2").respond_with_data("", status=301, content_type="text/html")
    page2_url = httpserver.url_for("/page2")

    httpserver.expect_request("/page3").respond_with_data(
        f'<a href="{page2_url}">page2</a>', status=301, content_type="text/html"
    )
    page3_url = httpserver.url_for("/page3")

    httpserver.expect_request("/").respond_with_data(
        f"""
    <a href="{page2_url}">page2</a>
    <a href="{page3_url}">page3</a>
    """,
        content_type="text/html",
    )
    page1_url = httpserver.url_for("/")

    crawler = Crawler(httpserver.url_for("/"), verbose=False, plugins=["Internal301"])
    (res,) = crawler.asyncio_crawl(save=False)

    expected_data = [
        {"src": page2_url, "dest": page2_url, "links": sorted([page1_url, page3_url])},
        {"src": page3_url, "dest": page3_url, "links": [page1_url]},
    ]

    assert res.data == expected_data
