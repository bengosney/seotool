# Third Party
from pytest_httpserver import HTTPServer

# First Party
from processors.plugins.ExternalImages import ResultData
from seotool.crawl import Crawler


def test_external(httpserver: HTTPServer):
    img = "http://example.com/external.png"
    httpserver.expect_request("/").respond_with_data(
        f'<img src="{img}" />',
        content_type="text/html",
    )

    crawler = Crawler(httpserver.url_for("/"), verbose=False, plugins=["ExternalImages"])
    (res,) = crawler.asyncio_crawl(save=False)

    expected_data = [ResultData(img)]

    assert res.data == expected_data


def test_not_external(httpserver: HTTPServer):
    httpserver.expect_request("/").respond_with_data(
        '<img src="internal.png" />',
        content_type="text/html",
    )

    crawler = Crawler(httpserver.url_for("/"), verbose=False, plugins=["ExternalImages"])
    (res,) = crawler.asyncio_crawl(save=False)

    assert res.data == []


def test_mixed(httpserver: HTTPServer):
    img = "http://example.com/external.png"
    httpserver.expect_request("/").respond_with_data(
        f'<img src="{img}" /><img src="internal.png" />',
        content_type="text/html",
    )

    crawler = Crawler(httpserver.url_for("/"), verbose=False, plugins=["ExternalImages"])
    (res,) = crawler.asyncio_crawl(save=False)

    expected_data = [ResultData(img)]

    assert res.data == expected_data
