# First Party
from processors import ResultSet, hookimpl_processor


class DuplicateMeta:
    """Duplicate Metadata."""

    def __init__(self, crawler):
        self.metas = {}
        self.crawler = crawler

    @hookimpl_processor
    def get_results_set(self):
        data = [{"meta": meta, "urls": sorted(urls)} for (meta, urls) in self.metas.items() if len(urls) > 1]

        return ResultSet("Duplicate Metadata", f"{self.__doc__}", data)

    @hookimpl_processor
    def process(self, html, url):
        metas = html.find_all("meta", {"name": "description"})
        canonicals = html.find_all("link", {"rel": "canonical"})
        if len(canonicals) > 0:
            try:
                url = canonicals[0]["href"]
            except KeyError:
                pass

        for metaTag in metas:
            meta = metaTag.attrs["content"]
            if meta == "":
                continue

            try:
                self.metas[meta].append(url)
                self.metas[meta] = list(set(self.metas[meta]))
                self.crawler.printERR(f"Meta Description already seen on {', '.join(self.metas[meta])}")
            except KeyError:
                self.metas.update({meta: [url]})
