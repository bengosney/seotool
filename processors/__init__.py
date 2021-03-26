import pluggy

from processors.dataModels import ResultSet  # noqa
from processors.outputprocessor import OutputProcessor  # noqa
from processors.preprocessor import PreProcessor  # noqa
from processors.processor import Processor  # noqa

hookimpl_processor = pluggy.HookimplMarker("processors")
hookimpl_pre_processor = pluggy.HookimplMarker("pre_processors")
hookimpl_output_processor = pluggy.HookimplMarker("output_processors")
