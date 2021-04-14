# Third Party
from bs4 import BeautifulSoup

# First Party
from processors.plugins.ScriptTags import ScriptTags
from seotool.crawl import Crawler

c = Crawler("example.com")


def test_script_tabs():
    html = BeautifulSoup(
        """
<script src="/script.js"></script>
<script src="http://www.example.com/script.js"></script>
<script>console.log('Hello World!');</script>
    """,
        "html.parser",
    )

    plugin = ScriptTags(c)
    plugin.process(html=html, url="/")
    res = plugin.get_results_set()

    expected_data = [
        {"src": "/script.js", "url": "/"},
        {"src": "http://www.example.com/script.js", "url": "/"},
    ]

    assert res.data == expected_data
