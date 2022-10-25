# Third Party
from pytest_httpserver import HTTPServer

# First Party
from processors.plugins.ImageErrors import ResultData
from seotool.crawl import Crawler


def test_image_error(httpserver: HTTPServer):
    img = "http://example.com/external.png"
    httpserver.expect_request("/").respond_with_data(
        f'<img src="{img}" />',
        content_type="text/html",
    )

    crawler = Crawler(httpserver.url_for("/"), verbose=False, plugins=["ImageErrors"])
    (res,) = crawler.asyncio_crawl(save=False)

    expected_data = [ResultData(img, "404", [httpserver.url_for("/")])]

    assert res.data == expected_data


def test_image_ok(httpserver: HTTPServer):
    img = "https://crawler-test.com/image_link.png"
    httpserver.expect_request("/").respond_with_data(
        f'<img src="{img}" />',
        content_type="text/html",
    )

    crawler = Crawler(httpserver.url_for("/"), verbose=False, plugins=["ImageErrors"])
    (res,) = crawler.asyncio_crawl(save=False)

    expected_data = []

    assert res.data == expected_data


def test_image_mixed(httpserver: HTTPServer):
    img_bad = "http://example.com/external.png"
    img_ok = "https://crawler-test.com/image_link.png"
    httpserver.expect_request("/").respond_with_data(
        f'<img src="{img_ok}" /><img src="{img_bad}" />',
        content_type="text/html",
    )

    crawler = Crawler(httpserver.url_for("/"), verbose=False, plugins=["ImageErrors"])
    (res,) = crawler.asyncio_crawl(save=False)

    expected_data = [ResultData(img_bad, "404", [httpserver.url_for("/")])]

    assert res.data == expected_data
