# Third Party
from pytest_httpserver import HTTPServer

# First Party
from seotool.crawl import Crawler


def test_duplicates(httpserver: HTTPServer):
    httpserver.expect_request("/page2").respond_with_data("<h1>page1</h1>", content_type="text/html")
    page2_url = httpserver.url_for("/page2")
    httpserver.expect_request("/").respond_with_data(f'<h1>page1</h1><a href="{page2_url}">page 2</a>', content_type="text/html")

    crawler = Crawler(httpserver.url_for("/"), verbose=False, plugins=["DuplicateH1"])
    (res,) = crawler.asyncio_crawl(save=False)

    expected_data = [{"h1": "page1", "urls": sorted([httpserver.url_for("/"), httpserver.url_for("/page2")])}]

    assert res.data == expected_data


def test_no_duplicates(httpserver: HTTPServer):
    httpserver.expect_request("/page2").respond_with_data("<h1>page2</h1>", content_type="text/html")
    page2_url = httpserver.url_for("/page2")
    httpserver.expect_request("/").respond_with_data(f'<h1>page1</h1><a href="{page2_url}">page 2</a>', content_type="text/html")

    crawler = Crawler(httpserver.url_for("/"), verbose=False, plugins=["DuplicateH1"])
    res = crawler.asyncio_crawl(save=False)[0]

    assert res.data == []
