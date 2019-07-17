class MissingMeta:
    def __init__(self, crawler):
        self.missing_metas = []
        self.crawler = crawler

    def get_results_header(self):
        return ["url"]

    def get_results(self):
        return self.missing_metas

    def parse(self, html_soup, url=None):
        metas = html_soup.find_all("meta", {"name": "description"})

        if len(metas) == 0:
            self.missing_metas.append([url])
            self.crawler.printERR(f"Found no Meta Description on {url}")
