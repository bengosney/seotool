# Third Party
import pluggy

# First Party
from processors.dataModels import BaseResultData, ResultSet
from processors.processor import Processor

hookimpl_processor = pluggy.HookimplMarker("seo_processor")

__all__ = [
    "ResultSet",
    "BaseResultData",
    "Processor",
    "hookimpl_processor",
]
