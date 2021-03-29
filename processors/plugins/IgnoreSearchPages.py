import processors


class IgnoreSearchPages:
    @processors.hookimpl_processor
    def process_html(self, html):
        links = html.find_all("a")
        for link in links:
            try:
                href = link["href"]
            except KeyError:
                continue

            if "/search/" in href:
                link.decompose()
