# Third Party
from pytest_httpserver import HTTPServer

# First Party
from seotool.crawl import Crawler


def test_external(httpserver: HTTPServer):
    link = "http://example.com/"
    httpserver.expect_request("/").respond_with_data(
        f'<a href="{link}">external</a>',
        content_type="text/html",
    )

    crawler = Crawler(httpserver.url_for("/"), verbose=False, plugins=["ExternalLinks"])
    (res,) = crawler.asyncio_crawl(save=False)

    expected_data = [{"link": link}]

    assert res.data == expected_data


def test_not_external(httpserver: HTTPServer):
    httpserver.expect_request("/").respond_with_data(
        '<a href="/bob">bob</a>',
        content_type="text/html",
    )

    crawler = Crawler(httpserver.url_for("/"), verbose=False, plugins=["ExternalLinks"])
    (res,) = crawler.asyncio_crawl(save=False)

    assert res.data == []


def test_mixed(httpserver: HTTPServer):
    link = "http://example.com/"
    httpserver.expect_request("/").respond_with_data(
        f'<a href="{link}">external</a><a href="/bob">bob</a>',
        content_type="text/html",
    )

    crawler = Crawler(httpserver.url_for("/"), verbose=False, plugins=["ExternalLinks"])
    (res,) = crawler.asyncio_crawl(save=False)

    expected_data = [{"link": link}]

    assert res.data == expected_data
