# Third Party
import click
from pyppeteer import launch

# First Party
from engines import engine, response
import asyncio
from playwright.async_api import async_playwright
from playwright.async_api._context_manager import PlaywrightContextManager
from playwright.sync_api import sync_playwright

from icecream import ic

class playwright(engine):
    playwright = None
    browser = None

    def __init__(self, crawler, screenshot=False) -> None:
        super().__init__()
        self.crawler = crawler  # type : seotool.Crawler
        self.screenshot = screenshot

    async def __aenter__(self):
        if self.playwright is None:
            self.playwright = await async_playwright().start()

        if self.browser is None:
            self.browser = await self.playwright.chromium.launch()

        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.browser is not None:
            await self.browser.close()
            self.browser = None

        if self.playwright is not None:
            await self.playwright.stop()
            self.playwright = None

    async def get(self, url: str, **kwargs) -> response:
        page = await self.browser.new_page()
        result = await page.goto(url)

        return response(headers=result.headers, status_code=result.status, url=result.url, body=await page.content())