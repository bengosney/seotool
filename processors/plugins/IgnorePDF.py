import mimetypes
import os
from urllib.parse import urlparse

import processors
from seotool.crawl import SkipPage


class IgnorePDF:
    @processors.hookimpl_processor
    def process_html(self, html, response):
        content_type = response.headers["content-type"]
        extension = mimetypes.guess_extension(content_type)

        if extension == "pdf":
            raise SkipPage

        links = html.find_all("a")
        for link in links:
            try:
                href = link["href"]
            except KeyError:
                continue

            path = urlparse(href).path
            ext = os.path.splitext(path)[1]

            if ext == ".pdf":
                link.decompose()

        return html
