# Standard Library
import contextlib
import inspect
from typing import TYPE_CHECKING, Any, Awaitable, Callable, cast

# Third Party
import pluggy
from bs4 import BeautifulSoup
from click.decorators import FC

# First Party
from engines.dataModels import response
from processors import hookspecs, plugins
from processors.dataModels import ResultSet

if TYPE_CHECKING:
    # First Party
    from seotool.crawl import Crawler

# Locals
from .hookType import HookType


class Processor:
    def __init__(
        self,
        crawler: "Crawler",
        enabled: list[str] | None = None,
        disabled: list[str] = [],
        plugin_options: dict[str, Any] = {},
    ):
        self.crawler = crawler
        self.enabled = enabled
        self.disabled = disabled
        self.plugin_options = plugin_options

        self.plugin_names: list[str] = []
        self.pm = self.get_plugin_manager()
        self.hook: HookType = cast(HookType, self.pm.hook)

    def get_plugin_manager(self) -> pluggy.PluginManager:
        pm = pluggy.PluginManager("seo_processor")
        pm.add_hookspecs(hookspecs.processor)
        plugin_default_disabled = []
        for plugin in plugins.__all__:
            __import__(f"processors.plugins.{plugin}")
            _module = getattr(plugins, plugin)
            _class = getattr(_module, plugin)

            args = {"crawler": self.crawler, **self.plugin_options}
            sig = inspect.signature(_class)
            supported_prams = [p.name for p in sig.parameters.values()]
            pm.register(_class(**{key: value for (key, value) in args.items() if key in supported_prams}), plugin)
            with contextlib.suppress(AttributeError):
                if _class.default_disabled:
                    plugin_default_disabled.append(plugin)

        pm.load_setuptools_entrypoints("seo_processor")
        plugin_names = [p for p, _ in pm.list_name_plugin()]

        if self.enabled is None:
            self.enabled = [n for n in plugin_names if n not in plugin_default_disabled]

        for plugin in plugin_names:
            if plugin not in self.enabled or plugin in self.disabled:
                pm.set_blocked(plugin)
            else:
                self.plugin_names.append(plugin)

        return pm

    def process_html(self, html: BeautifulSoup, url: str, status_code: int, response: response) -> None:
        self.hook.process_html(html=html, response=response, url=url, status_code=status_code)

    def process(self, html: BeautifulSoup, url: str, status_code: int, response: response) -> None:
        self.hook.process(html=html, response=response, url=url, status_code=status_code)

    def get_results_sets(self) -> list[ResultSet]:
        return self.hook.get_results_set()

    def process_results_sets(self, resultsSets: list[ResultSet]) -> list[Awaitable[None]]:
        return [a for a in self.hook.process_output(resultsSets=resultsSets) if a is not None]

    def get_options(self) -> list[Callable[[FC], FC]]:
        return self.hook.get_options()

    def should_process(self, url: str, response: response) -> bool:
        return all(self.hook.should_process(url=url, response=response))

    def log(self, line, style) -> None:
        self.hook.log(line=line, style=style)

    def log_error(self, line) -> None:
        self.hook.log_error(line=line)
