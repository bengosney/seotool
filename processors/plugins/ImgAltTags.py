# First Party
from processors import ResultSet, hookimpl_processor


class ImgAltTags:
    """Images missing alt tags."""

    def __init__(self, crawler):
        self.missing_alts = []
        self.crawler = crawler

    @hookimpl_processor
    def get_results_set(self):
        return ResultSet("Images missing alt tags", f"{self.__doc__}", self.missing_alts)

    @hookimpl_processor
    def process(self, html, url):
        images = html.find_all("img")

        for image in images:
            try:
                image["alt"]
            except KeyError:
                try:
                    output = image["src"]
                except KeyError:
                    output = str(image)

                self.missing_alts.append({"url": url, "src": output})
                self.crawler.printERR(f"Found missing alt tag for {output}")
