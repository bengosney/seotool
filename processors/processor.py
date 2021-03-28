from typing import List, Optional

import pluggy

from processors import hookspecs, plugins
from processors.dataModels import ResultSet


class Processor:
    def __init__(self, crawler, enabled: Optional[List] = None, disabled: List = []):
        self.crawler = crawler
        self.enabled = enabled
        self.disabled = disabled

        self.plugin_names = []
        self.pm = self.get_plugin_manager()
        self.hook = self.pm.hook

    def get_plugin_manager(self):
        pm = pluggy.PluginManager("seo_processor")
        pm.add_hookspecs(hookspecs.processor)
        pm.load_setuptools_entrypoints("seo_processor")

        for plugin in plugins.__all__:
            __import__(f"processors.plugins.{plugin}")
            _module = getattr(plugins, plugin)
            _class = getattr(_module, plugin)
            try:
                pm.register(_class(self.crawler), plugin)
            except TypeError:
                pm.register(_class(), plugin)

        plugin_names = [p for p, _ in pm.list_name_plugin()]

        if self.enabled is None:
            self.enabled = plugin_names

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

    def process_results_sets(self, resultsSets: List[ResultSet]) -> None:
        return self.hook.process_output(resultsSets=resultsSets)  # type: ignore
