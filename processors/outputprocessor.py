from typing import List

import pluggy

from processors import hookspecs, plugins
from processors.dataModels import ResultSet


class OutputProcessor:
    def __init__(self, crawler, enabled: List = [], disabled: List = []) -> None:
        self.crawler = crawler
        self.enabled = enabled if len(enabled) else plugins.__all__
        self.disabled = disabled

        self.pm = self.get_plugin_manager()
        self.hook = self.pm.hook

    def get_plugin_manager(self) -> pluggy.PluginManager:
        pm = pluggy.PluginManager("output_processors")
        pm.add_hookspecs(hookspecs.output_processor)
        pm.load_setuptools_entrypoints("output_processors")
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

    def process_results_sets(self, resultsSets: List[ResultSet]) -> None:
        return self.hook.process_output(resultsSets=resultsSets)  # type: ignore
