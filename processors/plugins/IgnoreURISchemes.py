import processors


class IgnoreURISchemes:
    @processors.hookimpl_processor
    def process_html(self, html, response):
        links = html.find_all("a")
        for link in links:
            try:
                href = link["href"]
            except KeyError:
                continue

            if href.lower().startswith(("tel:", "mailto:")):
                link.decompose()

        return html
