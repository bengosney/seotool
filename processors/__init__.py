import pluggy

from processors.dataModels import ResultSet
from processors.processor import Processor

hookimpl_processor = pluggy.HookimplMarker("seo_processor")

__all__ = [
    "ResultSet",
    "Processor",
    "hookimpl_processor",
]
