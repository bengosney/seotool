class DuplicateTitle:
    def __init__(self, crawler):
        self.titles = {}
        self.crawler = crawler

    def get_results_header(self):
        return ["title", "urls"]

    def get_results(self):
        return [[title, *urls] for (title, urls) in self.titles.items() if len(urls) > 1]

    def parse(self, html_soup, url=None):
        titles = html_soup.find_all("title")

        canonicals = html_soup.find_all("link", {"rel": "canonical"})
        if len(canonicals) > 0:
            try:
                url = canonicals[0]["href"]
            except KeyError:
                pass

        for titleTag in titles:
            title = titleTag.getText()
            try:
                self.titles[title].append(url)
                self.titles[title] = list(set(self.titles[title]))
                self.crawler.printERR(f"Title already seen on {', '.join(self.titles[title])}")
            except KeyError:
                self.titles.update({title: [url]})
