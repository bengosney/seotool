import mimetypes
from urllib.parse import urlparse
import os


class IgnorePDF:
    def __init__(self, crawler):
        self.crawler = crawler

    def process_html(self, html, response):
        content_type = response.headers["content-type"]
        extension = mimetypes.guess_extension(content_type)

        if extension == "pdf":
            self.crawler.skip_page()

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
