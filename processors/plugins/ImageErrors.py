# Standard Library
import urllib.parse
from collections import defaultdict
from dataclasses import dataclass

# Third Party
import requests

# First Party
from processors import BaseResultData, ResultSet, hookimpl_processor


@dataclass
class ResultData(BaseResultData):
    image: str
    status_codes: str
    urls: list[str]


@dataclass
class ImageError:
    url: str
    path: str
    status_code: int


class ImageErrorException(Exception):
    status_code: int
    path: str

    def __init__(self, path: str, status_code: int, *args: object) -> None:
        super().__init__(f"{path} has status code {status_code}", *args)
        self.status_code = status_code
        self.path = path


class ImageErrors:
    """List of dead image links."""

    default_disabled = False

    def __init__(self, crawler):
        self.crawler = crawler
        self.images: list[ImageError] = []
        self.errors: dict[str, int] = {}

    @hookimpl_processor
    def get_results_set(self):

        errors: dict[str, list[str]] = defaultdict(lambda: set())
        status: dict[str, set[int]] = defaultdict(lambda: set())

        for image in self.images:
            errors[image.path].add(image.url)
            status[image.path].add(image.status_code)

        data: list[ResultData] = [
            ResultData(
                image,
                status_codes=", ".join(map(str, status[image])),
                urls=list(value),
            )
            for image, value in errors.items()
        ]

        return ResultSet("Image Errors", f"{self.__doc__}", data)

    @hookimpl_processor
    def process(self, html, url):
        images = html.find_all("img")
        base_url_parts = urllib.parse.urlparse(self.crawler.base_url)

        for image in images:
            try:
                image_parts = urllib.parse.urlparse(image["src"])
                if missing_parts := {
                    field: getattr(base_url_parts, field)
                    for field in image_parts._fields
                    if getattr(image_parts, field) == ""
                }:
                    image_parts._replace(**missing_parts)

                image_path = urllib.parse.urlunparse(image_parts)
                request = requests.head(image_path)
                if request.status_code < 200 or request.status_code > 299:
                    raise ImageErrorException(image_path, request.status_code)
            except ImageErrorException as e:
                self.crawler.printERR(f"Image error: {e}")
                self.images.append(ImageError(url, e.path, e.status_code))
