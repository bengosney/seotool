import urllib.parse


class ExternalLinksPerPage:
    def __init__(self, crawler):
        self.crawler = crawler
        self.links = {}

    def get_results_header(self):
        return ["src", "dest", "pages"]

    def get_results(self):
        return [[url] + links for (url, links) in self.links.items()]

    def parse(self, html_soup, url=None):
        links = html_soup.find_all("a")
        urls = []
        parsed_base = urllib.parse.urlparse(self.crawler.base_url)

        for link in links:
            try:
                full_url = urllib.parse.urljoin(self.crawler.base_url, link["href"])
            except KeyError:
                continue
            
            parsed_url = urllib.parse.urlparse(full_url)
            if parsed_url.netloc != parsed_base.netloc:
                urls.append(full_url)

        self.links.update({url: urls})
