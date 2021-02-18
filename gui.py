from rich.console import Console
from rich.layout import Layout
from rich.live import Live

from rich.panel import Panel

from time import sleep

console = Console()
layout = Layout()

# Divide the "screen" in to three parts
layout.split(
    Layout(Panel('SEO Tool'), name="header", size=3),
    Layout(ratio=1, name="main"),
    Layout(size=10, name="footer"),
)
# Divide the "main" layout in to "side" and "body"
layout["main"].split(
    Layout(name="side"),
    Layout(name="body", ratio=2),
    direction="horizontal"
)
# Divide the "side" layout in to two
layout["side"].split(Layout(), Layout())

with Live(layout, screen=True):
    while True:
        sleep(1)
