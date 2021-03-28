import asyncio
import os
import urllib.parse
from collections import deque

import click
import urllib3
from bs4 import BeautifulSoup
from requests import head
from requests.exceptions import TooManyRedirects

import engines
from engines import EngineException
from processors import Processor

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SkipPage(Exception):
    pass


class Crawler:
    def __init__(self, url, plugins=[], verbose=True, verify=True, disabled=[], delay=0, engine="pyppeteer"):
        self.verify = verify
        self.base_url = head(url, verify=verify).url
        self.plugins = plugins if len(plugins) else None
        self.plugin_classes = []
        self.plugin_pre_classes = []
        self.plugin_post_classes = []
        self.visited = deque([])
        self.urls = deque([self.base_url])
        self.all_urls = [self.base_url]
        self.resolve_cache = {}
        self.disabled = disabled
        self.delay = delay
        self.engine = engine

        self.verbose = verbose

        self._init_plugins()

        if self.base_url != url:
            self.print(f"\nBase URL {url} resolved to {self.base_url}\n", "yellow")

        self.base_netloc = urllib.parse.urlparse(self.base_url).netloc
        self.results_base_path = os.path.join(os.getcwd(), f"results-{self.base_netloc}")

        self.engine_instance = None

    @staticmethod
    def get_plugin_dir():
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "plugins")

    @staticmethod
    def get_plugin_list():
        allFiles = os.listdir(Crawler.get_plugin_dir())

        return [f[:-3] for f in allFiles if f[-3:] == ".py" and f[0] != "_"]

    def skip_page(self):
        raise SkipPage

    def _init_plugins(self):
        self.processor = Processor(self, self.plugins, self.disabled)
        self.print(f"Loaded plugins: {', '.join(self.processor.plugin_names)}")

    def _add_links(self, html_soup):
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

    def print(self, text, color="white"):
        if self.verbose:
            click.secho(text, fg=color)

    def printERR(self, text):
        self.print(text, "red")

    def save_results(self):
        self.print(f"\nSaving results to {self.results_base_path}\n", "green")

        try:
            os.makedirs(self.results_base_path)
        except FileExistsError:
            pass

        results_store = self.processor.get_results_sets()
        self.processor.process_results_sets(results_store)

    async def crawl(self):
        self._crawling = True

        engine = await self.getEngine()
        async with engine:
            try:
                await self._crawl()
            except KeyboardInterrupt:
                self.printERR("User Interrupt: Stopping and saving")
                self._crawling = False

        self.save_results()

    async def getEngine(self):
        if self.engine_instance is None:
            engine_cls = getattr(engines, self.engine)
            self.engine_instance = engine_cls()

        return self.engine_instance

    async def getResponse(self, url):
        engine = await self.getEngine()
        try:
            return await engine.get(url, verify=self.verify)
        except Exception as ERR:
            raise EngineException() from ERR

    def should_process(self, url, response):
        self.resolve_cache.update({url: response.url})
        if url != response.url and response.url in self.visited:
            self.print(f"{url} resolves to {response.url} and has already been visited", "yellow")
            return False

        content_type = response.headers["content-type"].split(";")[0]
        if content_type != "text/html":
            self.print(f"{content_type} is not crawlable", "yellow")
            return False

        return True

    async def _crawl(self):

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
