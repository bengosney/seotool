# Third Party
import click
from pyppeteer import launch

# First Party
from engines import engine, response


class pyppeteer(engine):
    browser = None

    def __init__(self, crawler, screenshot=False) -> None:
        super().__init__()
        self.crawler = crawler  # type : seotool.Crawler
        self.screenshot = screenshot

    async def get(self, url: str, **kwargs) -> response:
        page = await self.browser.newPage()
        result = await page.goto(url, {"waitUntil": "domcontentloaded"})

        if self.screenshot:
            title = await page.title()
            path = self.crawler.get_output_name(title, "png", "screenshots")
            await page.screenshot({"path": path, "fullPage": True})

        responseObj = response(
            headers=result.headers,
            status_code=result.status,
            url=result.url,
            body=await page.content(),
        )

        await page.close()

        return responseObj

    async def __aenter__(self):
        if self.browser is None:
            self.browser = await launch()

        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.browser is not None:
            await self.browser.close()
            self.browser = None

    @staticmethod
    def get_options():
        return [click.option("--screenshot", is_flag=True, help="Take screen shots of every page (pyppeteer only)")]
