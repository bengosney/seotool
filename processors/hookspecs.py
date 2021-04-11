# Standard Library
from typing import Dict, List, Optional

# Third Party
import pluggy
from bs4 import BeautifulSoup

# First Party
from processors.dataModels import ResultSet

hookspec_processor = pluggy.HookspecMarker("seo_processor")


class processor:
    @hookspec_processor
    def process_html(self, html: BeautifulSoup, url: str, response: Dict, status_code: str) -> None:
        """Pre-process the html before any checks are run."""

    @hookspec_processor
    def process(self, html: BeautifulSoup, url: str, response: Dict, status_code: str) -> None:
        """Process the html."""

    @hookspec_processor
    def get_results_set(self) -> Optional[ResultSet]:
        """Get a results object."""

    @hookspec_processor
    def process_output(self, resultsSets: List[ResultSet]):
        """Process the data into a format."""

    @hookspec_processor
    def get_options(self):
        """Get any cli arguments."""

    @hookspec_processor(firstresult=True)
    def log(self, line, style):
        """Output any log messages."""
