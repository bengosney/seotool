#!/usr/bin/env python3

import asyncio

import click

from .crawl import Crawler


@click.command()
@click.argument("url", required=False)
@click.option("--plugin", multiple=True, help="Only load named plugins")
@click.option("--disable", multiple=True, help="Disable plugins")
@click.option("--verbose/--quiet", default=True, help="Show or suppress output")
@click.option("--verify/--noverify", default=True, help="Verify SSLs")
@click.option("--list-plugins", is_flag=True, help="Lists plugins")
@click.option("--delay", help="Delay between crawling pages", default=0)
@click.option("--pyppeteer/--requests", default=True, help="Select the fetch and parse method")
def main(url, verbose, plugin, verify, disable, list_plugins, delay, pyppeteer):
    """This script will crawl give URL and analyse the output using plugins"""
    if list_plugins:
        plugins = Crawler.get_plugin_list()
        [click.echo(plugin) for plugin in plugins]
    else:
        if url is None:
            ctx = click.get_current_context()
            click.echo(ctx.get_help())
            ctx.exit()

        engine = "pyppeteer" if pyppeteer else "requests"
        crawler = Crawler(url, verbose=verbose, plugins=plugin, verify=verify, disabled=disable, delay=delay, engine=engine)
        asyncio.run(crawler.crawl())


if __name__ == "__main__":
    main()
