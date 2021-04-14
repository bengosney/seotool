# Third Party
import pytest
from pytest_httpserver import HTTPServer

# First Party
from seotool.crawl import Crawler
from seotool.exceptions import SkipPage


def test_clean_name_no_change():
    name = "bob"
    cleaned_name = Crawler._clean_filename(name)
    assert name == cleaned_name


def test_clean_name_changes():
    name = "-bOb:: '#' ::dOd-"
    cleaned_name = Crawler._clean_filename(name)
    assert cleaned_name == "bob-dod"


def test_skip_page():
    c = Crawler("example.com")
    with pytest.raises(SkipPage):
        c.skip_page()


def test_can_crawl(httpserver: HTTPServer):
    httpserver.expect_request("/page2").respond_with_data("<h1>page2</h1>", content_type="text/html")
    page2_url = httpserver.url_for("/page2")
    httpserver.expect_request("/").respond_with_data(f'<a href="{page2_url}">page 2</a>', content_type="text/html")

    crawler = Crawler(httpserver.url_for("/"), verbose=False)
    crawler.asyncio_crawl(save=False)

    assert len(crawler.all_urls) == 2
    assert page2_url in crawler.all_urls


def test_runs_plugin(httpserver: HTTPServer):
    httpserver.expect_request("/").respond_with_data("<h1>page2</h1>", content_type="text/html")

    crawler = Crawler(httpserver.url_for("/"), verbose=False, plugins=["MultipleH1", "MissingH1"])
    results = crawler.asyncio_crawl(save=False)

    assert len(results) == 2
