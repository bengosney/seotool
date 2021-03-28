from typing import List

import pluggy

from processors import hookspecs, plugins
from processors.dataModels import ResultSet


class Processor:
    def __init__(self, crawler, enabled: List = [], disabled: List = []):
        self.crawler = crawler
        self.enabled = enabled if len(enabled) else plugins.__all__
        self.disabled = disabled

        self.pm = self.get_plugin_manager()
        self.hook = self.pm.hook

    def get_plugin_manager(self):
        pm = pluggy.PluginManager("seo_processor")
        pm.add_hookspecs(hookspecs.processor)
        pm.load_setuptools_entrypoints("seo_processor")
        pm.enable_tracing()

        for plugin in plugins.__all__:
            __import__(f"processors.plugins.{plugin}")
            _module = getattr(plugins, plugin)
            _class = getattr(_module, plugin)
            try:
                pm.register(_class(self.crawler), plugin)
            except TypeError:
                pm.register(_class(), plugin)

        return pm

    def process_html(self, html, url, status_code, response):
        self.hook.process_html(html=html, response=response, url=url, status_code=status_code)  # type: ignore

    def process(self, html, url, status_code, response) -> None:
        self.hook.process(html=html, response=response, url=url, status_code=status_code)  # type: ignore

    def get_results_sets(self) -> List[ResultSet]:
        return self.hook.get_results_set()  # type: ignore

    def process_results_sets(self, resultsSets: List[ResultSet]) -> None:
        return self.hook.process_output(resultsSets=resultsSets)  # type: ignore

    @property
    def plugin_names(self):
        return [p for p, _ in self.pm.list_name_plugin()]
