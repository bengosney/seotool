# Third Party
import lorem
from pytest_httpserver import HTTPServer

# First Party
from processors.plugins.DuplicateContent import ResultData
from seotool.crawl import Crawler


def test_duplicates(httpserver: HTTPServer):
    content = lorem.paragraph()

    httpserver.expect_request("/page2").respond_with_data(f"<p>{content}</p>", content_type="text/html")
    page2_link = f'<a href="{httpserver.url_for("/page2")}">page 2</a>'
    httpserver.expect_request("/page3").respond_with_data(f"<p>{content}</p>", content_type="text/html")
    page3_link = f'<a href="{httpserver.url_for("/page3")}">page 3</a>'

    httpserver.expect_request("/").respond_with_data(f"{page2_link}{page3_link}", content_type="text/html")

    crawler = Crawler(httpserver.url_for("/"), verbose=False, plugins=["DuplicateContent"])
    (res,) = crawler.sync_crawl(save=False)

    expected_data = [ResultData(content, sorted([httpserver.url_for("/page2"), httpserver.url_for("/page3")]))]

    assert res.data == expected_data


def test_no_duplicates(httpserver: HTTPServer):
    httpserver.expect_request("/page2").respond_with_data(f"<p>{lorem.paragraph()}</p>", content_type="text/html")
    page2_link = f'<a href="{httpserver.url_for("/page2")}">page 2</a>'
    httpserver.expect_request("/page3").respond_with_data(f"<p>{lorem.paragraph()}</p>", content_type="text/html")
    page3_link = f'<a href="{httpserver.url_for("/page3")}">page 3</a>'

    httpserver.expect_request("/").respond_with_data(f"{page2_link}{page3_link}", content_type="text/html")

    crawler = Crawler(httpserver.url_for("/"), verbose=False, plugins=["DuplicateContent"])
    (res,) = crawler.sync_crawl(save=False)

    expected_data = []

    assert res.data == expected_data
