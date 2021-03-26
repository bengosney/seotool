from typing import List

import pluggy

from processors import hookspecs, plugins


class PreProcessor:
    def __init__(self, crawler, enabled: List = [], disabled: List = []):
        self.crawler = crawler
        self.enabled = enabled if len(enabled) else plugins.__all__
        self.disabled = disabled

        self.hook = self.get_plugin_manager().hook

    def get_plugin_manager(self):
        pm = pluggy.PluginManager("pre_processors")
        pm.add_hookspecs(hookspecs.pre_processor)
        pm.load_setuptools_entrypoints("pre_processors")

        for plugin in plugins.__all__:
            __import__(f"processors.plugins.{plugin}")
            _module = getattr(plugins, plugin)
            _class = getattr(_module, plugin)
            try:
                pm.register(_class(self.crawler))
            except TypeError:
                pm.register(_class())

        return pm

    def process_html(self, html, url, status_code, response):
        self.hook.process_html(html=html, response=response, url=url, status_code=status_code)  # type: ignore
