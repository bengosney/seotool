import pluggy

from processors.dataModels import ResultSet
from processors.processor import Processor

hookimpl_processor = pluggy.HookimplMarker("seo_processor")
hookimpl_pre_processor = pluggy.HookimplMarker("seo_processor")
hookimpl_output_processor = pluggy.HookimplMarker("seo_processor")

__all__ = [
    "ResultSet",
    "Processor",
    "hookimpl_processor",
    "hookimpl_pre_processor",
    "hookimpl_output_processor",
]
