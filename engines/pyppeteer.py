
from pyppeteer import launch

from engines import engine, response


class pyppeteer(engine):
    async def get(self, url: str, **kwargs):
        browser = await launch()
        page = await browser.newPage()
        result = await page.goto(url, {"waitUntil": "domcontentloaded"})
        # await page.screenshot({'path': 'example.png'})

        responseObj = response(
            headers=result.headers,
            status_code=result.status,
            url=result.url,
            body=await page.content(),
        )

        await browser.close()

        return responseObj
