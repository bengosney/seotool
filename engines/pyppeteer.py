from pyppeteer import launch

from engines import engine, response


class pyppeteer(engine):
    browser = None

    async def get(self, url: str, **kwargs):
        page = await self.browser.newPage()
        result = await page.goto(url, {"waitUntil": "domcontentloaded"})
        # await page.screenshot({'path': 'example.png'})

        responseObj = response(
            headers=result.headers,
            status_code=result.status,
            url=result.url,
            body=await page.content(),
        )

        return responseObj

    async def __aenter__(self):
        if self.browser is None:
            self.browser = await launch()

        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.browser is not None:
            await self.browser.close()
            self.browser = None
