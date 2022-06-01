# Standard Library

# Standard Library
from typing import Callable

# Third Party
import pluggy
from bs4 import BeautifulSoup
from click.decorators import FC

# First Party
from engines.dataModels import response
from processors.dataModels import ResultSet

hookspec_processor = pluggy.HookspecMarker("seo_processor")


class processor:
    @hookspec_processor
    def process_html(self, html: BeautifulSoup, url: str, response: response, status_code: int) -> None:
        """Pre-process the html before any checks are run."""
        ...

    @hookspec_processor
    def process(self, html: BeautifulSoup, url: str, response: response, status_code: int) -> None:
        """Process the html."""
        ...

    @hookspec_processor
    def get_results_set(self) -> ResultSet:
        """Get a results object."""
        ...

    @hookspec_processor
    def process_output(self, resultsSets: list[ResultSet]):
        """Process the data into a format."""
        ...

    @hookspec_processor
    def get_options(self) -> list[Callable[[FC], FC]]:
        """Get any cli arguments."""
        ...

    @hookspec_processor
    def should_process(self, url: str, response: response) -> bool:
        """Do we want to process this url?"""
        ...

    @hookspec_processor(firstresult=True)
    def log(self, line: str, style: str) -> None:
        """Output any log messages."""
        ...

    @hookspec_processor(firstresult=True)
    def log_error(self, line: str) -> None:
        """Output any error messages."""
        ...
