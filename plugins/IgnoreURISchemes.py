import mimetypes
from urllib.parse import urlparse
import os


class IgnoreURISchemes:
    def __init__(self, crawler):
        self.crawler = crawler

    def process_html(self, html, response):
        links = html.find_all("a")
        for link in links:
            try:
                href = link["href"]
            except KeyError:
                continue

            if href.lower().startswith(('tel:', 'mailto:')):
                link.decompose()

        return html
