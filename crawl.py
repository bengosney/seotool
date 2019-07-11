#!/usr/bin/env python3

from requests import get, head
from requests.exceptions import TooManyRedirects
from bs4 import BeautifulSoup
from collections import deque
import urllib.parse
import click
import os
import csv
import importlib

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import plugins
from plugins import *


class Crawler:
    def __init__(self, url, plugins=[], verbose=True, verify=True):
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

        self.verbose = verbose

        self._init_plugins()

        if self.base_url != url:
            self.print(f"\nBase URL {url} resolved to {self.base_url}\n", 'yellow')

        self.base_netloc = urllib.parse.urlparse(self.base_url).netloc
        self.results_base_path = os.path.join(os.getcwd(), f"results-{self.base_netloc}")


    def _init_plugins(self):
        import importlib

        pluginList = []
        pluginPreList = []
        pluginPostList = []

        self.print("Loading plugins...")
        for fileName in os.listdir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "plugins")):
            pluginName = fileName[:-3]
            if fileName == '__init__.py' or fileName[-3:] != '.py' or fileName[0] == '_':
                continue

            if len(self.plugins) == 0 or pluginName in self.plugins:
                _module = getattr(plugins, pluginName)
                _class = getattr(_module, pluginName)
                instance = _class(self)
                if all(hasattr(instance, func) for func in ['get_results_header', 'get_results', 'parse']):
                    self.plugin_classes.append(instance)
                    pluginList.append(pluginName)

                if all(hasattr(instance, func) for func in ['process_html']):
                    self.plugin_pre_classes.append(instance)
                    pluginPreList.append(pluginName)
                    
                if all(hasattr(instance, func) for func in ['process_results']):
                    self.plugin_post_classes.append(instance)
                    pluginPostList.append(pluginName)
                    

        if len(pluginPreList):
            self.print(f"Loaded pre processing plugins: {', '.join(pluginPreList)}")
            
        if len(pluginList) > 0:
            self.print(f"Loaded parsing plugins: {', '.join(pluginList)}")
        else:
            self.print("Error no plugins loaded")
            exit(0)

        if len(pluginPostList):
            self.print(f"Loaded results processing plugins: {', '.join(pluginPostList)}")
        

    def _add_links(self, html_soup):
        links = html_soup.find_all('a')
        for link in links:
            try:
                abs_url = urllib.parse.urljoin(self.base_url, link['href'])
            except KeyError:
                continue

            if urllib.parse.urlparse(abs_url).netloc != self.base_netloc:
                continue

            if abs_url in self.resolve_cache:
                abs_url = self.resolve_cache[abs_url]
                
            if abs_url not in self.all_urls:
                self.urls.append(abs_url)
                self.all_urls.append(abs_url)

    def print(self, text, color='white'):
        if self.verbose:
            click.secho(text, fg=color)

    def printERR(self, text):
        self.print(text, 'red')

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
                with open(path, 'w') as f:
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
                    
            
    def crawl(self):
        while True:
            try:
                url = self.urls.pop()
            except IndexError:
                break

            if url in self.visited:                
                continue

            self.visited.append(url)
            self.print(f"\n-- Crawling {url}\n")

            try:
                response = get(url, verify=self.verify)
            except TooManyRedirects:
                self.printERR("Too many redirects, skipping")
                continue

            self.resolve_cache.update({url: response.url})
            if url != response.url and response.url in self.visited:
                self.print(f"{url} resolves to {response.url} and has already been visited", "yellow")
                continue
                
            html_soup = BeautifulSoup(response.text, 'html.parser')

            for plugin in self.plugin_pre_classes:
                html_soup = plugin.process_html(html_soup)

            self._add_links(html_soup)

            for plugin in self.plugin_classes:
                plugin.parse(html_soup, url=url)
                
        self.save_results()


@click.command()
@click.argument('url')
@click.option('--plugin', multiple=True, help="Only load named plugins")
@click.option('--verbose/--quiet', default=True, help="Show or supress output")
@click.option('--verify/--noverify', default=True, help="Verify SSLs")
def main(url, verbose, plugin, verify):
    """This script will crawl give URL and analyse the output using plugins"""
    crawler = Crawler(url, verbose=verbose, plugins=plugin, verify=verify)
    crawler.crawl()

if __name__ == '__main__':
    main()
