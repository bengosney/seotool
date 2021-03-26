import pluggy

from processors.dataModels import ResultSet
from processors.outputprocessor import OutputProcessor
from processors.preprocessor import PreProcessor
from processors.processor import Processor

hookimpl_processor = pluggy.HookimplMarker("processors")
hookimpl_pre_processor = pluggy.HookimplMarker("pre_processors")
hookimpl_output_processor = pluggy.HookimplMarker("output_processors")

__all__ = [
    "ResultSet",
    "OutputProcessor",
    "PreProcessor",
    "Processor",
    "hookimpl_processor",
    "hookimpl_pre_processor",
    "hookimpl_output_processor",
]
