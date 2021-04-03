# First Party
from processors import ResultSet, hookimpl_processor


class MissingH1:
    """H1's give users and search engins a good idea of what the page is
    about."""

    def __init__(self, crawler):
        self.missing_h1s = []
        self.crawler = crawler

    @hookimpl_processor
    def get_results_set(self):
        data = [{"url": v} for v in self.missing_h1s]
        return ResultSet("Missing H1's", f"{self.__doc__}", data)

    @hookimpl_processor
    def process(self, html, url):
        h1s = html.find_all("h1")

        if len([h1 for h1 in h1s if h1.getText() != ""]) == 0:
            self.missing_h1s.append(url)
            self.crawler.printERR(f"Found no H1 on {url}")
