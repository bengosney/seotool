#!/usr/bin/env python3

# Standard Library
import asyncio
import contextlib
import pathlib

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
    for plugin in Crawler.get_plugin_list():
        click.echo(f"\t{plugin}")

    ctx.exit()


@click.command()
@click.argument("url", required=False)
@click.option("--plugin", multiple=True, help="Only load named plugins")
@click.option("--disable", multiple=True, help="Disable plugins")
@click.option("--verbose/--quiet", default=True, help="Show or suppress output")
@click.option("--verify/--noverify", default=True, help="Verify SSLs")
@click.option("--delay", help="Delay between crawling pages", default=0)
@click.option("--engine", default="playwright", help="Fetch and parse engine to use")
@click.option("--workers", type=int, default=0, help="Number of workers to run, defaults to CPU core count")
@click.option(
    "--list-plugins", is_flag=True, callback=list_plugins, expose_value=False, is_eager=True, help="Lists plugins"
)
@click.option("--ignore-robots", default=False, is_flag=True, help="Ignores the robots.txt for dissalowed urls")
@click.version_option()
def main(url, verbose, plugin, verify, disable, delay, engine, workers: int, ignore_robots, **kwargs):
    """This script will crawl give URL and analyse the output using plugins."""

    if verbose:
        traceback_install()

    if url is None:
        console = Console()
        ctx = click.get_current_context()
        with contextlib.suppress(FileNotFoundError):
            rawMarkdown = pathlib.Path("README.md").read_text()
            md = Markdown(rawMarkdown)
            console.print(md)
            console.print("\n")
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
        worker_count=workers,
        ignore_robots=ignore_robots,
    )
    asyncio.run(crawler.crawl())


options = Crawler.get_extra_options()
for plugin_options in options:
    for func in plugin_options:
        func(main)

if __name__ == "__main__":
    main()
