# Standard Library

# Third Party
from pytest_httpserver import HTTPServer

# First Party
from processors.plugins.ExternalLinksByURL import ResultData
from seotool.crawl import Crawler


def test_external(httpserver: HTTPServer):
    link = "http://example.com/"
    httpserver.expect_request("/page1").respond_with_data(
        f'<a href="{link}">external</a>',
        content_type="text/html",
    )
    httpserver.expect_request("/page2").respond_with_data(
        f'<a href="{link}">external</a>',
        content_type="text/html",
    )
    httpserver.expect_request("/").respond_with_data(
        f"""
        <img src="internal.png" />
        <a href="{httpserver.url_for("/page1")}">page1</a>
        <a href="{httpserver.url_for("/page2")}">page2</a>
        """,
        content_type="text/html",
    )

    crawler = Crawler(httpserver.url_for("/"), verbose=False, plugins=["ExternalLinksByURL"])
    (res,) = crawler.sync_crawl(save=False)

    expected_data = [ResultData(link, sorted([httpserver.url_for("/page1"), httpserver.url_for("/page2")]))]

    assert res.data == expected_data
