#!/usr/bin/env python3

import asyncio
from pprint import pprint

import click

from seotool.crawl import Crawler


def list_plugins(ctx, param, value):
    plugins = Crawler.get_plugin_list()
    [click.echo(plugin) for plugin in plugins]
    ctx.exit()


@click.command()
@click.argument("url", required=False)
@click.option("--plugin", multiple=True, help="Only load named plugins")
@click.option("--disable", multiple=True, help="Disable plugins")
@click.option("--verbose/--quiet", default=True, help="Show or suppress output")
@click.option("--verify/--noverify", default=True, help="Verify SSLs")
@click.option("--delay", help="Delay between crawling pages", default=0)
@click.option("--engine", default="pyppeteer", help="Fetch and parse engine to use")
# @click.option("--list-plugins",  is_flag=True, callback=list_plugins, expose_value=False, is_eager=True, help="Lists plugins")
@click.version_option()
def main(url, verbose, plugin, verify, disable, delay, engine, **kwargs):
    """This script will crawl give URL and analyse the output using plugins"""

    pprint(kwargs)

    if url is None:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()

    crawler = Crawler(url, verbose=verbose, plugins=plugin, verify=verify, disabled=disable, delay=delay, engine=engine, plugin_options=kwargs)
    asyncio.run(crawler.crawl())


options = Crawler.get_plugin_options()
for plugin_options in options:
    for func in plugin_options:
        func(main)

if __name__ == "__main__":
    main()
