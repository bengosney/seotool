#!/usr/bin/env python3

# Standard Library
import asyncio

# Third Party
import click
from rich.console import Console
from rich.markdown import Markdown
from rich.traceback import install as traceback_install

# First Party
from seotool.crawl import Crawler


def list_plugins(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return

    click.secho("\nAvailable plugins:\n", fg="green")
    plugins = Crawler.get_plugin_list()
    [click.echo(f"\t{plugin}") for plugin in plugins]
    ctx.exit()


@click.command()
@click.argument("url", required=False)
@click.option("--plugin", multiple=True, help="Only load named plugins")
@click.option("--disable", multiple=True, help="Disable plugins")
@click.option("--verbose/--quiet", default=True, help="Show or suppress output")
@click.option("--verify/--noverify", default=True, help="Verify SSLs")
@click.option("--delay", help="Delay between crawling pages", default=0)
@click.option("--engine", default="playwright", help="Fetch and parse engine to use")
@click.option("--workers", type=int, default=None, help="Number of workers to run, defaults to CPU core count")
@click.option(
    "--list-plugins", is_flag=True, callback=list_plugins, expose_value=False, is_eager=True, help="Lists plugins"
)
@click.version_option()
def main(url, verbose, plugin, verify, disable, delay, engine, workers, **kwargs):
    """This script will crawl give URL and analyse the output using plugins."""

    if verbose:
        traceback_install()

    if url is None:
        console = Console()
        ctx = click.get_current_context()
        try:
            with open("README.md") as f:
                rawMarkdown = f.read()
            md = Markdown(rawMarkdown)
            console.print(md)
            console.print("\n")
        except FileNotFoundError:
            pass
        console.print(ctx.get_help())
        ctx.exit()

    crawler = Crawler(
        url,
        verbose=verbose,
        plugins=plugin,
        verify=verify,
        disabled=disable,
        delay=delay,
        engine=engine,
        plugin_options=kwargs,
    )
    asyncio.run(crawler.crawl())


options = Crawler.get_extra_options()
for plugin_options in options:
    for func in plugin_options:
        func(main)

if __name__ == "__main__":
    main()
