# Third Party
from rich.console import Console

# First Party
from processors import hookimpl_processor


class LogRich:
    def __init__(self):
        self.console = Console()
        self.error_console = Console(stderr=True, style="bold red")

    @hookimpl_processor
    def log(self, line, style):
        self.console.print(line, style=style)
        return True

    @hookimpl_processor
    def log_error(self, line):
        self.error_console.print(line)
        return True
