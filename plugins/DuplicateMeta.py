class DuplicateMeta:
    def __init__(self, crawler):
        self.metas = {}
        self.crawler = crawler

    def get_results_header(self):
        return ['meta', 'urls']
        
    def get_results(self):
        return [[meta, *urls] for (meta, urls) in self.metas.items() if len(urls) > 1]
        
    def parse(self, html_soup, url=None):
        metas = html_soup.find_all('meta', {"name": "description"})
        
        for metaTag in metas:
            meta = metaTag.attrs['content']
            if meta == "":
                continue
            
            try:
                self.metas[meta].append(url)
                self.crawler.printERR(f"Meta Description already seen on {', '.join(self.metas[meta])}")
            except KeyError:
                self.metas.update({meta: [url]})