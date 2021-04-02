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
    httpserver.expect_request("/page2.pdf").respond_with_data(
        "<h1>Page 2</h1>",
        content_type="application/pdf",
    )

    httpserver.expect_request("/").respond_with_data(
        f"""
        <a href="{httpserver.url_for("/page1")}">page1</a>
        <a href="{httpserver.url_for("/page2.pdf")}">page2</a>
        """,
        content_type="text/html",
    )

    crawler = Crawler(httpserver.url_for("/"), verbose=False, plugins=["IgnorePDF"])
    crawler.asyncio_crawl(save=False)

    assert sorted(crawler.all_urls) == sorted([httpserver.url_for("/page1"), httpserver.url_for("/")])
