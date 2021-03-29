# First Party
from processors import ResultSet, hookimpl_processor


class MultipleH1:
    """Multiple H1's confuse search engines and screen readers"""

    def __init__(self, crawler):
        self.multiple_h1s = []
        self.crawler = crawler

    @hookimpl_processor
    def get_results_set(self):
        return ResultSet("Multiple H1's", f"{self.__doc__}", self.multiple_h1s)

    @hookimpl_processor
    def process(self, html, url):
        h1s = html.find_all("h1")

        count = len(h1s)
        if count > 1:
            h1s = [h1.getText() for h1 in h1s]
            self.multiple_h1s.append({"url": url, "h1s": h1s})
            self.crawler.printERR(f"Found {count} H1s on {url}")
