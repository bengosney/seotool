# Future
from __future__ import annotations

# Standard Library
import asyncio
import inspect
import os
import re
import string
import urllib.parse
from collections import deque
from functools import cached_property
from typing import Callable

# Third Party
import click
import pkg_resources
import urllib3
from bs4 import BeautifulSoup
from requests import head
from requests.exceptions import MissingSchema, TooManyRedirects

# First Party
from engines import EngineException
from engines.dataModels import response
from engines.engines import engine
from processors import Processor
from seotool.exceptions import SkipPage

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Crawler:
    def __init__(self, url: str, plugins=[], verbose=True, verify=True, disabled=[], delay=0, engine="pyppeteer", plugin_options={}) -> None:
        self.url = url
        self.verify = verify
        self.plugins = plugins if len(plugins) else None
        self.visited: deque[str] = deque([])
        self.urls: deque[str] = deque([])
        self.all_urls: list[str] = []
        self.resolve_cache: dict[str, str] = {}
        self.disabled = disabled
        self.delay = delay
        self.engine = engine
        self.plugin_options = plugin_options

        self.verbose = verbose

        self._init_plugins(plugin_options)

    @cached_property
    def base_url(self) -> str:
        try:
            return head(self.url, verify=self.verify).url
        except MissingSchema:
            self.url = f"https://{self.url}"
        finally:
            return head(self.url, verify=self.verify).url

    @cached_property
    def base_netloc(self) -> str:
        return urllib.parse.urlparse(self.base_url).netloc

    @cached_property
    def results_base_path(self) -> str:
        return os.path.join(os.getcwd(), f"results-{self.base_netloc}")

    @staticmethod
    def get_plugin_list() -> list[str]:
        p = Processor(None)
        return p.plugin_names

    @staticmethod
    def get_plugin_options() -> list[list[Callable]]:
        p = Processor(None)
        return p.get_options()

    @classmethod
    def get_extra_options(cls) -> list[list[Callable]]:
        return cls.get_plugin_options() + [cls.get_engine_options()]

    def skip_page(self) -> None:
        raise SkipPage

    def _init_plugins(self, plugin_options={}) -> None:
        self.processor = Processor(self, self.plugins, self.disabled, plugin_options)
        self.print(f"Loaded plugins: {', '.join(self.processor.plugin_names)}")

    def _add_links(self, html_soup) -> None:
        links = html_soup.find_all("a")
        for link in links:
            try:
                abs_url = urllib.parse.urljoin(self.base_url, link["href"]).split("#")[0].split("?")[0]
            except KeyError:
                continue

            if urllib.parse.urlparse(abs_url).netloc != self.base_netloc:
                continue

            if abs_url in self.resolve_cache:
                abs_url = self.resolve_cache[abs_url]

            if abs_url not in self.all_urls:
                self.urls.append(abs_url)
                self.all_urls.append(abs_url)

    def print(self, text, color="white") -> None:
        if self.verbose:
            click.secho(text, fg=color)

    def printERR(self, text) -> None:
        self.print(text, "red")

    def save_results(self) -> None:
        self.print(f"\nSaving results to {self.results_base_path}\n", "green")

        try:
            os.makedirs(self.results_base_path)
        except FileExistsError:
            pass

        results_store = self.processor.get_results_sets()
        self.processor.process_results_sets(results_store)

    def get_output_name(self, name: str, extention: str, folder: str = "") -> str:
        path = os.path.join(self.results_base_path, folder)
        try:
            os.makedirs(path)
        except FileExistsError:
            pass

        return os.path.join(path, f"{self._clean_filename(name)}.{extention}")

    @staticmethod
    def _clean_filename(filename) -> str:
        regex_not_special = re.compile(f"[^{string.ascii_letters}{string.digits}_\\-. ]")
        regex_whitespace = re.compile(r"\s+")

        cleaned_filename = regex_not_special.sub(" ", filename)
        return regex_whitespace.sub("-", cleaned_filename[:255]).lower().strip("-")

    def reset_urls(self) -> None:
        self.urls = deque([self.base_url])
        self.all_urls = [self.base_url]

    async def crawl(self) -> None:
        self._crawling = True
        self.reset_urls()

        engine = self.engine_instance
        async with engine:
            try:
                await self._crawl()
            except KeyboardInterrupt:
                self.printERR("User Interrupt: Stopping and saving")
                self._crawling = False

        self.save_results()

    @staticmethod
    def get_engine_options() -> list[Callable]:
        options = []
        for entry_point in pkg_resources.iter_entry_points("seo_engines"):
            engine_cls = entry_point.load()
            options += engine_cls.get_options()

        return options

    @cached_property
    def engine_instance(self) -> engine:
        self.print(f"Attempting to load {self.engine}")
        engine_cls = None
        for entry_point in pkg_resources.iter_entry_points("seo_engines"):
            if self.engine == entry_point.name:
                engine_cls = entry_point.load()

        if engine_cls is None:
            raise EngineException(f"Engine not found: {self.engine}")

        args = {"crawler": self, **self.plugin_options}
        sig = inspect.signature(engine_cls)
        supported_prams = [p.name for p in sig.parameters.values()]

        return engine_cls(**{key: value for (key, value) in args.items() if key in supported_prams})

    async def getResponse(self, url) -> response:
        engine = self.engine_instance
        try:
            return await engine.get(url, verify=self.verify)
        except Exception as ERR:
            raise EngineException() from ERR

    def should_process(self, url, response) -> bool:
        self.resolve_cache.update({url: response.url})
        if url != response.url and response.url in self.visited:
            self.print(f"{url} resolves to {response.url} and has already been visited", "yellow")
            return False

        try:
            content_type = response.headers["content-type"].split(";")[0]
        except KeyError:
            content_type = None
        if content_type != "text/html":
            self.print(f"{content_type} is not crawlable", "yellow")
            return False

        return True

    async def _crawl(self) -> None:
        while self._crawling:
            if self.delay:
                await asyncio.sleep(self.delay)

            try:
                url = self.urls.pop()
            except IndexError:
                break

            if url in self.visited:
                continue

            self.visited.append(url)
            self.print(f"\n-- Crawling {url}\n")

            try:
                response = await self.getResponse(url)
            except TooManyRedirects:
                self.printERR("Too many redirects, skipping")
                continue

            if not self.should_process(url, response):
                continue

            html_soup = BeautifulSoup(response.body, "html.parser")

            try:
                self.processor.process_html(html_soup, url, response.status_code, response)
            except SkipPage:
                continue
            finally:
                self._add_links(html_soup)

            self.processor.process(html_soup, url, response.status_code, response)
