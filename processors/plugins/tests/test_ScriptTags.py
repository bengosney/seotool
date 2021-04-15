# Third Party
from bs4 import BeautifulSoup

# First Party
from processors.plugins.ScriptTags import ResultData, ScriptTags
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
        ResultData("/script.js", "/"),
        ResultData("http://www.example.com/script.js", "/"),
    ]

    assert res.data == expected_data
