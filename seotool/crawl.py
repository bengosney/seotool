import asyncio
import csv
import inspect
import os
import urllib.parse
from collections import deque

import click
import urllib3
from bs4 import BeautifulSoup
from requests import head
from requests.exceptions import TooManyRedirects

import engines
import plugins
from engines import EngineException
from plugins import *  # noqa

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SkipPage(Exception):
    pass


class Crawler:
    def __init__(self, url, plugins=[], verbose=True, verify=True, disabled=[], delay=0, engine="pyppeteer"):
        self.verify = verify
        self.base_url = head(url, verify=verify).url
        self.plugins = plugins
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

        pluginList = []
        pluginPreList = []
        pluginPostList = []

        self.print("Loading plugins...")

        if len(self.plugins) == 0:
            self.plugins = self.get_plugin_list()

        for pluginName in [p for p in self.plugins if p not in self.disabled]:
            _module = getattr(plugins, pluginName)
            _class = getattr(_module, pluginName)
            instance = _class(self)

            if all(hasattr(instance, func) for func in ["get_results_header", "get_results", "parse"]):
                self.plugin_classes.append(instance)
                pluginList.append(pluginName)

            if all(hasattr(instance, func) for func in ["process_html"]):
                self.plugin_pre_classes.append(instance)
                pluginPreList.append(pluginName)

            if all(hasattr(instance, func) for func in ["process_results"]):
                self.plugin_post_classes.append(instance)
                pluginPostList.append(pluginName)

        if len(pluginPreList):
            self.print(f"Loaded pre processing plugins: {', '.join(pluginPreList)}")

        if pluginList:
            self.print(f"Loaded parsing plugins: {', '.join(pluginList)}")
        else:
            self.print("Error no plugins loaded")
            exit(0)

        if len(pluginPostList):
            self.print(f"Loaded results processing plugins: {', '.join(pluginPostList)}")

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

        results_store = {}

        for plugin in self.plugin_classes:
            plugin_name = plugin.__class__.__name__
            path = os.path.join(self.results_base_path, f"{plugin_name}.csv")

            try:
                results = plugin.get_results()
                results_header = plugin.get_results_header()

                results_store.update({plugin_name: [results_header] + results})
                with open(path, "w") as f:
                    w = csv.writer(f)
                    w.writerow(results_header)
                    if results is not None and len(results):
                        w.writerows(results)
            except Exception as ERR:
                self.printERR(f"Uncaught error saving output of {plugin.__class__.__name__}\n {ERR}")
                continue

        for plugin in self.plugin_post_classes:
            self.print(f"Processing results with {plugin.__class__.__name__}")
            plugin.process_results(results_store)

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

        try:
            content_type = response.headers["content-type"].split(";")[0]
        except KeyError:
            content_type = None
        if content_type != "text/html":
            self.print(f"{content_type} is not crawlable", "yellow")
            return False

        return True

    def pre_process(self, html, args):
        for plugin in self.plugin_pre_classes:
            try:
                supported_prams = plugin.supported_prams
            except AttributeError:
                sig = inspect.signature(plugin.process_html)
                supported_prams = [p.name for p in sig.parameters.values()]
                plugin.supported_prams = supported_prams

            html = plugin.process_html(
                html,
                **{key: value for (key, value) in args.items() if key in supported_prams},
            )

        return html

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
            args = {
                "status_code": response.status_code,
                "url": url,
                "response": response,
            }

            try:
                html_soup = self.pre_process(html_soup, args)
            except SkipPage:
                continue

            self._add_links(html_soup)

            for plugin in self.plugin_classes:
                try:
                    supported_prams = plugin.supported_prams
                except AttributeError:
                    sig = inspect.signature(plugin.parse)
                    supported_prams = [p.name for p in sig.parameters.values()]
                    plugin.supported_prams = supported_prams

                plugin.parse(html_soup, **{key: value for (key, value) in args.items() if key in supported_prams})
