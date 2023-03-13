# Standard Library
from time import sleep

# Third Party
import pytest
from pytest_httpserver import HTTPServer
from werkzeug.wrappers import Request, Response

# First Party
from engines.playwright import playwright
from seotool.crawl import Crawler
from seotool.exceptions import Timeout


@pytest.mark.asyncio
async def test_timeout(httpserver: HTTPServer):
    def slow_response(_: Request) -> Response:
        sleep(10)
        return Response()

    httpserver.expect_request("/").respond_with_handler(slow_response)
    crawler = Crawler(httpserver.url_for("/"), verbose=False)

    engine = playwright(crawler, timeout=1)

    with pytest.raises(Timeout):
        async with engine:
            await engine.get(httpserver.url_for("/"))


@pytest.mark.asyncio
async def test_no_timeout(httpserver: HTTPServer):
    def quick_response(_: Request) -> Response:
        return Response()

    httpserver.expect_request("/").respond_with_handler(quick_response)
    crawler = Crawler(httpserver.url_for("/"), verbose=False)

    engine = playwright(crawler)

    try:
        async with engine:
            await engine.get(httpserver.url_for("/"))
    except Timeout as e:
        assert False, f"Engine timed out {e}"
