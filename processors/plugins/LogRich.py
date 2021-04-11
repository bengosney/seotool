# Third Party
from rich.console import Console

# First Party
from processors import hookimpl_processor


class LogRich:
    def __init__(self):
        self.console = Console()

    @hookimpl_processor
    def log(self, line, style):
        self.console.print(f"{line}", style=style)
        return True
