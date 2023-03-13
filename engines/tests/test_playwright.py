# Standard Library
from time import sleep

# Third Party
import pytest
from pytest_httpserver import HTTPServer
from werkzeug.wrappers import Request, Response

# First Party
from engines.playwright import playwright
from seotool.crawl import Crawler


@pytest.mark.asyncio
async def test_timeout(httpserver: HTTPServer):
    def slow_response(_: Request) -> Response:
        sleep(10)
        return Response()

    httpserver.expect_request("/").respond_with_handler(slow_response)
    crawler = Crawler(httpserver.url_for("/"), verbose=False)

    engine = playwright(crawler, timeout=1)

    async with engine:
        await engine.get(httpserver.url_for("/"))
