# First Party
from processors import ResultSet, hookimpl_processor


class MissingMeta:
    """Metatags give search engins a better idea of what the page is about"""

    def __init__(self, crawler):
        self.missing_metas = []
        self.crawler = crawler

    @hookimpl_processor
    def get_results_set(self):
        data = [{"url": v} for v in self.missing_metas]
        return ResultSet("Missing metatags's", f"{self.__doc__}", data)

    @hookimpl_processor
    def process(self, html, url):
        metas = html.find_all("meta", {"name": "description"})

        if len(metas) == 0:
            self.missing_metas.append(url)
            self.crawler.printERR(f"Found no H1 on {url}")
