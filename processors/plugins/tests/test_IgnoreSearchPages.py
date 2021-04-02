# Standard Library

# Third Party
from pytest_httpserver import HTTPServer

# First Party
from seotool.crawl import Crawler


def test_ignoring_pdf(httpserver: HTTPServer):
    httpserver.expect_request("/page1").respond_with_data(
        "<h1>Page 1</h1>",
        content_type="text/html",
    )
    httpserver.expect_request("/search/page1").respond_with_data(
        "<h1>Search Page 1</h1>",
        content_type="text/html",
    )

    httpserver.expect_request("/").respond_with_data(
        f"""
        <a href="{httpserver.url_for("/page1")}">page1</a>
        <a href="{httpserver.url_for("/search/page1")}">page2</a>
        """,
        content_type="text/html",
    )

    crawler = Crawler(httpserver.url_for("/"), verbose=False, plugins=["IgnoreSearchPages"])
    crawler.asyncio_crawl(save=False)

    assert sorted(crawler.all_urls) == sorted([httpserver.url_for("/page1"), httpserver.url_for("/")])
