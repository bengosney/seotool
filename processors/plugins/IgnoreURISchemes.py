# Standard Library
from urllib.parse import urlparse

# First Party
import processors


class IgnoreURISchemes:
    @processors.hookimpl_processor
    def process_html(self, html, response):
        links = html.find_all("a")
        for link in links:
            try:
                href = link["href"].lower()
            except KeyError:
                continue

            parts = urlparse(href)
            if parts.scheme not in ["", "http", "https"]:
                link.decompose()

            if href.startswith(("tel:", "mailto:")):
                link.decompose()

        return html
