#!/usr/bin/env python3

from requests import get
from bs4 import BeautifulSoup
from collections import deque
import urllib.parse
import click
import os
import csv
import importlib

import plugins
from plugins import *


class Crawler:
    def __init__(self, url, plugins=[], verbose=True):
        self.base_url = url
        self.plugins = plugins
        self.plugin_classes = []
        self.base_netloc = urllib.parse.urlparse(self.base_url).netloc

        self.visited = deque([])
        self.urls = deque([self.base_url])

        self.verbose = verbose

        self._init_plugins()

    def _init_plugins(self):
        import importlib

        pluginList = []

        self.print("Loading plugins...")
        for fileName in os.listdir(os.path.join(os.path.dirname(__file__), "plugins")):
            pluginName = fileName[:-3]
            if fileName == '__init__.py' or fileName[-3:] != '.py' or fileName[0] == '_':
                continue

            if len(self.plugins) == 0 or pluginName in self.plugins:
                _module = getattr(plugins, pluginName)
                _class = getattr(_module, pluginName)            
                self.plugin_classes.append(_class(self))
                pluginList.append(pluginName)

        if len(pluginList) > 0:
            self.print("Loaded {}".format(", ".join(pluginList)))
        else:
            self.print("Error no plugins loaded")
            exit(0)
            

    def _add_links(self, html_soup):
        links = html_soup.find_all('a')
        for link in links:
            try:
                abs_url = urllib.parse.urljoin(self.base_url, link['href'])
            except KeyError:
                continue

            if urllib.parse.urlparse(abs_url).netloc != self.base_netloc:
                continue
        
            if abs_url not in self.urls and abs_url not in self.visited:
                self.urls.append(abs_url)

    def print(self, text, color='white'):
        if self.verbose:
            click.secho(text, fg=color)

    def printERR(self, text):
        self.print(text, 'red')

    def save_results(self):
        base_path = os.path.join(os.path.dirname(__file__), "results", self.base_netloc)
        try:
            os.makedirs(base_path)
        except FileExistsError:
            pass
        
        for plugin in self.plugin_classes:
            plugin_name = plugin.__class__.__name__
            path = os.path.join(base_path, "{}.csv".format(plugin_name))
            
            with open(path, 'w') as f:
                w = csv.writer(f)
                w.writerow(plugin.get_results_headder())
                w.writerows(plugin.get_results())
            
    def crawl(self):
        while True:
            try:
                url = self.urls.pop()
            except IndexError:
                break

            if url in self.visited:                
                continue
            
            self.visited.append(url)
            self.print("\n-- Crawling {}\n".format(url))
            
            response = get(url)
            html_soup = BeautifulSoup(response.text, 'html.parser')

            self._add_links(html_soup)

            for plugin in self.plugin_classes:
                plugin.parse(html_soup, url=url)
                
        self.save_results()


@click.command()
@click.argument('url')
@click.option('--plugin', multiple=True, help="Only load named plugins")
@click.option('--verbose', default=True)
def main(url, verbose, plugin):
    """This script will crawl give URL and analyse the output using plugins"""
    crawler = Crawler(url, verbose=verbose, plugins=plugin)
    crawler.crawl()

if __name__ == '__main__':
    main()
