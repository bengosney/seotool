# Future
from __future__ import annotations

# Standard Library
import asyncio
import contextlib
import inspect
import multiprocessing
import os
import re
import string
import urllib.parse
from collections import defaultdict, deque
from collections.abc import Callable
from functools import cached_property
from time import time
from urllib.robotparser import RobotFileParser

# Third Party
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
from processors.dataModels import ResultSet
from seotool.exceptions import SkipPage, Timeout
from seotool.queue import Queue

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Crawler:
    def __init__(
        self,
        url: str,
        plugins: list[str] = [],
        verbose: bool = True,
        verify: bool = True,
        disabled=[],
        delay: int = 0,
        engine: str | object = "requests",
        plugin_options={},
        worker_count: int | None = None,
        ignore_robots: bool = False,
    ) -> None:
        self.url = url
        self.verify = verify
        self.plugins = plugins if len(plugins) else None
        self.visited: deque[str] = deque([])
        self.urls: deque[str] = deque([])
        self.all_urls: list[str] = []
        self.resolve_cache: dict[str, str] = {}
        self.disabled = disabled
        self.delay: float = delay
        self.engine = engine
        self.plugin_options = plugin_options

        self.worker_count = worker_count or min(multiprocessing.cpu_count() - 1, 6)

        self.verbose = verbose

        self._init_plugins(plugin_options)

        self._last_request: float = 0
        self.rp = RobotFileParser()
        self.ignore_robots = ignore_robots

        self.fails = defaultdict(lambda: 0)

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

    def _init_plugins(self, plugin_options=None) -> None:
        self.processor: Processor = Processor(self, self.plugins, self.disabled, plugin_options or {})
        self.print(f"Loaded plugins: {', '.join(self.processor.plugin_names)}")

    @property
    def plugin_manager(self):
        return self.processor.plugin_manager

    async def _add_links(self, html_soup: BeautifulSoup) -> None:
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
                await self.queue.put(abs_url)

    def print(self, text: str, style: str | None = None) -> None:
        if self.verbose:
            self.processor.log(text, style=style)

    def printERR(self, text: str) -> None:
        self.processor.log_error(text)

    async def save_results(self) -> None:
        self.print(f"\nSaving results to {self.results_base_path}\n", "green")
        with contextlib.suppress(FileExistsError):
            os.makedirs(self.results_base_path)
        results_store = self.processor.get_results_sets()
        awaits = self.processor.process_results_sets(results_store)

        await asyncio.wait(awaits)

    def get_output_name(self, name: str, extention: str, folder: str = "") -> str:
        path = os.path.join(self.results_base_path, folder)
        with contextlib.suppress(FileExistsError):
            os.makedirs(path)
        return os.path.join(path, f"{self._clean_filename(name)}.{extention}")

    @staticmethod
    def _clean_filename(filename: str) -> str:
        regex_not_special = re.compile(f"[^{string.ascii_letters}{string.digits}_\\-. ]")
        regex_whitespace = re.compile(r"\s+")

        cleaned_filename = regex_not_special.sub(" ", filename)
        return regex_whitespace.sub("-", cleaned_filename[:255]).lower().strip("-")

    async def reset_urls(self) -> None:
        self.urls = deque([self.base_url])
        self.all_urls = [self.base_url]

        self.queue.empty()
        await self.queue.put(self.base_url)

    def parse_robots(self):
        self.print("Fetching robots.txt")
        self.rp.set_url(f"{self.base_url}robots.txt")
        self.rp.read()
        if not self.rp.mtime():
            self.rp.modified()

        if request_rate := self.rp.request_rate("*"):
            self.delay = max(self.delay, (request_rate.seconds / request_rate.requests))

        if crawl_delay := self.rp.crawl_delay("*"):
            self.delay = max(self.delay, float(crawl_delay))

    def can_crawl(self, url: str) -> bool:
        return self.ignore_robots or self.rp.can_fetch("*", url)

    async def crawl(self, save: bool = True) -> list[ResultSet]:
        self._crawling = True

        self.print(f"Crawling with {self.worker_count} workers")

        self.queue = Queue(self.worker_count)

        await self.reset_urls()
        self.parse_robots()
        if not self.can_crawl(self.base_url):
            self.printERR("Robots.txt disallows all")
            return []

        engine = self.engine_instance
        async with engine:
            try:
                await asyncio.gather(*(self._crawl() for _ in range(self.worker_count)))
            except KeyboardInterrupt:
                self.printERR("User Interrupt: Stopping and saving")
                self._crawling = False

        if save:
            await self.save_results()

        return self.processor.get_results_sets()

    def sync_crawl(self, save: bool = True) -> list[ResultSet]:
        return asyncio.run(self.crawl(save))

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
        for entry_point in pkg_resources.iter_entry_points("seo_engines"):
            if self.engine == entry_point.name:
                engine_cls = entry_point.load()
                break
        else:
            raise EngineException(f"Engine not found: {self.engine}")

        args = {"crawler": self, **self.plugin_options}
        sig = inspect.signature(engine_cls)
        supported_prams = [p.name for p in sig.parameters.values()]

        return engine_cls(**{key: value for (key, value) in args.items() if key in supported_prams})

    async def getResponse(self, url: str) -> response:
        engine = self.engine_instance
        try:
            return await engine.get(url, verify=self.verify)
        except (Timeout, TooManyRedirects) as e:
            raise e
        except Exception as ERR:
            raise EngineException() from ERR

    def should_process(self, url: str, response: response) -> bool:
        self.resolve_cache.update({url: response.url})

        should_process = self.processor.should_process(url, response)

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

        return should_process

    async def _delay(self):
        while True:
            ts = time()
            if self.delay <= (ts - self._last_request):
                self._last_request = ts
                return

            await asyncio.sleep(0.25)

    async def _crawl(self) -> None:
        while self._crawling:
            if sorted(self.visited) == sorted(self.urls) and await self.queue.try_stop():
                self._crawling = False
                break

            async with self.queue as q:
                url = await q.get()

            if url is None:
                break

            if url in self.visited:
                continue

            if not self.can_crawl(url):
                continue

            await self._delay()

            self.visited.append(url)
            self.print(f"\n-- Crawling {url}\n")

            try:
                response = await self.getResponse(url)
            except Timeout:
                self.printERR(f"Timeout: {url}")
                if self.fails[url] < 4:
                    self.fails[url] += 1
                    self.visited.remove(url)
                    await self.queue.put(url)
                continue
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
                await self._add_links(html_soup)

            self.processor.process(html_soup, url, response.status_code, response)
