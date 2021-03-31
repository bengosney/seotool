# First Party
from processors import ResultSet, hookimpl_processor


class DuplicateH1:
    """Duplicate H1."""

    def __init__(self, crawler):
        self.h1s = {}
        self.crawler = crawler

    @hookimpl_processor
    def get_results_set(self):
        data = [{"h1": h1, "url": sorted(urls)} for (h1, urls) in self.h1s.items() if len(urls) > 1]

        return ResultSet("Duplicate H1's", f"{self.__doc__}", data)

    @hookimpl_processor
    def process(self, html, url):
        h1s = html.find_all("h1")
        canonicals = html.find_all("link", {"rel": "canonical"})
        if len(canonicals) > 0:
            try:
                url = canonicals[0]["href"]
            except KeyError:
                pass

        for h1Tag in h1s:
            h1 = h1Tag.getText()
            try:
                self.h1s[h1].append(url)
                self.h1s[h1] = list(set(self.h1s[h1]))
                self.crawler.printERR(f"H1 already seen on {', '.join(self.h1s[h1])}")
            except KeyError:
                self.h1s.update({h1: [url]})
