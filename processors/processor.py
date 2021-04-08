# Standard Library
import inspect
from typing import Any, Awaitable, Dict, List, Optional

# Third Party
import pluggy

# First Party
from processors import hookspecs, plugins
from processors.dataModels import ResultSet


class Processor:
    def __init__(
        self, crawler, enabled: Optional[List] = None, disabled: List = [], plugin_options: Dict[str, Any] = {}
    ):
        self.crawler = crawler
        self.enabled = enabled
        self.disabled = disabled
        self.plugin_options = plugin_options

        self.plugin_names = []
        self.pm = self.get_plugin_manager()
        self.hook = self.pm.hook

    def get_plugin_manager(self):
        pm = pluggy.PluginManager("seo_processor")
        pm.add_hookspecs(hookspecs.processor)
        pm.load_setuptools_entrypoints("seo_processor")
        plugin_default_disabled = []
        for plugin in plugins.__all__:
            __import__(f"processors.plugins.{plugin}")
            _module = getattr(plugins, plugin)
            _class = getattr(_module, plugin)

            args = {"crawler": self.crawler, **self.plugin_options}
            sig = inspect.signature(_class)
            supported_prams = [p.name for p in sig.parameters.values()]
            pm.register(_class(**{key: value for (key, value) in args.items() if key in supported_prams}), plugin)
            try:
                if _class.default_disabled:
                    plugin_default_disabled.append(plugin)
            except AttributeError:
                pass

        plugin_names = [p for p, _ in pm.list_name_plugin()]

        if self.enabled is None:
            self.enabled = [n for n in plugin_names if n not in plugin_default_disabled]

        for plugin in plugin_names:
            if plugin not in self.enabled or plugin in self.disabled:
                pm.set_blocked(plugin)
            else:
                self.plugin_names.append(plugin)

        return pm

    def process_html(self, html, url, status_code, response):
        self.hook.process_html(html=html, response=response, url=url, status_code=status_code)  # type: ignore

    def process(self, html, url, status_code, response) -> None:
        self.hook.process(html=html, response=response, url=url, status_code=status_code)  # type: ignore

    def get_results_sets(self) -> List[ResultSet]:
        return self.hook.get_results_set()  # type: ignore

    def process_results_sets(self, resultsSets: List[ResultSet]) -> List[Awaitable]:
        return self.hook.process_output(resultsSets=resultsSets)  # type: ignore

    def get_options(self) -> List:
        return self.hook.get_options()  # type: ignore
