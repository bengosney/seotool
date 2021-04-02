# First Party
from processors import ResultSet, hookimpl_processor


class ScriptTags:
    """Script tags used in the site."""

    def __init__(self, crawler):
        self.scriptTags = []
        self.crawler = crawler

    @hookimpl_processor
    def get_results_set(self):
        data = [{"src": src, "url": url} for (url, src) in self.scriptTags]
        return ResultSet("Script tags", f"{self.__doc__}", data)

    @hookimpl_processor
    def process(self, html, url):
        scriptTags = html.find_all("script")

        for scriptTag in scriptTags:
            try:
                self.scriptTags.append([url, scriptTag["src"]])
            except KeyError:
                pass
