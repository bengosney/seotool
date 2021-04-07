# First Party
from processors import ResultSet, hookimpl_processor


class MissingMeta:
    """Meta descriptions give search engins a synopsys of the page."""

    def __init__(self, crawler):
        self.missing_metas = []
        self.crawler = crawler

    @hookimpl_processor
    def get_results_set(self):
        data = [{"url": v} for v in self.missing_metas]
        return ResultSet("Missing meta descriptions", f"{self.__doc__}", data)

    @hookimpl_processor
    def process(self, html, url):
        metas = html.find_all("meta", {"name": "description"})

        if len([meta for meta in metas if meta["content"] != ""]) == 0:
            self.missing_metas.append(url)
            self.crawler.printERR(f"Found no meta description on {url}")
