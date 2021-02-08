class scriptTags:
    def __init__(self, crawler):
        self.scriptTags = []
        self.crawler = crawler

    def get_results_header(self):
        return ["src", "url"]

    def get_results(self):
        return self.scriptTags

    def parse(self, html_soup, url=None):
        scriptTags = html_soup.find_all("script")

        for scriptTag in scriptTags:
            try:
                self.scriptTags.append([url, scriptTag["src"]])
            except KeyError:
                pass
