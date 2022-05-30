import click
from playwright.async_api import async_playwright

# First Party
from engines import engine, response

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

        if self.screenshot:
            title = await page.title()
            path = self.crawler.get_output_name(title, "png", "screenshots")
            await page.screenshot(path=path, full_page=True)

        return response(headers=result.headers, status_code=result.status, url=result.url, body=await page.content())

    @staticmethod
    def get_options():
        return [click.option("--screenshot", is_flag=True, help="Take screen shots of every page (playwrite only)")]