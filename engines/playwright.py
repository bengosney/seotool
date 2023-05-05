# Standard Library
import subprocess

# Third Party
import click
from playwright.async_api import TimeoutError, async_playwright

# First Party
from engines import engine, response
from engines.exceptions import EngineResultFailed, EngineUninitialized
from seotool.exceptions import Timeout


class playwright(engine):
    playwright = None
    browser = None
    timeout = 10_000
    browser_name = "chromium"

    def __init__(self, crawler, screenshot=False, timeout=10_000, browser="chromium") -> None:
        super().__init__()
        self.crawler = crawler  # type : seotool.Crawler
        self.screenshot = screenshot
        self.timeout = timeout
        self.browser_name = browser

    async def __aenter__(self):
        if self.playwright is None:
            self.playwright = await async_playwright().start()

        if self.browser is None:
            self.browser = await self.playwright[self.browser_name].launch()

        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.browser is not None:
            await self.browser.close()
            self.browser = None

        if self.playwright is not None:
            await self.playwright.stop()
            self.playwright = None

    async def get(self, url: str, **kwargs) -> response:
        if self.browser is None:
            raise EngineUninitialized()

        page = await self.browser.new_page()
        try:
            result = await page.goto(url, timeout=self.timeout)
        except TimeoutError as e:
            raise Timeout from e

        if result is None:
            raise EngineResultFailed()

        if self.screenshot:
            title = await page.title()
            path = self.crawler.get_output_name(title, "png", "screenshots")
            await page.screenshot(path=path, full_page=True)

        return response(headers=result.headers, status_code=result.status, url=result.url, body=await page.content())

    @classmethod
    def get_supported_browsers(cls):
        return ["chromium", "chrome", "chrome-beta", "msedge", "msedge-beta", "msedge-dev", "firefox", "webkit"]

    @classmethod
    def get_options(cls):
        def install(ctx, param, value) -> None:
            if value is not None:
                cmd = ["python", "-m", "playwright", "install"]
                if value != "default":
                    cmd.append(value)
                subprocess.run(cmd)

                ctx.exit()

        return [
            click.option("--screenshot", is_flag=True, help="Take screen shots of every page (playwrite only)"),
            click.option("--timeout", type=int, help="Browser timeout"),
            click.option(
                "--playwright-browser",
                type=click.Choice(cls.get_supported_browsers(), case_sensitive=False),
                default="chromium",
                help="Browser for playwright to use",
            ),
            click.option(
                "--playwright-install",
                type=click.Choice(
                    [
                        "default",
                    ]
                    + cls.get_supported_browsers(),
                    case_sensitive=False,
                ),
                callback=install,
                expose_value=False,
                is_eager=True,
                help="Install the browsers for playwright",
            ),
        ]
