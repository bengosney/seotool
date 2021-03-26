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
        pm = pluggy.PluginManager("processors")
        pm.add_hookspecs(hookspecs.processor)
        pm.load_setuptools_entrypoints("processors")
        pm.enable_tracing()

        for plugin in plugins.__all__:
            __import__(f"processors.plugins.{plugin}")
            _module = getattr(plugins, plugin)
            _class = getattr(_module, plugin)
            try:
                pm.register(_class(self.crawler))
            except TypeError:
                pm.register(_class())

        return pm

    def process(self, html, url, status_code, response) -> None:
        self.hook.process(html=html, response=response, url=url, status_code=status_code)

    def get_results_sets(self) -> List[ResultSet]:
        return self.hook.get_results_set()
